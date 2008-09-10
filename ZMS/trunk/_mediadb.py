################################################################################
# _mediadb.py
#
# $Id: _mediadb.py,v 1.4 2004/11/30 20:03:17 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.4 $
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
from Globals import HTMLFile, Persistent   
from ZPublisher.Iterators import filestream_iterator
import OFS.SimpleItem
import Acquisition
import AccessControl.Role
import os
import urllib
import time
# Product Imports.
import _blobfields
import _fileutil
import _globals
import _objattrs


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################

def manage_addMediaDb(self, location, REQUEST=None, RESPONSE=None):
  """ manage_addMediaDb """
  obj = MediaDb(location)
  self._setObject(obj.id, obj)
  recurse_addMediaDb(self,self.getMediaDb())
  if RESPONSE is not None:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


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
            if v is not None:
              mediadbfile = mediadb.storeFile(v)
              v.mediadbfile = mediadbfile
              v.data = ''
              _objattrs.setobjattr(self,obj_vers,obj_attr,v,lang)
  
  # Process children.
  if self.meta_id != 'ZMSLinkElement':
    for ob in self.getChildNodes():
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
  objs = [self]
  objs.extend(objs[0].getTreeNodes())
  objs.extend(objs[0].getTrashcan().getTreeNodes())
  filenames = []
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
  
  c = 0
  t = 0
  path = self.getMediaDb().location
  for filename in os.listdir(path):
    if filename not in filenames:
      filepath = path + os.sep + filename
      if os.path.isfile(filepath):
        os.remove(filepath)
        c += 1
    t += 1

  # Debug.
  if _globals.debug( self):
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
  #++ print "[%s.recurse_delMediaDb]:"%(self.meta_id)

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


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class MediaDb(
    OFS.SimpleItem.Item,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager
    ): 

    # Properties.
    # -----------
    meta_type = 'MediaDb'

    # Management Options.
    # -------------------
    manage_options = (
	{'label': 'Edit','action': 'manage_browse'},
	{'label': 'Properties','action': 'manage_properties'},
        ) 

    manage_index_html = HTMLFile('dtml/acl_mediadb/manage_index', globals())
    manage_browse = HTMLFile('dtml/acl_mediadb/manage_browse', globals())
    manage_properties = HTMLFile('dtml/acl_mediadb/manage_properties', globals())

    """
    ############################################################################
    #
    #   CONSTRUCTOR
    #
    ############################################################################
    """

    ############################################################################
    #  MediaDb.__init__: 
    #
    #  Initialise a new instance of MediaDb.
    ############################################################################
    def __init__(self, location):
      self.id = 'acl_mediadb'
      self.location = location
      _fileutil.mkDir(location)


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
      if len(path) < len(self.location):
        path = self.location
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
    #  MediaDb.getDateStr
    # --------------------------------------------------------------------------
    def getDateStr(self, tTime, sFmt='DATETIME_FMT'):
      dateFmt = {
          'TIME_FMT':'%H:%M:%S',
          'DATE_FMT':'%Y/%m/%d',
          'DATETIME_FMT':'%Y/%m/%d %H:%M:%S',
         }
      try:
        s = time.strftime(dateFmt[sFmt],time.localtime(tTime))
      except:
        s = str(tTime)
      return s


    # --------------------------------------------------------------------------
    #  MediaDb.getDataSizeStr
    # --------------------------------------------------------------------------
    def getDataSizeStr(self, len): 
      return _fileutil.getDataSizeStr(len)


    # --------------------------------------------------------------------------
    #  MediaDb.getFile
    # --------------------------------------------------------------------------
    def getFile(self, REQUEST,RESPONSE): 
      filename = _fileutil.extractFilename( self.getPath( REQUEST))
      RESPONSE.setHeader('Content-Type','Unknown')
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      return self.retrieveFileStreamIterator( filename, REQUEST)


    # --------------------------------------------------------------------------
    #	MediaDb.storeFile
    # --------------------------------------------------------------------------
    def storeFile(self, file):
      filename = _fileutil.extractFilename(file.filename)
      if len( filename) > 0:
        fileext = _fileutil.extractFileExt(file.filename)
        filename = filename[:-(len(fileext)+1)] + '_' + str(time.time()).replace('.','') + '.' + fileext
        filepath = _fileutil.getOSPath('%s/%s'%(self.location,filename))
        _fileutil.exportObj(file,filepath)
      return filename


    # --------------------------------------------------------------------------
    #	MediaDb.retrieveFileStreamIterator
    # --------------------------------------------------------------------------
    def retrieveFileStreamIterator(self, filename, REQUEST=None):
      threshold = 2 << 16 # 128 kb
      local_filename = _fileutil.getOSPath('%s/%s'%(self.location,filename))
      fsize = os.path.getsize( local_filename)
      REQUEST.RESPONSE.setHeader( 'content-length' ,fsize)
      if fsize < threshold or REQUEST.RESPONSE is None:
        try:
          f = open( local_filename, 'rb')
          data = f.read()
        finally:
          f.close()
      else:
        data = filestream_iterator( local_filename, 'rb')
      return data


    # --------------------------------------------------------------------------
    #	MediaDb.retrieveFile
    # --------------------------------------------------------------------------
    def retrieveFile(self, filename):
      try:
        local_filename = _fileutil.getOSPath('%s/%s'%(self.location,filename))
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
      local_filename = _fileutil.getOSPath('%s/%s'%(self.location,filename))
      fsize = os.path.getsize( local_filename)
      return fsize


    # --------------------------------------------------------------------------
    #	MediaDb.destroyFile
    # --------------------------------------------------------------------------
    def destroyFile(self, filename):
      try:
        filepath = _fileutil.getOSPath('%s/%s'%(self.location,filename))
        _fileutil.remove(filepath)
      except:
        pass


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
