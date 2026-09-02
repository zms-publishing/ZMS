# Content Reindexing (REST‑based) — Background Job & CLI

## Purpose

This module implements **asynchronous, paged content reindexing** for ZMS.  
It uses a **pure REST traversal** to discover ZMS nodes and calls the configured search connector (e.g., OpenSearch) to reindex content in pages.

The implementation consists of:

- `ZMSIndexSchematizedReindexer` — standalone REST reindexer (no Zope required)
- `manage_reindex_content_bg` — Zope external method running the reindexer in a background thread
- CLI runner for local/manual reindexing

---

## Architecture Overview

### Components

- **REST tree traversal** (`++rest_api/.../list_child_nodes`)
- **Paged reindexing** via `reindex_page`
- **Threaded background worker** inside Zope
- **Cross‑process locking** to prevent concurrent runs
- **CLI tool** for standalone operation

---

## High‑Level Flow

### Zope Background Job (`manage_reindex_content_bg`)

1. User triggers reindexing from Zope UI (`manage_main`) or via code.
2. A **single‑flight lock** ensures only one job per base URL runs at a time:
   - in‑process lock (`RUN_LOCK`)
   - cross‑process lock (`fcntl` lockfile)
3. A **daemon worker thread** is started.
4. The worker opens a fresh Zope context:
   - `Zope2.app()`
   - `makerequest(app)`
   - `newSecurityManager(..., system_user)`
5. The worker instantiates `ZMSIndexSchematizedReindexer`.
6. `reindexer.run()`:
   - traverses REST tree
   - yields only nodes with `meta_id == "ZMS"`
   - calls `reindex_page` for each UID
   - aggregates statistics (`success`, `failed`, `objects`, etc.)
7. Final statistics are logged via Zope’s logger.
8. Locks are released and the job ends.

The UI immediately redirects with:

- **“Background Job has Started”**  
- or **“Background Job is already running”** if a lock is held

---

## REST Tree Traversal

Traversal starts at the base URL and uses:

```
GET {base_url}/++rest_api/{path}/list_child_nodes
```

Each node returns:

```json
{
  "uid": "...",
  "meta_id": "ZMSDocument",
  "getPath": "/myzms/content/e1/e2"
}
```

Traversal rules:

- Only nodes with `meta_id == "ZMS"` are **reindexed**
- Only ZMS nodes are **descended into**
- Duplicate UIDs are skipped
- Errors during traversal are logged but do not stop the job

---

## Reindexing API

For each UID, the worker calls:

```
GET {connector}/reindex_page
```

Query parameters:

| Parameter        | Meaning |
|------------------|---------|
| `uid`            | Node UID (connector-specific formatting) |
| `page_size:int`  | Page size for paged reindexing |
| `clients:int`    | Always `0` in this implementation |
| `fileparsing:int`| `0` or `1` depending on CLI/UI flag |

Example:

```
GET http://127.0.0.1:8080/myzmsx/content/zcatalog_adapter/zcatalog_connector/reindex_page
    ?uid={$uid:2d5dd14c-4fb0-4e79-8d9b-dd795a65cc0b}
    &page_size=10
```

Expected response:

```json
{
  "success": 3,
  "failed": 1,
  "log": [
    {
      "index": 0,
      "path": "/myzms/content/e1/e2",
      "meta_id": "ZMSDocument",
      "objects": { "lang": 4 }
    }
  ],
  "next_node": "{$uid:68eeb9a5-c69e-4d0f-8869-b07f07e18d1a}"
}
```

The reindexer aggregates:

- number of candidates
- number of REST requests
- number of objects processed
- success/failed counts

---

## Concurrency & Safety

### In‑Process Lock

A global Python lock prevents multiple threads inside the same Zope instance:

```python
RUN_LOCK = threading.Lock()
RUN_IN_PROGRESS = False
```

### Cross‑Process Lock

A lockfile prevents multiple Zope processes from running the job simultaneously:

```
/tmp/zms_reindex_<sanitized-base-url>.lock
```

Acquired via:

```python
fcntl.flock(fd, LOCK_EX | LOCK_NB)
```

### Thread‑Safe Zope Context

The worker:

- opens a fresh Zope app
- creates a new request
- installs a system user security manager
- aborts transactions after each run
- closes DB connections cleanly

This ensures the background job does not interfere with the request thread.

---

## CLI Runner

The script can run standalone without Zope:

```
src/zms/Products/zms/conf/metacmd_manager/manage_reindex_content_bg$ python3 manage_reindex_content_bg.py http://127.0.0.1:8080/myzmsx/content \
    --connector /zcatalog_adapter/zcatalog_connector/ \
    --uid {$} \
    --page-size 100 \
    --fileparsing
```

CLI behavior:

- prints progress to stdout
- prints final summary
- uses the same REST traversal and reindexing logic

---

## Logging

Both Zope and CLI modes log:

- start/end markers
- each UID being processed
- REST logs returned by the connector
- aggregated statistics

Zope logs use `logging.getLogger("Zope")`.  
CLI logs use `logging.getLogger("ZMSReindex")`.

---

## Return Behavior of `manage_reindex_content_bg`

The external method **never waits** for the job to finish.

It immediately redirects to `manage_main` with one of:

- `Background Job has Started`
- `Background Job is already running`

The actual work happens in the background thread.

---

## Troubleshooting Checklist

1. **Job does not start**  
   Check lockfile in `/tmp` and Zope logs for lock contention.

2. **No nodes found**  
   Test REST traversal manually:  
   `GET base_url/++rest_api//list_child_nodes`

3. **Connector errors**  
   Inspect connector logs for mapping/bulk/indexing failures.

4. **REST payload errors**  
   The reindexer attempts JSON → `json.loads` → `ast.literal_eval`.  
   If all fail, the raw payload is logged.

5. **Performance issues**  
   Increase `page_size` or disable `fileparsing`.
