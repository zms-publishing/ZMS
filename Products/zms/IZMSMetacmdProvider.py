"""
IZMSMetacmdProvider.py

Interface definitions for ZMS metacommand providers.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface
# Product Imports.
from Products.zms import IZMSActionListContributor

class IZMSMetacmdProvider(Interface, IZMSActionListContributor.IZMSActionListContributor):

  def getMetaCmdDescription(self, id):
    """
    Returns description of meta-command specified by ID.
    @rtype: C{str}
    """

  def getMetaCmd(self, id):
    """
    Returns action.
    @rtype: C{dict}
    """

  def getMetaCmdIds(self, sort=True):
    """
    Returns list of action-ids.
    @rtype: C{list}
    """

  def getMetaCmds(self, context=None, stereotype='', sort=True):
    """
    Returns list of actions.
    @rtype: C{list}
    """
