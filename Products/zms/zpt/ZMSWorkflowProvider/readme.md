# ZMS Workflow Manager

The ZMS Workflow Manager (`ZMSWorkflowProvider`) implements a state-machine
model for editorial content workflows. It defines **activities** (states)
and **transitions** (edges between states) that control how content moves
through review and publication stages.

The provider object lives at `workflow_manager` inside the ZMS root and
implements `IZMSWorkflowProvider`, `IZMSConfigurationProvider`, and
`IZMSRepositoryProvider`.

## Core Concepts

| Concept | Description |
|---|---|
| **Activity** | A named workflow state (e.g. *Draft*, *Pending Review*, *Published*). Displayed with an icon and label. |
| **Transition** | A directed edge from one or more *source* activities to a *target* activity. May carry executable code (Page Template or Script Python) and a list of permitted **performers** (roles). |
| **Autocommit** | When the workflow is **inactive** (autocommit = on), changes are committed immediately without workflow steps. When **active** (autocommit = off), changes go through the defined state machine. |
| **Node Assignment** | A list of ZMS node references (`{$}` = root) defines where in the content tree the workflow applies. |
| **Version Control** | An independent versioning mechanism that can be activated alongside or instead of the workflow. It keeps history snapshots of content nodes. |
| **Performer** | A Zope role (e.g. *ZMSEditor*, *ZMSAdministrator*) that is allowed to execute a given transition. Missing roles are created automatically on workflow import. |

## Data Model

### Activities

Stored in `self.activities` as a flat alternating-pair list:

```
[id_0, {name, icon_clazz, icon}, id_1, {...}, ...]
```

Each activity dict contains:

| Key | Type | Description |
|---|---|---|
| `name` | str | Display name |
| `icon_clazz` | str | FontAwesome CSS class |
| `icon` | Image/None | Optional uploaded icon blob |

Activity IDs are conventionally prefixed `AC_` (e.g. `AC_DRAFT`).

### Transitions

Stored in `self.transitions` as the same flat-pair pattern:

```
[id_0, {name, icon_clazz, from, to, performer}, id_1, {...}, ...]
```

| Key | Type | Description |
|---|---|---|
| `name` | str | Display name |
| `icon_clazz` | str | FontAwesome CSS class |
| `from` | list | Source activity IDs |
| `to` | list | Target activity IDs (usually one) |
| `performer` | list | Roles allowed to execute this transition |

Each transition may have an associated **Zope object** (Page Template or
Script Python) stored as a child of `workflow_manager`. This code executes
when the transition fires. Transition IDs are conventionally prefixed `TR_`.

## GUI Layout

The admin interface (`manage_main`) is organised into **three tabs**:

### Tab 1 — Workflow Model

Controls and displays the state-machine definition:

- **Active checkbox** — enables/disables the workflow (toggle autocommit).
- **Revision** — semantic version string (`MAJOR.MINOR.PATCH`) for the
  workflow configuration.
- **Import / Export** — upload or download the workflow as `workflow.xml`.
- **Clear** — auto-commits all pending changes and removes all activities
  and transitions.

Below the controls, two sections list the current configuration:

| Section | Description |
|---|---|
| **Activities** | Sortable table of workflow states. Each row shows the activity icon and name. A visual connection matrix illustrates how activities link to one another through transitions. Click an activity to edit its properties (ID, name, icon). |
| **Transitions** | Sortable table of edges. Each row shows *From* activities → Transition box → *To* activities, plus the list of permitted performers. Click a transition to edit its properties and code. |

Insert buttons (`+`) open modal dialogs for creating new activities or
transitions. Transitions can be typed as *Page Template*, *Script (Python)*,
or *None* (no executable code).

### Tab 2 — Content Assignment

A textarea accepting ZMS node references (one per line). The workflow
applies to these content branches. The default `{$}` targets the entire
site.

### Tab 3 — Version Control

Independent versioning configuration:

- **Active checkbox** — enable/disable version history.
- **Nodes** — textarea of node references where versioning applies.

Deactivating versioning packs history for the affected nodes.

### Acquired Workflow

Multi-site (portal client) setups show a separate
`manage_main_acquired.zpt` template where a child site can activate
a workflow inherited from the master and define its own node assignments.

## Import / Export

Workflow configurations are serialisable as XML:

```
manage_changeWorkflow?lang=ger&btn=BTN_EXPORT   → download workflow.xml
manage_changeWorkflow?lang=ger&btn=BTN_IMPORT    → upload file or select init-conf
```

The XML contains all activities and transitions. On import, missing Zope
roles referenced as performers are created automatically.

## Repository Integration

`ZMSWorkflowProvider` implements `IZMSRepositoryProvider`:

| Method | Description |
|---|---|
| `provideRepository(r, ids)` | Serialise activities + transitions for filesystem export. |
| `updateRepository(r)` | Restore activities + transitions from filesystem import. |
| `translateRepositoryModel(r)` | Convert repository dict format to the internal flat-pair list format. |

Repository files are stored under `workflow/` with `__init__.py`, plus
separate sub-entries for each activity and transition.

## API Reference

### ZMSWorkflowProvider

| Method | Description |
|---|---|
| `getAutocommit()` | `1` if autocommit (no workflow), `0` if workflow active. |
| `getNodes()` | List of node references the workflow applies to. |
| `getRevision()` / `setRevision(r)` | Workflow configuration version string. |
| `doAutocommit(lang, REQUEST)` | Commit all pending changes in the content tree. |
| `importXml(xml)` | Replace workflow definition from XML string. |
| `manage_changeWorkflow(lang, btn, key, REQUEST, RESPONSE)` | Main form handler for all three tabs. |

### Activities (via ZMSWorkflowActivitiesManager)

| Method | Description |
|---|---|
| `getActivities()` | List of activity dicts. |
| `getActivityIds()` | List of activity ID strings. |
| `getActivity(id, for_export=False)` | Single activity dict. With `for_export=True`, icon is URL path. |
| `getActivityDetails(id)` | Dict with `froms` and `tos` index lists showing connected transitions. |
| `setActivity(id, newId, newName, ...)` | Create or update an activity. |
| `manage_changeActivities(lang, btn, ...)` | ZMI form handler for activity CRUD. |

### Transitions (via ZMSWorkflowTransitionsManager)

| Method | Description |
|---|---|
| `getTransitions()` | List of transition dicts. |
| `getTransitionIds()` | List of transition ID strings. |
| `getTransition(id, for_export=False)` | Single transition dict including `ob` (Zope object) and `type`. |
| `setTransition(id, newId, newName, newType, newIconClass, newFrom, newTo, newPerformer, newData)` | Create or update a transition and its associated Zope object. |
| `manage_changeTransitions(lang, btn, ...)` | ZMI form handler for transition CRUD. |

### Utility

| Method | Description |
|---|---|
| `delItem(id, key)` | Remove an item from the `activities` or `transitions` list by ID. |
| `moveItem(id, pos, key)` | Reorder an item within its list. |
