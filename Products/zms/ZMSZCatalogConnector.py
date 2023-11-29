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
import json
import re
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
    def getActions(self, pattern=None):
      root = self.getRootElement()
      metaobjAttrs = root.getMetaobjAttrs(self.id)
      actions = [root.getMetaobjAttr(self.id, x['id']) for x in metaobjAttrs if x['type'] in ['py','External Method','Script (Python)']]
      if pattern:
        actions = [x for x in actions if re.match(pattern,x['id'])]
      return actions

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_init
    # --------------------------------------------------------------------------
    def manage_init(self):
      [x['ob'](self) for x in self.getActions(r'^manage_(.*?)_init$')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_objects_add
    #
    #  @param objects ((node, data), (node, data), (node, data), ...)
    #  @type  objects list|tuple 
    #  @return success, failed
    #  @rtype  tuple
    # --------------------------------------------------------------------------
    def manage_objects_add(self, objects):
      return [x['ob'](self, objects) for x in self.getActions(r'^manage_(.*?)_objects_add$')][0]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_objects_remove
    # 
    #  @param   nodes
    #  @type    nodes list|tuple 
    #  @return  success, failed
    #  @rtype   tuple
    # --------------------------------------------------------------------------
    def manage_objects_remove(self, nodes):
      return [x['ob'](self, nodes) for x in self.getActions(r'^manage_(.*?)_objects_remove$')][0]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_destroy
    # --------------------------------------------------------------------------
    def manage_destroy(self):
      [x['ob'](self) for x in self.getActions(r'^manage_(.*?)_destroy$')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.search_json
    # --------------------------------------------------------------------------
    def search_json(self, REQUEST, RESPONSE):
      """ search_json """
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
      result = [x['ob'](self, REQUEST) for x in self.getActions(r'(.*?)_query$')][0]
      return result

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_page
    # --------------------------------------------------------------------------
    def reindex_page(self, uid, page_size, clients=False, fileparsing=True, REQUEST=None, RESPONSE=None):
      """ reindex_page """
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
      adapter = self.getCatalogAdapter()
      count = 0
      node = self.getLinkObj(uid)
      root_node = self.getRootElement()
      root_path = '/'.join(root_node.getPhysicalPath())
      result = {'log':[]}
      objects = []
      while node and count < page_size:
        path = '/'.join(node.getPhysicalPath())
        log = {'index':count,'path':path,'meta_id':node.meta_id}
        objects.extend(adapter.get_catalog_objects(self, node, fileparsing))
        result['log'].append(log)
        node = node.get_next_node(clients)
        if node \
          and not '/'.join(node.getPhysicalPath()).startswith(root_path) \
          and not node.meta_id == 'ZMS' and not clients:
          node = None
        result['next_node'] = None if not node else '{$%s}'%node.get_uid()
        count += 1
      return json.dumps(result,indent=2)

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
            default_value = property['default_value']
            value = REQUEST.get(id,default_value)
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
