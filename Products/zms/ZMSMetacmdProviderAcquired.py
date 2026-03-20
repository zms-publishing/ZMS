"""
ZMSMetacmdProviderAcquired.py

Defines ZMSMetacmdProviderAcquired for command and action metadata registration.
It registers custom ZMI actions, toolbar commands, and context-menu entries for admin interfaces.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSMetacmdProvider, ZMSMetacmdProvider


@implementer(
        IZMSMetacmdProvider.IZMSMetacmdProvider)
class ZMSMetacmdProviderAcquired(
        ZMSMetacmdProvider.ZMSMetacmdProvider):

    """Delegate metacommand definitions to the portal master."""

    # Properties.
    # -----------
    meta_type = 'ZMSMetacmdProviderAcquired'

    def __init__(self, commands=[]):
      """Initialize the acquired metacommand manager stub.

      @param commands: Unused compatibility argument.
      @type commands: C{list}
      """
      self.id = 'metacmd_manager'

    def getMetaCmdDescription(self, id):
      """Return a metacommand description from the portal master.

      @param id: Metacommand identifier.
      @type id: C{str}
      @return: Metacommand description text.
      @rtype: C{str}
      """
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        return self.getPortalMaster().getMetaCmdDescription(id)
      return ''

    def getMetaCmdIds(self, sort=True):
      """Return metacommand ids from the portal master.

      @param sort: Sort the command ids when true.
      @type sort: C{bool}
      @return: Metacommand identifiers.
      @rtype: C{list}
      """
      rtn = []
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        rtn.extend(portal_master.getMetaCmdIds(sort))
      return rtn

    def getMetaCmds(self, context=None, stereotype='', sort=True):
      """Return metacommand definitions from the portal master.

      @param context: Optional content context used for filtering.
      @type context: C{object}
      @param stereotype: Optional command stereotype filter.
      @type stereotype: C{str}
      @param sort: Sort the command list when true.
      @type sort: C{bool}
      @return: Metacommand definitions marked as acquired.
      @rtype: C{list}
      """
      rtn = []
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        rtn.extend(portal_master.getMetaCmds(context, stereotype, sort))
        for d in rtn:
            d['acquired'] = 1
      return rtn

