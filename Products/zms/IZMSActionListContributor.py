"""
IZMSActionListContributor.py

Interface definitions for ZMS components that contribute action lists.

License: GNU General Public License v2 or later
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