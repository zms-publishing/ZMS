# D. For Developers

This chapter covers setting up a development environment, understanding the ZMS object model, and using the ZMS Python/TAL API. It also explains cache-control integration and how to extend ZMS with custom content classes, actions, and themes.

> **See also:**
> - [develop_intro_en.md](develop_intro_en.md) — full installation walkthrough
> - [develop_api_exampels_en.md](develop_api_exampels_en.md) — annotated API code examples
> - [develop_cache.md](develop_cache.md) — proxy cache and NGINX control in depth
> - [admin_intro_en.md](admin_intro_en.md) — configuration menu reference (content model design)

---

## 1. Development Environment Setup

Follow the standard installation from [A. Getting Started](a_getting_started.md). For development, the editable install is strongly recommended:

```console
~$ ./pip install --use-pep517 --config-settings editable_mode=compat \
       -e git+https://github.com/zms-publishing/ZMS.git@main#egg=Products.zms
```

This places the ZMS source under `/home/zope/src/ZMS/` so code changes take effect after a Zope restart (or without restart for TAL templates and Python scripts stored in ZODB).

### Enabling debug mode

Set the system property `ZMS.debug = True` in your ZMS instance to activate:

- Detailed error tracebacks in the ZMI.
- Auto-sync of the Repository Manager on model changes.
- Additional logging output.

### Running tests

```console
~$ cd /home/zope/src/ZMS
~$ python -m pytest -q
```

> **Note:** Tests import Zope/OFS modules. A fully installed Zope environment is required — `pytest` alone without Zope will fail.

---

## 2. The ZMS Object Model

### 2.1 ZODB persistence

ZMS objects are stored in the Zope Object Database (ZODB), a Python object graph database. Each ZMS content node is a persistent Python object. The object graph is traversed by Zope to handle URL requests.

### 2.2 Content tree structure

```
ZMS (site root)
└── content/
    ├── metaobj_manager/       ← content class definitions
    ├── metacmd_manager/       ← custom actions
    ├── zmsindex_catalog       ← fast ID→path lookup catalog
    ├── catalog_eng            ← ZCatalog for English full-text search
    └── e1/                    ← ZMSFolder (root content node)
        ├── e2/                ← ZMSDocument
        │   ├── e3             ← ZMSTextarea (block element)
        │   └── e4             ← ZMSGraphic (block element)
        └── e5/                ← ZMSFolder (sub-section)
```

Object IDs follow the pattern `e<integer>` (sequential). The `zmsindex_catalog` object maps ZMS IDs, UUID strings, and Zope paths, enabling link resolution by any of these identifiers.

### 2.3 Metaobjects

Content classes are defined as metaobjects in `Products/zms/conf/metaobj_manager/`. Each metaobject is a folder containing:

- `__init__.yaml` — class definition (id, label, type, attributes).
- Sibling `.zpt`, `.py`, or resource files for attribute templates and scripts.

Custom metaobjects added through the ZMS configuration menu are stored in the ZODB and can be exported to the filesystem via the Repository Manager.

### 2.4 Versioning model

Each block-level content object exists in two versioned slots:

- `version_live_id` — the currently published version.
- `version_work_id` — the version being edited.

The parent page container keeps an aggregate version vector, incrementing its version on any child change. See [E. Appendices — Versioning](e_appendices.md#versioning) for the full model.

---

## 3. ZMS API Examples

> **Full annotated examples:** [develop_api_exampels_en.md](develop_api_exampels_en.md)

### 3.1 `renderShort()` — custom ZMI block view

Override the default ZMI summary view for a content class by adding a `renderShort` Python attribute:

```python
## Script (Python) "ZMSDocument.renderShort"
##parameters=zmscontext=None,options=None
# --// renderShort //--
alert = '<div class="alert alert-warning">Creator is missing!</div>'
if zmscontext.attr('attr_dc_creator'):
    alert = ''
return '<h1>%s<br/><small>%s</small></h1>%s' % (
    zmscontext.attr('title'),
    zmscontext.attr('attr_dc_description'),
    alert,
)
# --// /renderShort //--
```

![renderShort example](images/develop_api_renderShort.png)

### 3.2 `pathhandler` — custom URL traversal

Add a `pathhandler` Python attribute to a content class to intercept URL traversal and control when binary assets are delivered:

```python
## Script (Python) "ZMSFile.pathhandler"
##parameters=zmscontext=None,options=None
# --// pathhandler //--
request = container.REQUEST
if zmscontext.isActive(request):
    return zmscontext.attr('file')
else:
    return False
# --// /pathhandler //--
```

![pathhandler example](images/develop_api_pathhandler.png)

### 3.3 `getNavItems()` — navigation generation

Generate a hierarchical `<ul>/<li>/<a>` navigation from the content tree:

```python
nav = zmscontext.getNavItems(zmscontext, request, {
    'add_self': False,
    'deep': True,
    'complete': True,
    'maxdepth': 2,
    'id': 'sidebarnav',
    'cssclass': 'sidenav',
})
```

Equivalent TAL:

```html
<nav tal:content="structure python: zmscontext.getNavItems(zmscontext, request, {
    'add_self': False, 'deep': True, 'complete': True,
    'maxdepth': 2, 'id': 'sidebarnav', 'cssclass': 'sidenav'
})"></nav>
```

### 3.4 `evalMetaobjAttr()` — cross-context attribute execution

Python (`py`) attributes stored in the metaobject manager have a dot in their Zope ID (e.g. `test.primitive_py`), which prevents direct attribute access from outside the owning object. Use `evalMetaobjAttr()` to call them from any context:

```python
res = zmscontext.getRootElement().metaobj_manager.evalMetaobjAttr(
    'test', 'primitive_py', options={'zmscontext': zmscontext}
)
```

### 3.5 `ZMSIndex.catalog()` — short URL / ID resolution

The `zmsindex_catalog` enables ID-to-path resolution for implementing short URLs:

```python
catalog = zmscontext.getZMSIndex().get_catalog()
results = catalog({'id': 'e1758'})
for r in results:
    return r['getPath']
```

To resolve by UUID:

```python
results = catalog({'get_uid': 'uid:d67ef401-db9b-46bd-9108-35f3c8d959a0'})
```

Or use `getLinkObj()` in TAL with ZMS internal URL syntax:

```python
obj = zmscontext.getLinkObj('{$uid:d67ef401-db9b-46bd-9108-35f3c8d959a0}')
```

### 3.6 `getObjOptions()` — select list labels

Retrieve the human-readable labels for a `select` or `multiselect` attribute:

```python
opt = zmscontext.getObjAttrs().get('attr_event_category')
opt_list = zmscontext.getObjOptions(opt, request)
opt_dict = {k: v for k, v in opt_list}
label = opt_dict.get('social')   # → "Social / Networking Event"
```

### 3.7 `internal_dict` — per-node metadata storage

The built-in multilingual attribute `internal_dict` is a Python dict attached to every content object. It can store arbitrary technical metadata (e.g. CSS class overrides for ZMI customisation):

```python
# Add CSS classes via ZMS action (manage_css_classes)
self.setObjProperty('internal_dict', {'css_classes': ['ZMSAuthor_special']}, request)
```

### 3.8 Custom logout endpoint

Customise ZMS logout behaviour (e.g. for `Products.PluggableAuthService`) via the configuration parameter `ZMS.logout.href`:

```python
# Zope Python Script: "zmi_logout"
redirect_url = 'https://%s' % zmscontext.getConfProperty('ASP.ip_or_domain', 'example.com')
request.set('HTTP_REFERER', redirect_url)
context.manage_zmi_logout(request, response)
response.redirect(redirect_url)
```

Set `ZMS.logout.href = zmi_logout` in the root ZMS node's system properties. Zope acquisition ensures the correct context is used in multisite setups.

---

## 4. Proxy Cache and HTTP Caching

> **Full reference:** [develop_cache.md](develop_cache.md)

### 4.1 Core helper

```python
from Products.zms import standard
standard.set_response_headers_cache(context, request, cache_max_age=6*3600, cache_s_maxage=86400)
```

Call this near the top of your `standard_html` template.

### 4.2 Cache behaviour summary

| Scenario | Headers set |
|---|---|
| Preview or restricted content | `Cache-Control: no-cache`, `Expires: -1` |
| Public content, static TTL | `Cache-Control: s-maxage=<proxy>, max-age=<browser>, public` |
| Content with future publish date | TTL tightened; `X-Accel-Expires: <seconds>` added |
| Versioned asset (`?ETag=<token>`) | Very long TTL; cache key changes with token |

### 4.3 Dynamic expiry mechanism

During render, `ObjAttrs.isActive` (in `_objattrs.py`) stores the nearest future `attr_active_start` or `attr_active_end` value in the request variable `ZMS_CACHE_EXPIRE_DATETIME`. `set_response_headers_cache` reads this and tightens the proxy TTL accordingly.

### 4.4 Active cache purge

Import the `manage_cachepurge` ZMS action and implement the `cache_purge` external method to invoke your proxy's cache-purge script when an editor explicitly invalidates a page.

---

## 5. Extending ZMS

### 5.1 Custom content classes

1. Design the attribute schema in **Administration → Content-Objects**.
2. Write the `standard_html` TAL template.
3. Add optional Python attributes (`renderShort`, `pathhandler`, …) as `py` primitives.
4. Export to the filesystem via the Repository Manager and commit to Git.

### 5.2 Custom actions (metacmd)

ZMS *actions* are Python scripts or external methods that appear in the ZMS context menus. Store them under `Products/zms/conf/metacmd_manager/<action_id>/` with a `__init__.yaml` manifest. Import them via **Administration → Actions**.

### 5.3 Custom RTE plugins

Add a rich-text editor plugin at `Products/zms/plugins/rte/<MyRTE>/manage_form.zpt`. Place JavaScript/CSS under `Products/zms/plugins/www/<MyRTE>/`. The plugin will appear as a choice in the `ZMS.richtext.plugin` system parameter.

### 5.4 Theming

Themes live in your site's filesystem and are composed of TAL/METAL templates referencing ZMS API calls. Use `getNavItems()`, `getLangStr()`, `getConfProperty()`, and `attr()` to drive navigation, i18n, configuration, and content rendering.

For theming documentation see [C. For Site Administrators — Theming](c_for_site_administrators.md#theming-and-design) and the files under `docs/theming/`.

### 5.5 REST API

ZMS exposes a REST API at `++rest_api/`. Endpoints include:

- `++rest_api/content` — read content tree as JSON.
- `++rest_api/llm_chat` — chat with the configured LLM connector.

The REST API is consumed by the built-in search JavaScript module and the `llm_chat` block widget.

---

## 6. Useful Patterns and Tips

### Accessing the ZMS root from any context

```python
root = context.content.getRootElement()
```

### Generating a content URL

```python
url = zmscontext.getHref2IndexHtml(request)
```

### Checking if content is active/published

```python
is_active = zmscontext.isActive(request)
```

### Reading a configuration property with a fallback

```python
val = zmscontext.getConfProperty('ZMS.myconfig', default='fallback')
```

### Getting a translated ZMI string

```python
label = zmscontext.getLangStr('ATTR_TITLE')
```

### Iterating child nodes

```python
children = zmscontext.getChildNodes(request, ['ZMSDocument', 'ZMSFolder'])
```

---

## 7. Contributing

1. Fork the repository on GitHub: <https://github.com/zms-publishing/ZMS>
2. Install in editable mode (see § 1).
3. Create a feature branch, make your changes, and run the test suite.
4. Submit a pull request with a clear description of the change.

Follow the existing code style (PEP 8 for Python, consistent indentation in ZPT templates). When adding a new feature, also update the relevant documentation file in `docs/`.
