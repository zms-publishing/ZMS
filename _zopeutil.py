################################################################################
# _zopeutil.py
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
from Products.ExternalMethod import ExternalMethod
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
# Product Imports.
import _fileutil

def addObject(container, meta_type, id, title, data):
  """
  Add Zope-object to container.
  """
  if meta_type == 'DTML Document':
    addDTMLDocument( container, id, title, data)
  elif meta_type == 'DTML Method':
    addDTMLMethod( container, id, title, data)
  elif meta_type == 'External Method':
    addExternalMethod( container, id, title, data)
  elif meta_type == 'Page Template':
    addPageTemplate( container, id, title, data)
  elif meta_type == 'Script (Python)':
    addPythonScript( container, id, title, data)

def getObject(container, id):
  """
  Get Zope-object from container.
  """
  ob = getattr(container,id,None)
  return ob

def readObject(container, id, default=None):
  """
  Read Zope-object from container.
  """
  data = default
  ob = getObject(container,id)
  if ob is None and default is not None:
    return default
  if ob.meta_type in [ 'DTML Method', 'DTML Document']:
    data = ob.raw
  elif ob.meta_type == 'Page Template':
    data = ob.read()
  elif ob.meta_type == 'Script (Python)':
    data = ob.read()
  elif ob.meta_type == 'External Method':
    filepath = INSTANCE_HOME+'/Extensions/'+id+'.py'
    f = open( filepath, 'r')
    data = f.read()
    f.close()
  return data

def removeObject(container, id, removeFile=True):
  """
  Remove Zope-object from container.
  """
  if id in container.objectIds():
    ob = getattr(container,id)
    if ob.meta_type == 'External Method' and removeFile:
      filepath = INSTANCE_HOME+'/Extensions/'+id+'.py'
      _fileutil.remove( filepath)
    container.manage_delObjects( ids=[ id])

def initPermissions(container, id):
  """
  Init permissions for Zope-object:
  - set Proxy-role 'Manager'
  - set View-permissions to 'Authenticated' and remove acquired permissions for manage-objects.
  """
  ob = getattr( container, id)
  ob._proxy_roles=('Manager')
  if id.find( 'manage_') >= 0:
    ob.manage_role(role_to_manage='Authenticated',permissions=['View'])
    ob.manage_acquiredPermissions([])

def addDTMLMethod(container, id, title, data):
  """
  Add DTML-Method to container.
  @deprecated
  """
  container.manage_addDTMLMethod( id, title, data)
  initPermissions(container, id)

def addDTMLDocument(container, id, title, data):
  """
  Add DTML-Document to container.
  @deprecated
  """
  container.manage_addDTMLDocument( id, title, data)
  initPermissions(container, id)

def addExternalMethod(container, id, title, data):
  """
  Add External Method to container.
  """
  if data != '':
    filepath = INSTANCE_HOME+'/Extensions/'+id+'.py'
    _fileutil.exportObj( data, filepath)
  ExternalMethod.manage_addExternalMethod( container, id, title, id, id)

def addPageTemplate(container, id, title, data):
  """
  Add Page Template to container.
  """
  ZopePageTemplate.manage_addPageTemplate( container, id, title=title, text=data)
  ob = getattr( container, id)
  ob.output_encoding = 'utf-8'

def addPythonScript(container, id, title, data):
  """
  Add Script (Python) to container.
  """
  PythonScript.manage_addPythonScript( container, id)
  ob = getattr( container, id)
  ob.ZPythonScript_setTitle( title)
  ob.write( data)
  initPermissions(container, id)