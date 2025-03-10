################################################################################
# IZMSCatalogConnector.py
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
