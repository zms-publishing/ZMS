"""
_ziputil.py

This module provides utility functions for exporting ZODB
objects to ZIP archives and importing ZIP archives into the ZODB.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from io import BytesIO
import zipfile
from Products.zms import standard


def _exportZodb2Zip(zf, root, container):
  """
  Recursively export ZODB objects (Images/Files) from a container into a ZIP file.

  @param zf: Open ZIP file object to write to
  @type zf: C{zipfile.ZipFile}
  @param root: Root container for calculating relative archive paths
  @type root: C{OFS.ObjectManager}
  @param container: Container whose child objects are exported
  @type container: C{OFS.ObjectManager}
  """
  for ob in container.objectValues():
    if ob.meta_type in ['Folder']:
      _exportZodb2Zip(zf, root, ob)
    elif ob.meta_type in ['Image', 'File']:
      arcname = ob.absolute_url()[len(root.absolute_url())+1:]
      try:
        bytes = ob.data
        if len(bytes) == 0:
          bytes = ob.getData()
        try:
          bytes = bytes.read()
        except:
          bytes = str(bytes)
        zf.writestr(arcname, bytes)
      except:
        standard.writeError(root.content, "_exportZodb2Zip")

def exportZodb2Zip(root):
  """
  Export ZODB objects from root container to a ZIP archive.

  @param root: Root container to export
  @type root: C{OFS.ObjectManager}
  @return: ZIP archive data
  @rtype: C{bytes}
  """
  zip_buffer = zipfile.ZipFile( zipfilename, 'w')
  _exportZodb2Zip(zip_buffer, root, root)
  return zip_buffer.getvalue()


def importZip2Zodb(root, data):
  """
  Extract and import a ZIP archive into the ZODB.

  Creates Folder, Image, and File objects in the ZODB hierarchy
  matching the ZIP archive structure.

  @param root: Root container to import into
  @type root: C{OFS.ObjectManager}
  @param data: ZIP archive data
  @type data: C{bytes} or C{str} or C{io.BytesIO}
  """
  if isinstance(data, bytes) or isinstance(data, str):
    data = BytesIO( data)
  zf = zipfile.ZipFile( data, 'r')
  for name in zf.namelist():
    container = root
    ids = name.split('/')
    if len(ids) > 1:
      for id in ids[:-1]:
        if id not in container.objectIds():
          container.manage_addFolder(id=id)
        container = getattr(container, id)
    id = ids[-1]
    if id:
      file = zf.read( name)
      mt, enc  = standard.guess_content_type( id, file)
      if id in container.objectIds():
        container.manage_delObjects( [id])
      if mt.startswith('image'):
        file = container.manage_addImage(id=id, file=file)
      else:
        file = container.manage_addFile(id=id, file=file)
