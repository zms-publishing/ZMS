# ZMS Repository Manager

The **Repository Manager** is a ZMS administration interface for synchronizing the current ZMS configuration (stored in the ZODB) with a filesystem-based repository. It enables version-controlled management of ZMS configuration objects such as content-model definitions, meta-commands, workflows, filters, and system configuration.

> **Path:** *Login as ZMS Admin → Configuration → Repository*

---

## Overview

The Repository Manager compares configuration objects living in the ZODB (referred to as **local**) with their filesystem representation (referred to as **remote / repository**). Configuration objects are serialized as Python class files (`__init__.py` / `__acquired__.py`) along with associated artefacts (templates, scripts, images, etc.) so that they can be tracked by a version control system like Git.

---

## GUI Layout

The interface is organized into **two tabs**:

### 1. Code-Diff Tab (default)

This is the main working area. It shows the synchronization state between ZODB and filesystem.

#### Control Bar (sticky)

| Element | Description |
|---|---|
| **☑ Select All / None** | Toggle button to select or deselect all listed configuration objects at once. |
| **Refresh** | Reloads the diff view by re-reading local (ZODB) and remote (filesystem) files and re-computing the differences. |
| **Export** | Commits the selected configuration objects from the ZODB **to** the filesystem repository. This button is highlighted (primary style) when the working mode is set to *Export Mode*. |
| **Import** | Updates the selected configuration objects in the ZODB **from** the filesystem repository. This button is highlighted (primary style) when the working mode is set to *Import Mode*. |
| **Repository-Interaction** *(dropdown, optional)* | A dropdown menu listing custom meta-commands registered for the `repository` context (e.g. Git status, Git pull, Git push). These are project-specific commands configured in the *Meta-Command Manager*. |

#### System-Path Display

Shows the currently configured filesystem path that connects the ZMS instance to the repository. Double-clicking this field switches to the *Properties* tab and focuses the path input for editing.

The path may contain the following variables:
- `$INSTANCE_HOME` – resolves to the Zope instance home directory.
- `$HOME_ID` – resolves to a slash-separated path built from the ZMS home object IDs in the breadcrumb hierarchy.

#### Working Mode Indicator

Displays the active comparison direction and a color legend:

| Color | State |
|---|---|
| 🟩 **Green** (`alert-success`) | **New** – the object exists only on one side. |
| 🟨 **Yellow** (`alert-warning`) | **Modified** – the object exists on both sides but content differs. |
| 🟥 **Red** (`alert-danger`) | **Deleted** – the object has been removed from one side. |

#### File List (no differences)

When all configuration objects are in sync, a flat list with ✅ check-marks is displayed for each provider, confirming that no differences were found.

#### File List (with differences)

When differences exist, objects are grouped by **provider** (e.g. `metaobj_manager`, `metacmd_manager`, `workflow_manager`, `filter_manager`, `zcatalog_connector`, `sys_conf`, etc.). Each provider section contains a table of changed objects:

| Column | Description |
|---|---|
| **Checkbox** | Select individual objects for import or export. |
| **Object ID** | The identifier of the configuration object (with an icon reflecting its type). Clicking opens the object's configuration page in a new tab. |
| **Changed Files** | Lists the individual files that differ for this object. Each file entry shows a colored state indicator (new / modified / deleted) and the filename. Clicking a filename scrolls to its detailed diff view below. Double-clicking opens the object's edit page. |

#### Changesets (Diff View)

Below the file list, the **Changesets** section shows a side-by-side text diff for every modified text-based file (Python, ZPT, JSON, XML, YAML, JavaScript, DTML, CSS, etc.):

- **File header:** Shows the filename, MIME type, ZODB version/size, and repository version/size with a directional arrow (← for import, → for export).
- **Diff rendering:** Uses the *google-diff-match-patch* library to highlight inserted (`<ins>`) and deleted (`<del>`) text. Unchanged lines are collapsed by default; clicking the object's name in the header toggles full-file display.

> **Note:** Binary files (images, etc.) are not displayed in the diff view.

---

### 2. Properties Tab

This tab configures the Repository Manager settings.

| Field | Description |
|---|---|
| **System Path** | The filesystem path to the repository folder. Supports the variables `$INSTANCE_HOME` and `$HOME_ID`. If the system property `ZMS.conf.paths` is set (comma-separated list), a dropdown selection is shown instead of a free-text input. The selected path is stored in the system property `ZMS.conf.path`. |
| **Working Mode** | Controls how code differences are colored: |
|  | • **Import Mode** *(default)*: Shows changes in the filesystem compared to ZMS – use this to review what *would be imported* into the ZODB. |
|  | • **Export Mode**: Shows changes in ZMS compared to the filesystem – use this to review what *would be exported* to the repository. |
| **Ignore orphans** | When checked, files in the filesystem that have no corresponding reference in the ZODB model are ignored in the diff view. This prevents showing leftover or manually added files as differences. |
| **Ignore sys_conf** | When checked, the system configuration provider (`sys_conf`) is excluded from the diff comparison. |
| **Save** | Persists the settings above. |

---

## How to Synchronize Configuration with a Repository

### Initial Setup

1. Navigate to **ZMS Admin → Configuration → Repository**.
2. Switch to the **Properties** tab.
3. Enter or select the **System Path** pointing to your repository's configuration folder (e.g. `$INSTANCE_HOME/../src/myproject/model`).
4. Choose the appropriate **Working Mode** (typically *Import Mode* for pulling changes, *Export Mode* for pushing changes).
5. Click **Save**.

### Exporting Configuration to the Filesystem (ZODB → Repository)

Use this workflow to persist the current ZODB configuration to disk so it can be committed to Git.

1. On the **Code-Diff** tab, click **Refresh** to compute the current differences.
2. Review the listed differences. Yellow-highlighted objects have been modified, green ones are new, red ones have been deleted.
3. Select the objects you want to export using the checkboxes (or use the **Select All** toggle).
4. Click **Export**.
5. The selected objects are serialized as Python class files and written to the configured filesystem path.
6. Use the **Repository-Interaction** dropdown (if configured) or a terminal to run Git commands (`git add`, `git commit`, `git push`).

### Importing Configuration from the Filesystem (Repository → ZODB)

Use this workflow to load configuration changes from the filesystem (e.g. after a `git pull`) into the running ZMS instance.

1. If needed, pull the latest changes from your remote Git repository first (via **Repository-Interaction** dropdown or terminal).
2. On the **Code-Diff** tab, click **Refresh** to see what has changed on the filesystem.
3. Review the diff view carefully – especially version numbers and the changeset details.
4. Select the objects you want to import.
5. Click **Import**.
6. The selected configuration objects in the ZODB are updated from the filesystem data.

### Tips

- **Version tracking:** Each configuration object carries a `revision` property (e.g. `1.0.0`). The diff view shows version numbers for both sides. An *incoming* change is detected when the repository version is higher than the ZODB version.
- **Events:** The Repository Manager triggers `beforeCommitRepositoryEvt` / `afterCommitRepositoryEvt` for exports and `beforeUpdateRepositoryEvt` / `afterUpdateRepositoryEvt` for imports. These can be used to hook custom automation (e.g. cache clearing, reindexing).
- **Providers:** Configuration objects are organized by *providers* – manager objects that implement `IZMSRepositoryProvider` (e.g. MetaObj-Manager for content models, MetaCmd-Manager for meta-commands, etc.). Each provider serializes and deserializes its own objects.
- **Conflict resolution:** If both ZODB and filesystem have diverged, carefully review the diff before deciding whether to import or export. There is no automatic merge – the selected action fully overwrites one side with the other.

---

## File Structure on the Filesystem

A typical repository folder looks like this:

```
<basepath>/
├── metaobj_manager/
│   ├── com.example.article/
│   │   ├── __init__.py          # Python class representation
│   │   ├── standard_html.zpt    # Associated page template
│   │   └── icon.png             # Icon artefact
│   └── com.example.news/
│       └── __init__.py
├── metacmd_manager/
│   └── manage_myaction/
│       └── __init__.py
├── workflow_manager/
│   └── com.example.workflow/
│       └── __init__.py
├── filter_manager/
│   └── ...
└── sys_conf/
    └── __init__.py              # System configuration
```

Each `__init__.py` contains a Python class whose attributes represent the configuration object's properties. Artefacts (templates, scripts, images) are stored as sibling files within the same folder.

---

## Related System Properties

| Property | Description |
|---|---|
| `ZMS.conf.path` | The active filesystem path to the repository. |
| `ZMS.conf.paths` | Comma-separated list of selectable repository paths (enables dropdown in Properties). |
| `ZMS.conf.ignore.sys_conf` | Set to `1` to exclude `sys_conf` from the diff. |
| `ZMS.mode.debug` | Enables additional CSS classes for debugging in the diff view. |
