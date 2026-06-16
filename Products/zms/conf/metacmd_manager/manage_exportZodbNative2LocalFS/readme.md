# Export ZODB to LocalFS

## Purpose
This meta-command exports selected Zope objects from the ZODB into files on the local filesystem.

It is useful when you want to:
- inspect source artifacts outside the ZMI
- version object content with Git
- compare template/script changes with standard file diff tools
- build a local backup of editable object definitions

## What gets exported
The command traverses the site below Home and lists exportable objects. The following object types are supported:

- DTML Method -> .dtml
- Page Template -> .zpt
- Script (Python) -> .py
- Z SQL Method -> .zsql
- File -> no extra extension
- Image -> no extra extension

Folder-like containers are traversed recursively:
- Folder
- ZMS
- ZMSMetacmdProvider
- ZMSMetamodelProvider
- ZMSWorkflowProvider

## How path mapping works
For each selected object, the export target is built from:

1. the Path value you enter in the form
2. plus /var
3. plus the object URL path below the ZMS Home object
4. plus the mapped extension (if any)

## How to use in ZMI
1. Open the ZMS meta-command: "Export ZODB to LocalFS".
2. Verify or adjust the Path field (default is INSTANCE_HOME).
3. Keep or change the object selection in the table.
4. Click Execute.
5. Check the Status column for Done messages and output file paths.

## Notes
- Refresh reloads the object list without writing files.
- Existing files at target paths may be overwritten by export.
- The command is available for role ZMSAdministrator.

