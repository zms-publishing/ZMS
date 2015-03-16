################################################################################
# ZMSZCatalogAdapter.py
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
import copy
import urllib
import zope.interface
# Product Imports.
import _confmanager
import _globals
import IZMSCatalogAdapter,IZMSConfigurationProvider
import ZMSItem


# ------------------------------------------------------------------------------
#  updateVersion:
# ------------------------------------------------------------------------------
def updateVersion(root):
  if not root.REQUEST.get('ZMSCatalogAdapter_updateVersion',False):
    root.REQUEST.set('ZMSCatalogAdapter_updateVersion',True)
    if root.getConfProperty('ZMS.catalog.build',0) == 0:
      if len(root.getConnectors()) == 0:
        root.addConnector('ZMSZCatalogConnector')
      root.setConfProperty('ZMS.catalog.build',1)

# ------------------------------------------------------------------------------
#  remove_tags:
# ------------------------------------------------------------------------------
def remove_tags(self, s):
  s = s \
    .replace('&ndash;','-') \
    .replace('&nbsp;',' ') \
    .replace('&ldquo;','') \
    .replace('&sect;','') \
    .replace('&Auml;','\xc2\x8e') \
    .replace('&Ouml;','\xc2\x99') \
    .replace('&Uuml;','\xc2\x9a') \
    .replace('&auml;','\xc2\x84') \
    .replace('&ouml;','\xc2\x94') \
    .replace('&uuml;','\xc2\x81') \
    .replace('&szlig;','\xc3\xa1')
  s = self.re_sub('<script(.*?)>(.|\\n|\\r|\\t)*?</script>',' ',s)
  s = self.re_sub('<style(.*?)>(.|\\n|\\r|\\t)*?</style>',' ',s)
  s = self.re_sub('<[^>]*>',' ',s)
  while s.find('\t') >= 0:
    s = s.replace('\t',' ')
  while s.find('\n') >= 0:
    s = s.replace('\n',' ')
  while s.find('\r') >= 0:
    s = s.replace('\r',' ')
  while s.find('  ') >= 0:
    s = s.replace('  ',' ')
  s = s.strip()
  return s


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSZCatalogAdapter(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSCatalogAdapter.IZMSCatalogAdapter)

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogAdapter'
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
    manage = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_main',globals())
    manage_main = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_main',globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_changeProperties', 'manage_main',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    ############################################################################
    #  ZMSZCatalogAdapter.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'zcatalog_adapter'

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.search_xml:
    # --------------------------------------------------------------------------
    def search_xml(self, q, page_index=0, page_size=10, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogAdapter.search_xml """
      # Check constraints.
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang',REQUEST.get('lang',self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/plain; charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      clients = self.getConfProperty('ZCatalog.portalClients',1)
      results = self.search(q,clients)
      # Assemble xml.
      xml = self.getXmlHeader()
      xml += '<response>'
      xml += '<status>'
      xml += '<code>1</code>'
      xml += '<message></message>'
      xml += '</status>'
      xml += '<results>'
      xml += '<pagination>'
      xml += '<page>%i</page>'%page_index
      xml += '<abs>%i</abs>'%len(results)
      xml += '<total>%i</total>'%len(results)
      xml += '</pagination>'
      if len(results) > page_size:
        results = results[page_index*page_size:(page_index+1)*page_size]
      for result in results:
        xml += '<result>'
        for k in result.keys():
          v = result[k]
          if k == 'absolute_url':
            k = 'loc'
          elif k == 'zcat_custom':
            k = 'custom'
          elif k == 'standard_html':
            k = 'snippet'
            v = self.search_quote(v) # TODO: better snippet...
          xml += '<%s>%s</%s>'%(k,v,k)
        xml += '</result>'
      xml += '</results>'
      xml += '</response>'
      return xml


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.search:
    # --------------------------------------------------------------------------
    def search(self, qs, order=None):
      rtn = []
      if len(qs) > 0:
        for connector in self.getConnectors():
          rtn.extend(connector.search(qs,order))
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self):
      for connector in self.getConnectors():
        connector.reindex()


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.ids: getter and setter
    # --------------------------------------------------------------------------
    def getIds(self):
      return getattr(self,'_ids',[])

    def setIds(self, ids):
      setattr(self,'_ids',ids)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.attr_ids: getter and setter
    # --------------------------------------------------------------------------
    def getAttrIds(self):
      return getattr(self,'_attr_ids',[])

    def setAttrIds(self, attr_ids):
      setattr(self,'_attr_ids',attr_ids)



    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.getConnectorMetaTypes
    # --------------------------------------------------------------------------
    def getConnectorMetaTypes(self):
      return ['ZMSZCatalogConnector','ZMSZCatalogSolrConnector']

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.getConnectors
    # --------------------------------------------------------------------------
    def getConnectors(self):
      updateVersion(self)
      return self.objectValues(self.getConnectorMetaTypes())

    def addConnector(self,meta_type):
      connector = _confmanager.ConfDict.forName(meta_type+'.'+meta_type)()
      self._setObject(connector.id, connector)
      return getattr(self,connector.id)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_sitemap
    #
    #  @param self
    #  @param  cb  callback
    # --------------------------------------------------------------------------
    def get_sitemap(self, cb):
      
      #-- Add node.
      def add(node):
        d = {}
        d['id'] = node.id
        d['meta_id'] = node.meta_id
        for attr_id in self.getAttrIds():
          value = node.attr(attr_id)
          d[attr_id] = remove_tags(self,value)
        cb(node,d)
      
      #-- Traverse tree.
      def traverse(node):
        # Check meta-id.
        if node.meta_id in self.getIds():
          add(node)
        # Handle child-nodes.
        for childNode in node.filteredChildNodes(node.REQUEST):
          traverse(childNode)
      
      self.REQUEST.set('lang',self.getPrimaryLanguage())
      traverse(self.getDocumentElement())
      
      #-- Process clients.
      if self.getConfProperty('ZCatalog.portalClients',1) == 1:
        for portalClient in self.getPortalClients():
          for adapter in portalClient.getCatalogAdapters():
            adapter.get_sitemap(cb)


    ############################################################################
    #  ZMSZCatalogAdapter.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """ ZMSZCatalogAdapter.manage_changeProperties: """
        message = ''
        ids = REQUEST.get('objectIds',[])
        
        # Delegate to connectors.
        # -----------------------
        for connector in self.getConnectors():
          message += connector.manage_changeProperties(connector.id in ids, btn, lang, REQUEST)
        
        # Add.
        # ----
        if btn == 'Add':
          meta_type = REQUEST['meta_type']
          connector = self.addConnector(meta_type)
          message += 'Added '+meta_type
        
        # Save.
        # -----
        elif btn == 'Save':
          self.setConfProperty('ZMS.CatalogAwareness.active',REQUEST.get('catalog_awareness_active')==1)
          self._ids = REQUEST.get('ids',[])
          self._attr_ids = REQUEST.get('attr_ids',[])
          message += self.getZMILangStr('MSG_CHANGED')
        
        # Remove.
        # -------
        elif btn == 'Remove':
          if len(ids) > 0:
            self.manage_delObjects(ids)
            message += self.getZMILangStr('MSG_DELETED')%len(ids)
        
        # Return with message.
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
