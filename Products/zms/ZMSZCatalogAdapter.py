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
  # Todo: Remove preview-parameter.
  d['index_html'] = node.getHref2IndexHtmlInContext(node.getRootElement(), REQUEST=request)
  d['lang'] = request.get('lang',node.getPrimaryLanguage())
  d['created_dt'] = get_zoned_dt(node.attr('created_dt'))
  d['change_dt'] = get_zoned_dt(node.attr('change_dt')) or d['created_dt']
  d['indexing_dt'] = get_zoned_dt(time.gmtime())
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
      if file:
        data = file.getData()
        if data:
          content_type = file.getContentType()
          text = content_extraction.extract_content(node, data, content_type)
          d['standard_html'] = text
        else:
          standard.writeLog( node, "WARN - get_file: file.data is empty")
      else:
        standard.writeLog( node, "WARN - get_file: file not found")
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
      if 'zcatalog_connector' not in root.getMetaobjIds() and self.REQUEST.get('zcatalog_init', 1) == 1:
        _confmanager.initConf(root, 'conf:com.zms.catalog.zcatalog')

    ############################################################################
    #  Initialize 
    ############################################################################
    def initialize(self):
      self.setIds(['ZMSFolder', 'ZMSDocument', 'ZMSFile'])
      self.setAttrIds(['title', 'titlealt', 'attr_dc_description', 'standard_html'])

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex
    # --------------------------------------------------------------------------
    def reindex(self, connector, base, recursive=True, fileparsing=True):
      def traverse(node, recursive):
        objects = self.get_catalog_objects(node, fileparsing)
        success, failed = connector.manage_objects_add(objects)
        if recursive:
          for childNode in node.filteredChildNodes(request):
            childSuccess, childFailed = traverse(childNode, recursive)
            success += childSuccess
            failed += childFailed
        return success, failed 
      request = self.REQUEST
      request.set('lang', self.REQUEST.get('lang', self.getPrimaryLanguage()))
      result = []
      result.append('%i objects cataloged (%s failed)'%traverse(base, recursive))
      return ', '.join([x for x in result if x])

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex_node
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      connectors = []
      fileparsing = False
      try:
        if self.getConfProperty('ZMS.CatalogAwareness.active', 1):
          breadcrumbs = node.breadcrumbs_obj_path()
          breadcrumbs.reverse()
          # Determine the node's page container 
          # because this is what usually is to be indexed.
          page_nodes = [e for e in breadcrumbs if e.isPage()]
          container_page = page_nodes[0]
          container_nodes = standard.difference_list(breadcrumbs, page_nodes)
          container_nodes.append(container_page)
          filtered_container_nodes = [e for e in container_nodes if self.matches_ids_filter(e)]
          # Hint: getCatalogAdapter prefers local adapter, otherwise root adapter.
          connectors = node.getCatalogAdapter().get_connectors()
          if filtered_container_nodes:
            fileparsing = standard.pybool(node.getConfProperty('ZMS.CatalogAwareness.fileparsing', 1))
            # Reindex filtered container node's content by each connector.
            for connector in connectors:
              for filtered_container_node in filtered_container_nodes:
                # Avoid reindexing the same node multiple times.
                if not hasattr(self.REQUEST, 'reindex_node_log'):
                  self.REQUEST.set('reindex_node_log', [])
                if filtered_container_node.id not in self.REQUEST.get('reindex_node_log'):
                  self.reindex(connector, filtered_container_node, recursive=False, fileparsing=fileparsing)
                  # Add reindexed node to log variable.
                  reindex_node_log = self.REQUEST.get('reindex_node_log')
                  reindex_node_log.append(filtered_container_node.id)
                  # Update request variable.
                  self.REQUEST.set('reindex_node_log', reindex_node_log)
          elif container_page.getId() not in self.REQUEST.get('reindex_node_log', []):
            # Remove from catalog if editing leads to filter-not-matching 
            # and node was not part of current reindexing.
            for connector in connectors:
              connector.manage_objects_remove([container_page])
        return True
      except:
        standard.writeError( self, "can't reindex_node")
        return False

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.unindex_nodes
    # --------------------------------------------------------------------------
    def unindex_nodes(self, nodes=[], forced=False):
      # Is triggered by zmscontainerobject.moveObjsToTrashcan().
      if not nodes:
        standard.writeLog( self, "No nodes given to unindex")
        return False
      try:
        if self.getConfProperty('ZMS.CatalogAwareness.active', 1) or forced:
          # ------------------------------------------------------
          # [1] PAGELEMENTS: Reindex PAGE-container nodes of deleted page-element.
          # ------------------------------------------------------
          pageelement_nodes = [node for node in nodes if not node.isPage()]
          pageelement_pages = [] # page that contain the pageelements.
          for pageelement_node in pageelement_nodes:
              path_nodes = pageelement_node.getParentNode().breadcrumbs_obj_path()
              path_nodes.reverse()
              path_nodes = [e for e in path_nodes if e.isPage()]
              if path_nodes[0] not in pageelement_pages:
                pageelement_pages.append(path_nodes[0])
          for pageelement_page in list(set(pageelement_pages)):  # Remove duplicates.
            # Reindex page that formerly contained the deleted pageelement.
            self.reindex_node(node=pageelement_page)
          # ------------------------------------------------------
          # [2] PAGES: Remove page-nodes that are moved to trashcan.
          # ------------------------------------------------------
          trashcan = nodes[0].getParentNode().getTrashcan()
          if not trashcan:
            standard.writeLog( self, "No trashcan found for %s"%(nodes[0].getParentNode().id) )
            return False
          trashcan_items = trashcan.objectValues()
          if not trashcan_items:
            standard.writeLog( self, "No trashcan items found after deleting content from  %s"%(nodes[0].getParentNode().id) )
            return False
          # Get page-nodes that are moved to trashcan.
          delnodes = [i for i in trashcan_items if i in nodes and i.isPage()]
          if not delnodes:
            standard.writeLog( self, "No page-nodes found in trashcan after deleting content from %s"%(nodes[0].getParentNode().id) )
            return False
          # Eventually add all sub-pages if deleted page-node is a tree-root.
          for delnode in delnodes:
            # Get all sub-pages of deleted page-node.
            subpages = delnode.getTreeNodes(self.REQUEST,self.PAGES)
            if subpages:
              delnodes.extend(subpages)
          # Remove deleted nodes from catalog.
          delnodes = list(set(delnodes))  # Remove duplicates.
          connectors = self.getCatalogAdapter().get_connectors()
          if delnodes and connectors:
            for connector in connectors:
              # Remove deleted nodes from catalog.
              connector.manage_objects_remove(delnodes)
            standard.writeLog(self,"Unindexed %s pages after moving to trashcan."%(len(delnodes)) )
            return True
      except:
        standard.writeError( self, "Cannot unindex_nodes. Check if catalog is initialized.")
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
      return getattr(self, '_custom_filter_function', '##\nreturn context.meta_id in meta_ids\\\n    and (context.isVisible(context.REQUEST))')

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
      root = self.getRootElement()
      return list(sorted([x for x in root.getCatalogAdapter().objectValues(['ZMSZCatalogConnector']) if x.__name__!='broken object']))

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_connector
    # --------------------------------------------------------------------------
    def get_connector(self, id):
      return [[x for x in self.get_connectors() if x.id == id]+[None]][0]

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
        # ZMSFile.standard_html will be done in get_file().
        if not (node.meta_id == 'ZMSFile' and attr_id == 'standard_html'):
          try:
            value = node.attr(attr_id)
            # Stringify date/datetime.
            if attr_type in ['date', 'datetime']:
              value = standard.getLangFmtDate(node, value, 'eng', 'ISO8601')
            # Stringify dict/list.
            elif type(value) in (dict, list):
              value = standard.str_item(value, f=True)
          except:
            standard.writeError(node, "can't get attr %s"%attr_id)
            value = 'DATA ERROR'
            pass

          if attr_type in ['int', 'float', 'amount', 'date', 'datetime', 'time', 'bool']:
            d[attr_id] = value
          else:
            # Add plain text to data.
            d[attr_id] = content_extraction.extract_text_from_html(node, value)
      # Prevent in-place redirecting by resetting status code and location header.
      request.RESPONSE.setStatus(200) 
      request.RESPONSE.setHeader('Location', '')

    # --------------------------------------------------------------------------
    #  Get catalog objects data for given node.
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
      if fileparsing and node.meta_id == 'ZMSFile':
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
