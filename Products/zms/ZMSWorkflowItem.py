"""
ZMSWorkflowItem.py - ZMS Workflow Item

Defines ZMSWorkflowItem for workflow state machines and activity processing.
It manages activity definitions, transitions, permission checks, and state lifecycle events.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
from Products.zms import standard


class ZMSWorkflowItem(object):

    def getAutocommit(self):
      """
      Return whether this object should bypass workflow transitions.

      The method disables auto-commit for objects located below configured
      workflow nodes and caches resolved node paths in the request buffer.
      """
      workflow_manager = self.getWorkflowManager()
      if not workflow_manager.getAutocommit():
        nodes = []
        reqBuffId = 'ZMSWorkflowManager.getNodes'
        try:
          nodes = self.fetchReqBuff(reqBuffId)
        except:
          for node in workflow_manager.getNodes():
            ob = self.getLinkObj(node)
            if ob is not None:
              nodes.append(ob.getPhysicalPath())
        self.storeReqBuff(reqBuffId, nodes)
        phys_path = self.getPhysicalPath()
        for node in nodes:
          if len(node) <= len(phys_path) and phys_path[:len(node)] == node:
            return False
      return True


    def filtered_workflow_actions(self, path=''):
      """
      Build the list of workflow transition actions visible to the user.

      @param path: Optional URL prefix for generated action links.
      @type path: C{str}
      @return: Workflow actions ready for rendering in the ZMI.
      @rtype: C{list}
      """
      actions = []
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']

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
            actions.append((transition['name'], path + 'manage_wfTransition', transition.get('icon_clazz', 'fas fa-square')))

      if len(actions) > 0:
        actions.insert(0, ('----- %s -----' % self.getZMILangStr('TAB_WORKFLOW'), 'workflow-action'))

      return actions
