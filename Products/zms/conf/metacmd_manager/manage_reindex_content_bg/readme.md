# Content Reindexing (REST‑based) — Background Job & CLI

> **Since 0.2.0** the job (worker thread, lock, status, pause/stop) is implemented
> in ZMS core (`ZMSZCatalogAdapterQueue`, endpoints `manage_reindex_start|status|pause|proceed|stop`
> on the catalog adapter). The worker runs in-process with its own ZODB connection and no longer calls
> the REST API over HTTP. This command is only the UI and delegates to
> `getCatalogAdapter().start_reindex_job()` etc.; the sections below on HTTP/REST
> traversal describe the legacy design and the CLI client. Lock and status file names are unchanged.


## Purpose

`manage_reindex_content_bg.py` reindexes ZMS content for the configured search
connector (e.g. ZCatalog or OpenSearch) as an **asynchronous background job**.
The ZMI bulk job runs in-process through the core catalog adapter. The page
also exposes the on-change indexing mode (`sync` or `async`), pending queue
count, and failed queue entries. The REST-based CLI remains available as a
standalone client.

The file contains three parts:

- `ZMSIndexSchematizedReindexer` — REST reindexer; it needs only `requests`, not Zope
- `start`, `stop` and `manage_reindex_content_bg` — Zope external-method code that delegates
  bulk job control to the core adapter and renders the ZMI page
- `main()` — command-line runner for standalone use

The meta-command is declared in `__init__.yaml` for the meta types `ZMS` and
`ZMSFolder` and for the role `ZMSAdministrator`.

---

## High‑Level Flow (ZMI)

1. The user opens **Reindex Content (Background)**, selects the ZMS clients to
   reindex in the sitemap tree (checkboxes `home_ids:list`, all checked by
   default) and sets the *Page Size* (default `1`: one node per connector call).
2. **Start** (`btn=BTN_START`) calls `start(self)`, which:
   - resolves each selected `home_ids` value (e.g. `{$portal/clientA@}`) with
     `getLinkObj` to a ZMS client node (physical path, UID, `meta_id`); values that
     cannot be resolved are skipped; if nothing is left, “No ZMS-node selected”
     is shown and no job starts,
   - resolves the connector from the root's catalog adapter (first connector),
   - acquires the single‑flight lock (see below); if it is held, the page shows
     “Background Job is already running”,
   - creates a fresh status record and starts a **daemon thread**.
3. The worker thread creates a `ZMSIndexSchematizedReindexer` and runs it. It
   logs through the `Zope` logger and writes progress to the status record.
4. When the run ends (completed, stopped or failed) the worker writes the final
   state, removes the stop marker and releases the lock.
5. The Start/Pause/Proceed and Stop buttons are submitted by JavaScript (`fetch`, POST with all
   form data plus `control=1`), so the page is **not reloaded** and the sitemap keeps
   its expansion and selection. The command answers with JSON `{"message": ...}`;
   the message (e.g. “Background Job is already running”, “No ZMS-node selected”)
   is shown as the first line of the status panel, and polling (re)starts. The
   request never waits for the job. (POST is used because Zope does not parse form
   data from PUT bodies.) Without `control=1` the page is rendered as before, but
   without an alert box.

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

- **ZMI:** the selected ZMS clients are processed one after another. For each
  client the client node itself is reindexed first (it is not returned by
  `list_child_nodes`), then its content tree. **Sub-clients (`meta_id` ZMS) are
  not entered**; they are reindexed only if they are selected themselves.
- **CLI:** no start nodes are passed, so traversal starts at the root of
  `base_url` and also enters sub-clients. Programmatic callers may pass a list
  `start_nodes` of `{home_id, uid, meta_id, getPath}` to the class.
- Every returned child's `getPath` is pushed on the stack, so the whole tree is
  walked, but only nodes whose `meta_id` is allowed are sent to `reindex_page`:
  - **ZMI:** the meta ids configured in the catalog adapter
    (`getTypedMetaIds(catalog_adapter.getIds())`, e.g. pages and `ZMSFile`);
    blocks such as `ZMSTextarea` are not reindexed. The adapter's custom filter
    function (e.g. visibility) is still applied by the connector itself.
  - **CLI:** all nodes, unless `--meta-ids` is given.
  - Nodes that are walked but not reindexed do not count as `candidates`.
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
| `objects`         | Catalog objects the connector collected: sum of the per-language counts of all log entries |
| `success`/`failed`| Connector's top‑level `success`/`failed`, or the sum of the log entries if absent; an exception counts as one failure |
| `skipped`         | Reserved; currently always `0` |

---

## Status Record & Polling

The worker publishes progress in a JSON file shared by all Zope processes:

```
{tempdir}/zms_reindex_<sanitized-base-url>.lock.status.json
```

It holds `job_id`, `state`, `started_at`, `updated_at`, `finished_at`,
`current_uid`, `current_path`, the counters above, `error` and the client lists
`total_clients`, `total_nodes`, `current_client` (home id of the ZMS client being processed, `null` otherwise), `completed_clients` and `failed_clients` (home ids, growing as
each selected ZMS client finishes; a client is “failed” if a branch could not be
read or a node failed). Reads take a
shared `flock`, writes an exclusive one; a stale worker (different `job_id`)
cannot overwrite a newer run's record. The file is kept after the run so the
final result stays visible.

States: `idle` (no record), `running`, `pausing`, `paused`, `stopping`, `stopped`, `completed`, `failed`.

Before the job starts, `start()` asks the ZMSIndex catalog (path and the adapter's
meta ids, in the request thread) how many nodes each selected client has and
stores the sum as `total_nodes` (`null` if a count fails). The UI progress bar
shows `nodes_completed / total_nodes` as a percentage; the count is an estimate
(it comes from the catalog, not from the traversal), so the bar is capped at 100 %
and set to 100 % on completion. Without a total (e.g. CLI) the bar is striped and
animated while running and only shows the processed count. The bar is blue while
running, orange when stopping/stopped, green when completed and red on failure.

The command also answers `manage_reindex_content_bg?status=1` with this record as
JSON (`Cache-Control: no-store`). The ZMI page shows a status panel and polls that
URL every two seconds, stopping once the state is no longer `running` or
`stopping`. The panel lists the completed ZMS-nodes, and the page
marks the matching sitemap entries with the CSS class `zmi-reindex-running` (the client currently processed, only while the job is running/stopping), `zmi-reindex-done`
(`zmi-reindex-failed` for clients with errors), re-applied on every poll and
whenever sitemap nodes are loaded.

---

## Controller: Start, Pause, Proceed, Stop

A small JavaScript `Controller` on the page maps the job state reported by the
status endpoint to the buttons (as in the ZMS catalog connector page):

| State | Start button | Stop button |
|-------|--------------|-------------|
| idle / completed / stopped / failed | ▶ Start (`BTN_START`) | disabled |
| running | ⏸ Pause (`BTN_PAUSE`) | enabled |
| pausing / paused | ▶ Proceed (`BTN_PROCEED`) | enabled |
| stopping | disabled | disabled |

Because the state comes from the server, the buttons are correct after a page
reload or when another user controls the job.

**Pause** creates the `.pause` marker and sets the state `pausing`. The worker
checks the marker before each node (and before each client), so the REST request
in flight finishes first; then it reports `paused` and sleeps, polling the marker
every 0.5 s. The run lock stays held, so no second job can start. **Proceed**
removes the marker and the worker continues (`running`). Stop while paused ends
the job as usual and clears the marker; a new Start also clears stale markers.

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
| `zms_reindex_<url>.lock.pause` | Pause marker; the worker waits while it exists |
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
  `--fileparsing`, `--meta-ids`.
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
