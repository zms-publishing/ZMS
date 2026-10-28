# llmtools: How agent mode works

1. `ZMSLLMConnector.chat_with_tools()` asks the _ZMSLLMToolsAdapter_ for the active
   tool schemas and sends them with the conversation to the provider (OpenAI,
   Anthropic Claude, GitHub Models, Ollama). Providers convert the OpenAI-style
   schema to their native format; the reply is always normalized to
   message.tool_calls = [{id, type: 'function', function: {name, arguments}}].
2. For each tool call the adapter looks for a script named llmtool_<name> in the
   selected toolset and calls it as llmtool_<name>(connector, context, args).
   - args is a dict (already JSON-decoded).
   - If the toolset has no such script, the built-in executor in
     Products.zms.llmtools.execute_llmtool() is used as fallback.
   - Exceptions are caught and returned to the model as {'error': '...'}.
3. The JSON-serializable result is appended as a 'tool' message and the loop
   continues until the model answers with plain text (max_rounds, default 5).

Parameters passed to every executor:

| Parameter | Description |
| --- | --- |
| `connector` | The ZMSLLMConnector (`connector.getConfProperty('llm.xyz')`). |
| `context` | The ZMS node the chat was started from; use `context.getRootElement()`, `context.metaobj_manager`, `context.getLLMConnector()`, ... |
| `args` | Dict with the arguments declared in the tool schema. |


## Toolset structure

A toolset is a ZMSLibrary meta-object (e.g. _com.zms.llmtools.ollama_)

  - id must end with '_llmtools', or end with '_connector' and live in a package
    starting with 'com.zms.llmtools.' (as this one: com.zms.llmtools.ollama).
  - get_llmtools            External Method, returns the tool schema list
  - llmtool_<name>          External Method per tool, executes the call
  - readme                  infos

Select the toolset in the ZMS-UI _AI-Lab > Configuration > LLM Tools_ (property `llm.llmtools.id`). Empty = built-in tools of llmtools.py.


## Customizing existing tools

Hide tools from the model (e.g. no destructive tools): filter the built-ins in
get_llmtools. A tool that is not listed is never offered to the model.

```py
import copy
from Products.zms import llmtools

READ_ONLY = {'list_content_types', 'get_content_type', 'export_content_type_xml'}

def get_llmtools(connector, context):
    tools = copy.deepcopy(llmtools.BUILTIN_LLM_TOOLS)
    return [t for t in tools if t['function']['name'] in READ_ONLY]
```

Change behaviour of one tool: edit its llmtool_<name> script, e.g. block deletion
of protected content types:

```py
from Products.zms import llmtools

PROTECTED = ('ZMSDocument', 'ZMSFolder', 'ZMSTextarea')

def llmtool_delete_content_type(connector, context, args):
    if args.get('id') in PROTECTED:
        return {'error': "Content type '%s' is protected." % args.get('id')}
    return llmtools.execute_llmtool('delete_content_type', args or {}, context)
```

Improve how the model uses a tool: tune the 'description' texts in the schema.
Descriptions are the only guidance the model gets - state when to use the tool,
what the arguments mean, and which tool to call first.


## Adding a new agentic function

_Example_: a tool that returns the title and URL of all direct child pages of a
ZMS node. Three steps are required.

**Step 1** - declare the tool in get_llmtools (OpenAI function-calling format,
parameters is a JSON Schema object, everything must be JSON-serializable):

```py
import copy
from Products.zms import llmtools

def get_llmtools(connector, context):
    tools = copy.deepcopy(llmtools.BUILTIN_LLM_TOOLS)
    tools.append({
        "type": "function",
        "function": {
            "name": "list_child_pages",
            "description": (
                "List title and URL of the direct child pages of a ZMS node. "
                "Use it to explore the site tree before reading or changing content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute ZMS path, e.g. 'content/news'. Empty = current node.",
                    },
                    "lang": {
                        "type": "string",
                        "description": "Language id, e.g. 'eng'. Default: 'eng'.",
                    },
                },
                "required": [],
            },
        },
    })
    return tools
```

get_llmtools may also return {"tools": [...]}. Every entry must have
type == 'function' and function.name, otherwise the adapter raises an error.

**Step 2 **- add the executor script llmtool_list_child_pages (External Method,
signature (connector, context, args), return a JSON-serializable dict):

```py
def llmtool_list_child_pages(connector, context, args):
    args = args or {}
    request = context.REQUEST
    request.set('lang', args.get('lang') or 'eng')
    node = context
    path = (args.get('path') or '').strip('/')
    if path:
        try:
            node = context.getRootElement().getHome().restrictedTraverse(path)
        except Exception:
            return {'error': "Path '%s' not found." % path}
    pages = [
        {
            'id': child.id,
            'title': child.getTitle(request),
            'url': child.getHref2IndexHtml(request),
        }
        for child in node.getChildNodes(request, meta_types=['ZMSDocument', 'ZMSFolder'])
    ]
    return {'path': path, 'count': len(pages), 'pages': pages}
```

**Step 3** - register both attributes in the toolset. Either use the meta-object
editor (Content Model > ollama_connector > add attribute of type 'External Method'
with id 'llmtool_list_child_pages') or add it to `__init__.yaml` of this package:

```yml
    - id: llmtool_list_child_pages
      name: 'Tool: list_child_pages'
      mandatory: 0
      multilang: 0
      repetitive: 0
      type: External Method
```

Place the script file next to the others as llmtool_list_child_pages.py.
(get_llmtools was already registered, only its body changes.)

Then open ZMSLLMConnector > Chat, enable "Agent" and ask:
"Which child pages does content/news have?"


## Tool that calls external services

Executors run inside the Zope process, so any Python library is usable. Read
configuration from the connector and always set timeouts:

```py
import requests

def llmtool_search_wiki(connector, context, args):
    base = connector.getConfProperty('llm.wiki.url', 'https://wiki.example.org')
    try:
        r = requests.get(base + '/api/search', params={'q': args['query']}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {'error': 'Wiki search failed: %s' % e}
    return {'hits': r.json().get('results', [])[:10]}
```


## Tool that changes content (write access)

Executors run as the logged-in ZMI user. Use restrictedTraverse so Zope
permissions apply. Guard destructive operations, require explicit arguments and report
what was done so the model can tell the user:

```py
def llmtool_set_page_title(connector, context, args):
    if not args.get('path') or not args.get('title'):
        return {'error': "Arguments 'path' and 'title' are required."}
    request = context.REQUEST
    lang = args.get('lang') or 'eng'
    request.set('lang', lang)
    try:
        # restrictedTraverse enforces the Zope permissions of the current user
        node = context.getRootElement().getHome().restrictedTraverse(args['path'].strip('/'))
    except Exception:
        return {'error': "Path '%s' not found or not permitted." % args['path']}
    old = node.getTitle(request)
    node.setObjProperty('title', args['title'], lang)
    node.onChangeObj(request)
    return {'path': args['path'], 'old_title': old, 'new_title': args['title']}
```

## Best practices

- Keep tools small and single-purpose; let the model combine them.
- Return {'error': 'clear message'} instead of raising, include hints such as
"Use list_content_types first". The model reads the message and retries.
- Limit result size (e.g. first 20 items, truncated text); results are sent
back to the model and consume its context window.
- Return only JSON-serializable data (str, int, float, bool, list, dict).
- Use snake_case names; the script id must be exactly 'llmtool_' + name.
- Small local models (Ollama) may print the call as JSON text instead of a real
tool call. ZMS parses such text calls as fallback, but keep schemas simple:
few arguments, flat types, precise descriptions.
- Test an executor without the model:

    ```py
    connector = context.getLLMConnector()
    from Products.zms import llmtools
    adapter = llmtools.ZMSLLMToolsAdapter(connector, context)
    print(adapter.get_llmtools())
    print(adapter.execute_llmtool('list_child_pages', {'path': 'content'}))
    ```

## Creating your own toolset

To keep customizations separate from this reference toolset:

  1. Copy this package folder (e.g. to com.zms.llmtools.myproject), rename the
     package and the library id (e.g. myproject_connector) in `__init__.yaml`, or
     create a ZMSLibrary named myproject_llmtools in the content model.
  2. Keep _get_llmtools_ and _add/remove llmtool_<name>_ scripts.
  3. Select it under ZMSLLMConnector > Configuration > LLM Tools.

## Troubleshooting

> "Connector '...' is missing required script `get_llmtools`"
* The toolset has no _get_llmtools_ attribute of type External Method/py.

>"each tool must include type='function' and function.name"
* A schema entry is malformed.

> Model never calls the tool
* The tool is not returned by _get_llmtools_, the description is unclear, or the model has no tool support (try another model/provider).

> "Connector '...' llmtool_<name> failed: ..."
* Exception inside your executor; check the Zope event log for the traceback.
