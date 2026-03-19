"""
IZMSCatalogConnector.py

Interface definitions for ZMS catalog connectors.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSCatalogConnector(Interface):

    def search_json(self, REQUEST=None, RESPONSE=None):
      """
      Search.
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @return: JSON-list of result items
      @rtype: C{str}
      """

    def reindex_page(self, uid, page_size, clients=False, fileparsing=True, REQUEST=None, RESPONSE=None):
      """
      Reindex page.
      @param uid: the uid of the page's start-node
      @param page_size: the page-size
      @param clients: process clients
      @type clients: C{Boolean}
      @param fileparsing: parse files
      @type fileparsing: C{Boolean}
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @return log
      @rtype: C{str}
      """
