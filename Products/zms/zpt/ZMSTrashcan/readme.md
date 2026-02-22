# ZMS Trashcan

The ZMS Trashcan (`ZMSTrashcan`) provides a recycle-bin for deleted content
objects. Instead of permanently removing nodes, ZMS moves them into the
trashcan so they can be inspected or recovered before automatic cleanup takes
place.

Every ZMS site contains exactly one trashcan instance (id `trashcan`).
The trashcan inherits from `ZMSContainerObject` so it can hold arbitrary
ZMS child nodes.

## Core Concepts

| Concept | Description |
|---|---|
| **Soft Delete** | Deleting a ZMS node moves it to the trashcan rather than destroying it. The node retains its `del_dt` (deletion timestamp). |
| **Garbage Collection** | A configurable timer automatically purges objects that have been in the trashcan longer than a given number of days. |
| **Catalog Unindexing** | When nodes are moved to the trashcan, `ZMSZCatalogAdapter.unindex_nodes()` is called to remove them from the search index. |
| **CopySupport Override** | `_verifyObjectPaste` is overridden to accept any object—the trashcan does not enforce paste restrictions. |

## Garbage Collection

The automatic purge logic lives in `run_garbage_collection()`:

1. Reads the configured retention period (`garbage_collection` attribute,
   default **2 days**).
2. Iterates over all child objects and compares each node's `del_dt`
   against the current time.
3. Objects older than the configured number of days are permanently deleted
   via `manage_delObjects`.
4. A `last_garbage_collection` timestamp is stored so the routine runs at
   most once per day (unless forced).

Garbage collection runs automatically during normal operation and can also
be triggered manually from the Properties tab.

## GUI — Properties Tab

The trashcan's **Properties** tab (`manage_properties`) exposes:

| Field | Description |
|---|---|
| **Garbage Collection** | Number of days after deletion before objects are permanently removed (integer, default `2`). |
| **Last Executed** | Timestamp of the most recent garbage-collection run. |

Clicking **Save** persists the retention period *and* immediately triggers
a forced garbage-collection run.

## Display Behaviour

- **`isActive(REQUEST)`** — returns `True` only when the trashcan contains
  at least one child node, causing the trashcan icon to appear in the ZMS
  navigation tree.
- **`isPage()`** — always `False` (the trashcan is never a navigable page).
- **`isPageContainer()`** — always `True` (it can hold page-like children).
- **`getTitle(REQUEST)`** — shows the object type and the count of contained
  objects, e.g. *"ZMSTrashcan (3 Objects)"*.

## API Reference

| Method | Description |
|---|---|
| `run_garbage_collection(forced=0)` | Purge expired objects. Pass `forced=1` to ignore the once-per-day throttle. |
| `manage_changeProperties(lang, REQUEST)` | Save the retention period and trigger garbage collection. |
| `isActive(REQUEST)` | `True` if the trashcan contains child nodes. |
| `getDCCoverage(REQUEST)` | Always returns `'global.<primaryLanguage>'`. |