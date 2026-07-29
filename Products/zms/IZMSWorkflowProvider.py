"""
IZMSWorkflowProvider.py

Defines IZMSWorkflowProvider for ZMS plugin interfaces.
It establishes contracts for provider implementations, ensuring loose coupling and extensibility.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSWorkflowProvider(Interface):

  def getAutocommit(self):
    """
    @rtype: C{Boolean}
    """

  def getActivities(self):
    """
    @rtype: C{list}
    """

  def getActivityIds(self):
    """
    @rtype: C{list}
    """
  
  def getActivity(self, id):
    """
    @rtype: C{dict}
    """

  def getActivityDetails(self, id):
    """
    @rtype: C{dict}
    """

  def getTransitions(self):
    """
    @rtype: C{list}
    """

  def getTransitionIds(self):
    """
    @rtype: C{list}
    """