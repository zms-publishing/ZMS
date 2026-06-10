# C. For Site Administrators

This chapter covers the configuration and operation of a ZMS installation. It addresses user management, multilingual configuration, content-model design, search indexing, AI/LLM connectors, theming, and production deployment topics such as caching and reverse-proxy integration.

---

## 1. The Configuration Menu

The ZMS configuration menu (accessible via the gear icon in the top bar, visible to users with admin privileges) provides ten main sections:

| # | Section | Purpose |
|---|---|---|
| 1 | **User** | Manage user accounts and access rights |
| 2 | **System** | System variables, multisite hierarchies, functional components |
| 3 | **Languages** | Languages and their editorial dependencies |
| 4 | **Meta-Attributes** | General content attributes (Dublin Core-style metadata) |
| 5 | **Content-Objects** | Model content classes and their attribute schemas |
| 6 | **Paragraph-Formats** | Text block formatting presets |
| 7 | **Character-Formats** | Text inline formatting (bold, italic, custom spans) |
| 8 | **Actions** | Additional / self-programmed helper functions |
| 9 | **Search** | Configure content indexing (ZCatalog, Solr) |
| 10 | **Design** | Design themes and JS/CSS customization |

---

## 2. User Management

The **User** section of the configuration menu lets the administrator:

- Create, edit, and delete local ZMS user accounts.
- Assign users to roles: *Reader*, *Author*, *Editor*, *Manager*.
- Delegate authentication to Zope's built-in user folder or an external LDAP/Active Directory source.

Roles control which workflow transitions a user can trigger and which parts of the configuration menu are visible.

---

## 3. Languages {#languages}

ZMS uses a **symmetric hierarchical** multilingual model:

- **Symmetric** — all language variants of a content object are stored side-by-side in a single object (not in separate sub-sites).
- **Hierarchical** — languages are organised in a dependency tree. A *primary language* is the source; *secondary* or *dependent* languages inherit content from their parent and can override it with local variants.

### Configuring languages

Open **Administration → Languages**. The upper section defines available languages and their dependency structure. The lower section provides the **Language Dictionary** — a table of language-neutral keys and their translations.

![Language Configuration](images/admin_languages.gif)
*Language configuration: available languages and dependencies (upper); language dictionary (lower)*

### Language dictionary

Display labels for content classes and attributes in the ZMI can be internationalised. Naming conventions:

- `TYPE_<NAME>` — translation key for a content class display name (e.g. `TYPE_BOX`).
- `ATTR_<NAME>` — translation key for an attribute display name (e.g. `ATTR_TITLE`).

If a matching entry exists in the language dictionary, it overrides the literal label stored in the content model.

---

## 4. Meta-Attributes

Meta-attributes (or *metas*) are site-wide descriptive attributes inspired by the [Dublin Core Metadata Initiative](https://en.wikipedia.org/wiki/Dublin_Core). Every content object automatically inherits all configured meta-attributes.

Common defaults include:

- `attr_dc_title` — document title
- `attr_dc_description` — summary / abstract
- `attr_dc_creator` — author
- `attr_dc_date` — publication date
- `attr_dc_subject` — keyword tags

Administrators can add further meta-attributes and assign a data type to each. Because any meta-attribute becomes a new data type usable across all content classes, a coherent metadata concept reduces template complexity and supports consistent full-text indexing.

![Administration of Metadata](images/admin_gui_metas1.gif)
*Meta-attribute administration*

---

## 5. Content Objects (Content Model)

ZMS uses a **content model** (also called *schema*) that defines an arbitrary number of content class definitions.

### Pages and blocks

- **Page-like objects** (`ZMSFolder`, `ZMSDocument`) aggregate block elements and may nest other page objects.
- **Block elements** (`ZMSTextarea`, `ZMSFile`, `ZMSGraphic`, …) hold actual content and are arranged in sequences inside pages.

### Defining a content class

1. Open **Administration → Content-Objects**.
2. Add a new class and give it an ID and display label.
3. Add attributes by selecting from the available data types (text, integer, image, resource, TAL expression, Python script, …).
4. Mark attributes as **multilingual** (globe icon) if they need language-specific values.
5. After the attribute list is complete, edit the `standard_html` TAL template to render the content. Use the **Refresh** button to generate a prototype TAL snippet from the current attribute schema.

![Content Model Administration](images/admin_contentmodel_carditem.gif)
*Example: a `carditem` object model with image, text, and URL attributes*

![Nesting Content Objects](images/admin_contentmodel_conventions.gif)
*Nested models: a `card_container` aggregating `carditem` instances*

### Multilingual attribute labels

Attribute display names in the content model can be made multilingual by following the `TYPE_`/`ATTR_` naming convention described in [§ 3 Languages](#languages).

---

## 6. Paragraph and Character Formats

### Paragraph formats

Paragraph formats define the block-level HTML element wrapping a `ZMSTextarea` content. They are used by both the plain-text editor (applied to the whole block) and the rich-text editor (applied to individual paragraphs).

Each format is defined by:

- ID, display name
- Wrapping HTML element and attributes
- Newline tag
- Whether it is available in plain and/or rich-text editors
- Whether it is the default format
- Whether it forces use of the rich-text editor

![Paragraph Formats](images/admin_contentmodel_paragraph.gif)
*Paragraph format configuration form*

### Standard (plain-text) editor

The standard text editor provides a plain-text `<textarea>` input. It is possible to add inline HTML tags manually, but invalid HTML can creep in. To help catch this, enable the realtime HTML validity check via the system parameter:

```
ZMS.ZMSTextarea.show_htmlcheck = True
```

![HTML Validity Check](images/edit_gui_textarea_show_htmlcheck.png)
*HTML validity check indicator controlled by `ZMS.ZMSTextarea.show_htmlcheck`*

### Rich-text editors (RTE)

ZMS ships with four RTEs selectable via the system parameter `ZMS.richtext.plugin`:

1. **CKEditor** (HTML)
2. **TinyMCE** (HTML)
3. **SimpleMDE** (Markdown)
4. **EasyMDE** (Markdown)

To add a custom RTE, create a folder at `Products/zms/plugins/rte/MyRTE/` containing a TAL template `manage_form.zpt` that renders the editor's HTML snippet. Place JavaScript and CSS resources in `Products/zms/plugins/www/MyRTE/` and reference them with ZMS resource links.

### Character formats

Inline (character) formats add custom `<span>` wrappers or other inline HTML elements inside text blocks. Each format is defined by ID, display name, button icon, wrapping HTML element/attributes, and optional JavaScript event handling.

![Character Formats](images/admin_contentmodel_inlineformats.gif)
*Inline character-format configuration*

---

## 7. Search

### 7.1 ZCatalog (built-in)

ZMS integrates with Zope's built-in **ZCatalog** for lightweight full-text search.

- Open **Administration → Search → Adapter** to choose which content classes and attributes to index.
- Index objects are named `catalog_<lang>` (e.g. `catalog_eng`) and are held inside the ZMS `content` object.
- In a **multisite** hierarchy only the root ZMS catalog collects all index data. Local content classes not inherited from the root must be registered individually in each client's Search configuration. **Important:** attribute schemas defined in sub-sites are ignored for global indexing — all indexed attributes must be declared in the root ZMS object.

![Metadata to be indexed](images/admin_gui_search1.gif)
*Selecting content classes and attributes for indexing*

![Indexer Connector](images/admin_gui_search2.gif)
*ZCatalog connector administration*

### Integrating the search form in your theme

Your theme template must:

1. Provide a `ZMSDocument` page node containing a `ZMSTextarea` with the TAL-based search form (input field + results placeholder).
2. Include the ZMS search JavaScript module:

```html
<script type="text/javascript" src="/++resource++zms_/zmi.core.js"></script>
<script type="text/javascript" src="/++resource++zms_/ZMS/zmi_body_content_search.js"></script>
```

Full search form TAL template (input section + asynchronous results placeholder):

```html
<form class="search" method="get" xmlns:tal="http://xml.zope.org/namespaces/tal">

  <tal:block tal:condition="python:request.get('searchform',True)">
    <input tal:condition="python:request.get('searchform')" type="hidden" name="searchform"
           tal:attributes="value python:request.get('searchform')" />
    <input tal:condition="python:request.get('lang')" type="hidden" name="lang"
           tal:attributes="value python:request.get('lang')" />
    <input tal:condition="python:request.get('preview')" type="hidden" name="preview"
           tal:attributes="value python:request.get('preview')" />
    <legend tal:content="python:here.getZMILangStr('SEARCH_HEADER')">Search header</legend>
    <div class="form-group">
      <div class="col-md-12">
        <div class="input-group">
          <tal:block tal:content="structure python:here.getTextInput(fmName='searchform',elName='search',value=request.get('search',''))">the value</tal:block>
          <span class="input-group-btn">
            <button type="submit" class="btn btn-primary">
              <i class="fa fa-search icon-search"></i>
            </button>
          </span>
        </div>
      </div>
    </div><!-- .form-group -->
    <div class="form-group row"
         tal:condition="python:here.getPortalMaster() is not None or len(here.getPortalClients())>0">
      <div class="control-label col-md-12" tal:define="home_id python:here.getHome().id">
        <input type="hidden" name="home_id"
               tal:attributes="value python:request.get('home_id',home_id); data-value home_id" />
        <input type="checkbox" class="form-check-input"
               onchange="var $i=$('input[name=home_id]');$i.val(this.checked?$i.attr('data-value'):'');"
               tal:attributes="checked python:['','checked'][request.get('home_id',home_id)==home_id]" />
        <label class="form-check-label control-label">
          <strong tal:content="home_id">the home-id</strong> (local)
        </label>
      </div>
    </div><!-- .form-group -->
  </tal:block>

  <div id="search_results" class="form-group" style="display:none">
    <div class="col-md-12">
      <h4 tal:content="python:here.getZMILangStr('SEARCH_HEADERRESULT')">Result</h4>
      <div class="header row">
        <div class="col-md-12">
          <span class="small-head">
            <span class="glyphicon glyphicon-refresh fas fa-spinner fa-spin" alt="Loading..."></span>
            <tal:block tal:content="python:here.getZMILangStr('MSG_LOADING')">loading</tal:block>
          </span>
        </div>
      </div><!-- .header.row -->
      <div class="line row"></div>
      <div class="pull-right"><ul class="pagination"></ul></div>
    </div>
  </div>

</form>
```

The form's request is answered by an XML stream transformed into HTML by JavaScript.

**Permalink for the search page:** Instead of hardcoding the node ID, define a permalink property `ZMS.permalink.search` on the ZMS root node. Reference it in master templates like this:

```html
<html lang="en"
  tal:define="zmscontext options/zmscontext;
    search_node python: zmscontext.getLinkObj(
      zmscontext.getConfProperty('ZMS.permalink.search', default='{$@content}'), request);">
```

Generate the search link:

```html
<a href="#"
  tal:attributes="href python:search_node.getHref2IndexHtml(request)">
  <i class="fas fa-search"></i>&nbsp;
  <span tal:replace="python:zmscontext.getLangStr('SEARCH')">Search</span>
</a>
```

**Multisite search filtering:** To restrict search results to the current ZMS client, pass `home_id` in the form:

```html
<form class="search" method="get">
  <input type="hidden" name="home_id" value="myzms">
  ...
</form>
```

Reference the search page via a permalink system property `ZMS.permalink.search` to avoid hardcoded IDs across templates.

### 7.2 Apache Solr connector

For large sites or advanced search features (facets, highlighting, PDF indexing) ZMS provides a Solr connector.

**Overview:**

1. Import the two default ZMS actions from **Administration → Actions**:
   - `manage_zcatalog_create_sitemap` — generates a Solr-schema-conformant XML file.
   - `manage_zcatalog_update_documents` — transfers the XML to the Solr server.

2. Under **Administration → Search**, add the `ZMSZCatalogSolrConnector` and configure:
   - **URL** — HTTP API URL of the Solr server.
   - **Core** — name of the Solr core.

3. Create the Solr core on the server:
   ```shell
   solr@server:~$ solr create_core -c mysite
   ```

4. Run *Create XML Sitemap* then *Update SOLR Document Index* to perform the initial index load.

**PDF indexing:** Install `pdfminer.six` to enable automatic PDF text extraction into the sitemap XML:

```shell
zope@server:~$ ~/venv/bin/pip install pdfminer.six
```

![Indexing PDF Content](images/SOLR_PDF_Index.gif)
*ZMS transfers PDF content by extracting plain text and adding it to the sitemap XML.*

### Running Solr as a Docker container

#### Dockerfile

```docker
FROM solr:8

# Apply security updates
USER root
RUN apt-get update && apt-get -y upgrade && apt-get clean
USER solr
```

#### systemd service for Solr (Docker / Podman)

Place the following file at `/etc/systemd/system/solr.service` on the host:

```ini
[Unit]
Description=Apache SOLR search engine

[Service]
Type=simple
User=solr
Restart=always
Environment="GODEBUG=netdns=go"
# Remove old container before building a new image
ExecStartPre=-/usr/bin/podman container stop solr
ExecStartPre=-/usr/bin/podman container rm solr
# Apply security updates on each restart
ExecStartPre=/usr/bin/podman build --pull --no-cache -f /home/solr/Dockerfile -t solr:8-security-updated
ExecStart=/usr/bin/podman run --rm -it -v "/home/solr/data:/var/solr" -p 8983:8983 --name solr solr:8-security-updated
ExecStop=/usr/bin/podman stop solr

[Install]
WantedBy=multi-user.target
```

Enable and start:

```shell
root@server:~$ systemctl daemon-reload
root@server:~$ systemctl enable solr
root@server:~$ systemctl start solr
```

#### Creating a Solr core in a Docker container

```shell
localhost:~$ ssh root@solr.server.hosting
root@server:~$ su - solr
solr@server:~$ podman exec -it solr bash
solr@container:/opt/solr-8.11.2$ solr create_core -c playground
```

---

## 8. Repository Manager and Git Bridge

### 8.1 Repository Manager

The **ZMS Repository Manager** synchronises custom ZMS code (metadata, content models, actions, workflow definitions) between the ZODB and a filesystem folder. Activate it under **Administration → System**.

Key properties:

| Property | Description |
|---|---|
| **System Path** | Filesystem location for code replication. Default: `$INSTANCE_HOME/var/$zms_id`. The variable `$INSTANCE_HOME` resolves to the Zope instance folder. The system property `ZMS.conf.path` stores the active path; `ZMS.conf.paths` can hold a comma-separated list of candidates for selection. |
| **Working Mode** | *Export* (ZODB → filesystem) or *Import* (filesystem → ZODB) |
| **Ignore Orphans** | Skip files not managed by version control |
| **Auto-Sync** | Export automatically on model changes (requires `ZMS.debug = True`). In *Import* mode, Auto-Sync still requires manual confirmation. |

Diff colour conventions: green = new, red = deleted, yellow = modified. The colour perspective inverts between Export and Import modes: in Export mode, new ZODB code is green; in Import mode, newer filesystem code is green.

![Repository Manager](images/admin_repo_view.png)
*Repository Manager: diff view with Export/Import controls*

![ZMSRepositoryManager Properties](images/admin_repo_properties.png)
*Repository Manager properties: System Path supports `$INSTANCE_HOME` path components*

### 8.2 Git Bridge

The ZMS Git Bridge allows TTW (through-the-web) development to coexist with Git-based collaboration.

1. Configure the filesystem repository folder as a Git clone.
2. Import the three Git actions (`gitconfig`, `gitpull`, `gitpush`) from **Administration → Actions**.

![Import Git Actions](images/admin_repo_import_gitactions.png)

After importing, the Repository Manager gains a **Repository Interactions** pop-up menu:

- **Git Configuration** — enter the Git remote URL and optionally clone.
- **Git Pull** — pull the latest revision (or a specific commit). Use *Hard Reset* to force-overwrite local changes.
- **Git Push** — enter a commit message and push.

A dedicated SSH key for the Zope user is recommended:

```ini
# ~/.ssh/config
Host github.com
    HostName github.com
    IdentityFile ~/.ssh/zope_deploy_key
    User git
```

The `.git/config` file in the repository folder should be pre-configured before using it with ZMS:

```ini
[user]
    name = mygituser
    email = mygituser@mydomain.tld
[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true
[remote "origin"]
    url = git@github.com:mydomain/myproject.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
    remote = origin
    merge = refs/heads/master
```

> The Git URL saved via *Git Configuration* is only needed if cloning via the ZMS GUI. If the `.git/config` file is already in place, the URL does not need to be entered again.

The Git Bridge uses a minimal command set:

- **Git Pull** — pulls (with checkout) the latest `HEAD` or a specific revision ID; *Hard Reset* forces an overwrite of local changes.
- **Git Push** — pushes the current state to the main branch with a commit message.

![Git pull menu](images/admin_repo_show_gitpull.png)
*Git pull menu: optionally enter a revision ID and enable Hard Reset to force-overwrite local changes.*

![Git push menu](images/admin_repo_show_gitpush.png)
*Git push menu: enter a commit message before pushing.*

---

## 9. LLM / AI Configuration {#llm}

ZMS supports multiple Large Language Model (LLM) providers through a unified connector object `ZMSLLMConnector`. Add it at the ZMS site root and configure the provider type and credentials.

### Supported providers

| Provider | Key requirement | Use case |
|---|---|---|
| **OpenAI** | API key + internet | Cloud GPT models, production quality |
| **Ollama** | Local GPU/CPU server | Privacy-sensitive or offline deployments |
| **RAG (Qdrant + Ollama)** | Qdrant + Ollama | Site-specific question answering |

### Configuration properties

All configuration is done via the `ZMSLLMConnector` object properties.

#### General settings

| Property | Description | Default |
|---|---|---|
| `llm.provider` | Provider type: `openai`, `ollama`, or `rag` | `openai` |
| `llm.api.model` | Model name | `gpt-4o-mini` (OpenAI), `llama2` (Ollama) |
| `llm.temperature` | Sampling temperature 0.0–2.0 (higher = more creative) | `0.7` |
| `llm.top_p` | Nucleus sampling 0.0–1.0 | `0.9` |
| `llm.max_tokens` | Maximum tokens to generate (optional) | *(not set)* |
| `llm.num_ctx` | Context window size for Ollama/RAG | `4096` |

#### OpenAI configuration

| Property | Description | Default |
|---|---|---|
| `llm.api.key` | Your OpenAI API key | *(required)* |
| `llm.api.endpoint` | Custom endpoint URL | `https://api.openai.com/v1/chat/completions` |
| `llm.api.model` | Model name | `gpt-4o-mini` |
| `llm.store` | Enable storage for OpenAI's responses API | `False` |

#### Ollama configuration

| Property | Description | Default |
|---|---|---|
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name | `llama2` |
| `llm.num_ctx` | Context window size | `4096` |

> **Agent mode** requires a tool-capable model. Many older models (`llama2`, `mistral`, `codellama`) do not support Ollama's tool-calling protocol. Use `llama3.1`, `llama3.2`, `llama3.3`, `qwen2.5`, `qwen2.5-coder`, or `mistral-nemo` for agent mode.

#### RAG (Qdrant + Ollama) configuration

| Property | Description | Default |
|---|---|---|
| `llm.qdrant.host` | Qdrant server URL | `http://localhost:6333` |
| `llm.qdrant.collection` | Collection name for vector search | `zms_docs` |
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name | `llama2` |
| `llm.embedding.model` | SentenceTransformer model for embeddings | `all-MiniLM-L6-v2` |
| `llm.rag.top_k` | Number of documents to retrieve | `16` |
| `llm.rag.score_threshold` | Minimum similarity score (0.0–1.0) | `0.0` |
| `llm.temperature` | Temperature for RAG responses | `0.1` (recommended) |

RAG requires the `sentence-transformers` package:

```bash
pip install sentence-transformers
```

### Configuration examples

#### Example 1: OpenAI (cloud)

```python
llm.provider = openai
llm.api.key = sk-your-openai-api-key-here
llm.api.model = gpt-4o-mini
llm.temperature = 0.7
llm.top_p = 0.9
llm.store = True
```

#### Example 2: Ollama (local)

```python
llm.provider = ollama
llm.ollama.host = http://localhost:11434
llm.api.model = llama3.1
llm.temperature = 0.7
llm.num_ctx = 4096
```

For Docker deployments:

```python
llm.provider = ollama
llm.ollama.host = http://ollama:11434
llm.api.model = mistral
llm.temperature = 0.8
llm.num_ctx = 8192
```

#### Example 3: RAG with Qdrant

```python
llm.provider = rag
llm.qdrant.host = http://localhost:6333
llm.qdrant.collection = zms_documentation
llm.ollama.host = http://localhost:11434
llm.api.model = llama2
llm.embedding.model = all-MiniLM-L6-v2
llm.rag.top_k = 16
llm.rag.score_threshold = 0.3
llm.temperature = 0.1
llm.num_ctx = 4096
```

### Setting up Ollama

1. Install Ollama from <https://ollama.ai>.
2. Pull a model: `ollama pull llama3.1`
3. Start the server: `ollama serve`

Docker Compose snippet:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - zms_network
volumes:
  ollama_data:
```

### Setting up RAG with Qdrant

Docker Compose snippet:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    networks:
      - zms_network
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - zms_network
volumes:
  qdrant_storage:
  ollama_data:
networks:
  zms_network:
```

#### Populating Qdrant with embeddings

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="zms_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

documents = ["ZMS is a CMS built on Zope...", "To configure LLM settings..."]
points = [
    PointStruct(id=idx, vector=model.encode(doc).tolist(), payload={"text": doc})
    for idx, doc in enumerate(documents)
]
client.upsert(collection_name="zms_docs", points=points)
```

> Always use the same `llm.embedding.model` for ingestion and retrieval.

### REST API

```
GET /++rest_api/llm_chat?message=Your+question+here
GET /++rest_api/llm_provider_info
```

### Python API

```python
from Products.zms import llmapi

response = llmapi.chat(context, "What is ZMS?")
if 'error' in response:
    print(response['error']['message'])
else:
    print(response['message']['content'])

info = llmapi.get_provider_info(context)
print(f"Using {info['provider']} with model {info['model']}")
```

### LLM chat content block (`llm_chat`)

Enable the `llm_chat` metaobject from the package `com.zms.llm` to embed a chat widget directly on content pages. The block communicates with the `++rest_api/llm_chat` endpoint and supports multi-turn history and optional agent mode (tool-calling).

### Agentic RAG indexing with `index_qdrant`

ZMS ships an `index_qdrant` LLM tool that lets the agent crawl and index the entire site content into Qdrant on demand. When agent mode is enabled, simply ask in natural language:

> *"Please index all content of this ZMS site."*

The tool:
1. Queries the ZCatalog for all active pages.
2. Renders each page's body content via `getBodyContent()`.
3. Strips HTML and splits text into overlapping chunks (default 1 200 chars / 200 overlap).
4. Embeds chunks with `llm.embedding.model`.
5. Upserts vectors into Qdrant with metadata: `path`, `url`, `title`, `lang`, `meta_id`, `chunk_index`.
6. Returns a summary of pages indexed and chunks stored.

| Parameter | Description | Default |
|---|---|---|
| `lang` | Index only this language code (e.g. `eng`) | all languages |
| `collection` | Qdrant collection name | `llm.qdrant.collection` |
| `reset` | Drop and recreate collection before indexing | `true` |
| `chunk_size` | Maximum characters per chunk | `1200` |
| `chunk_overlap` | Overlap between consecutive chunks | `200` |

Prerequisites: `qdrant-client` and `sentence-transformers` installed; `llm.provider = rag` configured.

### Troubleshooting

| Problem | Solution |
|---|---|
| Cannot connect to Ollama | Check `curl http://localhost:11434/api/tags`; verify Docker network |
| Model not found | `ollama pull <model>` |
| Invalid OpenAI API key | Verify at <https://platform.openai.com/api-keys>; check for whitespace |
| Slow Ollama responses | Use a smaller model; reduce `llm.num_ctx`; enable GPU acceleration |
| RAG returns generic answers | Check Qdrant ingestion; lower `score_threshold`; increase `top_k`; verify embedding model matches |

### Best practices

1. Use **OpenAI** for production where fast, reliable responses are needed.
2. Use **Ollama** for development or privacy-sensitive deployments.
3. Use **RAG** when the LLM must answer questions based on your site documentation.
4. Set `llm.temperature` to 0.1–0.3 for RAG to ensure factual, grounded responses.
5. Match `llm.embedding.model` between ingestion and retrieval.
6. Re-index after significant content changes.
7. On multilingual sites, use the `lang` parameter to index languages into separate collections.

### Security considerations

- Never store API keys in version control — set them via the ZMS properties form or environment variables.
- Restrict network access to Ollama and Qdrant services to the Zope host.
- Rotate OpenAI API keys regularly.
- Be aware that `llm.store = True` sends interaction data to OpenAI for training.

---

## 10. Theming and Design

ZMS themes live in `docs/theming/` and the bundled theme templates are found under `Products/zms/zpt/`. The **Design** configuration menu section allows uploading and activating custom CSS/JS resources.

Key theming documentation:

| Document | Topic |
|---|---|
| [theming/structure.md](theming/structure.md) | Theme folder layout |
| [theming/templates.md](theming/templates.md) | TAL/METAL template conventions |
| [theming/css.md](theming/css.md) | CSS architecture |
| [theming/assets.md](theming/assets.md) | Static asset management |
| [theming/automation.md](theming/automation.md) | Build automation |
| [theming/ai.md](theming/ai.md) | AI-assisted theming |
| [theming/figma.md](theming/figma.md) | Figma-to-ZMS workflow |

---

## 11. Workflow Configuration {#workflow}

ZMS workflows are configured under **Administration → System → Workflow**. A workflow defines a set of *activity states* and *transitions* that content must pass through before publication.

Key concepts:

- **`TR_ENTER`** — implicit transition triggered whenever a content object is first modified (enters the workflow).
- **`TR_LEAVE`** — implicit transition that marks the end of the workflow cycle (content is committed/published).
- Each transition can be restricted to specific user roles.
- A transition may start from more than one state (e.g. *Commit* can be triggered from both *Changed* and *Commit requested*).

> For full workflow and versioning details see [E. Appendices](e_appendices.md).

---

## 12. Caching and Reverse-Proxy Deployment

In production ZMS sits behind a reverse proxy (NGINX, Apache). ZMS controls HTTP cache behaviour via response headers set by the helper function:

```python
# Products/zms/standard.py
set_response_headers_cache(context, request, cache_max_age=24*3600, cache_s_maxage=-1)
```

Key behaviours:

- **Preview / restricted content**: `Cache-Control: no-cache` is set automatically — proxies will not cache restricted pages.
- **Public content**: `Cache-Control: s-maxage=<proxy_ttl>, max-age=<browser_ttl>, public` is set.
- **Dynamic expiry**: when a page has a future `attr_active_start` or `attr_active_end` date, the TTL is automatically tightened to the nearest upcoming change. The `X-Accel-Expires` header carries this value to NGINX.
- **ETag cache-busting**: URLs with `?ETag=<token>` are cached indefinitely by the proxy; a changing token forces a new cache entry.

Typical production tuning:

```python
# In standard_html template (TAL)
<tal:block tal:define="
  standard modules/Products.zms/standard;
  dummy python:standard.set_response_headers_cache(this, request, cache_max_age=6*3600, cache_s_maxage=86400)">
</tal:block>
```

For instant cache invalidation, import the `manage_cachepurge` ZMS action and configure the external `cache_purge` method to call your NGINX cache-purge script. See [D. For Developers — Proxy Cache](d_for_developers.md#4-proxy-cache-and-http-caching) for the full proxy cache reference including ETag-based busting, parameter tuning, and purge script examples.

---

## 13. Security Hardening Checklist

- [ ] Run Zope as a dedicated non-root user.
- [ ] Restrict the Zope management interface (`/manage`) to localhost or a VPN.
- [ ] Use HTTPS with a valid certificate (Let's Encrypt or corporate CA) in front of the proxy.
- [ ] Rotate the Zope admin password after initial setup.
- [ ] Set `ZMS.debug = False` in production.
- [ ] Limit LDAP/Solr/Qdrant/Ollama network access to the Zope host.
- [ ] Keep ZMS, Zope, and all Python dependencies up to date.
- [ ] Never commit API keys or credentials to version control.
