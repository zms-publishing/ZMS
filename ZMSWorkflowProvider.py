################################################################################
# ZMSWorkflowProvider.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import time
import urllib
import zope.interface
# Product Imports.
import IZMSConfigurationProvider
import IZMSWorkflowProvider, ZMSWorkflowActivitiesManager, ZMSWorkflowTransitionsManager
import ZMSItem
import _accessmanager
import _fileutil


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ZMSWorkflowProvider.doAutocommit:
Commit pending changes of all objects.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def doAutocommit(self, REQUEST): 
  
  ##### Auto-Commit ####
  if len( self.getObjStates()) > 0:
    
    if self.inObjStates(['STATE_DELETED'],REQUEST):
       parent = self.getParentNode()
       parent.moveObjsToTrashcan([self.id], REQUEST)
       return
    
    if self.version_work_id is not None:
      if self.version_live_id is not None and \
         self.version_live_id in self.objectIds( self.dGlobalAttrs.keys()):
        ids = [ self.version_live_id]
        self.manage_delObjects( ids=ids)
      self.version_live_id = self.version_work_id
      self.version_work_id = None
    self.initializeWorkVersion()
  
  ##### Process child-objects ####
  for ob in self.getChildNodes():
    doAutocommit( ob, REQUEST)


"""
################################################################################
#
#   XML IM/EXPORT
#
################################################################################
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ZMSWorkflowProvider.exportXml
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def exportXml(self, REQUEST, RESPONSE):
  value = {}
  value['activities'] = []
  for x in self.getActivityIds():
      value['activities'].extend([x,self.getActivity(x,for_export=True)])
  value['transitions'] = []
  for x in self.getTransitionIds():
      value['transitions'].extend([x,self.getTransition(x,for_export=True)])
  export = self.getXmlHeader() + self.toXmlString(value,1)
  content_type = 'text/xml; charset=utf-8'
  filename = 'workflow.xml'
  RESPONSE.setHeader('Content-Type',content_type)
  RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
  return export


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSWorkflowProvider(
        ZMSItem.ZMSItem,
        ZMSWorkflowActivitiesManager.ZMSWorkflowActivitiesManager,
        ZMSWorkflowTransitionsManager.ZMSWorkflowTransitionsManager):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSWorkflowProvider.IZMSWorkflowProvider)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    meta_type = 'ZMSWorkflowProvider'
    icon = "++resource++zms_/img/ZMSWorkflowProvider.png"
    icon_clazz = "icon-random"

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Options
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'TAB_WORKFLOW','action': 'manage_main'},
        )

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Interface
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main',globals())
    manage_main = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main',globals())

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Permissions
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    __administratorPermissions__ = (
        'manage_main',
        'manage_changeWorkflow',
        'manage_changeActivities',
        'manage_changeTransitions',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.__init__: 
    
    Constructor.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self, autocommit=1, nodes=['{$}'], activities=[], transitions=[]):
      self.id = 'workflow_manager'
      self.autocommit = autocommit
      self.nodes = nodes
      self.activities = []
      self.transitions = []
      l = activities
      for li in range(len(l)/2):
        id = l[li*2]
        i = l[li*2+1]
        self.setActivity(id=None,newId=id,newName=i['name'],newIcon=i.get('icon'))
      l = transitions
      for li in range(len(l)/2):
        id = l[li*2]
        i = l[li*2+1]
        newDtml = i.get('dtml','')
        newType = i.get('type',['','DTML Method'][int(len(dtml)>0)])
        self.setTransition(id=None,newId=id,newName=i['name'],newType=newType,newFrom=i.get('from',[]),newTo=i.get('to',[]),newPerformer=i.get('performer',[]),newDtml=newDtml)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.importXml
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def importXml(self, xml, createIfNotExists=1):
      ids = map(lambda x: self.activities[x*2], range(len(self.activities)/2))
      for id in ids:
        self.delItem(id,'activities')
      ids = map(lambda x: self.transitions[x*2], range(len(self.transitions)/2))
      for id in ids:
        self.delItem(id,'transitions')
      v = self.parseXmlString(xml)
      l = v.get('activities',[])
      for li in range(len(l)/2):
        id = l[li*2]
        i = l[li*2+1]
        self.setActivity(id=None,newId=id,newName=i['name'],newIconClazz=i.get('icon_clazz',''),newIcon=i.get('icon'))
      l = v.get('transitions',[])
      for li in range(len(l)/2):
        id = l[li*2]
        i = l[li*2+1]
        newDtml = i.get('dtml','')
        newType = i.get('type',['','DTML Method'][int(len(newDtml)>0)])
        self.setTransition(id=None,newId=id,newName=i['name'],newType=newType,newFrom=i.get('from',[]),newTo=i.get('to',[]),newPerformer=i.get('performer',[]),newDtml=newDtml)
      # Create non existant roles.
      roles = []
      for transition in self.getTransitions():
        roles = self.concat_list(roles,transition.get('performer',[]))
      for newRole in filter(lambda x: x not in self.userdefined_roles(),roles):
        _accessmanager.addRole(self,newRole)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.getAutocommit
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getAutocommit(self):
      return self.autocommit


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.getNodes
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getNodes(self):
      return self.nodes


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.delItem
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def delItem(self, id, key):
      obs = getattr(self,key,[])
      # Update attribute.
      if id in obs:
        i = obs.index(id)
        ob = obs[i+1]
        for obj_id in [id,'%s.icon'%id]:
          if obj_id in self.objectIds():
            self.manage_delObjects([obj_id])
        del obs[i] 
        del obs[i] 
      # Update attribute.
      setattr(self,key,copy.copy(obs))
      # Return with empty id.
      return ''


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.moveItem
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def moveItem(self, id, pos, key):
      obs = getattr(self,key,[])
      # Move.
      i = obs.index(id)
      id = obs[i] 
      values = obs[i+1]
      del obs[i] 
      del obs[i] 
      obs.insert(pos*2,values)
      obs.insert(pos*2,id)
      # Update attribute.
      setattr(self,key,copy.copy(obs))


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.doAutocommit:
    
    Auto-Commit ZMS-tree.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def doAutocommit(self, lang, REQUEST):
      doAutocommit(self,REQUEST)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.writeProtocol
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def writeProtocol(self, entry):
      if len(filter(lambda x: x.id()=='protocol.txt', self.objectValues(['File'])))==0:
        self.manage_addFile(id='protocol.txt',file='',title='')
      file = filter(lambda x: x.id()=='protocol.txt', self.objectValues(['File']))[0]
      file.manage_edit(file.title,file.data+'\n'+entry)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProvider.manage_changeWorkflow:
    
    Chang workflow.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def manage_changeWorkflow(self, lang, key='', btn='', REQUEST=None, RESPONSE=None):
      """ ZMSWorkflowProvider.manage_changeWorkflow """
      message = ''
      
      # Active.
      # -------
      if key == 'custom' and btn == self.getZMILangStr('BTN_SAVE'):
        # Autocommit & Nodes.
        old_autocommit = self.autocommit
        new_autocommit = REQUEST.get('workflow',0) == 0
        self.autocommit = new_autocommit
        self.nodes = self.string_list(REQUEST.get('nodes',''))
        if old_autocommit == 0 and new_autocommit == 1:
          self.doAutocommit(lang,REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Clear.
      # ------
      elif key == 'clear' and btn == self.getZMILangStr('BTN_CLEAR'):
        self.doAutocommit(lang,REQUEST)
        self.autocommit = 1
        self.activities = []
        self.transitions = []
        message = self.getZMILangStr('MSG_CHANGED')
     
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
          xml = f
        else:
          filename = REQUEST.get('init')
          xml = open(_fileutil.getOSPath(filename),'rb')
        self.importXml(xml)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#_%s'%(lang,message,key))

################################################################################
