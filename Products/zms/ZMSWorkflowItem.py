"""
ZMSWorkflowItem.py

ZMS support for zmsworkflow item.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Product Imports.
from Products.zms import standard


class ZMSWorkflowItem(object): 

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSWorkflowItem.getAutocommit
    
    Returns true if auto-commit is active (workflow is inactive), false otherwise.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def getAutocommit(self):
      workflow_manager = self.getWorkflowManager()
      if not workflow_manager.getAutocommit():
        #-- [ReqBuff]: Fetch buffered value from Http-Request.
        nodes = []
        reqBuffId = 'ZMSWorkflowManager.getNodes'
        try: nodes = self.fetchReqBuff(reqBuffId)
        except:
          for node in workflow_manager.getNodes():
            ob = self.getLinkObj(node)
            if ob is not None:
              nodes.append(ob.getPhysicalPath())
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        self.storeReqBuff( reqBuffId, nodes)
        # Test nodes.
        phys_path = self.getPhysicalPath()
        for node in nodes:
          if len(node) <= len(phys_path) and phys_path[:len(node)] == node:
            return False
      return True


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
          wfFrom = transition.get('from', [])
          wfPerformer = transition.get('performer', [])
          wfTo = transition.get('to', [])
          append = False
          append = append or ((wfFrom is None or len(wfFrom) == 0) and len(wfTo) == 0)
          append = append or (len(standard.intersection_list(wfStates, wfFrom)) > 0 and len(wfTo) > 0)
          append = append and (len(standard.intersection_list(roles, wfPerformer)) > 0 or auth_user.has_permission('Manager', self))
          if append:
            actions.append((transition['name'], path+'manage_wfTransition', transition.get('icon_clazz', 'fas fa-square')))
      
      #-- Headline,
      if len( actions) > 0:
        actions.insert(0, ('----- %s -----'%self.getZMILangStr('TAB_WORKFLOW'), 'workflow-action'))
      
      # Return action list.
      return actions

################################################################################