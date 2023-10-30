################################################################################
# ZMSZCatalogLunrConnector.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSCatalogConnector
from Products.zms import ZMSItem
from Products.zms import standard


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSCatalogConnector.IZMSCatalogConnector)
class ZMSZCatalogLunrConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogLunrConnector'
    zmi_icon = "fas fa-search"

    # Management Interface.
    # ---------------------
    manage_input_form = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_lunr_connector', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
      'manage_changeProperties', 'manage_main',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
    )

    ############################################################################
    #  ZMSZCatalogLunrConnector.__init__:
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'zcatalog_lunr_connector'


    # --------------------------------------------------------------------------
    #  ZMSZCatalogLunrConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self, container=None):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_self(self, uid):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      pass


    ############################################################################
    #  ZMSZCatalogLunrConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, selected, btn, lang, REQUEST):
        message = ''

        # Save.
        # -----
        if btn == 'Save':
          self.setConfProperty('lunr.url', REQUEST['lunr_url'])
 
        return message

################################################################################
