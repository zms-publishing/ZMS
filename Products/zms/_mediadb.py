"""
_mediadb.py

The mediadb module provides functionality for managing binary assets 
(files, images, blobs) in a ZMS instance. It handles storage, retrieval, 
and organization of uploaded files in a filesystem-based repository.

Key Features:
  - Store and retrieve binary files (blobs) from disk
  - Organize files in flat or hierarchical directory structures
  - Track file references across ZMS objects and recordsets
  - Migrate between different directory structures
  - Identify and manage orphaned files
  - Serve files as HTTP streaming responses
  - Validate file integrity and references

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from ZPublisher.Iterators import filestream_iterator
from platform import python_version
from zExceptions import NotFound
import OFS.SimpleItem
import Acquisition
import json
import os
import shutil
import time
import tempfile
# Product Imports.
from Products.zms import standard
from Products.zms import _blobfields
from Products.zms import _fileutil
from Products.zms import _globals
from Products.zms import _objattrs


def manage_addMediaDb(self, location, REQUEST=None, RESPONSE=None):
  """
  Initialize a new MediaDb instance at the specified filesystem location and
  recursively attach all existing blob attributes from the object tree.

  @param self: ZMS object to attach the mediadb to.
  @type self: C{object}
  @param location: Filesystem path where the mediadb should store its files.
  @type location: C{str}
  @param REQUEST: Optional HTTP request object (not used).
  @type REQUEST: C{HTTPRequest}
  @param RESPONSE: Optional HTTP response object for redirection after creation.
  @type RESPONSE: C{HTTPResponse}
  """
  obj = MediaDb(location)
  self._setObject(obj.id, obj)
  recurse_addMediaDb(self,self.getMediaDb())
  if RESPONSE is not None:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


def containerFilter(container):
  """Return True for containers whose meta_type is 'ZMS' (used by addable object filter)."""
  return container.meta_type == 'ZMS'


def recurse_addMediaDb(self, mediadb):
  """Recursively attach all blob attributes of the object tree to the given mediadb."""
  if self.getType() == 'ZMSRecordSet':
    key = self.getMetaobjAttrIds(self.meta_id,types=['list'])[0]
    obj_attr = self.getObjAttr(key)
    lang = self.getPrimaryLanguage()
    for obj_vers in self.getObjVersions():
      v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
      c = 0
      for r in v:
        for k in r:
          u = r[k]
          if isinstance(u,_blobfields.MyBlob):
            mediadbfile = mediadb.storeFile(u)
            u.mediadbfile = mediadbfile
            u.data = ''
        c += 1

  # Process object.
  else:
    for key in self.getObjAttrs():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype in _globals.DT_BLOBS:
        for lang in self.getLangIds():
          for obj_vers in self.getObjVersions():
            v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
            if isinstance(v,_blobfields.MyBlob):
              _objattrs.setobjattr(self,obj_vers,obj_attr,v,lang)

  # Process children.
  for ob in self.objectValues( self.dGlobalAttrs):
    recurse_addMediaDb(ob,mediadb)


def getFilenamesFromValue(v):
  """Return a flat list of mediadb filenames referenced inside an attribute value."""
  rtn = []
  if type( v) is list:
    for i in v:
      rtn.extend( getFilenamesFromValue( i))
  elif type( v) is dict:
    for k in v:
      rtn.extend( getFilenamesFromValue( v[k]))
  elif isinstance(v,_blobfields.MyBlob):
    filename = v.getMediadbfile()
    if filename is not None:
      rtn.append(filename.split(os.sep)[-1])
  return rtn


def manage_structureMediaDb(self, structure, REQUEST=None, RESPONSE=None):
  """
  Reorganise mediadb files into the requested directory structure.
  The method moves all files into their new target location as computed by
  mediadb.targetFile(), which may involve creating intermediate directories for
  hierarchical structures. The method also updates the mediadb structure property
  to ensure future uploads are stored in the correct location.

  @param structure: Desired directory nesting depth (0 = flat).
  @type structure: C{int}
  @return: Message summarizing the restructuring outcome.
  @rtype: C{str}
  """
  message = ''
  mediadb = self.getMediaDb()
  mediadb.structure = structure

  # Temp location.
  path = mediadb.getLocation()
  location = mediadb.location
  mediadb.location = location + "_tmp"
  temp = mediadb.getLocation()

  # Traverse existing structure.
  def traverse(path, p):
    """
    Walk path recursively and move each file into its target location.
    The target location is computed by mediadb.targetFile() and may involve
    creating intermediate directories for hierarchical structures.
    @param path: Current filesystem path to traverse.
    @type path: C{str}
    @param p: Progress dict tracking total files processed (p['t']).
    @type p: C{dict}
    """
    standard.writeBlock( self, "[manage_structureMediaDb]: traverse %s"%path)
    for filename in os.listdir(path):
      filepath = os.path.join(path,filename)
      if os.path.isdir(filepath):
        traverse(filepath,p)
      elif os.path.isfile(filepath):
        targetpath = mediadb.targetFile(filepath)
        standard.writeBlock( self, "[manage_structureMediaDb]: %s -> %s"%(filepath,targetpath))
        targetdir = os.sep.join(targetpath.split(os.sep)[:-1])
        if not os.path.exists(targetdir):
          standard.writeBlock( self, "[manage_structureMediaDb]: makedirs %s"%targetdir)
          os.makedirs(targetdir)
        shutil.move(filepath,targetpath)
        p['t'] += 1

  standard.writeBlock( self, "[manage_structureMediaDb]: makedirs %s"%temp)
  os.makedirs(temp)
  p = {'t':0}
  traverse(path,p)
  standard.writeBlock( self, "[manage_structureMediaDb]: remove %s"%path)
  shutil.rmtree(path)
  standard.writeBlock( self, "[manage_structureMediaDb]: rename %s -> %s"%(temp,path))
  os.rename(temp,path)

  # Restore location.
  mediadb.location = location

  # Return with message.
  message = "Restructured Media-Folder %s: %i files proecessed."%(str(structure),p['t'])
  standard.writeBlock( self, "[manage_structureMediaDb]: "+message)
  return message


def manage_packMediaDb(self, REQUEST=None, RESPONSE=None):
  """
  Scan the mediadb and move all orphaned files (not referenced by any ZMS object)
  to a temporary folder for cleanup or archival.
  
  The method traverses the entire mediadb directory structure and identifies files
  that are not referenced by any blob attribute in the ZMS object tree. 
  It moves these  orphaned files to a temporary folder for manual review and cleanup. 
  The method returns a message summarizing the number of orphaned files found 
  and their new location.
  """
  message = ''
  mediadb = self.getMediaDb()
  path = mediadb.getLocation()

  # Get filenames.
  filenames = [x[1] for x in mediadb.valid_filenames()]
  standard.writeLog( self, "[manage_packMediaDb]: filenames %s"%str(filenames))
  tempfolder = tempfile.mkdtemp()
  os.makedirs(tempfolder, exist_ok=True)
  standard.writeLog( self, "[manage_packMediaDb]: tempfolder %s"%tempfolder)

  # Traverse existing structure.
  def traverse(path, p):
    """Walk path recursively and identify unreferenced files."""
    for filename in os.listdir(path):
      filepath = os.path.join(path,filename)
      if os.path.isdir(filepath):
        traverse(filepath,p)
      elif os.path.isfile(filepath):
        if filename not in p['filenames']:
          standard.writeBlock( self, "[manage_packMediaDb]: filename %s"%str(filename))
          shutil.move(filepath,p['tempfolder']+os.sep+filename)
          p['c'] += 1
        p['t'] += 1
  p = {'t':0,'c':0,'filenames':filenames,'tempfolder':tempfolder}
  traverse(path,p)

  # Return with message.
  message = "%i files (total %i) moved to %s."%(p['c'],p['t'],p['tempfolder'])
  standard.writeBlock( self, "[manage_packMediaDb]: "+message)
  return message


def recurse_delMediaDb(self, mediadb):
  """
  Recursively detach blobs from the mediadb and restore their data back into ZODB.
  The method traverses the object tree and for each blob attribute found, it
  retrieves the file from the mediadb using the stored filename reference, restores
  the blob's data attribute with the file content, and removes the mediadb reference.
  The method also processes recordsets by iterating through their list attributes 
  and applying the same logic to any blob values found within the records. Finally, 
  the method recurses into child objects to ensure all blobs in the tree are processed.
  CAVE: Restoring the blob-files back into the ZODB can massively enlarge it's size.

  @param self: Root object to start traversal from.
  @type self: C{object}
  @param mediadb: MediaDb instance to retrieve files from.
  @type mediadb: C{MediaDb}
  """
  if self.getType() == 'ZMSRecordSet':
    key = self.getMetaobjAttrIds(self.meta_id,types=['list'])[0]
    obj_attr = self.getObjAttr(key)
    lang = self.getPrimaryLanguage()
    for obj_vers in self.getObjVersions():
      v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
      for r in v:
        for k in r:
          u = r[k]
          mediadbfile = getattr(u,'mediadbfile',None)
          if mediadbfile is not None:
            u.mediadbfile = None
            u.data = mediadb.retrieveFile(mediadbfile)
  # Process object.
  else:
    for key in self.getObjAttrs():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype in _globals.DT_BLOBS:
        for lang in self.getLangIds():
          for obj_vers in self.getObjVersions():
            v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
            if v is not None:
              mediadbfile = getattr(v,'mediadbfile',None)
              if mediadbfile is not None:
                v.aq_parent = None
                v.mediadbfile = None
                v.data = mediadb.retrieveFile(mediadbfile)
                _objattrs.setobjattr(self,obj_vers,obj_attr,v,lang)

  # Process children.
  if self.meta_id != 'ZMSLinkElement':
    for ob in self.getChildNodes():
      recurse_delMediaDb(ob,mediadb)


def manage_delMediaDb(self, REQUEST=None, RESPONSE=None):
  """
  Detach the mediadb from this object and remove the acl_mediadb child.
  The method calls recurse_delMediaDb to restore all blob data back 
  into the ZODB, then deletes the mediadb object itself. 
  CAVE: Restoring the blob-files back into the ZODB can massively enlarge it's size.
  """
  message = ''
  recurse_delMediaDb(self,self.getMediaDb())
  self.manage_delObjects(ids=['acl_mediadb'])
  return message


class MediaDb(
      OFS.SimpleItem.Item,
      Persistent,
      Acquisition.Implicit):
    """
    Persistent Zope object that stores uploaded binary assets in a flat 
    or hierarchical filesystem.
    
    The MediaDb provides methods to store and retrieve files, compute target
    paths, and manage the storage structure.
    The mediadb is designed to be attached to a ZMS content object as a child
    with a fixed id (acl_mediadb) and accessed via the getMediaDb() method.
    The mediadb location is configurable and supports expansion of $INSTANCE_HOME.
    The mediadb also provides management interface methods to serve files as HTTP
    responses and to reorganize the storage structure.
    """

    security = ClassSecurityInfo()

    # Properties.
    # -----------
    meta_type = 'MediaDb'
    zmi_icon = "fas fa-images"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    manage_options = (
      {'label': 'Properties','action': 'acl_mediadb/manage_properties'},
      {'label': 'Edit','action': 'acl_mediadb/manage_browse'},
      )

    # Management Interface.
    # ---------------------
    manage_browse = PageTemplateFile('zpt/MediaDb/manage_browse', globals())
    manage_main = PageTemplateFile('zpt/MediaDb/manage_properties', globals())
    manage_properties = PageTemplateFile('zpt/MediaDb/manage_properties', globals())


    def __init__(self, location, structure=0):
      """Initialize the instance state."""
      self.id = 'acl_mediadb'
      self.setLocation(location)
      self.structure = structure
      _fileutil.mkDir(self.getLocation())


    def setLocation(self, location):
      """Set the filesystem root path for the mediadb, stripping any trailing slash."""
      if location.endswith('/'):
        location = location[:-1]
      self.location = location


    def getLocation(self):
      """Return the resolved filesystem root path, expanding $INSTANCE_HOME."""
      return self.location.replace('$INSTANCE_HOME', standard.getINSTANCE_HOME())

    def getStructure(self):
      """Return the directory nesting depth used for hierarchical storage (0 = flat)."""
      return getattr(self,'structure',0)


    def urlQuote(self, s):
      """Return the URL-encoded form of the given string."""
      return standard.url_quote(s)


    def getPath(self, REQUEST):
      """Return the requested filesystem path, defaulting to the mediadb root."""
      path = REQUEST.get('path','')
      if len(path) < len(self.getLocation()):
        path = self.getLocation()
      return path


    def readDir(self, path):
      """Return a directory listing for the given filesystem path."""
      return _fileutil.readDir(path)


    def getParentDir(self, path):
      """Return the parent directory of the given filesystem path."""
      return _fileutil.getFilePath(path)


    def getFile(self, REQUEST,RESPONSE):
      """Stream the file identified by the request path as an HTTP response."""
      filename = _fileutil.extractFilename( self.getPath( REQUEST))
      return self.retrieveFileStreamIterator( filename, REQUEST)


    def targetFile(self, filename):
      """Compute the full filesystem path where a file should be stored."""
      filepath = ''
      filename = _fileutil.extractFilename(filename)
      filename = filename.replace('..','')
      if len(filename) > 0:
        fileext = filename[filename.rfind('.'):]
        filename = filename[:filename.rfind('.')]
        location = [self.getLocation()]
        for i in reversed(range(self.getStructure())):
          location.append(filename[-(i+1)])
        location.append(filename+fileext)
        filepath = os.sep.join(location)
      return filepath


    def storeFile(self, file):
      """Store an uploaded file object into the mediadb and return its unique filename."""
      filepath = ''
      filename = _fileutil.extractFilename(file.filename)
      if len(filename) > 0:
        filename, fileext = os.path.splitext(filename)
        filename = filename + '_'+str(time.time()).replace('.','') + fileext
        filepath = self.targetFile(filename)
        _fileutil.exportObj(file,filepath)
      return filename


    security.declareProtected('ZMS Administrator', 'manage_index_html')
    def manage_index_html(self, filename, REQUEST=None):
      """Serve a mediadb file as a streaming HTTP response."""
      return self.retrieveFileStreamIterator(filename,REQUEST)


    def retrieveFileStreamIterator(self, filename, REQUEST=None):
      """Retrieve a mediadb file and return its content as a stream or bytes object."""
      threshold = 2 << 16 # 128 kb
      local_filename = self.targetFile(filename)
      if not os.path.exists(local_filename):
        # File not found: return dummy file.
        msg = 'File not found: %s'%(local_filename)
        msg = msg.encode('utf-8')
        standard.writeBlock(self, msg)
        filename = 'file_not_found_0.txt'
        mt, enc, data, fsize = 'text/plain', 'utf-8', msg, len(msg)
        REQUEST.response.setStatus(404)
      else:
        # File found.
        fsize = os.path.getsize( local_filename)
        if fsize < threshold or REQUEST.RESPONSE is None:
          try:
            # Open the file and ensure it is closed after reading.
            with open(local_filename, 'rb') as f:
                data = f.read()
          except FileNotFoundError:
            msg = 'File not found: %s' % (local_filename)
            msg = msg.encode('utf-8')
            standard.writeBlock(self, msg)
            filename = 'file_not_found_0.txt'
            mt, enc, data, fsize = 'text/plain', 'utf-8', msg, len(msg)
            REQUEST.response.setStatus(404)
        else:
          data = filestream_iterator( local_filename, 'rb')
        try:
          mt, enc = standard.guess_content_type( local_filename, data)
        except:
          mt, enc = 'application/octet-stream', ''
      # Remove timestamp from filename.
      filename = filename[:filename.rfind('_')]+filename[filename.rfind('.'):]
      standard.set_response_headers(filename,mt,fsize,REQUEST)
      return data


    def retrieveFile(self, filename):
      """Return the raw bytes of the given mediadb file."""
      filename = filename.replace('..','')
      try:
        location = self.getLocation()
        if not filename.startswith(location):
          filename = os.path.join(location,filename)
        with open(filename, 'rb') as f:
          data = f.read()
      except:
        standard.writeError(self, "can't retrieveFile(%s)"%str(filename))
        data = ''
      return data


    def getFileSize(self, filename):
      """Return the size in bytes of the given mediadb file."""
      location = self.getLocation()
      if not filename.startswith(location):
        filename = os.path.join(location,filename)
      fsize = os.path.getsize( filename)
      return fsize


    def valid_filenames(self):
      """Return a list of (attr_path, filename) pairs for all mediadb-referenced files."""
      filenames = []
      objs = [self.getSelf()]
      objs.extend(objs[0].getTreeNodes())
      objs.extend(objs[0].getTrashcan().getTreeNodes())
      for obj in objs:
        # Process recordset.
        if obj.getType() == 'ZMSRecordSet':
          si = obj.getMetaobjAttrIds(obj.meta_id)[0]
          obj_attr = obj.getObjAttr(si)
          for lang in obj.getLangIds():
            for obj_vers in obj.getObjVersions():
              obj_attr_name = '%s_%s'%(si,lang)
              v = _objattrs.getobjattr(obj,obj_vers,obj_attr,lang)
              for r in v:
                for k in r:
                  u = r[k]
                  mediadbfile = getattr(u,'mediadbfile',None)
                  if mediadbfile is not None:
                    filenamesFromValue = getFilenamesFromValue( u)
                    for filename in filenamesFromValue:
                      if filename not in filenames:
                        filenames.append(('/'.join(obj.getPhysicalPath())+'#'+obj_attr_name, filename))
        # Process object.
        else:
          obj_attrs = obj.getObjAttrs()
          for si in obj_attrs:
            obj_attr = obj_attrs[si]
            datatype = obj_attr['datatype']
            multilang = obj_attr['multilang']
            if datatype in [ 'file', 'image', 'list', 'dictionary']:
              for obj_vers in obj.getObjVersions():
                obj_attr_names = []
                if multilang:
                  for lang in self.getLangIds():
                    obj_attr_names.append('%s_%s'%(si,lang))
                else:
                  obj_attr_names.append(si)
                for obj_attr_name in obj_attr_names:
                  v = getattr(obj_vers,obj_attr_name,None)
                  filenamesFromValue = getFilenamesFromValue( v)
                  for filename in filenamesFromValue:
                    if filename not in filenames:
                      filenames.append(('/'.join(obj.getPhysicalPath())+'#'+obj_attr_name, filename))
      return filenames


    def manage_test(self, REQUEST, RESPONSE):
      """Scan the mediadb and return a JSON report of OK/MISSING file statuses."""
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')

      def traverse(path):
        """Collect filenames by walking path recursively."""
        files = []
        for filename in os.listdir(path):
          filepath = os.path.join(path,filename)
          if os.path.isdir(filepath):
            files.extend(traverse(filepath))
          elif os.path.isfile(filepath):
            files.append(filename)
        return files

      # Get filenames.
      path_filenames = traverse(self.getLocation())
      valid_filenames = self.valid_filenames()
      l = []
      l.extend([(attr, filename, 'OK' if filename in path_filenames else 'MISSING') for (attr, filename) in valid_filenames])
      l.extend([(None, filename, 'MISSING') for filename in path_filenames if filename not in [y[1] for y in valid_filenames]])
      return json.dumps(l, indent=2)


    def manage_changeProperties(self, submit, REQUEST, RESPONSE):
      """
      Apply submitted form changes to MediaDb location and redirect back 
      to properties.
      """
      message = ''
      # Change.
      if submit == 'Change':
        location = REQUEST.get('location',self.location)
        self.setLocation(location)
      # Return.
      if RESPONSE is not None:
        RESPONSE.redirect('manage_properties?manage_tabs_message=%s'%standard.url_quote(message))
