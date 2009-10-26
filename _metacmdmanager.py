################################################################################
# _metacmdmanager.py
#
# $Id: _metacmdmanager.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.7 $
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
from __future__ import nested_scopes
from App.special_dtml import HTMLFile
from Products.PythonScripts import PythonScript
import copy
import string
import urllib
# Product Imports.
import _globals
import _objattrs


# Example code.
# -------------

dtmlMethodExampleCode = \
  '<dtml-comment>\n' + \
  '# Example code:\n' + \
  '</dtml-comment>\n' + \
  '\n' + \
  '<dtml-call expr="REQUEST.set(\'message\',\'This is %s\'%meta_type)">\n' + \
  '<dtml-return message>\n' + \
  ''

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

def _importXml(self, item, zms_system=0, createIfNotExists=1):

  id = item['id']
  metaCmds = getRawMetacmds(self)
  metaCmds = filter(lambda x: x.get('zms_system',0)==1,metaCmds)
  ids = map(lambda x: x['id'], metaCmds)
  if createIfNotExists == 1 or id in ids:

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
    newMetaTypes = item['meta_types']
    newRoles = item['roles']
    newData = item['data']

    # Return with new id.
    return setMetacmd(self, None, newId, newAcquired, newName, newMethod, newData, newExec, newDescription, \
               newMetaTypes, newRoles, zms_system)


def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      id = _importXml(self,item,zms_system,createIfNotExists)
  else:
    id = _importXml(self,v,zms_system,createIfNotExists)


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
      newData=None, newExec=0, newDescription='', newMetaTypes=[], \
      newRoles=['ZMSAdministrator'], zms_system=0):
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
  new['meta_types'] = newMetaTypes
  new['roles'] = newRoles
  new['exec'] = newExec
  new['zms_system'] = zms_system
  obs.append(new)
  self.setConfProperty( CONF_METACMDS, obs)

  # Insert Template.
  if id is None:
    if newAcquired:
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        newMethod = getattr(portalMaster,newId).meta_type
    if newId in self.objectIds():
      self.manage_delObjects(ids=[newId])
    if newMethod == 'DTML Method':
      self.manage_addDTMLMethod(newId,'*** DO NOT DELETE OR MODIFY ***')
      if newData is None: newData = dtmlMethodExampleCode
    elif newMethod == 'DTML Document':
      self.manage_addDTMLDocument(newId,'*** DO NOT DELETE OR MODIFY ***')
      if newData is None: newData = dtmlMethodExampleCode
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
      elif ob.meta_type == 'Script (Python)':
        ob.ZPythonScript_edit(params='',body=newData)

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
              newData = masterDtmlMthd.raw
              ob = getattr(self,metaCmd['id'])
              ob.manage_edit(title=ob.title,data=newData)
          # Execute directly.
          if metaCmd.get('exec',0) == 1:
            ob = getattr(self,metaCmd['id'],None)
            if ob.meta_type in ['DTML Method','DTML Document']:
              message = ob(self,REQUEST,RESPONSE)
            elif ob.meta_type == 'Script (Python)':
              message = ob()
          # Execute redirect.
          else:
            return RESPONSE.redirect('%s?lang=%s'%(metaCmd['id'],lang))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,message))



################################################################################
################################################################################
###
###   class MetacmdManager
###
################################################################################
################################################################################
class MetacmdManager:

    # Management Interface.
    # ---------------------
    manage_customizeMetacmdForm = HTMLFile('dtml/metacmd/manage_customizeform', globals()) 


    # --------------------------------------------------------------------------
    #  MetacmdManager.getMetaCmd
    # --------------------------------------------------------------------------
    def getMetaCmd(self, id):
      obs = getRawMetacmds(self)
      obs = filter(lambda x: x['id']==id, obs)
      # Not found!
      if len(obs) == 0:
        return None
      ob = obs[0].copy()
      # Acquire from parent.
      if ob.get('acquired',0)==1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          ob = portalMaster.getMetaCmd(id)
          ob['acquired'] = 1
      ob['meta_type'] = getattr(self,id).meta_type
      return ob


    # --------------------------------------------------------------------------
    #  MetacmdManager.getMetaCmdIds
    #
    #  Returns list of action-Ids.
    # --------------------------------------------------------------------------
    def getMetaCmdIds(self, sort=1):
      obs = getRawMetacmds(self)
      if sort:
        obs = map(lambda x: (self.getMetaCmd(x['id'])['name'],x), obs)
        obs.sort()
        obs = map(lambda x: x[1],obs)
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
          newMetaTypes = REQUEST.get('el_meta_types',[])
          newRoles = REQUEST.get('el_roles',[])
          id = setMetacmd(self, id, newId, newAcquired, newName, newMethod, newData, newExec, newDescription, \
            newMetaTypes, newRoles)
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
          id = delMetacmd(self,id)
          message = self.getZMILangStr('MSG_DELETED')%int(1)
        
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
              el_meta_types = metaCmd['meta_types']
              el_roles = metaCmd['roles']
              el_exec = metaCmd['exec']
              # Object.
              ob = getattr(self,metaCmdId)
              el_meta_type = ob.meta_type
              if ob.meta_type in ['DTML Method','DTML Document']:
                el_data = ob.raw
              else:
                el_data = ob.body()
              # Value.
              value.append({'id':el_id,'name':el_name,'description':el_description,'meta_types':el_meta_types,'roles':el_roles,'exec':el_exec,'meta_type':el_meta_type,'data':el_data})
          # XML.
          if len(value)==1:
            value = value[0]
            filename = '%s.metacmd.xml'%ids[0]
          else:
            filename = 'export.metacmd.xml'
          content_type = 'text/xml; charset=utf-8'
          export = self.getXmlHeader() + self.toXmlString(value,1)
          
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
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
