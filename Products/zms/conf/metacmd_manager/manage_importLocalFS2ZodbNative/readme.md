# Import LocalFS to ZODB

## Purpose
This meta-command imports selected files from a local filesystem path into ZODB objects below a selectable target ZODB path.

It is the counterpart of `manage_exportZodbNative2LocalFS`.

## Supported import mapping
File type is inferred from filename extension first, then content-type fallback:

- `.dtml` -> `DTML Method`
- `.zpt` -> `Page Template`
- `.py` -> `Script (Python)`
- `.zsql` -> `Z SQL Method`
- everything else:
  - content type `image/*` -> `Image`
  - otherwise -> `File`

For script/template/sql/dtml files, the extension is removed from object id.
For file/image imports, the full filename is used as object id.

## Path mapping
- Source root: value of **LocalFS Path**
- Target root: value of **Target ZODB Path** (physical path)
- Relative subfolders under source root are created as `Folder` objects under target root.
- Each selected file is imported into its mapped target folder.

## How to use in ZMI
1. Open `Import LocalFS to ZODB`.
2. Set **LocalFS Path** (source directory).
3. Set **Target ZODB Path** (physical object path).
4. Choose safety behavior via **Allow overwrite of existing objects**.
5. Click **Refresh** to scan files recursively.
6. Select files to import.
7. Click **Execute**.

## Safety controls
- Overwrite safety switch:
  - disabled (default): imports fail for objects that already exist in target folders
  - enabled: existing objects are replaced before import
- Maximum file size guard:
  - constant `MAX_FILE_SIZE` in implementation
  - default: `1048576` bytes (`1 MB`) per file
  - files larger than this limit are skipped with an error status

## Notes
- Existing objects are only replaced when overwrite is enabled.
- Existing non-folder objects in required subfolder positions are reported as errors.
- The command is available for role `ZMSAdministrator`.
