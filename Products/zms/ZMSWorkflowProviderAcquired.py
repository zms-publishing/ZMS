"""
ZMSWorkflowProviderAcquired.py

Defines ZMSWorkflowProviderAcquired for workflow state machines and activity processing.
It manages activity definitions, transitions, permission checks, and state lifecycle events.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
from zope.interface import implementer
# Product Imports.
from Products.zms import standard
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSWorkflowProvider, ZMSWorkflowProvider
from Products.zms import ZMSItem


@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSWorkflowProvider.IZMSWorkflowProvider)
class ZMSWorkflowProviderAcquired(
        ZMSItem.ZMSItem):

    """Delegate workflow settings and definitions to the portal master."""

    meta_type = 'ZMSWorkflowProviderAcquired'
    zmi_icon = "fas fa-random acquired"
    icon_clazz = zmi_icon

    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      """Return parent management tabs with local relative actions."""
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      """Return the workflow manager sub tabs shown in the ZMI."""
      return (
        {'label': 'TAB_WORKFLOW','action': 'manage_main'},
        )

    manage = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main_acquired', globals())
    manage_main = PageTemplateFile('zpt/ZMSWorkflowProvider/manage_main_acquired', globals())

    def __init__(self, autocommit=1, nodes=['{$}']):
      """Initialize the acquired workflow manager stub.

      @param autocommit: Flag controlling automatic workflow commits.
      @type autocommit: C{int}
      @param nodes: Workflow-enabled node paths.
      @type nodes: C{list}
      """
      self.id = 'workflow_manager'
      self.autocommit = autocommit
      self.nodes = nodes

    def getAutocommit(self):
      """Return whether workflow autocommit is enabled locally."""
      return getattr(self, 'autocommit', 1)

    def getNodes(self):
      """Return workflow-enabled node paths."""
      return getattr(self, 'nodes', ['{$}'])

    def doAutocommit(self, lang, REQUEST):
      """Trigger a workflow autocommit run through the shared provider.

      @param lang: Active UI language.
      @type lang: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      """
      ZMSWorkflowProvider.doAutocommit(self, REQUEST)

    def getActivities(self):
      """Return workflow activities from the portal master."""
      return self.getPortalMaster().getWorkflowManager().getActivities()

    def getActivityIds(self):
      """Return workflow activity ids from the portal master."""
      return self.getPortalMaster().getWorkflowManager().getActivityIds()
  
    def getActivity(self, id):
      """Return a workflow activity definition from the portal master.

      @param id: Activity identifier.
      @type id: C{str}
      @return: Workflow activity definition.
      @rtype: C{dict}
      """
      return self.getPortalMaster().getWorkflowManager().getActivity(id)

    def getActivityDetails(self, id):
      """Return detailed workflow activity information from the portal master.

      @param id: Activity identifier.
      @type id: C{str}
      @return: Detailed workflow activity information.
      @rtype: C{dict}
      """
      return self.getPortalMaster().getWorkflowManager().getActivityDetails(id)

    def getTransitions(self):
      """Return workflow transitions from the portal master."""
      return self.getPortalMaster().getWorkflowManager().getTransitions()

    def getTransitionIds(self):
      """Return workflow transition ids from the portal master."""
      return self.getPortalMaster().getWorkflowManager().getTransitionIds()

    def getTransition(self, id, for_export=False):
      """Return a workflow transition definition from the portal master.

      @param id: Transition identifier.
      @type id: C{str}
      @param for_export: Include export-safe payload details when true.
      @type for_export: C{bool}
      @return: Workflow transition definition.
      @rtype: C{dict}
      """
      return self.getPortalMaster().getWorkflowManager().getTransition(id, for_export)

    def manage_changeWorkflow(self, lang, key='', btn='', REQUEST=None, RESPONSE=None):
      """Handle ZMI updates for acquired workflow settings.

      @param lang: Active UI language.
      @type lang: C{str}
      @param key: Edited settings section.
      @type key: C{str}
      @param btn: Submitted button id.
      @type btn: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: The active HTTP response.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Redirect response.
      @rtype: C{object}
      """
      message = ''
      
      # Active.
      # -------
      if key == 'custom' and btn == 'BTN_SAVE':
        # Autocommit & Nodes.
        old_autocommit = getattr(self, 'autocommit', 1)
        new_autocommit = REQUEST.get('workflow', 0) == 0
        self.autocommit = new_autocommit
        self.nodes = standard.string_list(REQUEST.get('nodes', ''))
        if old_autocommit == 0 and new_autocommit == 1:
          self.doAutocommit(lang, REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = standard.url_quote(message)
      return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#_%s'%(lang, message, key))

