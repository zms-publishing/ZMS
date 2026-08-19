# Content Reindexing as a Background Job

## Purpose

This module implements asynchronous paged content reindexing for ZMS by traversing ZMSIndex candidates, retrieving reindexing documents to the configured search connector (for example OpenSearch).

The implementation is located in:

- `manage_reindex_content_bg.py`

## High-Level Flow

1. `manage_reindex_content_bg(self)` is triggered from Zope UI or code.
2. A single-flight lock prevents concurrent runs for the same base URL.
3. A daemon worker thread starts.
4. The worker opens a fresh Zope app/request/security context.
5. `ZMSIndexSchematizedReindexer.run()`:
	 - reads index candidates from `zcatalog_index`
	 - calls REST endpoint `reindex_node` per UID for paged-processing
6. Final statistics are written to the Zope log.

## Scope Selection Logic

The reindex scope depends on the invocation context:

- **Portal master root call** (`self == self.getDocumentElement()` and no `Portal.Master`):
	- mode: `portal-master`
	- scope root: `self.getHome()`
	- effect: reindex full multisite under home folder
- **Any deeper call** (client/document/folder):
	- mode: `recursive`
	- scope root: `self`
	- effect: recursive reindex below the current node only

This is computed in `_get_reindex_scope(context)`.

## API Calls Used

### 1) Internal ZMS Catalog APIs

The reindexer uses internal APIs to discover candidates and write to search backends.

- `self.context.zcatalog_index({"path": self.scope_path})`
	- returns catalog brains inside scope path
- `self.context.getCatalogAdapter()`
	- obtains adapter to identify relevant indexed meta types
- `adapter.get_connectors()`
	- obtains configured connector(s)
- `connector.reindex_page(uid, page_size)`
	- reindex page

### 2) REST API for Schematized Content

For each candidate UID and each language, the worker calls:

`GET {base_url}/++rest_api/{uid-token}/get_indexschematized_content`

Query parameters:

- `preview=preview`
- `lang=<language-id>`

Example:

`GET http://127.0.0.1:8086/dev/myzmsx/content/++rest_api/uid:abc123/get_indexschematized_content?preview=preview&lang=de`

Expected payload:

```json
{
	"total": 1,
	"docs": [
		{
			"uid": "uid:abc123",
			"id": "node-id",
			"lang": "de",
			"meta_id": "ZMSDocument",
			"path": "/..."
		}
	]
}
```

Error handling:

- HTTP errors are raised by `response.raise_for_status()`
- parser fallback order:
	- `response.json()`
	- `json.loads(response.text)`
	- `ast.literal_eval(response.text)`
- payloads containing `{"ERROR": ...}` are converted to `LookupError`

### 3) OpenSearch Connector Behavior

When the configured connector is OpenSearch, `manage_opensearch_objects_add` transforms each source into a bulk action.

Important detail for multilingual indexing:

- default OpenSearch `_id` is generated as: `"{uid}:{lang}"`

Therefore, the background reindexer ensures language information is present per document.

## Multilingual Indexing

The worker iterates all available language IDs:

- source: `self.context.getLangIds()`
- fallback: `self.context.getPrimaryLanguage()`

For each `uid` and `lang`:

1. REST is called with the language parameter.
2. Returned docs are normalized.
3. Missing `lang` values are filled from current loop language.
4. Duplicate docs are filtered by `(uid, lang, id)`.

This guarantees separate language variants can be indexed and matched by connector-level `_id` suffixing.

## Document Normalization Before Indexing

`_normalize_doc_for_indexing` currently ensures:

- `lang` is present (if missing)
- datetime fields are converted to ISO-like format by replacing first space with `T`:
	- `created_dt`
	- `change_dt`
	- `start_dt`
	- `end_dt`
	- `indexing_dt`

Reason: avoid date parse failures in strict search-index mappings.

## Node Resolution Strategy

Returned docs are mapped back to runtime objects in this order:

1. `context.getLinkObj("{$uid:...}")`
2. `context.findObject("{$uid:...}")`
3. physical path fallback via:
	 - `doc["path"]`
	 - `doc["loc"]`
	 - catalog brain path fallback

If no object can be resolved, the doc is skipped and logged.

## Concurrency and Safety

### In-Process lock

- global lock + flag (`RUN_LOCK`, `RUN_IN_PROGRESS`) prevent duplicate starts in same process.

### Cross-process lock

- lock file in temp directory:
	- `zms_manage_reindex_content_bg_<sanitized-base-url>.lock`
- uses non-blocking `fcntl.flock(... LOCK_EX | LOCK_NB)`.

### Thread-safe Zope context

The worker does not use the request thread context directly. It opens its own app/request/security context:

- `Zope2.app()`
- `makerequest(app)`
- `newSecurityManager(..., system_user)`
- `app.unrestrictedTraverse(...)`

Cleanup:

- `transaction.abort()`
- `noSecurityManager()`
- close app jar connection

## Logging

Each run logs:

- start and finish markers
- selected scope mode, scope URL, scope path
- per-UID statuses: `indexed`, `skipped`, `failed`
- summary counters:
	- `candidates`
	- `requests`
	- `objects`
	- `success`
	- `failed`
	- `skipped`

## Return Behavior of `manage_reindex_content_bg`

- Starts worker thread asynchronously.
- Immediately redirects to `manage_main` with message: `Background Job has Started`.
- If a run is already active (or lock is held), redirects with message: `Background Job is already running`.

## Troubleshooting Checklist

1. Check lock contention messages if the job does not start.
2. Verify `scope_mode`, `scope_url`, `scope_path` in logs.
3. If all items are skipped as not found, test REST URL manually.
4. If indexing fails, inspect connector logs for bulk/mapping errors.
5. Confirm `lang` values are present in outgoing docs for multilingual content.
