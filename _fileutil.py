################################################################################
# _fileutil.py
#
# $Id: _fileutil.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.9 $
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
from App.Common import package_home
from ZPublisher.Iterators import filestream_iterator
try: # >= Zope-2.10
  from zope.contenttype import guess_content_type
except: # < Zope-2.10
  from zope.app.content_types import guess_content_type
import fnmatch
import os
import shutil
import stat
import tempfile
import zipfile


# ------------------------------------------------------------------------------
#  _fileutil.importZexp:
#
# Import file from specified path.
# ------------------------------------------------------------------------------
def importZexp(self, path, filename):
  src_filename = path + filename
  dst_filename = INSTANCE_HOME + '/import/' + filename
  if src_filename != dst_filename:
    try: 
      os.stat(getOSPath(dst_filename)) 
    except OSError:
      shutil.copy(src_filename,dst_filename)
  self.manage_importObject(filename)
  remove(dst_filename)


# ------------------------------------------------------------------------------
#  _fileutil.extractFilename:
#
#  Extract filename from path.
#  IN:  path
# ------------------------------------------------------------------------------
def extractFilename(path, sep=None):
  if sep is None:
    path = getOSPath(path) 
  items = path.split( os.sep)
  lastitem = items[len(items)-1]
  return lastitem


# ------------------------------------------------------------------------------
#  _fileutil.extractFileExt:
# 
#  Extract fileextension from path.
#  IN:  path
#  OUT: extension
# ------------------------------------------------------------------------------
def extractFileExt(path):
  items = path.split('.')
  lastitem = items[len(items)-1]
  return lastitem


# ------------------------------------------------------------------------------
#  _fileutil.getOSPath:
# 
#  Return path with OS separators.
# ------------------------------------------------------------------------------
def getOSPath(path, sep=None, chs=range(32)+[34,60,62,63,127]):
  if sep is None: sep = os.sep
  path = path.replace('\\',sep)
  path = path.replace('/',sep)
  if type( path) is type( ''):
    path = unicode(path, 'latin-1')
  path = path.encode('ascii', 'replace') # replace uncodable characters by ? (63)
  if len( chs) > 0:
    for ch in chs:
      path = path.replace(chr(ch),'')
  return path


# ------------------------------------------------------------------------------
#  _fileutil.getFilePath:
#
#  Extract filepath from path (cut-off filename).
#  IN:  path
#  OUT: filepath
# ------------------------------------------------------------------------------
def getFilePath(path):
  items = getOSPath(path).split(os.sep)
  filepath = ''
  for i in range(len(items)-1):
    filepath = filepath + items[i] + os.sep
  if len(filepath) > 0:
    if filepath[-1] == os.sep:
      filepath = filepath[:-1]
  return filepath


# ------------------------------------------------------------------------------
#  _fileutil.findExtension:
#
#  Searches path and all subdirectories for file with extension and returns 
#  complete filepath. Returns None if no file with specified extension exists.
#  IN:  extension
#       path
#  OUT: filepath
# ------------------------------------------------------------------------------
def findExtension(extension, path, deep=1):
  rtn = None
  path = getOSPath(path)
  for file in os.listdir(path):
    filepath = path + os.sep + file 
    if extractFileExt(file).lower() == extension:
      return filepath
    elif deep:
      mode = os.stat(filepath)[stat.ST_MODE]
      if stat.S_ISDIR(mode):
        rtn = findExtension(extension,filepath,deep)
        if rtn is not None:
          return rtn
  return rtn


# ------------------------------------------------------------------------------
#  _fileutil.readPath:
#
#  Reads path.
# ------------------------------------------------------------------------------
def readPath(path, data=True, recursive=True):
  l = []
  path = path.replace('\\',os.sep)
  path = path.replace('/',os.sep)
  filter = extractFilename(path, os.sep)
  if filter.find('*') >= 0 and filter.find('.') >= 0:
    path = getFilePath( path)
  else:
    filter = None
  mode = os.stat(path)[stat.ST_MODE]
  if stat.S_ISDIR(mode):
    for filename in os.listdir(path):
      local_filename = path + os.sep + filename
      filename = extractFilename(local_filename)
      if filter is None or fnmatch.fnmatch(filename, filter):
        d = {}
        d['local_filename']=unicode(local_filename,'latin-1').encode('utf-8')
        d['filename']=unicode(filename,'latin-1').encode('utf-8')
        mode = os.stat(local_filename)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
          if recursive:
            l.extend(readPath(local_filename))
          else:
            mtime = os.path.getmtime( local_filename)
            d['mtime']=mtime
            d['isdir']=True
            l.append(d)
        else:
          fdata = None
          if data:
            fdata, mt, enc, fsize = readFile( local_filename, 'b', -1)
            d['data']=fdata
            d['content_type']=mt
            d['encoding']=enc
          else:
            try:
              mt, enc = guess_content_type( local_filename)
            except:
              mt, enc = 'content/unknown', ''
            d['content_type']=mt
            d['encoding']=enc
          fsize = os.path.getsize( local_filename)
          d['size']=fsize
          mtime = os.path.getmtime( local_filename)
          d['mtime']=mtime
          d['isdir']=False
          l.append(d)
  return l


# ------------------------------------------------------------------------------
#  _fileutil.readFile:
#
#  Reads file (threshold for filesteam_iterator is 128 kb).
# ------------------------------------------------------------------------------
def readFile(filename, mode='b', threshold=2 << 16):
  size = os.path.getsize( filename)
  if size < threshold or -1 == threshold:
    f = None
    try:
      f = open( filename, 'r'+mode)
      data = f.read()
    finally:
      if f is not None:
        f.close()
  else:
    data = filestream_iterator( filename, 'r'+mode)
  try:
    mt, enc  = guess_content_type( filename, data)
  except:
    mt, enc = 'content/unknown', ''
  return data, mt, enc, size


# ------------------------------------------------------------------------------
#  _fileutil.importPath:
#
#  Imports path.
# ------------------------------------------------------------------------------
def importPath(self, path):
  path = getOSPath(path)
  mode = os.stat(path)[stat.ST_MODE]
  if stat.S_ISDIR(mode):
    for filename in os.listdir(path):
      filepath = path + os.sep + filename
      mode = os.stat(filepath)[stat.ST_MODE]
      if stat.S_ISDIR(mode):
        folder = self.manage_addFolder(id=filename)
        folder = getattr(self,filename)
        importPath(folder,filepath)
      else: 
        f = open(filepath,'rb')
        file = self.manage_addFile(id=filename,file=f.read())
        f.close()


# ------------------------------------------------------------------------------
#  _fileutil.remove:
#
#  Removes path (and all its subdirectories if deep==1).
# ------------------------------------------------------------------------------
def remove(path, deep=0):
  path = getOSPath(path)
  mode = os.stat(path)[stat.ST_MODE]
  if stat.S_ISDIR(mode):
    if deep == 1:
      for filename in os.listdir(path):
        filepath = path + os.sep + filename
        mode = os.stat(filepath)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
          remove(filepath,deep)
        else: 
          os.remove(filepath)
    os.rmdir(path)
  else:
    os.remove(path)


# ------------------------------------------------------------------------------
#  _fileutil.getDataSizeStr: 
#
#  Display string for file-size.
# ------------------------------------------------------------------------------
def getDataSizeStr(len):
  s = ''
  try:
    mod = 0
    while len > 1024.0 and mod < 3:
      len = len / 1024.0
      mod = mod + 1
    s = str(int(len))
    n = str(int(10*(len - int(len))))
    if mod == 0:
      s = "%sBytes"%s
    elif mod == 1:
      s = "%sKB"%s
    elif mod == 2:
      s = "%s.%s MB"%(s,n)
    elif mod == 3:
      s = "%s.%s GB"%(s,n)
  except:
    pass
  return s


# ------------------------------------------------------------------------------
#  _fileutil.executeCommand:
# ------------------------------------------------------------------------------
def executeCommand(path, command):
  os.chdir(path)
  os.system(command)

    
# ------------------------------------------------------------------------------
#  _fileutil.exportObj:
# ------------------------------------------------------------------------------
def exportObj(obj, filename, filetype='b'):
    
  #-- Try to create directory-tree.
  filename = getOSPath(filename)
  filepath = getFilePath(filename)
  mkDir(filepath)
        
  #-- Get object data.
  data = None
  try: # ImageFile
    f = open(obj.path,'r%s'%filetype)
    data = f.read()
    f.close()
  except:
    try: # Image / File
      data = obj.data
      if len(data) == 0:
        data = obj.getData()
    except: 
      try:
        data = obj.raw # DTML Method
      except:
        try:
          data = obj.read() # REQUEST.enctype multipart/form-data
        except:
          data = str(obj)
  
  #-- Save to file.
  if data is not None:
    objfile = open(filename,'w%s'%filetype)
    if type(data) is type(''):
      objfile.write(data)
    else:
      while data is not None:
        objfile.write(data.data)
        data=data.next
    objfile.close()


# ------------------------------------------------------------------------------
#  _fileutil.mkDir:
#
#  Make directory.
# ------------------------------------------------------------------------------
def mkDir(path):
  try:
    os.makedirs( path)
  except:
    pass


# ------------------------------------------------------------------------------
#  _fileutil.readDir
# ------------------------------------------------------------------------------
def readDir(path):
  obs = []
  path = getOSPath(path)
  for file in os.listdir(path):
    ob = {}
    ob['path'] = path + os.sep
    ob['file'] = file
    filepath = path + os.sep + file 
    ob['mtime'] = os.path.getmtime(filepath)
    ob['size'] = os.path.getsize(filepath)
    mode = os.stat(filepath)[stat.ST_MODE]
    if stat.S_ISDIR(mode): 
      ob['type'] = 'd'
    else:
      ob['type'] = 'f'
    obs.append((ob['type'],ob))
  obs.sort()
  return map(lambda ob: ob[1],obs)


################################################################################
###
###  PIL (Python Imaging Library)
###
################################################################################

# ------------------------------------------------------------------------------
#  _fileutil.createThumbnail:
#
#  Creates thumbnail of given image.
#  @param img
#  @return thumb
# ------------------------------------------------------------------------------
def createThumbnail(img, maxdim=100, qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = getOSPath('%s/%s'%(tempfolder,img.filename))
  exportObj(img,filename)
  
  # Call PIL to generate thumbnail.
  command = 'python ' + getOSPath(package_home(globals())+'/conf/pil/img_conv.py') + ' ' + str(maxdim) + ' ' + filename + ' ' + str(qual)
  os.system(command)
  
  # Read thumbnail from file-system.
  lang_sffx = '_' + img.lang
  thumb_sffx = '_thumbnail'
  filename = filename[:-(len(extractFileExt(filename))+1)]
  f = open(filename + thumb_sffx + '.jpg','rb')
  thumb_data = f.read()
  thumb_filename = filename
  if len(thumb_filename)>len(lang_sffx) and thumb_filename[-len(lang_sffx):]==lang_sffx: thumb_filename = thumb_filename[:-len(lang_sffx)]
  thumb_filename = extractFilename(thumb_filename + thumb_sffx + lang_sffx + '.jpg')
  thumb = {'data':thumb_data,'filename':thumb_filename}
  f.close()
    
  # Remove temp-folder and images.
  remove(tempfolder,deep=1)
  
  # Returns thumbnail.
  return thumb


# ------------------------------------------------------------------------------
#  _fileutil.pil_img_resize:
# ------------------------------------------------------------------------------
def pil_img_resize(img, size, mode='resize', sffx='none', qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = getOSPath('%s/%s'%(tempfolder,img.filename))
  exportObj(img,filename)
  
  # Call PIL to generate resized image.
  command = 'python ' + getOSPath(package_home(globals())+'/conf/pil/img_resize.py') + ' ' + str(size[0]) + ' ' + str(size[1]) + ' ' + filename + ' ' + mode + ' ' + str(qual)
  os.system(command)
  
  # Read resized image from file-system.

  if sffx == 'none':
      f = open(filename,'rb')
      resized_data = f.read()
      resized_filename = extractFilename(filename)
      resized = {'data':resized_data,'filename':resized_filename}
      f.close()
  else:
      # Read thumbnail from file-system.
      lang_sffx = '_' + img.lang
      thumb_sffx = '_thumbnail'
      newfilename = filename[:-(len(extractFileExt(filename))+1)]
      f = open(filename,'rb')
      thumb_data = f.read()
      thumb_filename = filename
      if len(thumb_filename)>len(lang_sffx) and thumb_filename[-len(lang_sffx):]==lang_sffx: thumb_filename = thumb_filename[:-len(lang_sffx)]
      thumb_filename = extractFilename(newfilename + thumb_sffx + lang_sffx + '.jpg')
      resized = {'data':thumb_data,'filename':thumb_filename}
      f.close()
  
  # Remove temp-folder and images.
  remove(tempfolder,deep=1)
  
  # Returns resized image.
  return resized


# ------------------------------------------------------------------------------
#  _fileutil.pil_img_crop:
# ------------------------------------------------------------------------------
def pil_img_crop(img, box, qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = getOSPath('%s/%s'%(tempfolder,img.filename))
  exportObj(img,filename)
  
  # Call PIL to generate resized image.
  command = 'python ' + getOSPath(package_home(globals())+'/conf/pil/img_crop.py') + ' ' + str(box[0]) + ' ' + str(box[1]) + ' ' + str(box[2]) + ' ' + str(box[3]) + ' ' + filename + ' ' + str(qual)
  os.system(command)
  
  # Read resized image from file-system.
  f = open(filename,'rb')
  cropped_data = f.read()
  cropped_filename = extractFilename(filename)
  cropped = {'data':cropped_data,'filename':cropped_filename}
  f.close()
  
  # Remove temp-folder and images.
  remove(tempfolder,deep=1)
  
  # Returns cropped image.
  return cropped


# ------------------------------------------------------------------------------
#  _fileutil.pil_img_rotate:
# ------------------------------------------------------------------------------
def pil_img_rotate(img, direction, qual=75):

    # Save image in temp-folder.
    tempfolder = tempfile.mktemp()
    filename = getOSPath('%s/%s'%(tempfolder,img.filename))
    exportObj(img,filename)

    # Call PIL to generate resized image.
    command = 'python ' + getOSPath(package_home(globals())+'/conf/pil/img_rotate.py') + ' ' + str(direction) + ' ' + filename + ' ' + str(qual)
    os.system(command)

    # Read resized image from file-system.
    f = open(filename,'rb')
    rot_data = f.read()
    rot_filename = extractFilename(filename)
    rotated = {'data':rot_data,'filename':rot_filename}
    f.close()

    # Remove temp-folder and images.
    remove(tempfolder,deep=1)

    # Returns cropped image.
    return rotated


################################################################################
###
###  ZIP
###
################################################################################

# ------------------------------------------------------------------------------
#  _fileutil.getZipArchive:
#
#  Extract files from zip-archive and return list of extracted files.
# ------------------------------------------------------------------------------
def getZipArchive(f):
  l = []
  
  # Saved zip-file in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = tempfolder + os.sep + extractFilename(tempfolder) + '.zip'
  exportObj(f,filename)
  
  # Unzip zip-file.
  extractZipArchive(filename)
  
  # Remove zip-file.
  remove(filename)
  
  # Read extracted files.
  l = readPath(tempfolder,data=True)
  
  # Remove temp-folder.
  remove(tempfolder,deep=1)
  
  # Return list of files.
  return l


# ------------------------------------------------------------------------------
#  _fileutil.extractZipArchive:
#
#  Unpack ZIP-Archive.
# ------------------------------------------------------------------------------
def extractZipArchive(file):
  zf = zipfile.ZipFile( file, 'r')
  for name in zf.namelist():
    dir = getOSPath( name)
    i = dir.rfind( os.sep) 
    if i > 0:
      dir = getFilePath(file) + os.sep + dir[ :i]
      mkDir( dir)
    localname = getOSPath( getFilePath(file) + os.sep + name)
    if localname[-1] != os.sep:
      f = open( localname, 'wb')
      f.write( zf.read( name))
      f.close()
  zf.close()


# ------------------------------------------------------------------------------
#  _fileutil.buildZipArchive:
#
#  Pack ZIP-Archive and return data.
# ------------------------------------------------------------------------------
def writeZipFile( zf, basepath, path, filter):
  for file in os.listdir( path):
    filepath = path+os.sep+file
    mode = os.stat( filepath)[stat.ST_MODE]
    if stat.S_ISDIR( mode): 
      writeZipFile( zf, basepath, filepath, filter)
    else:
      arcname = filepath[len( basepath)+1:]
      match = False
      for pattern in filter.split(';'):
        match = match or fnmatch.fnmatch( arcname, pattern)
      if match:
        zf.write( filepath, arcname)

def buildZipArchive( files, get_data=True):
  
  # Create temporary zip-file.
  zipfilename = tempfile.mktemp() + '.zip'
  
  # Write filtered files to zip-file.
  files = getOSPath( files)
  path = getFilePath( files)
  filter = extractFilename( files)
  zf = zipfile.ZipFile( zipfilename, 'w')
  writeZipFile( zf, path, path, filter)
  zf.close()
  
  # Read data from zip-file as return value.
  data = zipfilename
  if get_data:
    f = open( zipfilename, 'rb')
    data = f.read()
    f.close()
  
    # Remove temporary zip-file.
    os.remove( zipfilename)
  
  # Returns filename or data of zip-file.
  return data

################################################################################
