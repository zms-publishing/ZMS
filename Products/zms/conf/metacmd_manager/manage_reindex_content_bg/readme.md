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

`GET {connector_url}/reindex_page`

Query parameters:

- `preview=<uid>`
- `page_size=<page-size>`

Example:

`GET http://127.0.0.1:8080/myzmsx/content/zcatalog_adapter/zcatalog_connector/reindex_page?uid={$uid:2d5dd14c-4fb0-4e79-8d9b-dd795a65cc0b}&page_size=10`

Expected response:

```json
{
	"success": 3,
	"failed": 1,
	"log": [
        {
			"index": 0,
          	"path": "/myzmsx/content/e1/e2",
          	"meta_id": "ZMSDocument",
          	"objects": {
				"lang": 4
			}
		}
	],
	"next_node": "{$uid:68eeb9a5-c69e-4d0f-8869-b07f07e18d1a}"
}
```

Error handling:
`TODO`

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
- `TODO`

## Return Behavior of `manage_reindex_content_bg`

- Starts worker thread asynchronously.
- Immediately redirects to `manage_main` with message: `Background Job has Started`.
- If a run is already active (or lock is held), redirects with message: `Background Job is already running`.

## Troubleshooting Checklist

1. Check lock contention messages if the job does not start.
2. Verify `scope_mode`, `scope_url`, `scope_path` in logs.
3. If all items are skipped as not found, test REST URL manually.
4. If indexing fails, inspect connector logs for bulk/mapping errors.
