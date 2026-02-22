# ZMS ZCatalog Adapter

The ZMS ZCatalog Adapter (`ZMSZCatalogAdapter`) is the central configuration
hub for full-text search indexing. It defines **what** gets indexed (content
classes and attributes), **how** data is extracted from ZMS nodes, and
delegates the actual storage and retrieval to one or more pluggable
**connectors**.

The adapter lives at `zcatalog_adapter` inside the ZMS root and implements
`IZMSCatalogAdapter` and `IZMSConfigurationProvider`.

## Core Concepts

| Concept | Description |
|---|---|
| **Adapter** | Singleton configuration object that decides which content classes and attributes are indexed. Extracts data from ZMS nodes and passes it to connectors. |
| **Connector** | A `ZMSZCatalogConnector` child object that bridges to a concrete search backend (e.g. ZCatalog, OpenSearch, Solr). Multiple connectors can be active simultaneously. |
| **Meta-ID Filter** | A list of ZMS content-class IDs (e.g. `ZMSDocument`, `ZMSFile`) that are eligible for indexing. Supports type-wildcards like `type(ZMSDocument)`. |
| **Custom Filter Function** | Optional Python code that refines the filtering logic beyond meta-ID matching (e.g. exclude inactive nodes or specific attribute values). |
| **Catalog Awareness** | When active, every content change automatically triggers `reindex_node()` so the search index stays in sync without manual action. |
| **Attribute Schema** | A configurable set of ZMS attributes to extract and index, each with a **type** (text, int, date, …) and a **boost** factor for search relevance. |
| **Content Extraction** | Binary files (PDF, Office documents) are converted to plain text via Apache Tika or pdfminer before indexing. HTML attributes are stripped to plain text via BeautifulSoup. |

## Data Model

### Configured IDs (`_ids`)

A list of meta-IDs that should be indexed:

```python
['ZMSDocument', 'ZMSFolder', 'ZMSFile', 'type(ZMSDocument)']
```

The special `type(...)` syntax includes all content classes that inherit
from the named base type.

### Configured Attributes (`_attrs`)

A dict mapping attribute IDs to their index configuration:

```python
{
  'title':              {'boost': 1.0, 'type': 'text'},
  'titlealt':           {'boost': 1.0, 'type': 'text'},
  'attr_dc_description':{'boost': 1.0, 'type': 'text'},
  'standard_html':      {'boost': 1.0, 'type': 'text'},
}
```

### Default Catalog Data

Every indexed node automatically receives these built-in fields (not
editable in the schema GUI):

| Field | Description |
|---|---|
| `uid` | ZMS unique ID |
| `id` | Node ID suffixed with language (`<id>_<lang>`) |
| `meta_id` | Content class ID |
| `home_id` | ID of the node's home (client root) |
| `loc` | `absolute_url_path()` |
| `path` | `/`-joined physical path |
| `index_html` | URL to the node's rendered page |
| `lang` | Language code |
| `created_dt` | Creation timestamp (UTC) |
| `change_dt` | Last modification timestamp (UTC) |
| `indexing_dt` | Timestamp of this indexing run |

### Custom Hooks

Content classes can override indexing behaviour through special attributes:

- **`catalog_indexable`** — py-attribute returning `True`/`False` to
  include/exclude a node.
- **`catalog_index`** — py-attribute returning a list of dicts with custom
  field values, enabling one node to produce multiple index entries.

## GUI Layout

The admin interface (`manage_main`) is a single-page form with two main
sections:

### Connectors

Shown only on the master site (not on portal clients):

- **Add** — dropdown of available connector ZMSLibraries not yet
  instantiated, plus an *Add* button.
- **Connector list** — each connector shows its ID with links to the
  connector's own management page and the underlying ZMSLibrary
  customisation. A delete button removes a connector (except `zmsindex`).

### Schema

| Field | Description |
|---|---|
| **Awareness** | Checkbox to enable/disable automatic reindexing on content changes (`ZMS.CatalogAwareness.active`). |
| **Custom Filter-Function** | ACE editor for Python code. Receives `context` (current node) and `meta_ids` (configured IDs). Must return `True`/`False`. |
| **Model** | Two-column table: left column lists all content classes grouped by package (checkboxes to select), right column shows the union of attributes from all selected classes (checkboxes, type, boost). A "Show only page-like classes" filter toggle is available. |

Clicking **Save** persists the IDs, attributes, filter function, and
awareness flag.

### Connector Management Page

Each connector has its own page (`manage_zcatalog_connector.zpt`) with:

- **Sitemap** — an interactive tree view of the ZMS content. Nodes can be
  selected and then reindexed or tested via toolbar buttons.
- **Reindex / Test** — toolbar actions that operate on selected sitemap
  nodes through AJAX calls to the connector's endpoints.
- **Properties** — connector-specific settings (e.g. OpenSearch URL,
  index name) editable inline.
- **Schema** — the connector's field mapping, often imported from a JSON
  schema definition.

## Indexing Pipeline

```
Content Change
     │
     ▼
CatalogAwareness active?  ──no──▶  (skip)
     │ yes
     ▼
reindex_node(node)
     │
     ├── find containing page
     ├── matches_ids_filter()?  ──no──▶  remove from catalog
     │        │ yes
     ▼        ▼
get_catalog_objects(node)
     │
     ├── get_default_data()     → uid, path, dates, ...
     ├── get_attr_data()        → title, description, html, ...
     ├── get_file()             → extract text from binaries
     │
     ▼
connector.manage_objects_add(objects)
     │
     ▼
Search Backend (ZCatalog / OpenSearch / ...)
```

## Connectors — ZMSZCatalogConnector

Each connector (`ZMSZCatalogConnector`) discovers backend actions by
naming convention. Metaobj attributes matching these regex patterns are
called automatically:

| Pattern | Connector Method | Description |
|---|---|---|
| `^manage_(.*?)_init$` | `manage_init()` | Initialise the backend. |
| `^manage_(.*?)_objects_add$` | `manage_objects_add(objects)` | Index a list of `(node, data)` tuples. |
| `^manage_(.*?)_objects_remove$` | `manage_objects_remove(nodes)` | Remove nodes from the index. |
| `^manage_(.*?)_objects_clear$` | `manage_objects_clear(home_id)` | Clear all entries for a site. |
| `^manage_(.*?)_destroy$` | `manage_destroy()` | Destroy the backend (e.g. delete index). |
| `(.*?)_query$` | `search_json(q, ...)` | Execute a search query. |
| `(.*?)_suggest$` | `suggest_json(q, ...)` | Autocomplete suggestions. |

The connector also provides XML-formatted endpoints (`search_xml`,
`suggest_xml`) and a paginated `reindex_page` method for bulk reindexing
via the GUI.

## API Reference

### ZMSZCatalogAdapter

| Method | Description |
|---|---|
| `getIds()` / `setIds(ids)` | Get/set the list of indexable meta-IDs. |
| `getAttrIds()` / `setAttrIds(attr_ids)` | Get/set attribute IDs for indexing. |
| `getAttrs()` / `setAttrs(attrs)` | Get/set the full attribute dict (with boost and type). |
| `getCustomFilterFunction()` / `setCustomFilterFunction(f)` | Get/set the Python filter expression. |
| `matches_ids_filter(node)` | `True` if the node's meta-ID matches the configured filter. |
| `get_connectors()` | List of active `ZMSZCatalogConnector` instances. |
| `get_connector(id)` | Single connector by ID, or `None`. |
| `add_connector(id)` | Create and register a new connector. |
| `reindex(connector, base, recursive, fileparsing)` | Full reindex from a base node through a specific connector. |
| `reindex_node(node)` | Smart single-node reindex (CatalogAwareness). |
| `unindex_nodes(nodes, forced)` | Remove trashed/deleted nodes from all connectors. |
| `get_catalog_objects(node, fileparsing)` | Extract all catalog data tuples for a node. |
| `get_attr_data(node, d)` | Populate dict `d` with attribute values from `node`. |
| `manage_changeProperties(btn, lang, REQUEST, RESPONSE)` | Form handler: add/delete connectors, save schema. |

### ZMSZCatalogConnector

| Method | Description |
|---|---|
| `manage_init()` | Initialise the search backend. |
| `manage_objects_add(objects)` | Index objects. Returns `(success_count, failed_count)`. |
| `manage_objects_remove(nodes)` | Remove nodes from the index. |
| `manage_objects_clear(home_id)` | Clear all entries for a site. |
| `manage_destroy()` | Destroy the search backend. |
| `search_json(q, fq, order, limit, offset)` | JSON search results. |
| `search_xml(q, fq, order, rows, offset)` | XML search results (Solr-compatible format). |
| `suggest_json(q, limit)` | JSON autocomplete suggestions. |
| `reindex_page(uid, page_size)` | Paginated reindex; returns JSON progress. |

### Content Extraction

| Function | Description |
|---|---|
| `extract_content(node, data, content_type)` | Main dispatcher: tries Tika → pdfminer → string decode. |
| `extract_text_from_html(node, value)` | Strip HTML tags, collapse whitespace. |
| `tika_extract(node, data, content_type)` | Extract text via Apache Tika server. |
| `pdfminer_extract(data)` | Extract text from PDF via pdfminer.six. |

## Tips

- Install a connector ZMSLibrary (e.g. `zcatalog_connector` or
  `opensearch_connector`) via the Metamodel Manager before configuring the
  adapter.
- Use `catalog_index` py-attributes on custom content classes to produce
  tailored index entries beyond the default attribute extraction.
- The Custom Filter Function is useful for excluding draft or inactive
  content from the public search index.
- Set `ZMS.CatalogAwareness.active` to `0` during bulk imports, then run a
  full reindex via the connector's sitemap GUI afterwards.
