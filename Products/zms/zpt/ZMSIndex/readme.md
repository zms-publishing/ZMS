# ZMS Index Manager

The **ZMSIndex** is a ZMS administration interface for managing the internal **ZCatalog-based content index** (`zcatalog_index`). It provides a visual sitemap of all ZMS clients and offers operations for re-indexing, integrity testing, and link resynchronization across the entire content tree. Every ZMS content object receives a persistent **UID** (Unique Identifier), and the ZMSIndex keeps a catalog that maps UIDs to physical paths — enabling fast UID-based lookups and cross-referencing.

> **Path:** *Login as ZMS Admin → Configuration → ZMSIndex*

---

## Core Concepts

### The ZCatalog Index (`zcatalog_index`)

ZMSIndex maintains a Zope **ZCatalog** instance named `zcatalog_index` at the Zope home level. This catalog stores one record per ZMS content object with the following default fields:

| Index / Column | Description |
|---|---|
| **`id`** | The object's Zope id (e.g. `e42`). |
| **`meta_id`** | The ZMS content-type identifier (e.g. `ZMSDocument`, `ZMSFolder`, `ZMS`). |
| **`get_uid`** | The object's persistent UID — a unique hash used for internal cross-referencing. |
| **`path`** | A `PathIndex` for path-based catalog queries. |
| **`getPath`** | A metadata column storing the object's physical path string. |

The catalog is automatically updated during normal content operations (add, move, remove). The GUI provides manual operations for bulk maintenance.

### UIDs and Link Referencing

ZMS uses a UID-based referencing system for internal links. Link targets are stored as UID references like `{$<uid>}` rather than physical paths. This makes links **location-independent** — when a content object is moved, its UID stays the same, and all references remain valid.

The ZMSIndex catalog enables resolving these UID references to physical paths and vice versa.

---

## GUI Layout

### Sitemap (Client Tree)

The main area displays a **visual sitemap** showing all ZMS root objects and their portal clients as an expandable tree. Each node has:

- A **checkbox** to select it for indexing operations.
- A **link** to the node's ZMS management interface (opens in a new tab).
- The node's **UID** shown as a tooltip on the checkbox (e.g. `{$content@site1@}`).

#### Sitemap Controls

| Button | Description |
|---|---|
| **⊞ Expand Tree** | Fully expands the object tree. ⚠ *Mind system load on large sites.* |
| **☑ Select All / None** | Toggles all checkboxes in the sitemap. |
| **⤢ Expand / Compress** | Toggles the sitemap container between normal and full-width view. |

A **progress bar** shows the status of long-running operations (reindex, test, resync).

### Actions Dropdown

The **action dropdown** provides the main indexing operations:

| Action | Description |
|---|---|
| **Show zcatalog_index** | Opens the underlying ZCatalog's management interface in a new tab, allowing direct inspection of the catalog contents and query testing. |
| **Re-Index Selected Clients** | Rebuilds the ZCatalog index for all selected ZMS clients. Each selected node's content subtree is traversed, and every object is re-cataloged. If the catalog is empty, a full regeneration is performed automatically. |
| **Test ZMS-Index** | Runs an integrity test comparing the catalog contents against the actual content tree. Reports objects that are *in the catalog but missing from the tree* (orphaned entries) and objects that are *in the tree but missing from the catalog* (uncataloged objects). |
| **Path-based Resync** | ⚠ *Apply with care.* Validates and refreshes **link objects**, **inline links**, and **backlinks** that use path-based syntax (not UID-based). Traverses the full client hierarchy (or selected nodes) and converts path-based references to UID-based references where possible. Also resolves `not_found` references. |
| *(Custom Meta-Commands)* | Any meta-commands registered for the `zmsindex` context appear here as additional actions. |

### UID Renewal Toggle

A separate toggle button labeled **"UID Renewal"** controls whether UIDs should be regenerated during re-indexing:

- **Unchecked (default):** Re-indexing preserves existing UIDs. Duplicate UIDs are detected and auto-fixed only if the object has no incoming references.
- **Checked:** ⚠ *Apply with care — all existing links may become invalid!* Forces regeneration of UIDs for all objects.

### Log Level Selector

A dropdown to choose the verbosity of log output during operations:

| Level | Description |
|---|---|
| **DEBUG** | Most detailed output. |
| **INFO** | Standard operational messages (default selection). |
| **ERROR** | Only error messages. |

The **"Show"** checkbox next to the log level selector toggles inline display of log output directly in the GUI (in a `<pre>` block below the controls). When unchecked, logging still occurs server-side but is not displayed.

---

## Extending the Schema

The **"Extending Schema"** section allows adding custom content attributes to the ZMSIndex for special use cases.

### Add Attributes

Enter a comma-separated list of meta-attribute names in the input field (e.g. `attr_dc_identifier_doi`). After saving, these attributes will be added to the catalog as additional **FieldIndex** entries with a `zcat_` prefix (e.g. `zcat_attr_dc_identifier_doi`).

After saving, a **Re-Index** is required for the new fields to be populated.

### DOI / Short-URL Example

A common use case for schema extension is implementing **DOI-style short URLs**. By adding a meta-attribute like `attr_dc_identifier_doi` to document content-types and indexing it via ZMSIndex:

1. Add `attr_dc_identifier_doi` to the meta-object definition of `ZMSDocument` / `ZMSFolder`.
2. Enter `attr_dc_identifier_doi` in the ZMSIndex "Add Attributes" field and save.
3. Re-index the content.
4. The ZMSIndex `doi()` method then resolves URLs like `/doi/10.1109/5.771073` or `/doi/faq` by looking up the indexed value and redirecting to the corresponding content object's URL.

> **Tip:** The attribute can be defined as a `Py-Script` type that derives its value from another attribute, e.g.:
> ```python
> from Products.zms import standard
> return standard.id_quote(zmscontext.attr('titlealt'))
> ```

---

## Automatic Index Updates

The ZMSIndex hooks into ZMS content lifecycle events to keep the catalog in sync:

| Event | Action |
|---|---|
| **ObjectAdded** | Traverses the added subtree, assigns UIDs (if new), and catalogs each object. |
| **ObjectMoved** | Removes old catalog entries and re-catalogs the moved subtree at its new path. |
| **ObjectRemoved** | Uncatalogs all objects in the removed subtree. |
| **ObjectImported** | Optionally triggers a full re-index or resync (controlled by conf-properties). |

### Related Configuration Properties

| Property | Default | Description |
|---|---|---|
| `ZMSIndexZCatalog.ObjectImported.reindex` | `False` | Trigger automatic re-index after content import. |
| `ZMSIndexZCatalog.ObjectImported.resync` | `False` | Trigger automatic resync after content import. |
| `ZMSIndexZCatalog.resync.transaction_size` | `1000000` | Number of objects processed before an intermediate transaction commit during resync (prevents memory exhaustion on large sites). |

---

## Duplicate UID Handling

During re-indexing, ZMSIndex performs a **duplicate UID check** for each object:

1. Query the catalog for the object's current UID.
2. If other objects share the same UID (different path, different id, or different meta_id):
   - If the object has **no incoming references** (`getRefByObjs() == 0`): a new UID is auto-generated and logged as *"auto-fixed duplicate uid"*.
   - If the object **has incoming references**: the duplicate is logged as an error but the UID is preserved to avoid breaking existing links.

---

## Multi-Site Support

In a **multi-site (portal client) setup**, the ZMSIndex operates from the root ZMS instance. The sitemap shows all portal clients as child nodes. Operations like re-index and resync can be run on individual clients or across the entire site hierarchy.

The resync operation is especially important in multi-site setups: it resolves domain-based URLs and cross-site references by mapping domain names to physical paths and converting them to UID-based references.

---

## Tips

- **Regular re-indexing** is recommended after bulk content imports, major structural changes, or after restoring from a ZODB backup.
- **Test before resync:** Always run *Test ZMS-Index* first to understand the current state before running the potentially destructive *Path-based Resync*.
- **Resync is incremental:** The resync operation commits intermediate transactions (controlled by `ZMSIndexZCatalog.resync.transaction_size`) to prevent memory issues on large sites.
- **Direct catalog access:** Use the *Show zcatalog_index* action to directly query the ZCatalog for debugging — e.g. to find objects by UID, check path entries, or verify custom index fields.
- **Schema extensions are persistent:** Once custom attributes are added and saved, they survive restarts. Remove them by clearing the input field and saving, then optionally recreate the catalog via re-index.
