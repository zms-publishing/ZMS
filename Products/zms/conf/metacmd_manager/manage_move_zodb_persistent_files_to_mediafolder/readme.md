# Move ZODB Persistent Files to Media Folder

## Purpose

This ZMS-Action migrates binary large objects (BLOBs) that are stored persistently inside the ZODB to the ZMS *media folder* on the file system. Moving files out of the ZODB reduces database size, improves packing performance, and allows the web server to deliver static assets directly.

## How It Works

The action iterates over every ZMS content node starting from a configurable root node. For each node it inspects all object attributes whose datatype is a BLOB type (`DT_BLOBS`). If a blob contains data it is re-written via `_objattrs.setobjattr`, which persists the file to the media folder instead of the ZODB.

Processing is **paginated** — nodes are fetched in configurable increments (default 200) so that large sites can be migrated without timeouts or excessive memory usage.

### Mediafolder Auto-Creation

If a ZMS client does not yet have a mediafolder configured and the option **"Add ZMS-Client's mediafolder if not available"** is checked, the action automatically creates a new `MediaDb` object on the client's document element using the path convention:

```
$INSTANCE_HOME/var/mediafolder/<client_id>
```

The directory is created on disk automatically.

### Mediafolder Path Fixing

If a ZMS client already has a mediafolder configured but the stored path does not exist on the current system (e.g. after migrating the instance to a different server), the option **"Fix ZMS-Client's given mediafolder path if not available"** will update the path to the convention above and create the new directory. The original path is only changed when `os.path.isdir()` confirms that it is missing.

## User Interface

| Control | Description |
|---|---|
| **Increment Size** | Number of nodes processed per AJAX request (default: 200). |
| **Add ZMS-Client's mediafolder if not available** | Checkbox (default: on). Creates a mediafolder for any ZMS client that does not have one yet. |
| **Fix ZMS-Client's given mediafolder path if not available** | Checkbox (default: on). Corrects the mediafolder path if the configured directory does not exist on disk. |
| **Start / Pause** | Starts the migration; click again to pause. |
| **Stop** | Aborts the migration after the current page finishes. |
| **Progress Bar** | Shows the percentage of nodes processed. |
| **Statistics Table** | Lists object counts per `meta_id`, the number of moved files, total nodes processed, and throughput (nodes/sec). |

## Log Output

Only nodes where files were actually exported are logged. Each log entry contains:
- node id and `meta_id`
- the full OS file path of each exported blob (e.g. `/home/zope/instance/var/mediafolder/mysite/report_17127543210000.pdf`)
- a `@moved` marker

Nodes without blob data are processed silently (they still count towards progress).

## REST / JSON Endpoints

The action exposes two JSON endpoints (triggered by `?json=true`):

| Parameter | Description |
|---|---|
| `count=true&root_node={$}` | Returns the total number of catalogued objects below the root node grouped by `meta_id`. |
| `traverse=true&uid=...&page_size=N&add_mediafolder=true&fix_mediafolder_path=true` | Processes the next *N* nodes starting at `uid`. Optionally creates missing mediafolders and/or fixes broken paths. Returns a log of exported files, a `processed` count, and the `next_node` uid (`null` when finished). |

## Usage

1. Navigate to *ZMS > Configuration > ZMSIndex > Actions* and open **Media Folder: Move ZODB Persistent Files**.
2. Adjust the **Increment Size** if needed.
3. Check or uncheck the mediafolder options as appropriate.
4. Click the **Start** button.
5. Monitor the progress bar and statistics table until the migration completes (progress bar turns green).
6. After completion, pack the ZODB to reclaim the freed space.



