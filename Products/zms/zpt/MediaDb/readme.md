# ZMS Media Data Manager

The **Media Data Manager** (`acl_mediadb`) offloads BLOB storage — images,
documents, and other binary files — from the ZODB to the server filesystem.
This drastically reduces ZODB growth and speeds up packing, while media files
remain transparently accessible through the standard ZMS URL scheme.

## Core Concepts

| Concept | Description |
|---|---|
| **Location** | Absolute filesystem path where media files are stored. Supports the `$INSTANCE_HOME` variable for portability. |
| **Structure Depth** | Controls directory nesting: `0` = flat (all files in one folder), `N` = N-level subdirectory tree derived from the filename hash. Higher depth improves performance on filesystems with many files. |
| **Migration** | Adding or removing the MediaDb automatically migrates all existing BLOBs between ZODB and filesystem (`recurse_downloadRessources` / `recurse_uploadRessources`). |
| **Garbage Collection** | The `manage_gc` function detects orphaned files (present on disk but unreferenced by any ZMS object) and moves them to a temporary folder. |

## GUI Layout

The management interface has two tabs:

### Browse Tab
A sortable table listing every file in the media folder:

| Column | Content |
|---|---|
| **Filename** | The on-disk filename (timestamp-based unique name) |
| **Size** | File size in bytes / KB |
| **Last Modified** | Filesystem modification timestamp |

### Properties Tab
A form to view and change the storage configuration:

- **Location** — the filesystem path (editable, supports `$INSTANCE_HOME`)
- **Structure Depth** — nesting level for subdirectories

Changing the location triggers a full re-migration of all BLOBs.

## API Reference

### Properties

| Method | Returns | Description |
|---|---|---|
| `getLocation()` | `str` | Resolved filesystem path (variables expanded) |
| `setLocation(location)` | — | Set the storage path |
| `getStructure()` | `int` | Current directory nesting depth |
| `getFilenameFromName(name)` | `str` | Full filesystem path for a given media filename |

### File Operations

| Method | Returns | Description |
|---|---|---|
| `storeFile(file)` | `str` | Write a blob to disk; returns the generated filename |
| `retrieveFileStreamIterator(filename, mode='b')` | `bytes` | Read a file's content from disk |
| `retrieveFile(filename, REQUEST, RESPONSE)` | stream | Serve a file with proper HTTP headers (streams files > 128 KB) |
| `getPath(REQUEST)` | — | Public file-serving endpoint |

### Maintenance

| Method | Returns | Description |
|---|---|---|
| `targetFile(filename)` | `str` | Full path for a media filename |
| `valid_filenames()` | `set` | All media filenames referenced by ZMS objects (full tree traversal) |
| `manage_report(REQUEST)` | JSON | Compare filesystem files vs. referenced files (status: OK / MISSING) |
| `manage_gc()` | — | Move orphaned files to a temp folder |
| `manage_relocate()` | — | Restructure on-disk layout after changing structure depth |

## Tips

- Use **Structure Depth ≥ 2** for sites with thousands of media files to
  avoid filesystem performance issues.
- The `$INSTANCE_HOME` variable makes the configuration portable across
  environments (development, staging, production).
- Run the **Report** function periodically to detect MISSING files early.
- After removing the MediaDb, all BLOBs are automatically restored into the
  ZODB — no data is lost.
