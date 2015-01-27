################################################################################
# ZMSCustomCatalogAdapter.py
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
from Products.ZCatalog import ZCatalog
import copy
import urllib
import zope.interface
# Product Imports.
import IZMSCatalogAdapter,IZMSConfigurationProvider
import ZMSItem


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSCustomCatalogAdapter(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSCatalogAdapter.IZMSCatalogAdapter)

    # Properties.
    # -----------
    meta_type = 'ZMSCustomCatalogAdapter'
    icon = "/++resource++zms_/img/ZMSZCatalogAdapter.png"

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'TAB_SEARCH','action': 'manage_main'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_custom',globals())
    manage_main = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_custom',globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_changeProperties', 'manage_main',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    ############################################################################
    #  ZMSCustomCatalogAdapter.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'zcatalog_adapter'

    # --------------------------------------------------------------------------
    #  ZMSCustomCatalogAdapter.search:
    # --------------------------------------------------------------------------
    def search(self, qs, order, clients=False):
      rtn = []
      #-- Return objects in correct sort-order.
      return rtn

    # --------------------------------------------------------------------------
    #  ZMSCustomCatalogAdapter.reindex:
    # --------------------------------------------------------------------------
    def reindex(self, clients=False):
      message = ''
      
      REQUEST = self.REQUEST
      for lang in self.getLangIds():
        REQUEST.set('lang',lang)
        #-- Recreate catalog.
        # @TODO
        #-- Find items to catalog.
        # @TODO
      message += 'Catalog %s indexed successfully.'%self.getHome().id
      
      #-- Process clients.
      if clients:
        for portalClient in self.getPortalClients():
          for ob in portalClient.objectValues():
            if IZMSCustomCatalogAdapter.IZMSCustomCatalogAdapter in list(zope.interface.providedBy(ob)):
              message += ob.reindex(clients)
      
      # Return with message.
      return message


    ############################################################################
    #  ZMSCustomCatalogAdapter.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """ ZMSCustomCatalogAdapter.manage_changeProperties: """
        message = ''
        
        # Return with message.
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
