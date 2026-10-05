# Content Reindexing (REST‑based) — Background Job & CLI

## Purpose

`manage_reindex_content_bg.py` reindexes ZMS content for the configured search
connector (e.g. ZCatalog or OpenSearch) as an **asynchronous background job**.
It discovers nodes through the ZMS **REST API** and asks the connector to
reindex each node through its `reindex_page` endpoint.

The file contains three parts:

- `ZMSIndexSchematizedReindexer` — REST reindexer; it needs only `requests`, not Zope
- `start`, `stop` and `manage_reindex_content_bg` — Zope external-method code that runs the
  reindexer in a background thread, controls it and renders the ZMI page
- `main()` — command-line runner for standalone use

The meta-command is declared in `__init__.yaml` for the meta types `ZMS` and
`ZMSFolder` and for the role `ZMSAdministrator`.

---

## High‑Level Flow (ZMI)

1. The user opens **Reindex Content (Background)** on a ZMS node and sets the
   *Page Size* (default `1`: one node per connector call).
2. **Start** (`btn=BTN_START`) calls `start(self)`, which:
   - takes the **current context** as the starting node (physical path, UID, `meta_id`),
   - resolves the connector from the root's catalog adapter (first connector),
   - acquires the single‑flight lock (see below); if it is held, the page shows
     “Background Job is already running”,
   - creates a fresh status record and starts a **daemon thread**.
3. The worker thread creates a `ZMSIndexSchematizedReindexer` and runs it. It
   logs through the `Zope` logger and writes progress to the status record.
4. When the run ends (completed, stopped or failed) the worker writes the final
   state, removes the stop marker and releases the lock.
5. `start` returns only a message; the page is re-rendered directly (no redirect),
   so the request never waits for the job.

The worker does **not** open its own Zope application, request or security
context, and it does not touch the ZODB. All work happens through HTTP calls
(`requests.get`) to the site's own `base_url` (`root.absolute_url()`), so the
REST API and the connector endpoints must be reachable from the Zope server
itself. These calls carry no credentials.

---

## REST Tree Traversal

Traversal is a depth‑first walk using a stack of node paths:

```
GET {base_url}/++rest_api/{path}/list_child_nodes
```

Each child entry provides the fields used:

```json
{ "uid": "...", "meta_id": "ZMSDocument", "getPath": "/myzms/content/e1/e2" }
```

Rules:

- **ZMI:** the invocation context is reindexed first (it is not returned by
  `list_child_nodes`), then its descendants. Its UID is registered as seen.
- **CLI:** no start node is passed, so traversal starts at the root of `base_url`.
  Programmatic callers may pass `start_path` and `start_node` to the class.
- Every returned child is reindexed (there is no `meta_id` filter) and its
  `getPath` is pushed on the stack.
- Entries without `uid` or `getPath`, and duplicate UIDs, are skipped.
- A failed `list_child_nodes` request is logged and that branch is skipped; the
  job continues.
- The constructor argument `uid` (CLI `--uid`, request field `uid`) is accepted
  but **does not scope** the run; scope comes only from the start node/path.

---

## Reindexing API

For every discovered node the worker calls:

```
GET {base_url}/{connector}/reindex_page
```

with the query parameters

| Parameter         | Meaning |
|-------------------|---------|
| `uid`             | Client path of the node as `{$@<path>}` (see below) |
| `page_size:int`   | Page size passed to the connector |
| `clients:int`     | Always `0` |
| `fileparsing:int` | `1` if file parsing is enabled, else `0` (the ZMI page has no field for it; it can be set with a `fileparsing` request value; CLI: `--fileparsing`) |

The `uid` value is built from the node's physical path: the first segment (the
ZMS root object) and a leading or trailing `content` segment are removed, and
`/content/` inside the path becomes `@`. For example `/myzms/content/e1/content/e2`
yields `{$@e1@e2}`.

The connector is expected to answer with JSON like:

```json
{
  "success": 3,
  "failed": 1,
  "log": [ { "index": 0, "path": "...", "meta_id": "ZMSDocument",
             "objects": { "lang": 4 }, "success": 3, "failed": 1 } ],
  "next_node": "{$uid:68eeb9a5-c69e-4d0f-8869-b07f07e18d1a}"
}
```

The payload is parsed as JSON, then via `json.loads`, then `ast.literal_eval`.
`next_node` is only logged; the worker does not follow it, because the node
traversal supplies the next node itself.

Counters kept per run:

| Counter           | Meaning |
|-------------------|---------|
| `candidates`      | Nodes discovered and handed to reindexing so far (not a total) |
| `requests`        | `reindex_page` calls started |
| `nodes_completed` | Nodes whose call has finished (successfully or with error) |
| `objects`         | Sum of the largest per-language object count of each log entry |
| `success`/`failed`| Connector's top‑level `success`/`failed`, or the sum of the log entries if absent; an exception counts as one failure |
| `skipped`         | Reserved; currently always `0` |

---

## Status Record & Polling

The worker publishes progress in a JSON file shared by all Zope processes:

```
{tempdir}/zms_reindex_<sanitized-base-url>.lock.status.json
```

It holds `job_id`, `state`, `started_at`, `updated_at`, `finished_at`,
`current_uid`, `current_path`, the counters above and `error`. Reads take a
shared `flock`, writes an exclusive one; a stale worker (different `job_id`)
cannot overwrite a newer run's record. The file is kept after the run so the
final result stays visible.

States: `idle` (no record), `running`, `stopping`, `stopped`, `completed`, `failed`.

The command also answers `manage_reindex_content_bg?status=1` with this record as
JSON (`Cache-Control: no-store`). The ZMI page shows a status panel and polls that
URL every two seconds, stopping once the state is no longer `running` or
`stopping`. Because the node total is unknown during traversal, only counts are
shown, not a percentage.

---

## Stop

**Stop** (`btn=BTN_STOP`) calls `stop(self)`:

- If the job runs in **this Zope process**: its cancel event is set, the status
  becomes `stopping`, and the run lock is released **immediately**, which removes
  the lock file. A connector request already in flight may still finish; the
  worker stops before the next traversal or `reindex_page` request and records
  `stopped`. A new run can start straight away; its status record is protected
  from the old worker by the `job_id` check, but one outstanding request of the
  old run may overlap with it.
- If the lock is held by **another process**: a `.stop` marker file is created and
  the status becomes `stopping`. That worker sees the marker at its next
  checkpoint, ends, and releases its own lock.
- Otherwise the page reports “No background job is running”.

---

## Concurrency & Files

Only one job per `base_url` may run at a time:

- **In‑process:** `RUN_LOCK` (a `threading.Lock`) serializes start/stop/cleanup;
  `RUN_JOB`, `RUN_LOCK_FD` and `RUN_IN_PROGRESS` track the job of this process.
- **Cross‑process:** an exclusive `flock` on a run lock file. The kernel releases
  it if the process dies, so a crash leaves no permanently stuck lock.

Files in the system temporary directory (all processes serving the site must see
the same directory):

| File | Purpose |
|------|---------|
| `zms_reindex_<url>.lock` | Run lock; exists only while a job holds the lock |
| `zms_reindex_<url>.lock.guard` | Permanent helper lock serializing creation, check and removal of the run lock file, so removal cannot race with a new start |
| `zms_reindex_<url>.lock.stop` | Cancellation marker for stops from another process |
| `zms_reindex_<url>.lock.status.json` | Status record |

`<url>` is `root.absolute_url()` with every non‑alphanumeric character replaced
by `_`. The ZMI page treats a held lock file as “Background Job is running”.

---

## CLI Runner

The script can run without Zope:

```
python3 manage_reindex_content_bg.py http://127.0.0.1:8080/myzmsx/content \
    --connector /zcatalog_adapter/zcatalog_connector/ \
    --page-size 100 \
    --fileparsing
```

- Options: `--connector`, `--uid` (accepted, not scoping), `--page-size` (default `100`),
  `--fileparsing`.
- Traversal starts at the root of the given base URL.
- Progress lines and the final `Summary:` are printed to stdout.
- The CLI has no lock, stop marker or status record; stop it with Ctrl‑C.

---

## Logging

- Zope: every progress line goes to the `Zope` logger, including start, the
  per‑node lines (`Reindexing UID=...`), connector `LOG` entries, `Success=...`,
  stop notices and the final statistics (or the traceback on failure).
- CLI: the same lines are printed to stdout.
- Traversal errors are logged by the `ZMSReindex` logger in both modes.

---

## Troubleshooting

1. **“Already running” but nothing runs**
   Check the lock/status files in the temp directory; a held lock means a live
   process owns it. Use **Stop**, which also works from another process.
2. **Job ends immediately / no nodes**
   Test `GET {base_url}/++rest_api//list_child_nodes`; check for HTTP errors in
   the `ZMSReindex` log (the calls are unauthenticated).
3. **Connector errors**
   Look at the `ERROR calling REST API` lines and the connector logs.
4. **Invalid REST payload**
   The first 240 characters of the payload are included in the error.
5. **Status not updating in the UI**
   Confirm that all Zope processes use the same temporary directory.
6. **Performance**
   Increase *Page Size* or disable file parsing.
