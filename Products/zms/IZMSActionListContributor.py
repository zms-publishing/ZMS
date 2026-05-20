"""
IZMSActionListContributor.py

Defines IZMSActionListContributor for ZMS plugin interfaces.
It establishes contracts for provider implementations, ensuring loose coupling and extensibility.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSActionListContributor(Interface):

  def get_actions(self, context):
    """
    Returns actions
    @rtype: C{list}
    """