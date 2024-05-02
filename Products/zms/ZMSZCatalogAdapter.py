#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import time
from datetime import datetime, timezone
import zope.interface
# Product Imports.
from Products.zms import standard
from Products.zms import content_extraction
from Products.zms import _confmanager
from Products.zms import IZMSCatalogAdapter, IZMSConfigurationProvider
from Products.zms import ZMSItem


def get_default_data(node):
  """
  Get default catalog-data for node.
  """
  request = node.REQUEST
  request.set('ZMS_CONTEXT_URL', True)
  d = {}
  d['uid'] = node.get_uid()
  d['id'] = node.id
  d['home_id'] = node.getHome().id
  d['meta_id'] = node.meta_id
  d['index_html'] = node.getHref2IndexHtmlInContext(node.getRootElement(), REQUEST=request)
  d['lang'] = request.get('lang',node.getPrimaryLanguage())
  d['change_dt'] = get_zoned_dt(node.attr('change_dt'))
  d['created_dt'] = get_zoned_dt(node.attr('created_dt'))
  return d

def get_zoned_dt(struct_dt):
  try:
    dt = datetime.fromtimestamp(time.mktime(struct_dt))
    zdt = dt.replace(tzinfo=timezone.utc)
  except:
    zdt = None
  return zdt

def get_file(node, d, fileparsing=True):
  """
  Try to parse ZMSFile.file to standard_html.
  """
  if fileparsing and node.meta_id == 'ZMSFile':
    try:
      file = node.attr('file')
      data = file.getData()
      if data:
        content_type = file.getContentType()
        text = content_extraction.extract_content(node, data, content_type)
        d['standard_html'] = text
      else:
        standard.writeError( node, "WARN - extract_content: file.data is empty")
    except:
      standard.writeError( node, "can't extract_content")

################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################

@zope.interface.implementer(
    IZMSConfigurationProvider.IZMSConfigurationProvider,
    IZMSCatalogAdapter.IZMSCatalogAdapter
)

class ZMSZCatalogAdapter(ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogAdapter'
    zmi_icon = "fas fa-search"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    def manage_sub_options(self):
      return (
        {'label': 'TAB_SEARCH','action': 'manage_main'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_main', globals())
    manage_main = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_main', globals())

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

    def ensure_zcatalog_connector_is_initialized(self):
      root = self.getRootElement()
      if 'zcatalog_connector' not in root.getMetaobjIds():
        _confmanager.initConf(root, 'conf:com.zms.catalog.zcatalog')

    ############################################################################
    #  Initialize 
    ############################################################################
    def initialize(self):
      self.setIds(['ZMSFolder', 'ZMSDocument', 'ZMSFile'])
      self.setAttrIds(['title', 'titlealt', 'attr_dc_description', 'standard_html'])

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex_node
    # --------------------------------------------------------------------------
    def reindex_node(self, node, forced=False):
      standard.writeBlock(node, "[reindex_node]")
      try:
        if self.getConfProperty('ZMS.CatalogAwareness.active', 1) or forced:
          nodes = node.breadcrumbs_obj_path()
          nodes.reverse()
          for node in nodes:
            if self.matches_ids_filter(node):
              fileparsing = standard.pybool( self.getConfProperty('ZMS.CatalogAwareness.fileparsing', 1))
              connectors = self.get_connectors()
              # if local connectors are available, use them.
              # otherwise use global connector
              # Note: if local connectors are used, they must cover all connector types
              if not connectors:
                root = self.getRootElement()
                connectors = root.getCatalogAdapter().get_connectors()
              for connector in connectors:
                self.reindex(connector, node, recursive=False, fileparsing=fileparsing)
        return True
      except:
        standard.writeError( self, "can't reindex_node")
        return False

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.unindex_node
    # --------------------------------------------------------------------------
    def unindex_node(self, node, forced=False):
      standard.writeBlock(node, "[unindex_node]")
      try:
        if self.getConfProperty('ZMS.CatalogAwareness.active', 1) or forced:
          nodes = node.breadcrumbs_obj_path()
          nodes.reverse()
          for node in nodes:
            if self.matches_ids_filter(node):
              for connector in self.get_connectors():
                connector.manage_objects_remove([node])
            break
      except:
        standard.writeError( self, "can't unindex_node")
        return False

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.matches_ids_filter: 
    # --------------------------------------------------------------------------
    def matches_ids_filter(self, node):
      # Meta-Ids in context of current node.
      meta_ids = node.getMetaobjManager().getTypedMetaIds(self.getIds())
      if self.getCustomFilterFunction()=='':
        # Default filter-function.
        return node.meta_id in meta_ids
      else:
        return standard.dt_py(node, self.getCustomFilterFunction(), {'meta_ids':meta_ids})
    
    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.ids: 
    #  getter and setter for meta-ids, that can be cataloged
    # --------------------------------------------------------------------------
    def getIds(self):
      return getattr(self, '_ids', [])

    def setIds(self, ids):
      setattr(self, '_ids', ids)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.custom_filter_function: 
    #  getter and setter for custom filter-function
    # --------------------------------------------------------------------------
    def getCustomFilterFunction(self):
      return getattr(self, '_custom_filter_function', '##\nreturn context.meta_id in meta_ids')

    def setCustomFilterFunction(self, custom_filter_function):
      setattr(self, '_custom_filter_function', custom_filter_function)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.attr_ids:
    #  getter and setter for attribute-ids, that can be cataloged
    # --------------------------------------------------------------------------
    def _getAttrIds(self):
      return ['uid', 'id', 'meta_id', 'home_id', 'index_html'] + self.getAttrIds()

    def getAttrIds(self):
      return list(self.getAttrs())

    def setAttrIds(self, attr_ids):
      attrs = self.getAttrs()
      for attr_id in attr_ids:
        attrs[attr_id] = {'boost':1.0,'type':'text'}
      self.setAttrs(attrs)

    def getAttrs(self):
      return getattr(self, '_attrs', {})

    def setAttrs(self, attrs):
      setattr(self, '_attrs', attrs)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_available_connector_ids
    # --------------------------------------------------------------------------
    def get_available_connector_ids(self):
      return sorted([y for y in [self.getMetaobj(x) for x in self.getMetaobjIds()] if y['id'].endswith('_connector') and y['type'] in ['ZMSLibrary']],key=lambda x:x['id']);

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_connectors
    # --------------------------------------------------------------------------
    def get_connectors(self):
      self.ensure_zcatalog_connector_is_initialized()
      return list(sorted([x for x in self.objectValues(['ZMSZCatalogConnector']) if x.__name__!='broken object']))

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_connector
    # --------------------------------------------------------------------------
    def get_connector(self, id):
      root = self.getRootElement()
      return [[x for x in root.getCatalogAdapter().get_connectors() if x.id == id]+[None]][0]

    # --------------------------------------------------------------------------
    #  Add connector.
    # --------------------------------------------------------------------------
    def add_connector(self, id):
      from Products.zms import ZMSZCatalogConnector 
      connector = ZMSZCatalogConnector.ZMSZCatalogConnector(id)
      self._setObject(connector.id, connector)
      return getattr(self, connector.id)

    # --------------------------------------------------------------------------
    #   Get adapter's ids & attributes catalog-data.
    # --------------------------------------------------------------------------
    def get_attr_data(self, node, d):
      request = node.REQUEST
      # Is request['lang'] set?
      lang = request.get('lang', d.get('lang', node.getPrimaryLanguage()))
      # Additional defaults.
      d['id'] = '%s_%s'%(node.id,lang)
      d['lang'] = lang
      # Loop attrs.
      for attr_id in self.getAttrIds():
        attr = self.getAttrs().get(attr_id, {})
        attr_type = attr.get('type', 'string')
        # Get value for attr from node.
        value = ''
        try:
          # ZMSFile.standard_html will work in get_file.
          if not (node.meta_id == 'ZMSFile' and attr_id == 'standard_html'):
            value = node.attr(attr_id)
        except:
          standard.writeError(node, "can't get attr")
        # Stringify date/datetime.
        if attr_type in ['date', 'datetime']:
          value = standard.getLangFmtDate(node, value, 'eng', 'ISO8601')
        # Stringify dict/list.
        elif type(value) in (dict, list):
          value = standard.str_item(value, f=True)
        # Add to data.  
        d[attr_id] = standard.remove_tags(value)

    # --------------------------------------------------------------------------
    #  Get catalog objects data.
    # --------------------------------------------------------------------------
    def get_catalog_objects_data(self, node, d, fileparsing=True):
      request = node.REQUEST
      lang = standard.nvl(request.get('lang'), node.getPrimaryLanguage())
      # Additional defaults.
      d['id'] = '%s_%s'%(node.id,lang)
      d['lang'] = lang
      # Get adapter's ids & attributes catalog-data.
      self.get_attr_data(node, d)
      # ZMSFile.file to standard_html?
      get_file(node, d, fileparsing)
      # Add data via connector.
      return (node, d)
        
    # --------------------------------------------------------------------------
    #  Get catalog objects.
    # --------------------------------------------------------------------------
    def get_catalog_objects(self, node, fileparsing=True):
      objects = []
      indexable = True
      # Custom hook:
      # if catalog_indexable is in node-attributes, then retrieve value for it. 
      if 'catalog_indexable' in self.getMetaobjAttrIds(node.meta_id):
        indexable = node.attr('catalog_indexable')
      if indexable:
        # Custom hook:
        # if catalog_index is in node-attributes, then retrieve value for it. 
        if 'catalog_index' in self.getMetaobjAttrIds(node.meta_id):
          for data in node.attr('catalog_index'):
            objects.append(self.get_catalog_objects_data(node, data, fileparsing))
        # Catalog only desired typed meta-ids (resolves type(ZMS...)).
        if self.matches_ids_filter(node):
          data = get_default_data(node)
          objects.append(self.get_catalog_objects_data(node, data, fileparsing))
      return objects

    ############################################################################
    #  ZMSZCatalogAdapter.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """ ZMSZCatalogAdapter.manage_changeProperties """
        message = ''
        ids = REQUEST.get('objectIds', [])

        # Add.
        # ----
        if btn == 'BTN_ADD':
          api = REQUEST['api']
          connector = self.add_connector(api)
          message += 'Added ' + connector.id

        # Delete.
        # -------
        elif btn == 'BTN_DELETE':
          n = len(ids)
          if n > 0:
            self.manage_delObjects(ids)
            message += self.getZMILangStr('MSG_DELETED')%n

        # Save.
        # -----
        elif btn == 'BTN_SAVE':
          self.setConfProperty('ZMS.CatalogAwareness.active', standard.pybool(REQUEST.get('catalog_awareness_active')))
          self.setCustomFilterFunction(REQUEST.get('custom_filter_function'))
          self._ids = REQUEST.get('ids', [])
          attrs = {}
          for attr_id in REQUEST.get('attr_ids', []):
            attrs[attr_id] = {'boost':float(REQUEST.get('boost_%s'%attr_id, '1.0')),'type':REQUEST.get('type_%s'%attr_id, 'text')}
          self.setAttrs(attrs)
          message += self.getZMILangStr('MSG_CHANGED')

        elif btn == 'BTN_CANCEL':
          pass

        # Return with message.
        message = standard.url_quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#%s'%(lang, message, REQUEST.get('tab')))

################################################################################

