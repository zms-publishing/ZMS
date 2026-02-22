# ZMS Filter Manager

The **Filter Manager** is a ZMS administration interface for defining content **import and export filters**. Filters are processing pipelines that transform ZMS content into specific output formats (PDF, HTML, Excel, XML, …) or import external data (e.g. Excel spreadsheets) into ZMS content objects. Each filter chains one or more **processes** — the individual transformation steps.

> **Path:** *Login as ZMS Admin → Configuration → Filter*

---

## Core Concepts

### Filters

A **filter** defines a complete transformation pipeline. It specifies:

| Property | Description |
|---|---|
| **Id** | Unique identifier (e.g. `pdfExport`, `excel2ZMSRecordSetImport`). |
| **Display** | Human-readable name shown in the ZMS GUI (e.g. *"PDF-Printversion"*). |
| **Format** | The transformation direction and type: `import`, `export`, `XML`, `XHTML`, or a custom XML format. |
| **Content-Type** | The MIME type of the output (e.g. `application/pdf`, `text/html; charset=utf-8`, `text/xml`). |
| **Roles** | Which user roles are allowed to execute the filter (e.g. `ZMSAdministrator`, `ZMSEditor`, `ZMSAuthor`, or `*` for all). |
| **Objects** | Which ZMS meta-types the filter applies to (e.g. `ZMSDocument`, `ZMSFolder`, `ZMS`, or `*` for all). Can also filter by object type like `type(ZMSDocument)`. |
| **Description** | Optional description text. |
| **Process Sequence** | An ordered chain of process steps that are executed sequentially to produce the output. |

### Processes

A **process** is a single transformation step. Processes are defined globally and can be reused across multiple filters. Each process has:

| Property | Description |
|---|---|
| **Id** | Unique identifier (e.g. `xslt`, `fop`, `tidy`). |
| **Display** | Human-readable name (e.g. *"XSLT (Saxon)"*, *"FOP (XSLT)"*). |
| **Type** | The execution type — one of: |
| | • **`process`** — a shell command (command-line tool). |
| | • **`Script (Python)`** — a Zope Python Script executed inline. |
| | • **`External Method`** — a Zope External Method. |
| | • **`DTML Method`** — inline DTML code. |
| **Command** | The executable content: a shell command template for `process` type, or inline script code for the other types. |

### Filter–Process Pipeline

Filters execute their processes in a defined **sequence**. Each process step transforms the output of the previous step. The pipeline supports two patterns:

1. **Shell commands** use placeholder variables in the command template:
   - `{in}` — path to the input file (output of the previous step).
   - `{out.<ext>}` — path to the output file (e.g. `{out.xml}`, `{out.pdf}`).
   - `{trans}` — path to a companion resource file (e.g. an XSLT stylesheet, a Tidy config, a DTD).

2. **Inline scripts** (Python Script, DTML Method, External Method) are executed within the Zope context and have access to the ZMS content tree.

Each process step in a filter can carry an optional **resource file** (a companion file uploaded alongside the process reference). For shell-type processes, this file is passed via the `{trans}` placeholder.

---

## GUI Layout

The interface shows two main sections: **Filters** and **Processes**.

### Filters Section

#### Toolbar

| Button | Description |
|---|---|
| **☑ Select All / None** | Toggle-selects all filter checkboxes. |
| **＋ Insert** | Opens a dialog to create a new filter (Id, Display, Format, Content-Type). |
| **✕ Delete** | Deletes all selected filters after confirmation. |
| **⬆ Import** | Opens a dialog to import filter definitions from an `.filter.xml` file or from a built-in configuration template. |
| **⬇ Export** | Exports the selected filters (and their referenced processes) as an `.filter.xml` file. |

#### Filter List

Each filter row shows:
- A **checkbox** for selection.
- An **acquired** icon (↗) if the filter is inherited from a portal master site.
- A **collapse toggle** (▸) to reveal the filter's process pipeline visualization.
- The **filter name** as a link — clicking opens the filter's detail dialog.

#### Process Pipeline Visualization (collapsed by default)

Expanding a filter row reveals a vertical flow diagram:

```
 ┌──────────────┐
 │  XHTML       │  ← Format (blue box)
 └──────┬───────┘
        ↓
 ┌──────────────┐
 │  <HTML>Tidy  │  ← Process step (green box)
 └──────┬───────┘
     ── ┼ ──────── 0.tidy.zms2html.conf   ← Resource file (white box)
        ↓
 ┌──────────────┐
 │  XSLT (Saxon)│
 └──────┬───────┘
     ── ┼ ──────── 6.xhtml2fo.xsl
        ↓
 ┌──────────────┐
 │  FOP (XSLT)  │
 └──────┬───────┘
        ↓
 ┌──────────────┐
 │ ⬇ application │  ← Output content-type (blue box)
 │   /pdf        │
 └───────────────┘
```

Import filters show an **⬆ upload** icon instead of ⬇ at the bottom.

#### Filter Detail Dialog

Clicking a filter name opens a modal dialog with editable properties:

- **Id** and **Display** — the filter's identifier and display name.
- **Format** — dropdown: `Import`, `Export`, `XML-Export`, `XHTML-Export` (plus custom formats if configured).
- **Content-Type** — dropdown with registered MIME types.
- **Roles** — multi-select of user roles (including `*` for all).
- **Objects** — multi-select of ZMS meta-types (including `*` for all, and `type(...)` entries for broader object-type matching).
- **Description** — free-text description.
- **Process Sequence** — a sortable table of process steps:
  - Each row has a **sort-order** dropdown, a **process selector**, and an optional **resource file** upload.
  - Rows can be reordered by changing the sort dropdown value.
  - The **＋** button at the bottom adds a new process step.
  - The **✕** button removes a process step.

---

### Processes Section

#### Toolbar

| Button | Description |
|---|---|
| **☑ Select All / None** | Toggle-selects all process checkboxes. |
| **＋ Insert** | Opens a dialog to create a new process (Id, Display, Type). |
| **✕ Delete** | Deletes all selected processes after confirmation. |
| **⬆ Import** | Imports process definitions from an `.filter.xml` file. |
| **⬇ Export** | Exports selected processes as an `.filter.xml` file. |

#### Process List

Each process row shows:

| Column | Description |
|---|---|
| **Checkbox** | For selection (delete, export). |
| **Id + Name** | The process Id (bold) and display name. The icon reflects the Zope object type (⚙ for shell commands, script icon for Python/DTML). |
| **Command Preview** | A truncated preview of the process command. Hovering shows the full command in a tooltip. Clicking opens the detail dialog. |

#### Process Detail Dialog

Clicking a process opens a modal with:
- **Id** and **Display** — identifier and display name.
- **Type** — read-only display of the process type (set at creation time).
- **Command** — a full code editor (ACE Editor) for the shell command template or inline script code.

---

## Common Filter Examples

### Export Filters

| Filter | Description | Process Chain |
|---|---|---|
| **PDF-Printversion** | Renders ZMS content as PDF via XHTML→XSL-FO→PDF. | Tidy → (DTD/entity files) → htmlEntities → XSLT (xhtml2fo.xsl) → FOP |
| **HTML-Printversion** | Renders ZMS content as clean XHTML. | Tidy (with config) |
| **DocBook-Export** | Exports content in DocBook XML format. | XSLT transformations |
| **RecordSet Excel-Export** | Exports ZMSRecordSet data as Excel spreadsheet. | ZMSRecordSet2Excel (DTML) |

### Import Filters

| Filter | Description | Process Chain |
|---|---|---|
| **Excel Recordset-Import** | Imports Excel spreadsheet data into ZMSRecordSet objects. | excel2ZMSRecordSet (DTML) → XSLT transformation |
| **XHTML-Import** | Imports XHTML content into ZMS. | (custom process chain) |

---

## Import / Export of Filter Configurations

Filter and process definitions can be serialized as **XML configuration files** (`.filter.xml`). This allows:

- **Backup and restore** of filter configurations.
- **Transfer** of filter setups between ZMS instances.
- **Version control** via the Repository Manager (filters are stored under `filter_manager/filters/` and `filter_manager/processes/`).

### XML Import

1. Click the **⬆ Import** button.
2. Either upload a `.filter.xml` file or select a built-in template from the dropdown.
3. Click **Import**.

### XML Export

1. Select the desired filters or processes via checkboxes.
2. Click the **⬇ Export** button.
3. A `.filter.xml` file is downloaded containing the selected definitions.

---

## Repository Structure

When managed by the Repository Manager, filter configurations are stored on the filesystem:

```
filter_manager/
├── filters/
│   ├── pdfExport/
│   │   ├── __init__.py              # Filter definition (Python class)
│   │   ├── 0.tidy.zms2html.conf     # Resource file for process step 0
│   │   └── 6.xhtml2fo.xsl           # Resource file for process step 6
│   ├── xhtmlExport/
│   │   ├── __init__.py
│   │   └── 0.tidy.zms2html.conf
│   └── excel2ZMSRecordSetImport/
│       └── __init__.py
└── processes/
    ├── xslt/
    │   └── __init__.py              # Process definition (Python class)
    ├── fop/
    │   └── __init__.py
    ├── tidy/
    │   └── __init__.py
    └── excel2ZMSRecordSet/
        └── __init__.py
```

Each `__init__.py` contains a Python class representation of the filter or process. Resource files (XSLT stylesheets, Tidy configs, DTDs, etc.) are stored as sibling files within the filter's folder.

---

## Acquisition from Portal Master

In a **multi-site ZMS setup**, filters and processes can be **acquired** from a portal master site. Acquired items are shown with a ↗ icon and are read-only in the child site. This enables centralized filter management: define filters once in the master site and have all child sites inherit them automatically.

---

## Tips

- **Process reuse:** Define processes as generic building blocks (e.g. a generic XSLT process, a generic Tidy process) and combine them in different filters. This avoids duplication and simplifies maintenance.
- **Shell command paths:** Shell-type process commands typically reference external tools (Saxon, FOP, Tidy, etc.) by absolute path. Ensure these tools are installed and accessible on the server.
- **Resource files:** When a filter process step needs a companion file (e.g. an XSLT stylesheet), upload it in the process sequence section of the filter detail dialog. It will be stored as a Zope File object and passed to the process via the `{trans}` placeholder.
- **Testing pipelines:** Use the filter on a small content subtree first to verify the output before running it on the entire site.
- **Custom formats:** If a `getObjToXml_DocElmnt` method is available, an additional *myXML* export format appears in the format dropdown, enabling project-specific XML serialization.
