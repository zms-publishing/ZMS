################################################################################
# IZMSCatalogAdapter.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
from zope.interface import Interface

class IZMSCatalogAdapter(Interface):

  def reindex_node(self, node):
    """
    Reindex node.
    @param node: the node
    @type node: C{object}
    """

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