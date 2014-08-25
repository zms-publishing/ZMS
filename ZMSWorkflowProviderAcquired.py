################################################################################
# ZMSWorkflowProviderAcquired.py
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
import urllib
import zope.interface
# Product Imports.
import IZMSConfigurationProvider
import IZMSWorkflowProvider, ZMSWorkflowProvider
import ZMSItem


class ZMSWorkflowProviderAcquired(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSWorkflowProvider.IZMSWorkflowProvider)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    meta_type = 'ZMSWorkflowProviderAcquired'
    icon = "misc_/zms/ZMSWorkflowProvider.png"

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
    manage = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main_acquired',globals())
    manage_main = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main_acquired',globals())


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.__init__: 
    
    Constructor.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self, autocommit=1, nodes=['{$}']):
      self.id = 'workflow_manager'
      self.autocommit = autocommit
      self.nodes = nodes


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.getAutocommit
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getAutocommit(self):
      return getattr(self,'autocommit',1)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.getNodes
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getNodes(self):
      return getattr(self,'nodes',['{$}'])


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.doAutocommit:
    
    Auto-Commit ZMS-tree.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def doAutocommit(self, lang, REQUEST):
      ZMSWorkflowProvider.doAutocommit(self,REQUEST)


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.writeProtocol
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def writeProtocol(self, entry):
      self.getPortalMaster().workflow_manager.writeProtocol(entry)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActivities()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivities(self):
      return self.getPortalMaster().workflow_manager.getActivities()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActitiesIds()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivityIds(self):
      return self.getPortalMaster().workflow_manager.getActivityIds()
  
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActivity()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivity(self, id):
      return self.getPortalMaster().workflow_manager.getActivity(id)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getActivityDetails()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getActivityDetails(self, id):
      return self.getPortalMaster().workflow_manager.getActivityDetails(id)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getTransitions()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getTransitions(self):
      return self.getPortalMaster().workflow_manager.getTransitions()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getTransitionIds()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getTransitionIds(self):
      return self.getPortalMaster().workflow_manager.getTransitionIds()

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @see IZMSWorkflowProvider.getTransition()
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getTransition(self, id, for_export=False):
      return self.getPortalMaster().workflow_manager.getTransition(id,for_export)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowProviderAcquired.manage_changeWorkflow:
    
    Chang workflow.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def manage_changeWorkflow(self, lang, key='', btn='', REQUEST=None, RESPONSE=None):
      """ ZMSWorkflowProvider.manage_changeWorkflow """
      message = ''
      
      # Active.
      # -------
      if key == 'custom' and btn == self.getZMILangStr('BTN_SAVE'):
        # Autocommit & Nodes.
        old_autocommit = getattr(self,'autocommit',1)
        new_autocommit = REQUEST.get('workflow',0) == 0
        self.autocommit = new_autocommit
        self.nodes = self.string_list(REQUEST.get('nodes',''))
        if old_autocommit == 0 and new_autocommit == 1:
          self.doAutocommit(lang,REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#_%s'%(lang,message,key))

################################################################################