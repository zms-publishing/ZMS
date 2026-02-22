# ZMS Container Object

The **ZMS Container Object** is the abstract base class for all page-level
content nodes in ZMS. Every document, folder, or custom page type inherits
from `ZMSContainerObject`, which provides child-node management, navigation
tree construction, drag-and-drop ordering, import/export, and the main
editing interface.

## Core Concepts

### Page Elements vs. Pages

Child nodes are split into two categories:

| Category | Description |
|---|---|
| **Page Elements** | Content blocks displayed inline on the parent page (text areas, images, tables, etc.). These are non-page meta-types. |
| **Pages** | Child pages that form separate nodes in the navigation tree (documents, folders, custom page types). |

The main editing view renders page elements in the upper section and pages
in the lower section, each as a sortable list.

### Sort Order

Every child has a `sort_id` that determines its display position. The GUI
supports drag-and-drop reordering via `manage_ajaxDragDrop()`, which returns
an XML response and updates sort IDs accordingly.

### Meta-Type Constants

`getChildNodes()` accepts meta-type filter lists using built-in constants:

| Constant | Content |
|---|---|
| `PAGES` | All page-level meta-types |
| `PAGEELEMENTS` | All inline-element meta-types |
| `NOREF` | Exclude reference/link elements |
| `NORESOLVEREF` | Include links but don't resolve them |

## GUI Layout

### Main Edit View (`manage_main`)

The primary editing interface for any container page:

- **Page Elements** — sortable list of inline content blocks (text, images, etc.)
  with workflow state CSS classes (`is-new`, `is-modified`, `is-deleted`)
- **Pages** — sortable list of child pages with navigation links
- **Actions** — context menu for adding, cutting, copying, pasting, and
  deleting child nodes
- **Portal Clients** — section showing linked portal client sites (if any)

### Grid View (`main_grid`)

A paginated table view (10 items per page) with:

- Checkboxes for bulk selection
- Breadcrumb navigation
- Short content preview (`renderShort`)
- Page navigation controls

### System Tab (`manage_system`)

Lists all Zope sub-objects with their meta-type, ID, size, and modification
date. Provides standard Zope operations:

- Cut / Copy / Paste / Delete / Rename
- Import / Export

### Import/Export Tab (`manage_importexport`)

- **Import** — file upload with filter selection, options to ignore UIDs/IDs
- **Export** — supports XML, ZEXP, HTML, and filter-based formats with
  download/server-save and preview options

### Debug Filter Tab (`manage_importexportdebugfilter`)

An interactive step-by-step filter execution view with a visual process
chain and iframe-based log viewer for troubleshooting export/import filters.

## API Reference

### Child Node Management

| Method | Returns | Description |
|---|---|---|
| `getChildNodes(REQUEST, meta_types, reid)` | `list` | Core method: returns filtered, sorted child nodes by meta-type, coverage, and language |
| `manage_addZMSCustom(meta_id, values, REQUEST)` | object | Add a custom ZMS node by meta-object ID |
| `manage_addZMSModule(meta_id, values, REQUEST)` | object | Add a module node from ZEXP template |
| `addNode(REQUEST)` | object | Factory: create any ZMS object child |
| `moveObjsToTrashcan(ids, REQUEST)` | — | Move children to trashcan (cut + paste + unindex) |
| `manage_deleteObjs(ids, REQUEST)` | — | Physical delete of child objects |
| `manage_undoObjs(ids, REQUEST)` | — | Rollback changes on children with pending workflow states |
| `manage_eraseObjs(ids, REQUEST)` | — | Logical delete (trashcan or `STATE_DELETED`) |

### Sort Order

| Method | Returns | Description |
|---|---|---|
| `manage_ajaxDragDrop(id, pos, REQUEST)` | XML | Reorder children via drag-and-drop |
| `normalizeSortIds()` | — | Re-number sort IDs to 10, 20, 30… |
| `getNewSortID()` | `int` | Next available sort ID |

### Navigation

| Method | Returns | Description |
|---|---|---|
| `getFirstPage(REQUEST)` | node | First page of tree |
| `getPrevPage(REQUEST)` | node | Previous page in navigation |
| `getNextPage(REQUEST)` | node | Next page in navigation |
| `getLastPage(REQUEST)` | node | Last page of subtree |
| `getNavItems(current, REQUEST)` | `list` | DOM traversal for paged iteration across tree |
| `getNavElements(REQUEST)` | `list` | Main-navigation elements in content area |
| `getIndexNavElements(REQUEST)` | `list` | Index-navigation elements |

### Tree Traversal

| Method | Returns | Description |
|---|---|---|
| `getTreeNodes(REQUEST, meta_types)` | `list` | All visible children in subtree with optional ordering |
| `getFirstVisibleChildNode(REQUEST)` | node | First visible child |
| `filteredChildNodes(REQUEST, meta_types)` | `list` | All visible direct children |

### Presentation

| Method | Returns | Description |
|---|---|---|
| `getBodyContent(REQUEST)` | `str` | HTML content of the page body |
| `ajaxGetNode(context_id, REQUEST)` | JSON | ZMI context actions for a node |
| `getNavHtml(node, REQUEST, opt)` | `str` | HTML `<ul>` navigation with CSS classes |

## Tips

- Use the **Grid View** for quick overview and bulk operations on
  containers with many children.
- **Drag-and-drop** reordering works in both the main view and the grid view.
- The **Debug Filter** tab is invaluable for troubleshooting complex
  import/export filter chains step by step.
- `getChildNodes()` is the central method for all navigation and content
  rendering — it respects language, coverage, and meta-type filters.
