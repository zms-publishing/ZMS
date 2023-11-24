################################################################################
# ZMSZCatalogConnector.py
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
from Products.zms import standard
from Products.zms import IZMSCatalogConnector
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSCatalogConnector.IZMSCatalogConnector,
        IZMSRepositoryProvider.IZMSRepositoryProvider,)
class ZMSZCatalogConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogConnector'
    zmi_icon = "fas fa-search"

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_zcatalog_connector', globals())
    manage_main = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_zcatalog_connector', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
        'manage_changeProperties', 'manage_main',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )

    ############################################################################
    #  ZMSZCatalogConnector.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self, id):
      self.id = id


    ############################################################################
    #
    #  IRepositoryProvider
    #
    ############################################################################

    """
    @see IRepositoryProvider
    """
    def provideRepository(self, r, ids=None):
      standard.writeBlock(self, "[provideRepository]: ids=%s"%str(ids))
      r = {}
      id = self.id
      d = {'id':id,'revision':'0.0.0','__filename__':['__init__.py']}
      r[id] = d
      r[id]['Opensearch'] = [{
        'id':'schema',
        'ob': {
          'filename':'schema.json',
          'data':self.getConfProperty('opensearch.schema','{}'),
          'version':'0.0.0',
          'meta_type':'File',
        }
      }]
      return r

    """
    @see IRepositoryProvider
    """
    def updateRepository(self, r):
      id = r['id']
      [self.setConfProperty('opensearch.schema',x['data']) for x in r['Opensearch'] if x['id'] == 'schema']
      return id

    """
    @see IRepositoryProvider
    """
    def translateRepositoryModel(self, r):
      d = {}
      return d

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.getProperties
    # --------------------------------------------------------------------------
    def getProperties(self):
      return standard.parse_json(self.evalMetaobjAttr('%s.properties'%self.id))

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.getActions
    # --------------------------------------------------------------------------
    def getActions(self):
      root = self.getRootElement()
      metaobjAttrs = root.getMetaobjAttrs(self.id)
      return [root.getMetaobjAttr(self.id, x['id']) for x in metaobjAttrs if x['id'].startswith('manage_') and x['type'] in ['py','External Method','Script (Python)']]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_init
    # --------------------------------------------------------------------------
    def manage_init(self):
      [x['ob'](self) for x in self.getActions() if x['id'].endswith('_init')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_object_add
    # --------------------------------------------------------------------------
    def manage_object_add(self, node, data):
      [x['ob'](self, node, data) for x in self.getActions() if x['id'].endswith('_object_add')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_object_remove
    # --------------------------------------------------------------------------
    def manage_object_remove(self, node):
      [x['ob'](self, node) for x in self.getActions() if x['id'].endswith('_object_remove')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_destroy
    # --------------------------------------------------------------------------
    def manage_destroy(self):
      [x['ob'](self) for x in self.getActions() if x['id'].endswith('_destroy')]

    ############################################################################
    #  ZMSZCatalogConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """
        manage_changeProperties
        """
        message = ''
        
        # Save.
        # -----
        if btn == 'BTN_SAVE':
          properties = self.getProperties()
          for property in properties:
            id = property['id']
            defaultValue = property['defaultValue']
            value = REQUEST.get(id,defaultValue)
            if property.get('type','string') == 'password':
              if value:
                self.setConfProperty(id, value)
            else:
              self.setConfProperty(id, value)
          message += self.getZMILangStr('MSG_CHANGED')

        elif btn == 'BTN_CANCEL':
          pass

        # Return with message.
        message = standard.url_quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#%s'%(lang, message, REQUEST.get('tab')))

################################################################################
