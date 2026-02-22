# ZMS Link Element

The **ZMS Link Element** is a versatile reference object that can act as a
simple hyperlink, an inline content embed, or a full recursive proxy for
another content node — even across remote ZMS instances. It extends
`ZMSCustom` (and thus `ZMSContainerObject`) to integrate seamlessly into the
content tree.

## Core Concepts

### Embed Types

The behavior of a link element is determined by its embed type:

| Type | Description |
|---|---|
| **`embed`** | Displays the referenced object's content inline on the parent page. The link element itself is invisible in navigation. |
| **`recursive`** | Full proxy delegation — the link element mirrors the entire subtree of the referenced object, appearing as if the referenced content lives here. |
| **`remote`** | Fetches content from an external ZMS instance via REST API (`/manage_ajaxZMIActions` / JSON endpoints). |
| *(none)* | A simple hyperlink — renders as a clickable link in navigation or content. |

### Proxy Pattern

Nearly every method on `ZMSLinkElement` has a `*PROXY` counterpart (e.g.
`getNavItems` → `getNavItemsPROXY`). When the link is in recursive/embed
mode, the proxy method delegates to the referenced object's `getRefObj()`,
making the link element transparent to navigation, search, and rendering.

### Cyclic Reference Guard

`isEmbeddedRecursive()` checks for cyclic references and sets a `'cyclic'`
flag to prevent infinite recursion when link elements reference each other.

## GUI Layout

### Link Browser Dialog (`manage_browse_iframe`)

A modal dialog with two tabs for selecting link targets:

- **Sitemap Tab** — tree-based internal link picker with a search/filter bar.
  Search results show paginated, filterable content objects. Selecting a node
  generates a ZMS UID reference (`{$<uid>;lang=xx}`).
- **External Link Tab** — protocol dropdown (`https`, `http`, `file`,
  `mailto`, `ftp`) with a free-text URL input field.
- **Language Selector** — appears in multilingual sites to pick the target
  language variant.

### References Tab (`manage_refs_iframe`)

Shows all **back-references** — objects that link *to* this content node:

- Checkbox list of referencing objects with breadcrumb paths
- **Retarget** form to bulk-redirect selected references to a new target
  (uses the link picker and HTMX `hx-post="manage_change_refs"`)
- Success/warning message with counts of changed/unchanged references

## API Reference

### Embed & Reference

| Method | Returns | Description |
|---|---|---|
| `isEmbedded(REQUEST)` | `bool` | True if embed type is `embed` or `recursive` |
| `isEmbeddedRecursive(REQUEST)` | `bool` | True if embed type is `recursive` (with cyclic check) |
| `isRemote(REQUEST)` | `bool` | True if embed type is `remote` |
| `getRefObj()` | object | The referenced ZMS object (resolved from UID) |
| `getRemoteObj()` | object | Fetch remote object via REST API |
| `getEmbedUrl(REQUEST)` | `str` | URL of the embedded/referenced content |

### Properties & Metadata

| Method | Returns | Description |
|---|---|---|
| `getRef()` | `str` | Raw reference value (UID string or URL) |
| `isMetaType(meta_type)` | `bool` | Delegates to referenced object when embedded |
| `getTitlealt(REQUEST)` | `str` | Title (proxied from ref when embedded) |
| `getTitle(REQUEST)` | `str` | Display title (proxied from ref when embedded) |
| `getDCDescription(REQUEST)` | `str` | Dublin Core description (proxied) |
| `getDCCoverage(REQUEST)` | `str` | Dublin Core coverage (proxied) |

### Navigation (Proxy-Aware)

| Method | Returns | Description |
|---|---|---|
| `getNavItems(current, REQUEST)` | `list` | Navigation items (delegates to ref when recursive) |
| `getNavElements(REQUEST)` | `list` | Navigation elements (delegates to ref when recursive) |
| `isVisible(REQUEST)` | `bool` | Visibility check (respects embed type) |
| `isPage()` | `bool` | True if this acts as a page node |
| `isPageElement()` | `bool` | True if this acts as an inline element |

### Presentation

| Method | Returns | Description |
|---|---|---|
| `getBodyContent(REQUEST)` | `str` | Rendered HTML (from ref when embedded) |
| `renderShort(REQUEST)` | `str` | Short preview rendering |
| `printHtml(level, sectionizer, REQUEST)` | `str` | Print-optimized HTML output |

### Reference Management

| Method | Returns | Description |
|---|---|---|
| `synchronizeRefByObjs()` | — | Sync the back-reference index |
| `getRefByObjs(REQUEST)` | `list` | All objects that reference this node |
| `manage_change_refs(REQUEST)` | HTML | HTMX endpoint to retarget back-references |

## Tips

- Use **`embed`** mode to reuse content blocks (e.g. a shared disclaimer)
  across multiple pages without duplication.
- Use **`recursive`** mode to mirror an entire subtree — ideal for portal
  client scenarios where content from a master site appears in a sub-site.
- The **References Tab** is essential before deleting or moving content —
  it shows all incoming links that would break.
- **Remote embedding** requires the target ZMS instance to be accessible
  via HTTP and to expose its REST API endpoints.