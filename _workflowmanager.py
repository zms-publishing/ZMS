################################################################################
# _workflowmanager.py
#
# $Id: _workflowmanager.py,v 1.8 2004/11/23 23:26:37 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.8 $
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
from App.Common import package_home
from Globals import HTMLFile
import ZPublisher.HTTPRequest
import copy
import time
import urllib
# Product Imports.
import _blobfields
import _fileutil
import _globals
import _versionmanager


"""
################################################################################
#
#   K E Y S
#
################################################################################
"""

CONF_TRANSITIONS	= "ZMS.workflow.transitions"
CONF_ACTIVITIES		= "ZMS.workflow.activities"
CONF_PROTOCOL		= "ZMS.workflow.protocol"
CONF_PROTOCOL_KEEP	= "ZMS.workflow.protocol.keep_entries"
CONF_AUTOCOMMIT		= "ZMS.autocommit"
CONF_ACQUIRE		= "ZMS.workflow.acquire"
CONF_INIT		= "ZMS.workflow.init"
CONF_CHANGE_DT		= "ZMS.workflow.change_dt"
CONF_CHANGE_UID		= "ZMS.workflow.change_uid"


"""
################################################################################
#
#   X M L   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _workflowmanager.initConf:
# ------------------------------------------------------------------------------
def initConf(self, filename, REQUEST):
  xmlfile = open(_fileutil.getOSPath(filename),'rb')
  importXml(self, xmlfile, REQUEST)
  # Return filename.
  return filename

# ------------------------------------------------------------------------------
#  _workflowmanager.importXml
# ------------------------------------------------------------------------------
def importXml(self, xml, REQUEST):
  v = self.parseXmlString(xml)
  self.setConfProperty(CONF_CHANGE_DT, v.get('change_dt',_globals.getDateTime(time.time())))
  self.setConfProperty(CONF_CHANGE_UID, v.get('change_uid',REQUEST.get('AUTHENTICATED_USER',None)))
  self.setConfProperty(CONF_ACTIVITIES, v.get('activities',[]))
  self.setConfProperty(CONF_TRANSITIONS, v.get('transitions',[]))
  # Roles.
  wfRoles = []
  for wfTransition in self.getWfTransitions():
    wfRoles = self.concat_list(wfRoles,wfTransition.get('performer',[]))
  for newRole in self.difference_list(wfRoles, self.userdefined_roles()):
    REQUEST.set('newId', newRole)
    lang = REQUEST.get('lang')
    key = 'obj'
    btn = self.getZMILangStr('BTN_INSERT')
    self.manage_roleProperties(btn, key, lang, REQUEST)

# ------------------------------------------------------------------------------
#   _workflowmanager.exportXml
# ------------------------------------------------------------------------------
def exportXml(self, REQUEST, RESPONSE):
  value = {}
  value['change_dt'] = self.getConfProperty(CONF_CHANGE_DT,None)
  value['change_uid'] = self.getConfProperty(CONF_CHANGE_UID,None)
  value['activities'] = self.getConfProperty(CONF_ACTIVITIES,[])
  value['transitions'] = self.getConfProperty(CONF_TRANSITIONS,[])
  export = self.getXmlHeader() + self.toXmlString(value,1)
  content_type = 'text/xml; charset=utf-8'
  filename = 'workflow.xml'
  RESPONSE.setHeader('Content-Type',content_type)
  RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
  return export

"""
################################################################################
#
#   T R A N S I T I O N S
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _workflowmanager.setWfTransition
# ------------------------------------------------------------------------------
def setWfTransition(self, id, newId, newName, newFrom, newTo, newPerformer=[], newDtml=''):
  message = ''
  obs = self.getConfProperty(CONF_TRANSITIONS,[])
  # Remove exisiting entry.
  if id in obs:
    i = obs.index(id)
    del obs[i] 
    del obs[i] 
  else: 
    i = len(obs)
  if len(newTo) == 0:
    newTo = []
  else:
    newTo = [newTo]
  # Parse Dtml.
  message = _globals.dt_parse(self,newDtml)
  if len( message) > 0:
    message = '<div style="color:red; background-color:yellow; ">%s</div>'%message
  # Values.
  newValues = {}
  newValues['name'] = newName
  newValues['from'] = newFrom
  newValues['to'] = newTo
  newValues['performer'] = newPerformer
  newValues['dtml'] = newDtml
  # Update attribute.
  obs.insert(i,newValues)
  obs.insert(i,newId)
  self.setConfProperty(CONF_TRANSITIONS,copy.copy(obs))
  # Return with message.
  return message


"""
################################################################################
#
#   A C T I V I T I E S
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _workflowmanager.setWfActivity
# ------------------------------------------------------------------------------
def setWfActivity(self, id, newId, newName, newIcon=None):
  obs = self.getConfProperty(CONF_ACTIVITIES,[])
  # Remove exisiting entry.
  if id in obs:
    i = obs.index(id)
    del obs[i] 
    del obs[i] 
  else: 
    i = len(obs)
  # Values.
  newValues = {}
  newValues['name'] = newName
  newValues['icon'] = newIcon
  # Update attribute.
  obs.insert(i,newValues)
  obs.insert(i,newId)
  self.setConfProperty(CONF_ACTIVITIES,copy.copy(obs))
  # Return with new id.
  return newId


"""
################################################################################
#
#   I T E M
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _workflowmanager.delWfItem
# ------------------------------------------------------------------------------
def delWfItem(self, id, conf_key):
  obs = self.getConfProperty(conf_key,[])
  # Update attribute.
  if id in obs:
    i = obs.index(id)
    del obs[i] 
    del obs[i] 
  self.setConfProperty(conf_key,copy.copy(obs))
  # Return with empty id.
  return ''

# ------------------------------------------------------------------------------
#  _workflowmanager.moveWfItem
# ------------------------------------------------------------------------------
def moveWfItem(self, id, pos, conf_key):
  obs = self.getConfProperty(conf_key,[])
  # Move.
  i = obs.index(id)
  id = obs[i] 
  values = obs[i+1]
  del obs[i] 
  del obs[i] 
  obs.insert(pos*2,values)
  obs.insert(pos*2,id)
  # Update attribute.
  self.setConfProperty(conf_key,copy.copy(obs))


"""
################################################################################
#
#   P R O T O C O L
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _workflowmanager.writeProtocol
# ------------------------------------------------------------------------------
def writeProtocol(self, entry):
  keep_entries = self.getConfProperty(CONF_PROTOCOL_KEEP,0)
  if keep_entries > 0:
    log = self.getConfProperty(CONF_PROTOCOL,[])
    while len(log) > keep_entries:
      log.remove(log[-1])
    log.insert(0,entry)
    self.setConfProperty(CONF_PROTOCOL,log)

# ------------------------------------------------------------------------------
#  _workflowmanager.readProtocol
# ------------------------------------------------------------------------------
def readProtocol(self):
  log = ''
  for entry in self.getConfProperty(CONF_PROTOCOL,[]):
    log += entry + '\n'
  return log


################################################################################
################################################################################
###
###   class WorkflowItem
###
################################################################################
################################################################################
class WorkflowItem: 

    # --------------------------------------------------------------------------
    #  WorkflowItem.getAutocommit
    #
    #  Returns true if auto-commit is active (workflow is inactive), false otherwise.
    # --------------------------------------------------------------------------
    def getAutocommit(self): 
      autocommit = False
      if not autocommit:
        autocommit = autocommit or self.getConfProperty('ZMS.autocommit',1)==1
      if not autocommit:
        baseurl = self.getDocumentElement().absolute_url()
        url = self.absolute_url()
        if len( url) > len( baseurl):
          url = url[ len( baseurl)+1:]
        url = '$'+url
        found = False
        nodes = self.getConfProperty('ZMS.workflow.nodes',['{$}'])
        for node in nodes:
          if url.find(node[1:-1]) == 0:
            found = True
            break
        autocommit = autocommit or not found
      return autocommit


    # --------------------------------------------------------------------------
    #  WorkflowItem.filtered_workflow_actions:
    # --------------------------------------------------------------------------
    def filtered_workflow_actions(self, path=''):
      actions = []
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Workflow.
      if not self.getAutocommit() and self.isVersionContainer():
        wfStates = self.getWfStates(REQUEST)
        wfTransitions = self.getWfTransitions()
        roles = self.getUserRoles(auth_user)
        for wfTransition in wfTransitions:
          wfFrom = wfTransition.get('from',[])
          wfPerformer = wfTransition.get('performer',[])
          wfTo = wfTransition.get('to',[])
          append = False
          append = append or ((wfFrom is None or len(wfFrom) == 0) and len(wfTo) == 0)
          append = append or (len(self.intersection_list(wfStates,wfFrom)) > 0 and len(wfTo) > 0)
          append = append and (len(self.intersection_list(roles,wfPerformer)) > 0 or auth_user.has_permission('Manager',self))
          if append:
            actions.append((wfTransition['name'],path+'manage_wfTransition'))
      
      #-- Headline,
      if len( actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('TAB_WORKFLOW'),''))
      
      # Return action list.
      return actions


################################################################################
################################################################################
###
###   class WorkflowManager
###
################################################################################
################################################################################
class WorkflowManager: 

    # Management Interface.
    # ---------------------
    manage_customizeWorkflowForm = HTMLFile('dtml/ZMS/manage_customizeworkflowform', globals())


    # --------------------------------------------------------------------------
    #  WorkflowManager.doAutocommit:
    #
    #  Auto-Commit ZMS-tree.
    # --------------------------------------------------------------------------
    def doAutocommit(self, lang, REQUEST):
      _versionmanager.doAutocommit(self,REQUEST)


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfTransitions
    # --------------------------------------------------------------------------
    def getWfTransitions(self):
      acquired = self.getConfProperty(CONF_ACQUIRE,0)
      if acquired:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          wfTransitions = portalMaster.getWfTransitions()
      else:
        obs = self.getConfProperty(CONF_TRANSITIONS,[])
        wfTransitions = []
        for i in range(len(obs)/2):
          id = obs[i*2]
          wfTransition = obs[i*2+1].copy()
          wfTransition['id'] = id
          wfTransitions.append(wfTransition)
      return wfTransitions


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfTransitionsIds
    # --------------------------------------------------------------------------
    def getWfTransitionsIds(self):
      obs = self.getWfTransitions()
      return map(lambda x: x['id'], obs) 


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfTransition
    # --------------------------------------------------------------------------
    def getWfTransition(self, id):
      ob = filter(lambda x: x['id']==id, self.getWfTransitions())[0]
      return ob


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfActivities
    # --------------------------------------------------------------------------
    def getWfActivities(self): 
      acquired = self.getConfProperty(CONF_ACQUIRE,0)
      if acquired:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          workflowItms = portalMaster.getWfActivities()
      else:
        obs = self.getConfProperty(CONF_ACTIVITIES,[])
        workflowItms = []
        for i in range(len(obs)/2):
          id = obs[i*2]
          workflowItm = obs[i*2+1].copy()
          workflowItm['id'] = id
          workflowItms.append(workflowItm)
      return workflowItms


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfActivitiesIds
    # --------------------------------------------------------------------------
    def getWfActivitiesIds(self):
      obs = self.getWfActivities()
      return map(lambda x: x['id'], obs) 


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfActivity
    # --------------------------------------------------------------------------
    def getWfActivity(self, id):
      ob = filter(lambda x: x['id']==id, self.getWfActivities())[0]
      return ob


    # --------------------------------------------------------------------------
    #  WorkflowManager.getWfActivityDetails
    # --------------------------------------------------------------------------
    def getWfActivityDetails(self, id):
      ids = self.getWfActivitiesIds()
      froms = []
      tos = []
      for wfTransition in self.getWfTransitions():
        if wfTransition['to'] is not None and len(wfTransition['to']) > 0 and id in wfTransition['to']:
          for ac_id in wfTransition['from']:
            if ac_id in ids:
              idx = ids.index(ac_id)
              if idx not in froms:
                froms.append(idx)
        if wfTransition['from'] is not None and len(wfTransition['from']) > 0 and id in wfTransition['from']:
          for ac_id in wfTransition['to']:
            if ac_id in ids:
              idx = ids.index(ac_id)
              if idx not in tos:
                tos.append(idx)
      froms.sort()
      tos.sort()
      idxs = self.concat_list(froms,tos)
      idx = ids.index(id)
      return {'froms':froms, 'tos': tos, 'idxs': idxs, 'idx': idx}


    ############################################################################
    #  WorkflowManager.manage_changeWorkflow:
    #
    #  Customize workflow.
    ############################################################################
    def manage_changeWorkflow(self, lang, key='', btn='', REQUEST=None, RESPONSE=None):
      """ WorkflowManager.manage_changeWorkflow """
      message = ''
      
      # Active.
      # -------
      if key == 'custom' and btn == self.getZMILangStr('BTN_SAVE'):
        # Autocommit & Nodes.
        old_autocommit = self.getConfProperty('ZMS.autocommit',1)
        new_autocommit = REQUEST.get('workflow',0) == 0
        self.setConfProperty('ZMS.autocommit',new_autocommit)
        self.setConfProperty('ZMS.workflow.nodes',self.string_list(REQUEST.get('nodes','')))
        if old_autocommit == 0 and new_autocommit == 1:
          self.doAutocommit(lang,REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
        # Acquire.
        newAcquire = REQUEST.get('acquire',0) == 1
        self.setConfProperty(CONF_ACQUIRE,newAcquire)
        message = self.getZMILangStr('MSG_CHANGED')
        # Init.
        filename = REQUEST.get('filename','')
        self.setConfProperty(CONF_INIT,filename)
      
      # Protocol.
      # ---------
      elif key == 'protocol':
        # Change.
        if btn == self.getZMILangStr('BTN_SAVE'):
          keep_entries = REQUEST.get('keep_entries',0)
          self.setConfProperty(CONF_PROTOCOL_KEEP,keep_entries)
          if keep_entries == 0:
            self.setConfProperty(CONF_PROTOCOL,[])
          message = self.getZMILangStr('MSG_CHANGED')
        # Export.
        elif btn == self.getZMILangStr('BTN_EXPORT'):
          export = readProtocol(self)
          content_type = 'text/plain'
          filename = 'workFlow.protocol.log'
          RESPONSE.setHeader('Content-Type',content_type)
          RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
          return export
      
      # Export.
      # -------
      elif key == 'export' and btn == self.getZMILangStr('BTN_EXPORT'):
        return exportXml(self, REQUEST, RESPONSE)
      
      # Import.
      # -------
      elif key == 'import' and btn == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        if f:
          filename = f.filename
          importXml(self, xml=f, REQUEST=REQUEST)
        else:
          filename = REQUEST.get('init')
          self.setConfProperty(CONF_INIT,filename)
          filename = initConf(self, filename, REQUEST)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%f.filename)
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeWorkflowForm?lang=%s&manage_tabs_message=%s#_%s'%(lang,message,key))


    ############################################################################
    #  WorkflowManager.manage_changeWfActivities:
    #
    #  Customize workflow-activities.
    ############################################################################
    def manage_changeWfActivities(self, lang, btn='', REQUEST=None, RESPONSE=None):
      """ WorkflowManager.manage_changeWfActivities """
      message = ''
      id = REQUEST.get('id','')
      self.setConfProperty(CONF_CHANGE_DT,_globals.getDateTime(time.time()))
      self.setConfProperty(CONF_CHANGE_UID,REQUEST.get('AUTHENTICATED_USER',None))
      
      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_SAVE'):
        item = self.getWfActivity(id)
        newId = REQUEST.get('inpId').strip()
        newName = REQUEST.get('inpName').strip()
        newIcon = REQUEST.get('inpIcon','')
        if isinstance(newIcon,ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(newIcon,'filename',''))==0:
            newIcon = item.get('icon',None)
          else:
            newIcon = _blobfields.createBlobField(self,_globals.DT_IMAGE,newIcon)
        id = setWfActivity(self, item.get('id',None), newId, newName, newIcon)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn in ['delete',self.getZMILangStr('BTN_DELETE')]:
        id = delWfItem(self, id, CONF_ACTIVITIES)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        item = {}
        newId = REQUEST.get('newId').strip()
        newName = REQUEST.get('newName').strip()
        newIcon = REQUEST.get('newIcon','')
        if isinstance(newIcon,ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(newIcon,'filename',''))==0:
            newIcon = item.get('icon',None)
          else:
            newIcon = _blobfields.createBlobField(self,_globals.DT_IMAGE,newIcon)
        id = setWfActivity(self, item.get('id',None), newId, newName, newIcon)
        message = self.getZMILangStr('MSG_INSERTED')%id
      
      # Move to.
      # --------
      elif btn == 'move_to':
        pos = REQUEST['pos']
        moveWfItem(self, id, pos, CONF_ACTIVITIES)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%id),(pos+1))
        id = ''
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeWorkflowForm?lang=%s&manage_tabs_message=%s#_Activities'%(lang,message))


    ############################################################################
    #  WorkflowManager.manage_changeWfTransitions:
    #
    #  Customize workflow-transitions.
    ############################################################################
    def manage_changeWfTransitions(self, lang, btn='', REQUEST=None, RESPONSE=None):
      """ WorkflowManager.manage_changeWfTransitions """
      message = ''
      id = REQUEST.get('id','')
      self.setConfProperty(CONF_CHANGE_DT,_globals.getDateTime(time.time()))
      self.setConfProperty(CONF_CHANGE_UID,REQUEST.get('AUTHENTICATED_USER',None))
      
      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_SAVE'):
        item = self.getWfTransition(id)
        newId = REQUEST.get('inpId').strip()
        newName = REQUEST.get('inpName').strip()
        newFrom = REQUEST.get('inpFrom')
        newTo = REQUEST.get('inpTo')
        newPerformer = REQUEST.get('inpPerformer',[])
        newDtml = REQUEST.get('inpDtml','').strip()
        message += setWfTransition(self, item.get('id',None), newId, newName, newFrom, newTo, newPerformer, newDtml)
        message += self.getZMILangStr('MSG_CHANGED')
        id = newId
      
      # Delete.
      # -------
      elif btn in ['delete',self.getZMILangStr('BTN_DELETE')]:
        id = delWfItem(self, id, CONF_TRANSITIONS)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        item = {}
        newId = REQUEST.get('newId').strip()
        newName = REQUEST.get('newName').strip()
        newFrom = REQUEST.get('newFrom',[])
        newTo = REQUEST.get('newTo',[])
        newPerformer = REQUEST.get('newPerformer',[])
        newDtml = REQUEST.get('newDtml','').strip()
        message += setWfTransition(self, item.get('id',None), newId, newName, newFrom, newTo, newPerformer, newDtml)
        message += self.getZMILangStr('MSG_INSERTED')%id
        id = newId
      
      # Move to.
      # --------
      elif btn == 'move_to':
        pos = REQUEST['pos']
        moveWfItem(self, id, pos, CONF_TRANSITIONS)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%id),(pos+1))
        id = ''
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeWorkflowForm?id=%s&lang=%s&manage_tabs_message=%s#_Transitions'%(id,lang,message))

################################################################################
