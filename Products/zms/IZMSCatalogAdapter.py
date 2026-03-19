"""
IZMSCatalogAdapter.py

Interface definitions for ZMS catalog adapters.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSCatalogAdapter(Interface):

  def search(self, qs, order, clients=False):
    """
    Search catalog.
    @param qs: the query-string 
    @type qs: C{str}
    @param order: the sort-order 
    @type order: C{str}
    @param clients: flag to process clients recursicely
    @type clients: C{boolean=False}
    @returns: the list of search-results 
    @rtype: C{list}
    """