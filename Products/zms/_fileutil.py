"""
_fileutil.py - ZMS File System Utilities

This module provides file-system utility functions for ZMS, including
path handling, file reading/writing, ZEXP import/export, ZIP archive
creation/extraction, and data size formatting.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from ZPublisher.Iterators import filestream_iterator
from App.config import getConfiguration
import fnmatch
import os
import shutil
import tempfile
import zipfile
import zope.contenttype
# Product Imports.
from Products.zms import _blobfields
from Products.zms import zopeutil


################################################################################
# Module-level helper functions
################################################################################

def import_zexp(self, zexp, new_id, id_prefix, _sort_id=0):
  """
  Import a ZEXP file into the current container and normalize sort IDs.

  @param self: The container object to import into
  @type self: C{OFS.ObjectManager}
  @param zexp: The ZEXP file object to import
  @param new_id: Target ID for the imported object
  @type new_id: C{str}
  @param id_prefix: ID prefix for sort-ID normalization
  @type id_prefix: C{str}
  @param _sort_id: Initial sort ID
  @type _sort_id: C{int}
  """
  INSTANCE_HOME = getConfiguration().instancehome
  # Import
  filename = zexp.title_or_id()
  fileid = filename[:filename.find('.')]
  filepath = INSTANCE_HOME + '/import/' + filename
  exportObj( zexp, filepath)
  importZexp( self, filename)
  
  # Rename
  if new_id != fileid:
    self.manage_renameObject(fileid, new_id)
  
  ## Normalize Sort-IDs
  obj = getattr( self, new_id)
  obj.sort_id = _sort_id
  self.normalizeSortIds( id_prefix)


def importZexp(self, filename):
  """
  Import a ZEXP file from the INSTANCE_HOME/import folder.

  @param self: The container object to import into
  @type self: C{OFS.ObjectManager}
  @param filename: Name of the ZEXP file in the import folder
  @type filename: C{str}
  """
  ### Store copy of ZEXP in INSTANCE_HOME/import-folder.
  INSTANCE_HOME = getConfiguration().instancehome
  filepath = INSTANCE_HOME + '/import/' + filename
  self.manage_importObject(filename)
  remove(filepath)


def extractFilename(path, sep=None, undoable=False):
  """
  Extract the filename from a file path.

  @param path: File path
  @type path: C{str}
  @param sep: Custom separator (default: OS separator)
  @type sep: C{str} or C{None}
  @param undoable: Whether special characters should be preserved
  @type undoable: C{bool}
  @return: Filename portion of the path
  @rtype: C{str}
  """
  if sep is None:
    path = getOSPath(path, undoable=undoable)
  items = path.split( os.sep)
  lastitem = items[len(items)-1]
  return lastitem


def extractFileExt(path):
  """
  Extract the file extension from a path.

  @param path: File path
  @type path: C{str}
  @return: File extension (without dot)
  @rtype: C{str}
  """
  items = path.split('.')
  lastitem = items[len(items)-1]
  return lastitem


def getOSPath(path, chs=list(range(32))+[34, 39, 60, 62, 63, 127], undoable=False):
  """
  Normalize a path string to use OS-appropriate separators.

  @param path: File path to normalize
  @type path: C{str} or C{bytes}
  @param chs: List of character codes to strip (unused)
  @type chs: C{list}
  @param undoable: Whether special characters should be preserved
  @type undoable: C{bool}
  @return: Normalized path
  @rtype: C{str}
  """
  if isinstance(path, bytes):
    path = path.decode('utf-8')
  path = path.replace('\\', os.sep)
  path = path.replace('/', os.sep)
  # if isinstance(path, str):
  #   path = path.encode('ascii', 'replace')
  # if undoable or os.name != "nt":
  #   path = path.encode('ascii', 'replace') # replace uncodable characters by ? (63)
  # if len( chs) > 0:
  #   for ch in chs:
  #     path = path.replace(chr(ch), '')
  return path


def absoluteOSPath(path):
  """
  Convert a relative path to an absolute path, resolving '..' segments.

  @param path: File path (may contain '..' segments)
  @type path: C{str}
  @return: Absolute path with resolved parent references
  @rtype: C{str}
  """
  path = getOSPath(path)
  l0 = path.split(os.sep)
  l1 = []
  for i in l0:
    if i == '..':
      l1 = l1[:-1]
    else:
      l1 = l1 + [i]
  path = os.sep.join(l1)
  return path


def getFilePath(path):
  """
  Extract the directory path from a full file path (removing filename).

  @param path: Full file path
  @type path: C{str}
  @return: Directory path
  @rtype: C{str}
  """
  items = getOSPath(path).split(os.sep)
  filepath = ''
  for i in range(len(items)-1):
    filepath = filepath + items[i] + os.sep
  if len(filepath) > 0:
    if filepath[-1] == os.sep:
      filepath = filepath[:-1]
  return filepath


def findExtension(extension, path, deep=1):
  """
  Search a directory (optionally recursively) for a file with the given extension.

  @param extension: File extension to search for (without dot)
  @type extension: C{str}
  @param path: Directory path to search in
  @type path: C{str}
  @param deep: Whether to search subdirectories recursively
  @type deep: C{int}
  @return: Full path to the first matching file, or None
  @rtype: C{str} or C{None}
  """
  rtn = None
  path = getOSPath(path)
  for file in os.listdir(path):
    filepath = path + os.sep + file 
    if extractFileExt(file).lower() == extension:
      return filepath
    elif deep:
      if os.path.isdir(filepath):
        rtn = findExtension(extension, filepath, deep)
        if rtn is not None:
          return rtn
  return rtn


def readPath(path, data=True, recursive=True):
  """
  Read directory contents and return a list of file/directory info dicts.

  @param path: Directory path (may include glob wildcards)
  @type path: C{str}
  @param data: Whether to read file data
  @type data: C{bool}
  @param recursive: Whether to recurse into subdirectories
  @type recursive: C{bool}
  @return: List of dicts with keys: local_filename, filename, mtime, size,
           content_type, encoding, data (if requested), isdir
  @rtype: C{list}
  """
  l = []
  path = path.replace('\\', os.sep)
  path = path.replace('/', os.sep)
  filter = extractFilename(path, os.sep)
  if filter.find('*') >= 0 and filter.find('.') >= 0:
    path = getFilePath( path)
  else:
    filter = None
  if os.path.isdir(path):
    for filename in os.listdir(path):
      local_filename = os.path.join(path,filename)
      if filter is None or fnmatch.fnmatch(filename, filter):
        d = {}
        d['local_filename']=local_filename
        d['filename']=extractFilename(local_filename)
        if os.path.isdir(local_filename):
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
              mt, enc = zope.contenttype.guess_content_type( local_filename)
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
      if os.path.isdir(local_filename) and recursive:
        if filter is not None:
          local_filename = local_filename + '/' + filter
        l.extend(readPath(local_filename, data, recursive))
  return l


def readFile(filename, mode='b', threshold=2 << 16):
  """
  Read a file and return its data along with content-type information.

  Uses a filestream_iterator for files larger than the threshold.

  @param filename: Path to the file to read
  @type filename: C{str}
  @param mode: File open mode ('b' for binary, 't' for text)
  @type mode: C{str}
  @param threshold: Size threshold in bytes for using filestream_iterator
                    (-1 to always read into memory)
  @type threshold: C{int}
  @return: Tuple of (data, content_type, encoding, file_size)
  @rtype: C{tuple}
  """
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
    mt, enc  = zope.contenttype.guess_content_type( filename, data)
  except:
    mt, enc = 'content/unknown', ''
  return data, mt, enc, size


def remove(path, deep=0):
  """
  Remove a file or directory.

  @param path: Path to remove
  @type path: C{str}
  @param deep: Unused (directories are always removed recursively)
  @type deep: C{int}
  """
  path = getOSPath(path)
  if os.path.isdir(path):
    shutil.rmtree(path)
  else:
    os.remove(path)


def getDataSizeStr(len):
  """
  Format a file size in bytes as a human-readable string.

  @param len: File size in bytes
  @type len: C{int} or C{float}
  @return: Human-readable size string (e.g. '1KB', '2.5 MB')
  @rtype: C{str}
  """
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
      s = "%s.%s MB"%(s, n)
    elif mod == 3:
      s = "%s.%s GB"%(s, n)
  except:
    pass
  return s


def executeCommand(path, command):
  """
  Execute a shell command in the given directory.

  @param path: Working directory for the command
  @type path: C{str}
  @param command: Shell command to execute
  @type command: C{str}
  """
  os.chdir(path)
  os.system(command)


def exportObj(obj, filename):
  """
  Export an object's data to a file on disk.

  Supports MyBlob objects, Zope objects, ImageFile objects,
  file-like objects, and raw data.

  @param obj: The object to export
  @param filename: Destination file path
  @type filename: C{str}
  @return: The exported data, or None if no data
  @rtype: C{bytes} or C{None}
  """
  
  #-- Try to create directory-tree.
  filename = getOSPath(filename)
  filepath = getFilePath(filename)
  mkDir(filepath)
  
  #-- Get object data.
  data = None
  # MyBlob
  if isinstance(obj, _blobfields.MyBlob):
    data = obj.getData()
  elif getattr(obj, 'meta_type',None) is not None:
    data = zopeutil.readData(obj)
  else:
    try: # ImageFile
      f = open(obj.path,'rb')
      data = f.read()
      f.close()
    except:
      try:
        # data,io.RawIOBase
        data = obj.read()
      except:
        data = obj
    
  #-- Save to file.
  if data is not None:
    objfile = open(filename, 'wb')
    if isinstance(data, str):
      try:
        data = data.encode("utf-8")
      except:
        pass
    objfile.write(bytes(data))
    objfile.close()
  return data


def mkDir(path):
  """
  Create a directory and any necessary parent directories.

  @param path: Directory path to create
  @type path: C{str}
  """
  try:
    os.makedirs( path)
  except:
    pass


def readDir(path):
  """
  List directory contents with metadata.

  @param path: Directory path to list
  @type path: C{str}
  @return: List of dicts with keys: path, file, mtime, size, type ('d' or 'f'),
           sorted by type (directories first)
  @rtype: C{list}
  """
  obs = []
  path = getOSPath(path)
  for file in os.listdir(path):
    ob = {}
    ob['path'] = path + os.sep
    ob['file'] = file
    filepath = path + os.sep + file 
    ob['mtime'] = os.path.getmtime(filepath)
    ob['size'] = os.path.getsize(filepath)
    if os.path.isdir(filepath): 
      ob['type'] = 'd'
    else:
      ob['type'] = 'f'
    obs.append(ob)
  return sorted(obs, key=lambda x:x['type'])


#--------------------------------------------------------------------------
#  ZIP
#--------------------------------------------------------------------------

def getZipArchive(f):
  """
  Extract files from a ZIP archive and return a list of extracted files.

  Creates a temporary directory, extracts the archive, reads the contents,
  then cleans up.

  @param f: ZIP file data or object to extract
  @return: List of file info dicts (from L{readPath})
  @rtype: C{list}
  """
  l = []
  
  # Saved zip-file in temp-folder.
  tempfolder = tempfile.mkdtemp()
  filename = tempfolder + os.sep + extractFilename(tempfolder) + '.zip'
  exportObj(f, filename)
  
  # Unzip zip-file.
  extractZipArchive(filename)
  
  # Remove zip-file.
  remove(filename)
  
  # Read extracted files.
  l = readPath(tempfolder, data=True)
  
  # Remove temp-folder.
  remove(tempfolder, deep=1)
  
  # Return list of files.
  return l


def extractZipArchive(file):
  """
  Unpack a ZIP archive to the directory containing the archive file.

  Skips macOS metadata files (__MACOSX/, .DS_Store).

  @param file: Path to the ZIP archive file
  @type file: C{str}
  @return: List of extracted file paths
  @rtype: C{list}
  """
  l = []
  
  zf = zipfile.ZipFile( file, 'r')
  for name in zf.namelist():
    if name.startswith('__MACOSX/') or name.endswith('.DS_Store'):
        continue
    dir = getOSPath( name)
    i = dir.rfind( os.sep) 
    if i > 0:
      dir = getFilePath(file) + os.sep + dir[ :i]
      mkDir( dir)
    localname = getOSPath( getFilePath(file) + os.sep + name)
    if localname[-1] != os.sep:
      l.append( localname)
      f = open( localname, 'wb')
      f.write( zf.read( name))
      f.close()
  zf.close()
  
  # Return list of files.
  return l


def writeZipFile( zf, basepath, path, filter):
  """
  Recursively write files matching a filter pattern to a ZIP archive.

  @param zf: Open ZipFile object to write to
  @type zf: C{zipfile.ZipFile}
  @param basepath: Base path for computing archive names
  @type basepath: C{str}
  @param path: Current directory path to scan
  @type path: C{str}
  @param filter: Semicolon-separated glob patterns to match files
  @type filter: C{str}
  """
  for file in os.listdir( path):
    filepath = path+os.sep+file
    if os.path.isdir(filepath): 
      writeZipFile( zf, basepath, filepath, filter)
    else:
      arcname = filepath[len( basepath)+1:]
      match = False
      for pattern in filter.split(';'):
        match = match or fnmatch.fnmatch( arcname, pattern)
      if match:
        zf.write( filepath, str(arcname))


def buildZipArchive( files, get_data=True):
  """
  Build a ZIP archive from files matching a pattern and return data.

  @param files: File path pattern (e.g. '/path/to/dir/*.txt')
  @type files: C{str}
  @param get_data: If True, return archive data; if False, return temp filename
  @type get_data: C{bool}
  @return: ZIP archive data (bytes) or temporary file path
  @rtype: C{bytes} or C{str}
  """
  
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


def tail_lines(filename,linesback=10,returnlist=0):
    """
    Read the last N lines from a file, similar to 'tail -N filename'.

    @param filename: Path to the file to read
    @type filename: C{str}
    @param linesback: Number of lines to read from end of file
    @type linesback: C{int}
    @param returnlist: If true, return a list of lines; otherwise a string
    @type returnlist: C{int}
    @return: Last N lines as a string or list
    @rtype: C{str} or C{list}
    """
    avgcharsperline=75
    
    file = open(filename, 'r')
    while True:
        try: file.seek(-1 * avgcharsperline * linesback, 2)
        except IOError: file.seek(0)
        if file.tell() == 0: atstart=1
        else: atstart=0
        
        lines=file.read().split("\n")
        if (len(lines) > (linesback+1)) or atstart: break
        # The lines are bigger than we thought
        avgcharsperline=avgcharsperline * 1.3 #Inc avg for retry
    file.close()
    
    if len(lines) > linesback: start=len(lines)-linesback -1
    else: start=0
    if returnlist: return lines[start:len(lines)-1]
    
    out=""
    for l in lines[start:len(lines)-1]: out=out + l + "\n"
    return out
