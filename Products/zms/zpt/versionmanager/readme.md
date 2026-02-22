# ZMS Version Manager

The **Version Manager** controls the complete lifecycle of content changes in
ZMS — from initial editing through workflow approval to final publication. It
provides versioning, undo/rollback, tagging, and history tracking for every
content node.

## Core Concepts

### Version Number Scheme

Versions follow a three-part numbering: **`Major.Minor.Patch`**

| Component | Bumped when… |
|---|---|
| **Major** | `tagObjVersions()` is called (explicit tagging / release) |
| **Minor** | A work version is committed to live (`commitObjChanges`) |
| **Patch** | A new work copy is created (`setObjStateNew` — each save) |

### Object States

Every content node carries a list of state flags reflecting its editing status:

| State | Meaning |
|---|---|
| `STATE_NEW` | Newly created, not yet committed |
| `STATE_MODIFIED` | Existing object with pending changes |
| `STATE_DELETED` | Marked for deletion (logical delete) |
| `STATE_MODIFIED_OBJS` | Container whose children have pending changes |

### Attribute Containers

ZMS stores each version's data in a `ZMSAttributeContainer` sub-object.
There can be a **live** version (published) and a **work** version (draft)
simultaneously. Historical versions are retained when the `History` feature
is enabled.

## GUI Layout

### Undo / Diff View (`manage_UndoVersionForm`)

A side-by-side comparison of two tagged versions:

- **Left panel** — the selected historical version (rendered HTML)
- **Right panel** — the current live/work version
- **Diff toggle** — switch between visual HTML diff and raw JSON diff
- **Reset button** — restore the selected version (rollback)

### Object State Icons (`versionmanager_main_change`)

Inline icons rendered next to each content node showing:

- Language / globe indicators
- Workflow state badges
- Version number display
- Custom hook indicators

## API Reference

### Tagging & Versions

| Method | Returns | Description |
|---|---|---|
| `tagObjVersions(master_version)` | — | Tag all children with a new major version, reset minor/patch to 0 |
| `getObjVersion(REQUEST)` | `str` | Version string in `v.M.m.p` format |
| `getVersionItems(REQUEST)` | `list` | All non-container children recursively |

### State Management

| Method | Returns | Description |
|---|---|---|
| `setObjState(msg, t0, lang)` | — | Append a state entry with timestamp and user |
| `getObjStates()` | `list` | All current state entries |
| `getObjState(state, REQUEST)` | `int` | Check if a specific state flag is set |
| `resetObjStates()` | — | Clear all state entries |
| `getWfActivities()` | `list` | Workflow activity IDs matching current states |

### State Transitions

| Method | Description |
|---|---|
| `setObjStateNew(REQUEST, forced=False)` | Initialize work version, set `STATE_NEW` |
| `setObjStateModified(REQUEST)` | Mark as `STATE_MODIFIED`, create work copy |
| `setObjStateDeleted(REQUEST)` | Mark as `STATE_DELETED` |

### Commit & Rollback

| Method | Description |
|---|---|
| `onChangeObj(REQUEST)` | Trigger thumbnails, events, then auto-commit or enter workflow |
| `commitObj(REQUEST)` | Promote work version to live, bump minor version, sync catalog |
| `commitObjChanges(REQUEST, forced=False)` | Full commit with before/after event hooks |
| `rollbackObj(REQUEST)` | Reverse pending changes (new → trashcan, modified → restore live) |
| `rollbackObjChanges(REQUEST, forced=False)` | Full rollback with before/after event hooks |

### History

| Method | Returns | Description |
|---|---|---|
| `hasHistory(REQUEST)` | `bool` | Check if history is enabled for this path |
| `packHistory()` | — | Remove all non-live/work attribute containers |
| `ajaxGetBodyContent(REQUEST)` | XML | AJAX endpoint returning rendered body for a given version |
| `getVersionBuildNo(REQUEST)` | `list` | Resolve a build number to matching attribute containers |

### Version Access

| Method | Returns | Description |
|---|---|---|
| `getObjVersion(REQUEST)` | `str` | Formatted version string |
| `getObjVersions()` | `list` | All attribute containers sorted by version (descending) |
| `restoreObjVersion(build_no, REQUEST)` | — | Clone a historical version back to work |

### Workflow Integration

| Method | Description |
|---|---|
| `initializeWorkflow(REQUEST)` | Clear workflow states, re-enter auto-transition |
| `autoWfTransition(REQUEST)` | Auto-enter first workflow transition on content change |
| `executeWfTransition(REQUEST, trans)` | Execute a named workflow transition |
| `doWfTransition(REQUEST, trans)` | Full transition: delete old state, add new, call activities |

## Tips

- Enable **History** via the `ZMS.Version.history` conf-property to keep
  all previous versions for audit and rollback.
- Use `tagObjVersions()` before major releases to create a named snapshot
  of the entire content tree.
- The **Undo** view shows a visual diff — use it to review changes before
  rolling back.
- Workflow integration is automatic: when a workflow is active, `onChangeObj`
  delegates to the workflow instead of auto-committing.
- The `preview` request parameter controls whether the work or live version
  is displayed — useful for preview-before-publish workflows.
