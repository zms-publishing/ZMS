################################################################################
# _importable.py
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
from cStringIO import StringIO
import ZPublisher.HTTPRequest
import os
import sys
import tempfile
import time
import transaction
import urllib
import zExceptions
# Product Imports.
import _fileutil
import _filtermanager
import _globals
from _blobfields import recurse_uploadRessources, uploadRessources


# ------------------------------------------------------------------------------
#  _importable.recurse_importContent:
#
#  Process objects after import.
# ------------------------------------------------------------------------------
def recurse_importContent(self, folder):
  # Cleanup.
  for key in ['oRoot','oRootNode','oCurrNode','oParent','dTagStack','dValueStack']:
    try: delattr(self,key)
    except: pass
  
  # Upload ressources.
  uploadRessources(self,folder)
  
  # Commit object.
  self.onChangeObj( self.REQUEST, forced=1)
  transaction.commit()
  
  # Process children.
  for ob in self.getChildNodes():
    recurse_importContent(ob,folder)


# ------------------------------------------------------------------------------
#  _importable.importContent
# ------------------------------------------------------------------------------
def importContent(self, file):
  
  # Setup.
  catalog_awareness = self.getConfProperty('ZMS.CatalogAwareness.active',1)
  self.setConfProperty('ZMS.CatalogAwareness.active',0)
  self.dTagStack = _globals.MyStack()
  self.dValueStack = _globals.MyStack()
  self.oParent = self.getParentNode()
  
  # Parse XML-file.
  ob = self.parse(StringIO(file.read()),self,1)
  
  # Process objects after import
  recurse_importContent(ob,_fileutil.getFilePath(file.name))
  
  # Cleanup.
  self.setConfProperty('ZMS.CatalogAwareness.active',catalog_awareness)
  
  # Return imported object.
  return ob


# ------------------------------------------------------------------------------
#  _importable.importFile
# ------------------------------------------------------------------------------
def importFile(self, file, REQUEST, handler):
  
  # Get filename.
  if isinstance(file,ZPublisher.HTTPRequest.FileUpload):
    filename = file.filename
  else: 
    filename = file.name
  _globals.writeBlock( self, '[importFile]: filename='+filename)
  
  # Create temporary folder.
  folder = tempfile.mktemp()
  os.mkdir(folder)
  
  # Save to temporary file.
  filename = _fileutil.getOSPath('%s/%s'%(folder,_fileutil.extractFilename(filename)))
  _fileutil.exportObj(file,filename)
  
  # Find XML-file.
  if _fileutil.extractFileExt(filename) == 'zip':
    _fileutil.extractZipArchive(filename)
    filename = None
    for deep in [0,1]:
      for ext in ['xml', 'htm', 'html' ]:
        if filename is None:
          filename = _fileutil.findExtension(ext, folder, deep)
	  break
    if filename is None:
      raise zExceptions.InternalError('XML-File not found!')
  
  # Import Filter.
  if REQUEST.get('filter','') in self.getFilterIds():
    filename = _filtermanager.importFilter(self, filename, REQUEST.get('filter',''), REQUEST)
  
  # Import XML-file.
  _globals.writeBlock( self, '[importFile]: filename='+filename)
  f = open(filename, 'r')
  ob = handler(self, f)
  f.close()
  
  # Remove temporary files.
  _fileutil.remove(folder, deep=1)
  
  # Return imported object.
  return ob

################################################################################
