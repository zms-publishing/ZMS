# ZMS Meta-Command Provider

The **Meta-Command Provider** (`metacmd_manager`) manages custom actions —
executable scripts that extend the ZMS management interface with
project-specific operations. Actions can add new insert options, custom
management tabs, repository hooks, catalog integrations, and more.

## Core Concepts

### What is a Meta-Command?

A meta-command is a named, executable script (Page Template, Python Script,
External Method, or DTML) registered in ZMS and accessible through the
management GUI. Each command has:

- A unique **ID** following a naming convention that determines its role
- An **implementation** (the actual code)
- Optional **filters** controlling where and for whom the command appears

### Stereotypes (ID Naming Conventions)

The command's ID prefix determines how ZMS integrates it:

| Prefix | Stereotype | Behavior |
|---|---|---|
| `manage_add*` | Insert Action | Appears in the "Insert" menu for adding custom objects |
| `manage_tab*` | Custom Tab | Adds a new management tab to matching content types |
| `manage_repository*` | Repository Hook | Executes during repository sync operations |
| `manage_zcatalog*` | ZCatalog Hook | Integrates with ZCatalog indexing |
| `manage_zmsindex*` | ZMS Index Hook | Integrates with ZMS index operations |
| *(other)* | Generic Action | Appears in the context menu or action list |

### Execution Modes

| Mode | Label | Behavior |
|---|---|---|
| `0` | Normal | Execute server-side, then redirect back to the UI |
| `1` | Omit UI | Execute without rendering any management UI (headless) |
| `2` | Script | Client-side JavaScript execution |

### Implementation Types

| Type | Description |
|---|---|
| `Page Template` | Zope Page Template (ZPT) — full HTML rendering |
| `Script (Python)` | Restricted Python script |
| `External Method` | Unrestricted Python via filesystem module |
| `DTML Method` | Legacy DTML template (deprecated) |

### Filtering

Each command can be restricted by:

- **Meta-Types** — only show for specific content types
- **Roles** — only show for users with specific roles
- **Nodes** — only show on specific nodes (by path pattern)

### Acquisition

In multi-site setups, sub-sites can **acquire** commands from their portal
master, sharing custom actions without duplication.

## GUI Layout

### Actions Tab (`manage_main`)

The main command editor with a two-panel layout:

- **Left Panel** — list of all registered commands with icons, names, and
  package assignment. Click a command to edit it.
- **Right Panel** — editor for the selected command:
  - **Properties** — ID, revision, name, title, description, icon class
  - **Package** — group assignment for organization
  - **Meta-Types** — content types where this action appears
  - **Roles** — user roles allowed to execute this action
  - **Nodes** — path patterns restricting where the action is available
  - **Execution Mode** — normal, headless, or client-side
  - **Code Editor** — ACE editor with syntax highlighting for the
    implementation source code
  - **Import / Export / Copy / Delete** action buttons

### Acquire Dialog (`manage_main_acquire`)

Select commands from the portal master to inherit in the current site.

## API Reference

### Command Access

| Method | Returns | Description |
|---|---|---|
| `getMetaCmdDescription(id)` | `str` | Description string for a command |
| `getMetaCmd(id)` | `dict` | Full command definition (resolves acquired commands) |
| `getMetaCmdIds(sort)` | `list` | Sorted list of all command IDs |
| `getMetaCmds(context, stereotype, sort)` | `list[dict]` | Filtered list of commands for a given context, stereotype, and sort |

### Command CRUD

| Method | Description |
|---|---|
| `setMetacmd(id, ...)` | Create or update a command (creates the Zope object with example code if new) |
| `delMetacmd(id)` | Delete a command and its Zope template object |

### Import / Export

| Method | Description |
|---|---|
| `importMetacmdXml(xml)` | Import commands from XML |
| `manage_changeProperties(REQUEST)` | ZMI form handler: insert, save, copy, delete, export, import, acquire |

### Repository

| Method | Returns | Description |
|---|---|---|
| `provideRepository(ids)` | `dict` | Export commands to filesystem repository |
| `updateRepository(r)` | `str` | Import a command from filesystem repository |

### Command Properties

Each command dict contains:

| Key | Type | Description |
|---|---|---|
| `id` | `str` | Unique command ID (naming convention determines stereotype) |
| `name` | `str` | Display name |
| `title` | `str` | Tooltip / title text |
| `description` | `str` | Extended description |
| `icon_clazz` | `str` | Font Awesome icon class |
| `meta_types` | `list` | Content types where the command appears |
| `roles` | `list` | Roles allowed to execute |
| `nodes` | `str` | Node path filter pattern |
| `execution` | `int` | Execution mode (0=normal, 1=headless, 2=script) |
| `package` | `str` | Package grouping |
| `revision` | `str` | Revision identifier |
| `impl` | `str` | Implementation type (Page Template, Script, etc.) |
| `data` | `str` | Source code of the implementation |

## Tips

- Follow the **ID naming convention** strictly — ZMS uses the prefix to
  determine how and where the command appears in the UI.
- Use **`manage_tab*`** commands to add fully custom management tabs to
  specific content types.
- The **Execution Mode "Omit UI"** is ideal for background operations
  (batch processing, data migration) that don't need visual feedback.
- **Acquired** commands are read-only in sub-sites — edit them in the
  portal master.
- New commands are pre-filled with **example code** matching the selected
  implementation type — a useful starting point.
- Use **Roles** and **Meta-Types** filtering to keep context menus clean
  and prevent unauthorized access to sensitive operations.
- Commands are stored in the **filesystem repository** (when enabled),
  making them version-controllable with Git.
