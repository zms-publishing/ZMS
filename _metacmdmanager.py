################################################################################
# _metacmdmanager.py
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
from Products.PythonScripts import PythonScript
import copy
import string
import urllib
# Product Imports.
import _globals
import _objattrs


# Example code.
# -------------

dtmlMethodWithExecExampleCode = '<!-- @deprecated -->'

dtmlMethodWithoutExecExampleCode = '<!-- @deprecated -->'

pageTemplateExampleCode = \
  '<!DOCTYPE html>\n' + \
  '<html lang="en">\n' + \
  '<tal:block tal:content="structure python:here.zmi_html_head(here,request)">zmi_html_head</tal:block>\n' + \
  '<body class="zmi">\n' + \
  '<tal:block tal:content="structure python:here.zmi_body_header(here,request,options=here.customize_manage_options())">zmi_body_header</tal:block>\n' + \
  '<div id="zmi-tab">\n' + \
  '<tal:block tal:content="structure python:here.zmi_breadcrumbs(here,request)">zmi_breadcrumbs</tal:block>\n' + \
  '<div style="clear:both;">&nbsp;</div>\n' + \
  '</div><!-- #zmi-tab -->\n' + \
  '<script>\n' + \
  '</script>\n' + \
  '<tal:block tal:content="structure python:here.zmi_body_footer(here,request)">zmi_body_footer</tal:block>\n' + \
  '</body>\n' + \
  '</html>\n'

pyScriptExampleCode = \
  '# Example code:\n' + \
  '\n' + \
  '# Import a standard function, and get the HTML request and response objects.\n' + \
  'from Products.PythonScripts.standard import html_quote\n' + \
  'request = container.REQUEST\n' + \
  'RESPONSE =  request.RESPONSE\n' + \
  '\n' + \
  '# Return a string identifying this script.\n' + \
  'print "This is the", script.meta_type, \'"%s"\' % script.getId(),\n' + \
  'if script.title:\n' + \
  '    print "(%s)" % html_quote(script.title),\n' + \
  'print "in", container.absolute_url()\n' + \
  'return printed\n' + \
  ''


"""
################################################################################
#
#   K E Y S
#
################################################################################
"""

CONF_METACMDS = "ZMS.custom.commands"


"""
################################################################################
#
#   X M L   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _metacmdmanager.importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, createIfNotExists=1):

  id = item['id']
  if createIfNotExists == 1:

    # Delete existing object.
    try: delMetacmd(self, id)
    except: pass

    # Initialize attributes of new object.
    newId = id
    newAcquired = 0
    newName = item['name']
    newMethod = item['meta_type']
    newExec = item.has_key('exec') and item['exec']
    newDescription = item['description']
    newIconClazz = item.get('icon_clazz','')
    newMetaTypes = item['meta_types']
    newRoles = item['roles']
    newNodes = item.get('nodes','{$}')
    newData = item['data']

    # Return with new id.
    return setMetacmd(self, None, newId, newAcquired, newName, newMethod, \
      newData, newExec, newDescription, newIconClazz, newMetaTypes, newRoles, \
      newNodes)


def importXml(self, xml, REQUEST=None, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      id = _importXml(self,item,createIfNotExists)
  else:
    id = _importXml(self,v,createIfNotExists)


# ------------------------------------------------------------------------------
#  _metacmdmanager.getRawMetacmds:
# 
#  Returns raw list of actions.
# ------------------------------------------------------------------------------
def getRawMetacmds(self):
  return self.getConfProperty(CONF_METACMDS,[])


# ------------------------------------------------------------------------------
#  _metacmdmanager.delMetacmd:
# 
#  Delete Action specified by given Id.
# ------------------------------------------------------------------------------
def delMetacmd(self, id):

  # Catalog.
  obs = copy.deepcopy(getRawMetacmds(self))
  old = filter(lambda x: x['id']==id, obs)
  if len(old) > 0:
    obs.remove(old[0])
  self.setConfProperty( CONF_METACMDS, obs)

  # Remove Template.
  self.manage_delObjects(ids=[id])

  # Return with empty id.
  return ''

# ------------------------------------------------------------------------------
#  _metacmdmanager.setMetacmd:
#
#  Set/add Action specified by given Id.
# ------------------------------------------------------------------------------
def setMetacmd(self, id, newId, newAcquired, newName='', newMethod=None, \
      newData=None, newExec=0, newDescription='', newIconClazz='', newMetaTypes=[], \
      newRoles=['ZMSAdministrator'], newNodes='{$}'):
  obs = copy.deepcopy(getRawMetacmds(self))

  # Catalog.
  old = filter(lambda x: x['id'] in [id, newId], obs)
  if len(old) > 0:
    obs.remove(old[0])

  # Values.
  new = {}
  new['id'] = newId
  new['acquired'] = newAcquired
  new['name'] = newName
  new['description'] = newDescription
  new['icon_clazz'] = newIconClazz
  new['meta_types'] = newMetaTypes
  new['roles'] = newRoles
  new['nodes'] = newNodes
  new['exec'] = newExec
  obs.append(new)
  self.setConfProperty( CONF_METACMDS, obs)

  # Insert Template.
  if id is None:
    newTitle = '*** DO NOT DELETE OR MODIFY ***'
    if newAcquired:
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        newMethod = getattr(portalMaster,newId).meta_type
    if newId in self.objectIds():
      self.manage_delObjects(ids=[newId])
    if newMethod == 'DTML Method': 
      self.manage_addDTMLMethod(newId,newTitle) 
      if newData is None: 
        if newExec: 
          newData = dtmlMethodWithExecExampleCode 
        else: 
          newData = dtmlMethodWithoutExecExampleCode 
      newData = newData.replace('$$NAME$$',newName) 
    elif newMethod == 'DTML Document': 
      self.manage_addDTMLDocument(newId,newTitle) 
      if newData is None:
        newData = dtmlMethodExampleCode 
    elif newMethod == 'Page Template':
      self.manage_addProduct['PageTemplates'].manage_addPageTemplate(id=newId,title=newTitle,text=pageTemplateExampleCode)
    elif newMethod == 'Script (Python)':
      PythonScript.manage_addPythonScript(self,newId)
      if newData is None: newData = pyScriptExampleCode

  # Rename Template.
  elif id != newId:
    self.manage_renameObject(id=id,new_id=newId)

  # Update Template.
  ob = getattr(self,newId,None)
  if ob is not None:
    if newAcquired:
      newData = ''
    if newData is not None:
      if ob.meta_type in ['DTML Method','DTML Document']:
        ob.manage_edit(title=ob.title,data=newData)
      elif ob.meta_type == 'Page Template':
        ob.pt_edit(newData,content_type=ob.content_type)
      elif ob.meta_type == 'Script (Python)':
        ob.write(newData)

  # Return with new id.
  return newId


################################################################################
################################################################################
###
###   class MetacmdObject
###
################################################################################
################################################################################
class MetacmdObject:

    ############################################################################
    #  MetacmdObject.manage_executeMetacmd:
    #
    #  Execute Meta-Command.
    ############################################################################
    def manage_executeMetacmd(self, custom, lang, REQUEST, RESPONSE):
      """ MetacmdObject.manage_executeMetacmd """
      message = ''
      target = self
      
      # Execute.
      # --------
      for metaCmdId in self.getMetaCmdIds():
        metaCmd = self.getMetaCmd(metaCmdId)
        if metaCmd['name'] == custom:
          # Acquire from parent.
          if metaCmd.get('acquired',0) == 1:
            portalMaster = self.getPortalMaster()
            if portalMaster is not None:
              masterDtmlMthd = getattr(portalMaster,metaCmd['id'])
              ob = getattr(self,metaCmd['id'])
              if ob.meta_type in [ 'DTML Method', 'DTML Document']:
                newData = masterDtmlMthd.raw
                ob.manage_edit(title=ob.title,data=newData)
              elif ob.meta_type in [ 'Page Template']:
                newData = masterDtmlMthd.read()
                newContentType = masterDtmlMthd.content_type
                ob.pt_edit(newData,content_type=newContentType)
              elif ob.meta_type in [ 'Script (Python)']:
                newData = masterDtmlMthd.read()
                ob.ZPythonScript_setTitle( ob.title)
                ob.write(newData)
          # Execute directly.
          if metaCmd.get('exec',0) == 1:
            ob = getattr(self,metaCmd['id'],None)
            if ob.meta_type in ['DTML Method','DTML Document']:
              value = ob(self,REQUEST,RESPONSE)
            elif ob.meta_type == 'Page Template':
              value = ob()
            elif ob.meta_type == 'Script (Python)':
              value = ob()
            if type(value) is str:
              message = value
            elif type(value) is tuple:
              target = value[0]
              message = value[1]
          # Execute redirect.
          else:
            params = {'lang':REQUEST.get('lang'),'id_prefix':REQUEST.get('id_prefix'),'ids':REQUEST.get('ids',[])}
            return RESPONSE.redirect(self.url_append_params(metaCmd['id'],params,sep='&'))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s'%(target.absolute_url(),lang,message))



################################################################################
################################################################################
###
###   class MetacmdManager
###
################################################################################
################################################################################
class MetacmdManager:


    def getMetaCmdDescription(self, id=None, name=None):
      """
      Returns description of meta-command specified by ID.
      """
      return self.getMetaCmd(id,name).get('description','')


    # --------------------------------------------------------------------------
    #  MetacmdManager.getMetaCmd
    # --------------------------------------------------------------------------
    def getMetaCmd(self, id=None, name=None):
      obs = []
      for x in getRawMetacmds(self):
        # Acquire from parent.
        if x.get('acquired',0)==1:
          portalMaster = self.getPortalMaster()
          if portalMaster is not None:
            x = portalMaster.getMetaCmd(x['id']) 
            x['acquired'] = 1
        else:
          x = x.copy()
        obs.append(x)
      # Filter by Id.
      if id is not None:
        obs = filter(lambda x: x['id']==id, obs)
      # Filter by Name.
      if name is not None:
        obs = filter(lambda x: x['name']==name, obs)
      # Not found!
      if len(obs) == 0:
        return None
      ob = obs[0]
      ob['meta_type'] = getattr(self,ob['id']).meta_type
      return ob


    # --------------------------------------------------------------------------
    #  MetacmdManager.getMetaCmdIds
    #
    #  Returns list of action-Ids.
    # --------------------------------------------------------------------------
    def getMetaCmdIds(self, sort=1):
      obs = getRawMetacmds(self)
      if sort:
        obs = map(lambda x: self.getMetaCmd(x['id']), obs)
        obs = filter( lambda x: x is not None, obs)
        obs = map(lambda x: (x['name'],x), obs)
        obs.sort()
        obs = map(lambda x: x[1], obs)
      ids = map(lambda x: x['id'], obs)
      return ids


    ############################################################################
    #  MetacmdManager.manage_changeMetacmds:
    #
    #  Change Meta-Commands.
    ############################################################################
    def manage_changeMetacmds(self, btn, lang, REQUEST, RESPONSE):
        """ MetacmdManager.manage_changeMetacmds """
        message = ''
        id = REQUEST.get('id','')
        
        # Acquire.
        # --------
        if btn == self.getZMILangStr('BTN_ACQUIRE'):
          newId = REQUEST['aq_id']
          newAcquired = 1
          id = setMetacmd(self, None, newId, newAcquired)
          message = self.getZMILangStr('MSG_INSERTED')%id
        
        # Change.
        # -------
        elif btn == self.getZMILangStr('BTN_SAVE'):
          id = REQUEST['id']
          newId = REQUEST['el_id']
          newAcquired = 0
          newName = REQUEST.get('el_name','').strip()
          newMethod = None
          newData = REQUEST.get('el_data','').strip()
          newExec = REQUEST.get('el_exec',0)
          newDescription = REQUEST.get('el_description','').strip()
          newIconClazz = REQUEST.get('el_icon_clazz','')
          newMetaTypes = REQUEST.get('el_meta_types',[])
          newRoles = REQUEST.get('el_roles',[])
          newNodes = REQUEST.get('el_nodes','')
          id = setMetacmd(self, id, newId, newAcquired, newName, newMethod, \
            newData, newExec, newDescription, newIconClazz, \
            newMetaTypes, newRoles, newNodes)
          message = self.getZMILangStr('MSG_CHANGED')
        
        # Copy.
        # -----
        elif btn == self.getZMILangStr('BTN_COPY'):
          metaOb = self.getMetaCmd(id)
          if metaOb.get('acquired',0) == 1:
            portalMaster = self.getPortalMaster()
            if portalMaster is not None:
              REQUEST.set('ids',[id])
              xml =  portalMaster.manage_changeMetacmds(self.getZMILangStr('BTN_EXPORT'), lang, REQUEST, RESPONSE)
              importXml(self,xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
        
        # Delete.
        # -------
        elif btn == self.getZMILangStr('BTN_DELETE'):
          if id:
            ids = [id]
          else:
            ids = REQUEST.get('ids',[])
          for id in ids:
            delMetacmd(self,id)
          id = ''
          message = self.getZMILangStr('MSG_DELETED')%len(ids)
        
        # Export.
        # -------
        elif btn == self.getZMILangStr('BTN_EXPORT'):
          value = []
          ids = REQUEST.get('ids',[])
          for metaCmdId in self.getMetaCmdIds():
            if metaCmdId in ids or len(ids) == 0:
              metaCmd = self.getMetaCmd(metaCmdId)
              # Catalog.
              el_id = metaCmdId
              el_name = metaCmd['name']
              el_description = metaCmd['description']
              el_icon_clazz = metaCmd.get('icon_clazz','')
              el_meta_types = metaCmd['meta_types']
              el_roles = metaCmd['roles']
              el_exec = metaCmd['exec']
              # Object.
              ob = getattr(self,metaCmdId)
              el_meta_type = ob.meta_type
              if ob.meta_type in ['DTML Method','DTML Document']:
                el_data = ob.raw
              elif ob.meta_type in ['Page Template']:
                el_data = ob.read()
              elif ob.meta_type in ['Script (Python)']:
                el_data = ob.body()
              # Value.
              value.append({'id':el_id,'name':el_name,'description':el_description,'meta_types':el_meta_types,'roles':el_roles,'exec':el_exec,'icon_clazz':el_icon_clazz,'meta_type':el_meta_type,'data':el_data})
          # XML.
          if len(value)==1:
            value = value[0]
            filename = '%s.metacmd.xml'%value['id']
          else:
            filename = 'export.metacmd.xml'
          content_type = 'text/xml; charset=utf-8'
          export = self.getXmlHeader() + self.toXmlString(value,1)
          
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
          return export
        
        # Import.
        # -------
        elif btn == self.getZMILangStr('BTN_IMPORT'):
          f = REQUEST['file']
          if f:
            filename = f.filename
            importXml(self,xml=f)
          else:
            filename = REQUEST['init']
            createIfNotExists = 1
            self.importConf(filename, REQUEST, createIfNotExists)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%f.filename)
        
        # Insert.
        # -------
        elif btn == self.getZMILangStr('BTN_INSERT'):
          newId = REQUEST.get('_id').strip()
          newAcquired = 0
          newName = REQUEST.get('_name').strip()
          newMethod = REQUEST.get('_type','DTML Method')
          newData = None
          newExec = REQUEST.get('_exec',0)
          id = setMetacmd(self, None, newId, newAcquired, newName, newMethod, newData, newExec)
          message = self.getZMILangStr('MSG_INSERTED')%id
        
        # Return with message.
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_customizeMetacmdForm?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
