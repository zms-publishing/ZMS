# ZMS Meta-Model Provider

The **Meta-Model Provider** (`metaobj_manager`) is the central configuration
component for the ZMS content model. It manages two complementary registries:

- **Meta-Objects** (Content Types) — the structural building blocks of every
  ZMS site: documents, teasers, record sets, libraries, modules, etc.
- **Metadata Dictionary** — shared metadata attributes (Dublin Core fields,
  custom properties) reusable across multiple content types.

## Core Concepts

### Meta-Objects

A meta-object defines a content type — its attributes, rendering templates,
and behavior. Each meta-object has a unique ID and belongs to one of these
types:

| Type | Description |
|---|---|
| `ZMSDocument` | A page-level container (appears in navigation) |
| `ZMSObject` | An inline page element (text block, image, etc.) |
| `ZMSTeaserElement` | A teaser / reference element |
| `ZMSRecordSet` | Tabular data stored as a list of dictionaries |
| `ZMSResource` | A downloadable resource (file, archive) |
| `ZMSReference` | A reference / link element |
| `ZMSLibrary` | A shared library of reusable content |
| `ZMSPackage` | A package grouping related meta-objects |
| `ZMSModule` | An installable module (adds content + configuration) |

### Attribute Types

Each meta-object contains a list of typed attributes:

| Category | Types |
|---|---|
| **Data** | `string`, `text`, `richtext`, `int`, `float`, `amount`, `boolean`, `date`, `datetime`, `url`, `color`, `identifier`, `dictionary` |
| **Selection** | `select`, `multiselect`, `autocomplete`, `multiautocomplete` |
| **Media** | `image`, `file` |
| **Code** | `method`, `py`, `zpt`, `resource` |
| **Structure** | `constant`, `delimiter`, `hint` |
| **Zope** | `DTML Method`, `DTML Document`, `File`, `Folder`, `Image`, `Page Template`, `Script (Python)`, `Z SQL Method` |

### Metadata Dictionary

The metadata dictionary defines shared attributes available to all or
selected content types — typically Dublin Core fields like `DC.Title`,
`DC.Description`, `DC.Coverage`, plus custom metadata.

### Packages

Meta-objects can be grouped into **packages** for organization, export, and
import. A package bundles related content types together (e.g. a blog module
with its document types, teasers, and templates).

### Acquisition

In multi-site setups, sub-sites can **acquire** meta-objects from their
portal master, inheriting the content model without duplication.

## GUI Layout

### Content Types Tab (`manage_main`)

The main meta-object editor with a two-panel layout:

- **Left Panel** — list of all meta-objects grouped by package, with filter
  and search. Click a type to edit it.
- **Right Panel** — editor for the selected meta-object:
  - **Properties** — ID, name, type, description, package assignment, enabled
    flag
  - **Attributes Table** — ordered list of all attributes with columns for
    ID, name, type, mandatory, multilang, repetitive, and custom settings
  - **Attribute Editor** — inline form for adding/editing a single attribute
  - **Import / Export / Copy / Delete** action buttons

### Metadata Tab (`manage_metas`)

The metadata dictionary editor:

- Table of all defined metadata attributes
- For each: key, name, type, mandatory, default value
- Add / Edit / Delete / Reorder operations

### Import Dialog (`manage_main_import`)

Import meta-objects from:

- **XML file upload** — a `.metaobj.xml` export file
- **Built-in configurations** — pre-packaged content type definitions
  shipped with ZMS

### Acquire Dialog (`manage_main_acquire`)

Select meta-objects from the portal master to inherit in the current site.

### Big Picture (`manage_bigpicture`)

A visual diagram showing the full content model — all meta-objects and
their relationships (containment, references, packages).

### Analysis (`manage_analyze`)

Diagnostics view for detecting model inconsistencies, unused types, or
missing attributes.

## API Reference

### Meta-Object Access

| Method | Returns | Description |
|---|---|---|
| `getMetaobjIds(sort, excl)` | `list` | All meta-object IDs, optionally sorted and filtered |
| `getMetaobj(id)` | `dict` | Full meta-object definition by ID |
| `getMetaobjId(name)` | `str` | Resolve a meta-object ID from its display name |
| `getMetaobjRevision(id)` | `str` | Revision string of a meta-object |

### Meta-Object Attributes

| Method | Returns | Description |
|---|---|---|
| `getMetaobjAttrIds(id, types)` | `list` | Attribute IDs of a meta-object, optionally filtered by type |
| `getMetaobjAttrs(id, types)` | `list[dict]` | Full attribute dicts of a meta-object |
| `getMetaobjAttr(id, attr_id)` | `dict` | Single attribute definition |
| `evalMetaobjAttr(id, attr_id)` | varies | Evaluate (execute) a meta-object attribute |

### Meta-Object CRUD

| Method | Description |
|---|---|
| `setMetaobj(ob)` | Create or update a meta-object |
| `delMetaobj(id)` | Delete a meta-object |
| `acquireMetaobj(id)` | Acquire a meta-object from portal master |
| `setMetaobjAttr(id, attr_id, ...)` | Create or update an attribute |
| `delMetaobjAttr(id, attr_id)` | Delete an attribute |
| `moveMetaobjAttr(id, attr_id, pos)` | Reorder an attribute |

### Metadata Dictionary

| Method | Returns | Description |
|---|---|---|
| `getMetadictAttrs(types)` | `list[dict]` | All metadata attributes, optionally filtered |
| `getMetadictAttr(key)` | `dict` | Single metadata attribute by key |
| `setMetadictAttr(key, ...)` | — | Create or update a metadata attribute |
| `delMetadictAttr(key)` | — | Delete a metadata attribute |
| `moveMetadictAttr(key, pos)` | — | Reorder a metadata attribute |

### Rendering

| Method | Returns | Description |
|---|---|---|
| `renderTemplate(obj)` | `str` | Render a meta-object's presentation template |

### Import / Export

| Method | Returns | Description |
|---|---|---|
| `importMetaobjXml(xml)` | — | Import meta-objects from XML |
| `exportMetaobjXml(ids)` | XML | Export meta-objects as XML download |
| `importTheme(id)` | — | Import a ZMS theme package |

### Repository

| Method | Returns | Description |
|---|---|---|
| `provideRepository(ids)` | `dict` | Export model + metas to filesystem repository |
| `updateRepository(r)` | `str` | Import model + metas from filesystem repository |

## Tips

- Use **Packages** to organize related content types — this makes
  export/import and portal-master acquisition much cleaner.
- The **Big Picture** view is invaluable for understanding complex content
  models at a glance.
- When adding attributes of type `method`, `py`, or `zpt`, the code editor
  provides syntax highlighting via ACE editor.
- **Acquired** meta-objects are read-only in sub-sites — edit them in the
  portal master.
- The metadata dictionary is shared across all content types — use it for
  attributes like Dublin Core fields that apply universally.
- Use the **Analysis** view periodically to detect orphaned or inconsistent
  type definitions.
