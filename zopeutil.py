################################################################################
# zopeutil.py
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
from AccessControl.SecurityInfo import ModuleSecurityInfo
from OFS.CopySupport import absattr
from Products.ExternalMethod import ExternalMethod
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
import os
# Product Imports.
import standard
import _fileutil

security = ModuleSecurityInfo('Products.zms.zopeutil')

def nextObject(container, meta_type):
  """
  Get next parent Zope-object with given meta_type.
  """
  while not container.meta_type == meta_type:
    container = container.aq_parent
  return container

def getExternalMethodModuleName(container, id):
  """
  Add context-folder-id to module-name (to prevent deleting artefacts from other clients).
  """
  m = id
  if hasattr(container,'content') and int(getattr(container,'content').getConfProperty('zopeutil.getExternalMethodModuleName.addContextFolderId',True)):
    m = '%s.%s'%(absattr(nextObject(container,'Folder').id),m)
  return m

security.declarePublic('addObject')
def addObject(container, meta_type, id, title, data):
  """
  Add Zope-object to container.
  """
  #try: container.writeBlock("[zopeutil.addObject]: %s@%s +%s(%s)"%(container.meta_type,container.absolute_url(),id,meta_type))
  #except: pass
  if meta_type == 'DTML Document':
    addDTMLDocument( container, id, title, data)
  elif meta_type == 'DTML Method':
    addDTMLMethod( container, id, title, data)
  elif meta_type == 'External Method':
    addExternalMethod( container, id, title, data)
  elif meta_type == 'File':
    addFile( container, id, title, data)
  elif meta_type == 'Image':
    addImage( container, id, title, data)
  elif meta_type == 'Page Template':
    addPageTemplate( container, id, title, data)
  elif meta_type == 'Script (Python)':
    addPythonScript( container, id, title, data)
  elif meta_type == 'Folder':
    addFolder( container, id, title, data)
  elif meta_type == 'Z SQL Method':
    addZSqlMethod( container, id, title, data)

security.declarePublic('getObject')
def getObject(container, id):
  """
  Get Zope-object from container.
  """
  id = standard.operator_absattr(id)
  ob = getattr(container,id,None)
  return ob 

security.declarePublic('callObject')
def callObject(ob, zmscontext=None, options={}):
  """
  Call Zope-object.
  """
  v = None
  if ob.meta_type in [ 'DTML Method', 'DTML Document']:
    v = ob(zmscontext,zmscontext.REQUEST)
  elif options:
    v = ob(zmscontext=zmscontext,options=options)
  elif ob.meta_type in [ 'External Method' ]:
    v = ob()
  elif ob.meta_type in [ 'Script (Python)'] and readData(ob).find('##parameters=zmscontext')<0:
    v = ob()
  else:
    v = ob(zmscontext=zmscontext)
  return v

security.declarePublic('readData')
def readData(ob, default=None):
  """
  Read data of Zope-object.
  """
  data = default
  if ob is None and default is not None:
    return default
  if ob.meta_type in [ 'DTML Method', 'DTML Document']:
    data = ob.raw
  elif ob.meta_type in [ 'Image', 'File']:
    data = ob.data
  elif ob.meta_type in [ 'Page Template', 'Script (Python)']:
    data = ob.read()
  elif ob.meta_type == 'External Method':
    context = ob
    id = ob.id
    while context is not None:
      m = getExternalMethodModuleName(context, id)
      filepath = INSTANCE_HOME+'/Extensions/'+m+'.py'
      if os.path.exists(filepath):
        break
      try:
        context = context.getParentNode()
      except:
        context = None
    if context is None:
      m = id
    filepath = INSTANCE_HOME+'/Extensions/'+m+'.py'
    if os.path.exists(filepath):
      f = open(filepath, 'r')
      data = f.read()
      f.close()
  elif ob.meta_type == 'Z SQL Method':
    connection = ob.connection_id 
    params = ob.arguments_src
    data = '<connection>%s</connection>\n<params>%s</params>\n%s'%(connection,params,ob.src)
  return data

security.declarePublic('readObject')
def readObject(container, id, default=None):
  """
  Read Zope-object from container.
  """
  ob = getObject(container,id)
  return readData(ob,default)

security.declarePublic('removeObject')
def removeObject(container, id, removeFile=True):
  """
  Remove Zope-object from container.
  """
  #try: container.writeBlock("[zopeutil.removeObject]: %s@%s -%s"%(container.meta_type,container.absolute_url(),id))
  #except: pass
  if id in container.objectIds():
    ob = getattr(container,id)
    if ob.meta_type == 'External Method' and removeFile:
      m = getExternalMethodModuleName(container, id)
      filepath = INSTANCE_HOME+'/Extensions/'+m+'.py'
      if os.path.exists(filepath):
        os.remove(filepath)
    container.manage_delObjects(ids=[id])

security.declarePublic('initPermissions')
def initPermissions(container, id):
  """
  Init permissions for Zope-object:
  - set Proxy-role 'Manager'
  - set View-permissions to 'Authenticated' and remove acquired permissions for manage-objects.
  """
  ob = getattr( container, id)
  ob._proxy_roles=('Authenticated','Manager')
  permissions = []
  if id.find( 'manage_') >= 0:
    ob.manage_role(role_to_manage='Authenticated',permissions=['View'])
  else:
    # activate all acquired permissions
    permissions = map(lambda x:x['name'],filter(lambda x:x['selected']=='SELECTED',ob.permissionsOfRole('Manager')))
  ob.manage_acquiredPermissions(permissions)

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
  m = getExternalMethodModuleName(container, id)
  f = id
  if data:
    filepath = INSTANCE_HOME+'/Extensions/'+m+'.py'
    _fileutil.exportObj( data, filepath)
  elif m != f:
    context = container
    while context is not None:
      m = getExternalMethodModuleName(context, id)
      filepath = INSTANCE_HOME+'/Extensions/'+m+'.py'
      if os.path.exists(filepath):
        break
      context = context.getParentNode()
  ExternalMethod.manage_addExternalMethod( container, id, title, m, f)

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

def addFolder(container, id, title, data):
  """
  Add Folder to container.
  """
  container.manage_addFolder(id,title)
  ob = getattr( container, id)
  return ob

def addZSqlMethod(container, id, title, data):
  """
  Add Z Sql Method to container.
  """
  try:
    from Products.ZSQLMethods import SQL
    connection_id = container.SQLConnectionIDs()[0][1]
    arguments = ''
    template = ''
    SQL.manage_addZSQLMethod( container, id, title, connection_id, arguments, template)
  except:
    pass 
  if data:
    ob = getattr( container, id)
    connection = data
    connection = connection[connection.find('<connection>'):connection.find('</connection>')]
    connection = connection[connection.find('>')+1:]
    arguments = data
    arguments = arguments[arguments.find('<params>'):arguments.find('</params>')]
    arguments = arguments[arguments.find('>')+1:]
    template = data
    template = template[template.find('</params>'):]
    template = template[template.find('>')+1:]
    template = '\n'.join(filter( lambda x: len(x) > 0, template.split('\n')))
    ob.manage_edit(title=title,connection_id=connection,arguments=arguments,template=template) 

def addFile(container, id, title, data, content_type=None):
  """
  Add File to container.
  """
  if content_type is None:
    content_type, enc = standard.guess_content_type(id,data)
  container.manage_addFile(id=id,title=title,file=data,content_type=content_type)
  ob = getattr( container, id)
  return ob

def addImage(container, id, title, data, content_type=None):
  """
  Add Image to container.
  """
  if content_type is None:
    content_type, enc = standard.guess_content_type(id,data)
  container.manage_addImage(id=id,title=title,file=data,content_type=content_type)
  ob = getattr( container, id)
  return ob

security.apply(globals())