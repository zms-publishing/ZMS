# Collect Zope Artifacts (`manage_collect_zope_artifacts`)

## What this metacommand does

`manage_collect_zope_artifacts` scans the current Zope home tree for supported Zope artifacts and transfers selected ones into a `ZMSLibrary` meta-object.

The command is intended as a migration/helper tool for moving technical Zope assets into the ZMS meta-model:

- Python scripts and external methods
- page templates and DTML objects
- files and images
- Z SQL methods
- folder-based paths as library attribute ids

Each selected artifact is stored as one meta-object attribute in the target `ZMSLibrary`.
The attribute id is the artifact path relative to the Zope home folder.
The attribute type is taken from the source object's `meta_type`.
The attribute payload is read with `zopeutil.readData(...)` and stored as `newCustom`.

## How to get started

1. Ensure the metacommand is available:

- Definition: `Products/zms/conf/metacmd_manager/manage_collect_zope_artifacts/__init__.py`
- Implementation: `Products/zms/conf/metacmd_manager/manage_collect_zope_artifacts/manage_collect_zope_artifacts.py`

2. Ensure a target `ZMSLibrary` meta-object already exists:

- Open `content/metaobj_manager/manage_main`
- Create a new meta-object of type `ZMSLibrary` if needed

3. Open ZMS and run the action `Collect Zope Artifacts...`.

4. Select the target library, keep or adjust the checked artifacts, and click `Collect`.

5. Verify the imported attributes in the chosen `ZMSLibrary`.

## What the script collects

The script traverses `self.getHome()` recursively.

### Included object types

The collection uses `self.metaobj_manager.valid_zopetypes`, currently including:

- `DTML Method`
- `DTML Document`
- `External Method`
- `File`
- `Image`
- `Page Template`
- `Script (Python)`
- `Z SQL Method`

Note:
`Folder` is part of `valid_zopetypes`, but in this script it is used only as a traversal container. Folder objects themselves are not added as selectable import rows because the function descends into them first.

### Excluded paths

The script excludes paths that are already used as Zope-type attributes in existing meta-objects.

This exclusion list is built from:

```py
for metaobjId in self.getMetaobjIds():
  for metaobjAttrId in self.getMetaobjAttrIds(metaobjId, types=zope_objects):
    exclude_paths.append(metaobjAttrId)
```

This means the UI will not offer artifacts whose relative path already exists as a Zope-backed meta-object attribute somewhere in the model.

### Path mapping

For each matching source object, the stored attribute id is built from the physical path relative to the Zope home object.

Example pattern:

```py
path = '/'.join(node.getPhysicalPath())[len('/'.join(self.getHome().getPhysicalPath()))+1:]
```

A source object like:

```text
Extensions/my_report
```

becomes a library attribute with id:

```text
Extensions/my_report
```

## Important API functions (ZMS + script)

### Metacommand entrypoint

- `manage_collect_zope_artifacts(self, request=None)`
  Main function called by the metacommand. It scans the Zope tree, renders a selection form, and optionally imports the selected artifacts into the chosen library.

### Script helper logic

The implementation keeps its main logic inline, but these parts are the most important:

- `traverse(node, execute)`
  Recursively walks through folders, filters supported artifact types, and optionally performs the import for selected rows.

- `zopeutil.readData(node)`
  Reads the artifact payload from the source object. Depending on `meta_type`, this may return text, bytes, or a generated serialization such as the XML-like header for a `Z SQL Method`.

- `self.metaobj_manager.setMetaobjAttr(...)`
  Creates the target attribute inside the selected `ZMSLibrary`.

### Frequently used ZMS object APIs in this script

- `getHome()`
  Returns the root object used as traversal starting point.

- `getMetaobjIds()`
  Enumerates all meta-objects to build the exclusion list and fill the library select box.

- `getMetaobjAttrIds(metaobjId, types=...)`
  Returns existing attribute ids filtered by Zope types.

- `getMetaobj(metaobjId)`
  Loads the meta-object definition so the script can filter for `ZMSLibrary` entries.

- `metaobj_manager.valid_zopetypes`
  Defines which Zope object types are considered transferable artifacts.

## Existing import strategy

For each selected row, the script currently does this:

1. Take the selected target library id from `request['meta_id']`
2. Use the relative path as `newId` and `newName`
3. Detect the source `meta_type`
4. Read the source payload with `zopeutil.readData(node)`
5. Call `setMetaobjAttr(...)` on the target library

The core import block is:

```py
id = request['meta_id']
oldId = None
newId = path
newName = path
newType = node.meta_type
newCustom = zopeutil.readData(node)
self.metaobj_manager.setMetaobjAttr(
  id=id,
  oldId=oldId,
  newId=newId,
  newName=newName,
  newType=newType,
  newCustom=newCustom,
)
```

## Typical project adaptations

The safest customization point is the nested `traverse(node, execute)` function.

### Limit collection to specific folders

Add a path guard before appending/importing the item:

```py
if not path.startswith('Extensions/'):
  return rtn
```

A more practical variant inside the artifact branch is:

```py
if not (path.startswith('Extensions/') or path.startswith('skins/')):
  return rtn
```

### Skip specific artifact types

Add a `meta_type` filter before `setMetaobjAttr(...)` or before appending the row:

```py
if newType in ['Image']:
  return rtn
```

### Rename imported ids

If you want the target library ids to use another naming scheme, adapt `newId`:

```py
newId = 'legacy/' + path
newName = newId
```

### Normalize specific source types

If your project wants to map source object types to other attribute types, adapt `newType` before calling `setMetaobjAttr(...)`.

Example:

```py
if newType == 'Page Template':
  newType = 'zpt'
```

Only do this if your project explicitly relies on that alternative representation.

## Data format notes

`zopeutil.readData(...)` reads different object types differently:

- `DTML Document` / `DTML Method`: raw source text
- `Page Template` / `Script (Python)`: object `.read()` content
- `File` / `Image`: binary payload
- `External Method`: Python source from `INSTANCE_HOME/Extensions/...`
- `Z SQL Method`: generated text including connection and parameter metadata

This is important when verifying imported attributes in the target library.

## Common extension points

- Restrict traversal root: change `traverse(self.getHome(), execute)`

- Exclude more objects: extend the `exclude_paths` logic or add path filters in `traverse(...)`

- Change preselection behavior: edit the checkbox HTML generation in the table rows

- Change target id naming: adapt `newId = path`

- Add a status message or redirect after import: extend the `status` collection or response handling

## Troubleshooting

- Target library is not visible in the select list
  Only meta-objects with `metaobj['type'] == 'ZMSLibrary'` are shown. Create the library first in the meta-object manager.

- An expected artifact is missing from the table
  Check whether its `meta_type` is in `valid_zopetypes` and whether its relative path is already present in another Zope-type meta-object attribute.

- External method imports empty content
  Verify that the corresponding file exists in `INSTANCE_HOME/Extensions/` and that `zopeutil.readData(...)` can resolve it.

- Imported binary objects do not look readable in the model UI
  This can be normal for `File` or `Image` payloads because they are stored as binary content.

- Clicking `Collect` creates no useful result
  Ensure `meta_id` points to a real `ZMSLibrary` and at least one checkbox in `ids:list` is submitted.

## Quick integration checklist

1. Create or choose a target `ZMSLibrary`.
2. Run `Collect Zope Artifacts...`.
3. Check whether the proposed artifact list matches your migration scope.
4. Import a small subset first, especially for binaries or external methods.
5. Review the resulting attributes in the target library before importing everything.
6. If needed, adapt traversal filters or id mapping in `manage_collect_zope_artifacts.py`.