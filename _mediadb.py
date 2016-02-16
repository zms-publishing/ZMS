################################################################################
# _mediadb.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from ZPublisher.Iterators import filestream_iterator
from zExceptions import NotFound
import OFS.SimpleItem
import Acquisition
import os
import urllib
import time
# Product Imports.
import _blobfields
import _fileutil
import _globals
import _objattrs


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Constructor
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def manage_addMediaDb(self, location, REQUEST=None, RESPONSE=None):
  """ manage_addMediaDb """
  obj = MediaDb(location)
  self._setObject(obj.id, obj)
  recurse_addMediaDb(self,self.getMediaDb())
  if RESPONSE is not None:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


def containerFilter(container):
  return container.meta_type == 'ZMS'


################################################################################
###   
###   Create
###   
################################################################################
def recurse_addMediaDb(self, mediadb):

  # Process recordset.
  if self.getType()=='ZMSRecordSet':
    key = self.getMetaobjAttrIds(self.meta_id)[0]
    obj_attr = self.getObjAttr(key)
    for lang in self.getLangIds():
      for obj_vers in self.getObjVersions():
        v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
        c = 0
        for r in v:
          for k in r.keys():
            u = r[k]
            if getattr(u,'__class_name__',None) in [_blobfields.MyImage.__class_name__, _blobfields.MyFile.__class_name__]:
              mediadbfile = mediadb.storeFile(u)
              u.mediadbfile = mediadbfile
              u.data = ''
          c += 1
  
  # Process object. 
  else:
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype in _globals.DT_BLOBS:
        for lang in self.getLangIds():
          for obj_vers in self.getObjVersions():
            v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
            if v is not None and getattr(v,'__class_name__',None) in [_blobfields.MyImage.__class_name__, _blobfields.MyFile.__class_name__]:
              mediadbfile = mediadb.storeFile(v)
              v.mediadbfile = mediadbfile
              v.data = ''
              _objattrs.setobjattr(self,obj_vers,obj_attr,v,lang)
  
  # Process children.
  for ob in self.objectValues( self.dGlobalAttrs.keys()):
    recurse_addMediaDb(ob,mediadb)


################################################################################
###   
###   Compress
###   
################################################################################
def getFilenamesFromValue( v):
  rtn = []
  if type( v) is list:
    for i in v:
      rtn.extend( getFilenamesFromValue( i))
  elif type( v) is dict:
    for k in v.keys():
      rtn.extend( getFilenamesFromValue( v[k]))
  elif isinstance(v,_blobfields.MyImage) or isinstance(v,_blobfields.MyFile):
    filename = v.getMediadbfile()
    if filename is not None:
      rtn.append( v.getMediadbfile())
  return rtn

def manage_packMediaDb(self, REQUEST=None, RESPONSE=None):
  """ manage_packMediaDb """
  message = ''
  c = 0
  t = 0
  mediadb = self.getMediaDb()
  path = mediadb.getLocation()
  filenames = mediadb.valid_filenames()
  for filename in os.listdir(path):
    if filename not in filenames:
      filepath = path + os.sep + filename
      if os.path.isfile(filepath):
        os.remove(filepath)
        c += 1
    t += 1
  
  # Debug.
  _globals.writeLog( self, "[manage_packMediaDb]: files deleted %s"%str(filenames))
  
  # Return with message.
  message = 'Packed Media-Folder: %i files (total %i) deleted.'%(c,t)
  return message


################################################################################
###   
###   Destroy
###   
################################################################################
def recurse_delMediaDb(self, mediadb):

  # Process recordset.
  if self.getType()=='ZMSRecordSet':
    key = self.getMetaobjAttrIds(self.meta_id)[0]
    obj_attr = self.getObjAttr(key)
    for lang in self.getLangIds():
      for obj_vers in self.getObjVersions():
        v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
        for r in v:
          for k in r.keys():
            u = r[k]
            mediadbfile = getattr(v,'mediadbfile',None)
            if mediadbfile is not None:
              u.mediadbfile = None
              u.data = mediadb.retrieveFile(mediadbfile)
  # Process object. 
  else:
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype in _globals.DT_BLOBS:
        for lang in self.getLangIds():
          for obj_vers in self.getObjVersions():
            v = _objattrs.getobjattr(self,obj_vers,obj_attr,lang)
            if v is not None:
              mediadbfile = getattr(v,'mediadbfile',None)
              if mediadbfile is not None:
                v.mediadbfile = None
                v.data = mediadb.retrieveFile(mediadbfile)
                _objattrs.setobjattr(self,obj_vers,obj_attr,v,lang)
  
  # Process children.
  if self.meta_id != 'ZMSLinkElement':
    for ob in self.getChildNodes():
      recurse_delMediaDb(ob,mediadb)


def manage_delMediaDb(self, REQUEST=None, RESPONSE=None):
  """ manage_delMediaDb """
  message = ''
  recurse_delMediaDb(self,self.getMediaDb())
  self.manage_delObjects(ids=['acl_mediadb'])
  return message


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Class
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MediaDb(
      OFS.SimpleItem.Item,
      Persistent,
      Acquisition.Implicit):

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Properties.
    # -----------
    meta_type = 'MediaDb'
    icon_clazz = "icon-folder-close"

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


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Constructor
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self, location):
      self.id = 'acl_mediadb'
      self.location = location
      _fileutil.mkDir(self.getLocation())


    # --------------------------------------------------------------------------
    # MediaDb.getLocation
    # --------------------------------------------------------------------------
    def getLocation(self):
      return self.location.replace('$INSTANCE_HOME',INSTANCE_HOME)


    # --------------------------------------------------------------------------
    #  MediaDb.urlQuote
    # --------------------------------------------------------------------------
    def urlQuote(self, s): 
      return urllib.quote(s)

    # --------------------------------------------------------------------------
    #  MediaDb.getPath
    # --------------------------------------------------------------------------
    def getPath(self, REQUEST): 
      path = REQUEST.get('path','')
      if len(path) < len(self.getLocation()):
        path = self.getLocation()
      return path

    # --------------------------------------------------------------------------
    #	MediaDb.readDir
    # --------------------------------------------------------------------------
    def readDir(self, path):
      return _fileutil.readDir(path)

    # --------------------------------------------------------------------------
    #  MediaDb.getParentDir
    # --------------------------------------------------------------------------
    def getParentDir(self, path):
      return _fileutil.getFilePath(path)

    # --------------------------------------------------------------------------
    #  MediaDb.getFile
    # --------------------------------------------------------------------------
    def getFile(self, REQUEST,RESPONSE): 
      filename = _fileutil.extractFilename( self.getPath( REQUEST))
      parent.set_response_headers( filename)
      return self.retrieveFileStreamIterator( filename, REQUEST)

    # --------------------------------------------------------------------------
    #	MediaDb.storeFile
    # --------------------------------------------------------------------------
    def storeFile(self, file):
      filename = _fileutil.extractFilename(file.filename)
      if len( filename) > 0:
        fileext = _fileutil.extractFileExt(file.filename)
        filename = filename[:-(len(fileext)+1)] + '_' + str(time.time()).replace('.','') + '.' + fileext
        filepath = _fileutil.getOSPath('%s/%s'%(self.getLocation(),filename))
        _fileutil.exportObj(file,filepath)
      return filename

    # --------------------------------------------------------------------------
    # MediaDb.manage_index_html
    # --------------------------------------------------------------------------
    security.declareProtected('ZMS Administrator', 'manage_index_html')
    def manage_index_html(self, filename, REQUEST=None):
      """ MediaDb.manage_index_html """
      return self.retrieveFileStreamIterator(filename,REQUEST)

    # --------------------------------------------------------------------------
    # MediaDb.retrieveFileStreamIterator
    # --------------------------------------------------------------------------
    def retrieveFileStreamIterator(self, filename, REQUEST=None):
      filename = filename.replace('..','')
      threshold = 2 << 16 # 128 kb
      local_filename = _fileutil.getOSPath('%s/%s'%(self.getLocation(),filename))
      try:
        fsize = os.path.getsize( local_filename)
      except:
        fsize = 0
        raise NotFound
      if fsize < threshold or REQUEST.RESPONSE is None:
        try:
          f = open( local_filename, 'rb')
          data = f.read()
        finally:
          f.close()
      else:
        data = filestream_iterator( local_filename, 'rb')
      try:
        mt, enc = _globals.guess_contenttype( local_filename, data)
      except:
        mt, enc = 'content/unknown', ''
      # Remove timestamp from filename.
      filename = filename[:filename.rfind('_')]+filename[filename.rfind('.'):]
      REQUEST.RESPONSE.setHeader('Content-Type' ,mt)
      REQUEST.RESPONSE.setHeader('Content-Length' ,fsize)
      REQUEST.RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
      return data


    # --------------------------------------------------------------------------
    # MediaDb.retrieveFile
    # --------------------------------------------------------------------------
    def retrieveFile(self, filename):
      filename = filename.replace('..','')
      try:
        local_filename = _fileutil.getOSPath('%s/%s'%(self.getLocation(),filename))
        f = open( local_filename, 'rb')
        data = f.read()
        f.close()
      except:
        data = ''
      return data

    # --------------------------------------------------------------------------
    #	MediaDb.getFileSize
    # --------------------------------------------------------------------------
    def getFileSize(self, filename):
      local_filename = _fileutil.getOSPath('%s/%s'%(self.getLocation(),filename))
      fsize = os.path.getsize( local_filename)
      return fsize

    # --------------------------------------------------------------------------
    #  MediaDb.valid_filenames
    # --------------------------------------------------------------------------
    def valid_filenames(self):
      filenames = []
      objs = [self.getSelf()]
      objs.extend(objs[0].getTreeNodes())
      objs.extend(objs[0].getTrashcan().getTreeNodes())
      for obj in objs:
        # Process recordset.
        if obj.getType()=='ZMSRecordSet':
          si = obj.getMetaobjAttrIds(obj.meta_id)[0]
          obj_attr = obj.getObjAttr(si)
          for lang in obj.getLangIds():
            for obj_vers in obj.getObjVersions():
              v = _objattrs.getobjattr(obj,obj_vers,obj_attr,lang)
              for r in v:
                for k in r.keys():
                  u = r[k]
                  mediadbfile = getattr(u,'mediadbfile',None)
                  if mediadbfile is not None:
                    filenamesFromValue = getFilenamesFromValue( u)
                    for filename in filenamesFromValue:
                      if filename not in filenames:
                        filenames.append( filename)
        # Process object. 
        else:
          obj_attrs = obj.getObjAttrs()
          for si in obj_attrs.keys():
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
                      filenames.append( filename)
      return filenames


    """
    ############################################################################
    ###
    ###   P r o p e r t i e s
    ###
    ############################################################################
    """

    ############################################################################
    #  MediaDb.manage_changeProperties: 
    #
    #  Change MediaDb properties.
    ############################################################################
    def manage_changeProperties(self, submit, REQUEST, RESPONSE): 
      """ MediaDb.manage_changeProperties """
      
      message = ''

      # Change.
      if submit == 'Change':
        self.location = REQUEST.get('location',self.location)
        
      # Return.
      if RESPONSE is not None:
        RESPONSE.redirect('manage_properties?manage_tabs_message=%s'%urllib.quote(message))

################################################################################
