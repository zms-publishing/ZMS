"""
ZMSFormatProviderAcquired.py

ZMS support for zmsformat provider acquired.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
import copy
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSFormatProvider, ZMSFormatProvider


@implementer(
        IZMSFormatProvider.IZMSFormatProvider)
class ZMSFormatProviderAcquired(
        ZMSFormatProvider.ZMSFormatProvider):

    """Delegate formatting configuration to the portal master.

    The acquired provider exposes text and character formats from the master
    portal while adapting URLs for local editor usage.
    """

    # Properties.
    # -----------
    meta_type = 'ZMSFormatProviderAcquired'


    def __init__(self, textformats=[], charformats=[]):
      """Initialize the acquired format manager stub.

      @param textformats: Unused compatibility argument.
      @type textformats: C{list}
      @param charformats: Unused compatibility argument.
      @type charformats: C{list}
      """
      self.id = 'format_manager'


    def getTextFormatDefault(self):
      """Return the default text format from the portal master.

      @return: The default text format id or C{None}.
      @rtype: C{str}
      """
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        return portal_master.getTextFormatDefault()
      return None


    def getTextFormat(self, id, REQUEST):
      """Return a text format definition delegated from the portal master.

      @param id: Text format identifier.
      @type id: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Text format definition or C{None}.
      @rtype: C{dict}
      """
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        return portal_master.getTextFormat(id, REQUEST)
      return None


    def getTextFormats(self, REQUEST):
      """Return all available text formats from the portal master.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Text format definitions.
      @rtype: C{list}
      """
      rtn = []
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        rtn.extend(portal_master.getTextFormats(REQUEST))
      return rtn


    def getCharFormats(self):
      """Return character formats from the portal master with local button URLs.

      @return: Character format definitions.
      @rtype: C{list}
      """
      rtn = []
      portal_master = self.getPortalMaster()
      if portal_master is not None:
        rtn.extend(copy.deepcopy(portal_master.getCharFormats()))
        for d in rtn:
          btn = d.get('btn')
          if isinstance(btn, str) and btn.find('/') < 0:
            d['btn'] = '%s/%s'%(portal_master.getFormatManager().absolute_url(), btn)
      return rtn

