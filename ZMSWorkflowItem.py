################################################################################
# _workflowmanager.py
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


class ZMSWorkflowItem: 

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowItem.getAutocommit
    
    Returns true if auto-commit is active (workflow is inactive), false otherwise.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getAutocommit(self):
      workflow_manager = self.getWorkflowManager()
      autocommit = workflow_manager.getAutocommit()
      if not autocommit:
        baseurl = self.getDocumentElement().absolute_url()
        url = self.absolute_url()
        if len( url) > len( baseurl):
          url = url[ len( baseurl)+1:]
        url = '$'+url
        found = False
        nodes = workflow_manager.getNodes()
        for node in nodes:
          if url.find(node[1:-1]) == 0:
            found = True
            break
        autocommit = autocommit or not found
      return autocommit


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowItem.filtered_workflow_actions:
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def filtered_workflow_actions(self, path=''):
      actions = []
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Workflow.
      if not self.getAutocommit() and self.isVersionContainer():
        wfStates = self.getWfStates(REQUEST)
        transitions = self.getWorkflowManager().getTransitions()
        roles = self.getUserRoles(auth_user)
        for transition in transitions:
          wfFrom = transition.get('from',[])
          wfPerformer = transition.get('performer',[])
          wfTo = transition.get('to',[])
          append = False
          append = append or ((wfFrom is None or len(wfFrom) == 0) and len(wfTo) == 0)
          append = append or (len(self.intersection_list(wfStates,wfFrom)) > 0 and len(wfTo) > 0)
          append = append and (len(self.intersection_list(roles,wfPerformer)) > 0 or auth_user.has_permission('Manager',self))
          if append:
            actions.append((transition['name'],path+'manage_wfTransition','icon-check-empty'))
      
      #-- Headline,
      if len( actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('TAB_WORKFLOW'),'workflow-action'))
      
      # Return action list.
      return actions

################################################################################
