"""
ZMSZCatalogAdapter.py - Catalog adapter implementation for indexing ZMS content.

This module collects normalized metadata and extracted text for ZMS objects,
prepares index payloads, and exposes adapter logic used by catalog connectors
for search, faceting, and retrieval.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import contextlib
import copy
import json
import time
from datetime import datetime, timezone
import zope.interface
# Product Imports.
from Products.zms import standard
from Products.zms import content_extraction
from Products.zms import _confmanager
from Products.zms import IZMSCatalogAdapter, IZMSConfigurationProvider
from Products.zms import ZMSItem


_MISSING = object()


@contextlib.contextmanager
def catalog_request_context(node, lang=None):
  """
  Temporarily set the indexing context (language, ZMS_CONTEXT_URL) on the
  node's request and restore the previous request state afterwards.

  Yields the effective language: the given lang, else request['lang'], else
  the node's primary language. Prevents in-place redirects triggered by
  attribute rendering from leaking into the response.
  """
  request = node.REQUEST
  if not lang:
    lang = standard.nvl(request.get('lang'), node.getPrimaryLanguage())
  saved = {k: request.get(k, _MISSING) for k in ('lang', 'ZMS_CONTEXT_URL')}
  request.set('lang', lang)
  request.set('ZMS_CONTEXT_URL', True)
  try:
    yield lang
  finally:
    for k, v in saved.items():
      if v is _MISSING:
        request.other.pop(k, None)
      else:
        request.set(k, v)
    # Prevent in-place redirecting by resetting status code and location header.
    response = getattr(request, 'RESPONSE', None)
    if hasattr(response, 'setStatus'):
      response.setStatus(200)
      response.setHeader('Location', '')


def get_default_data(node, lang=None):
  """
  Extract and prepare default catalog metadata for a ZMS node.
  
  This function collects comprehensive metadata about a ZMS object for indexing
  in the catalog system. It gathers identification data (uid, id, meta_id),
  structural information (path hierarchy, sort order), temporal data (creation,
  modification, and activity timestamps), linguistic context (language), and
  navigation details (URLs). The collected data is used by catalog connectors
  for search indexing, sorting, filtering, and result retrieval.
  
  Args:
  node: A ZMS object instance containing metadata and content attributes.
  
  Returns:
  dict: A dictionary containing normalized catalog fields including:
    - uid: Unique identifier
    - id: Object ID
    - home_id: Root container ID
    - meta_id: Meta object type
    - loc: Absolute URL path
    - path: Physical path
    - index_html: URL to index.html in context
    - lang: Current language context
    - created_dt, change_dt: Creation and modification timestamps (UTC)
    - start_dt, end_dt: Activation time window
    - indexing_dt: Current indexing timestamp
    - sortid: 15-character tree sort identifier (up to 5 levels, 3 digits each)
  """
  request = node.REQUEST
  lang = lang or standard.nvl(request.get('lang'), node.getPrimaryLanguage())
  d = {}
  d['uid'] = node.get_uid()
  d['id'] = node.id
  d['home_id'] = node.getHome().id
  d['meta_id'] = node.meta_id
  d['loc'] = node.absolute_url_path()
  d['path'] = '/'.join(node.getPhysicalPath())
  # Todo: Remove preview-parameter.
  d['index_html'] = node.getHref2IndexHtmlInContext(node.getRootElement(), REQUEST=request)
  d['lang'] = lang
  d['created_dt'] = get_zoned_dt(node.attr('created_dt'))
  d['change_dt'] = get_zoned_dt(node.attr('change_dt')) or d['created_dt']
  d['start_dt'] = get_zoned_dt(node.attr('attr_active_start'))
  d['end_dt'] = get_zoned_dt(node.attr('attr_active_end'))
  d['indexing_dt'] = get_zoned_dt(time.localtime())
  d['sortid'] = '.'.join([f'{e.getSortId():04d}' for e in node.breadcrumbs_obj_path(False)[1:]])
  return d

def get_zoned_dt(struct_dt):
  """Return zoned dt."""
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
    """Provide helpers for ZMSZCatalogAdapter."""
    meta_type = 'ZMSZCatalogAdapter'
    zmi_icon = "fas fa-search"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      """Handle the ZMI action 'manage_options'."""
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    def manage_sub_options(self):
      """Handle the ZMI action 'manage_sub_options'."""
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
        'manage_reindex_start', 'manage_reindex_status', 'manage_reindex_pause',
        'manage_reindex_proceed', 'manage_reindex_stop',
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
      """Initialize the instance state."""
      self.id = 'zcatalog_adapter'

    def ensure_zcatalog_connector_is_initialized(self):
      """Implement 'ensure_zcatalog_connector_is_initialized'."""
      root = self.getRootElement()
      if 'zcatalog_connector' not in root.getMetaobjIds() and self.REQUEST.get('zcatalog_init', 1) == 1:
        _confmanager.initConf(root, 'conf:com.zms.catalog.zcatalog')

    ############################################################################
    #  Initialize 
    ############################################################################
    def initialize(self):
      """Implement 'initialize'."""
      self.setIds(['ZMSFolder', 'ZMSDocument', 'ZMSFile'])
      self.setAttrIds(['title', 'titlealt', 'attr_dc_description', 'standard_html'])

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex
    # --------------------------------------------------------------------------
    def reindex(self, connector, base, recursive=True, fileparsing=True):
      """Implement 'reindex'."""
      def traverse(node, recursive):
        """Implement 'traverse'."""
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
    def _get_reindexed_nodes(self, seen=None):
      """Return the set of paths of nodes already reindexed in this run.

      An explicitly given set is used as is. Otherwise the set is shared
      per request, so that repeated calls within one request don't reindex
      the same node again. This is the only place that touches the request
      for deduplication.
      """
      if seen is not None:
        return seen
      request = self.REQUEST
      seen = request.get('reindex_node_log')
      if not isinstance(seen, set):
        seen = set()
        request.set('reindex_node_log', seen)
      return seen

    def reindex_node(self, node, seen=None):
      """Implement 'reindex_node'.

      seen: optional set of paths of already reindexed nodes; it is updated
      in place. Defaults to a per-request set.
      """
      seen = self._get_reindexed_nodes(seen)
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
                path = '/'.join(filtered_container_node.getPhysicalPath())
                if path not in seen:
                  self.reindex(connector, filtered_container_node, recursive=False, fileparsing=fileparsing)
                  seen.add(path)
          elif '/'.join(container_page.getPhysicalPath()) not in seen:
            # Remove from catalog if editing leads to filter-not-matching 
            # and node was not part of current reindexing.
            for connector in connectors:
              connector.manage_objects_remove([container_page])
          if (node.meta_id =='ZMSFile' and '/'.join(node.getPhysicalPath()) not in seen):
            # Remove ZMSFile from catalog if editing leads to filter-not-matching 
            # and node was not part of current reindexing.
            for connector in connectors:
              connector.manage_objects_remove([node])
        return True
      except:
        standard.writeError( self, "can't reindex_node")
        return False

    # --------------------------------------------------------------------------
    #  Background reindex job (see ZMSZCatalogAdapterQueue).
    #  The job key is the root url, so there is one job per ZMS site.
    # --------------------------------------------------------------------------
    def get_reindex_job_key(self):
      """Return the key identifying the reindex job of this site."""
      return self.getRootElement().absolute_url()

    def start_reindex_job(self, home_ids, connector_id=None, page_size=1, fileparsing=False):
      """Start the reindex job for the given ZMS clients. Returns None if started, else a message."""
      from Products.zms import ZMSZCatalogAdapterQueue
      return ZMSZCatalogAdapterQueue.start(
        self.getRootElement(), home_ids, key=self.get_reindex_job_key(),
        connector_id=connector_id, page_size=page_size, fileparsing=fileparsing)

    def get_reindex_job_status(self):
      """Return the status dict of the reindex job."""
      from Products.zms import ZMSZCatalogAdapterQueue
      return ZMSZCatalogAdapterQueue.get_status(self.get_reindex_job_key())

    def pause_reindex_job(self):
      """Pause the reindex job. Returns a message."""
      from Products.zms import ZMSZCatalogAdapterQueue
      return ZMSZCatalogAdapterQueue.pause(self.get_reindex_job_key())

    def proceed_reindex_job(self):
      """Proceed the paused reindex job. Returns a message."""
      from Products.zms import ZMSZCatalogAdapterQueue
      return ZMSZCatalogAdapterQueue.proceed(self.get_reindex_job_key())

    def stop_reindex_job(self):
      """Stop the reindex job. Returns a message."""
      from Products.zms import ZMSZCatalogAdapterQueue
      return ZMSZCatalogAdapterQueue.stop(self.get_reindex_job_key())

    def _reindex_json(self, REQUEST, data):
      response = REQUEST.RESPONSE
      response.setHeader('Content-Type', 'application/json; charset=utf-8')
      response.setHeader('Cache-Control', 'no-store')
      return json.dumps(data)

    def _reindex_control(self, REQUEST, action):
      # State changes must not be triggered by GET (links, prefetching).
      if REQUEST.get('REQUEST_METHOD') != 'POST':
        REQUEST.RESPONSE.setStatus(405)
        REQUEST.RESPONSE.setHeader('Allow', 'POST')
        return self._reindex_json(REQUEST, {'message': 'POST required'})
      return self._reindex_json(REQUEST, {'message': action()})

    def manage_reindex_status(self, REQUEST):
      """Return the status of the reindex job as JSON."""
      return self._reindex_json(REQUEST, self.get_reindex_job_status())

    def manage_reindex_start(self, REQUEST):
      """Start the reindex job for the selected ZMS clients (home_ids) as JSON message."""
      def start():
        return self.start_reindex_job(
          REQUEST.get('home_ids', []),
          connector_id=REQUEST.get('connector_id') or None,
          page_size=max(1, int(REQUEST.get('page_size', 1))),
          fileparsing=standard.pybool(REQUEST.get('fileparsing', False)))
      return self._reindex_control(REQUEST, start)

    def manage_reindex_pause(self, REQUEST):
      """Pause the reindex job."""
      return self._reindex_control(REQUEST, self.pause_reindex_job)

    def manage_reindex_proceed(self, REQUEST):
      """Proceed the paused reindex job."""
      return self._reindex_control(REQUEST, self.proceed_reindex_job)

    def manage_reindex_stop(self, REQUEST):
      """Stop the reindex job."""
      return self._reindex_control(REQUEST, self.stop_reindex_job)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.unindex_nodes
    # --------------------------------------------------------------------------
    def unindex_nodes(self, nodes=[], forced=False):
      # Is triggered by zmscontainerobject.moveObjsToTrashcan().
      """Implement 'unindex_nodes'."""
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
          # Get page-nodes and ZMS files that are moved to trashcan.
          delnodes = [i for i in trashcan_items if i in nodes and (i.isPage() or i.meta_id == 'ZMSFile')]
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
      """Implement 'matches_ids_filter'."""
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
      """Return ids."""
      return getattr(self, '_ids', [])

    def setIds(self, ids):
      """Set ids."""
      setattr(self, '_ids', ids)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.custom_filter_function: 
    #  getter and setter for custom filter-function
    # --------------------------------------------------------------------------
    def getCustomFilterFunction(self):
      """Return customfilterfunction."""
      return getattr(self, '_custom_filter_function', '##\nreturn context.meta_id in meta_ids\\\n    and (context.isVisible(context.REQUEST))')

    def setCustomFilterFunction(self, custom_filter_function):
      """Set customfilterfunction."""
      setattr(self, '_custom_filter_function', custom_filter_function)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.attr_ids:
    #  getter and setter for attribute-ids, that can be cataloged
    # --------------------------------------------------------------------------
    def _getAttrIds(self):
      """Implement '_getAttrIds'."""
      return ['uid', 'id', 'meta_id', 'home_id', 'loc', 'path', 'index_html'] + self.getAttrIds()

    def getAttrIds(self):
      """Return attrids."""
      return list(self.getAttrs())

    def setAttrIds(self, attr_ids):
      """Set attrids."""
      attrs = self.getAttrs()
      for attr_id in attr_ids:
        attrs[attr_id] = {'boost':1.0,'type':'text'}
      self.setAttrs(attrs)

    def getAttrs(self):
      """Return attrs."""
      return getattr(self, '_attrs', {})

    def setAttrs(self, attrs):
      """Set attrs."""
      setattr(self, '_attrs', attrs)

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_available_connector_ids
    # --------------------------------------------------------------------------
    def get_available_connector_ids(self):
      """Return available connector ids."""
      return sorted([y for y in [self.getMetaobj(x) for x in self.getMetaobjIds()] if y['id'].endswith('_connector') and y['type'] in ['ZMSLibrary']],key=lambda x:x['id']);

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_connectors
    # --------------------------------------------------------------------------
    def get_connectors(self):
      """Return connectors."""
      self.ensure_zcatalog_connector_is_initialized()
      root = self.getRootElement()
      return list(sorted([x for x in root.getCatalogAdapter().objectValues(['ZMSZCatalogConnector']) if x.__name__!='broken object']))

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.get_connector
    # --------------------------------------------------------------------------
    def get_connector(self, id):
      """Return connector."""
      return [[x for x in self.get_connectors() if x.id == id]+[None]][0]

    # --------------------------------------------------------------------------
    #  Add connector.
    # --------------------------------------------------------------------------
    def add_connector(self, id):
      """Implement 'add_connector'."""
      from Products.zms import ZMSZCatalogConnector 
      connector = ZMSZCatalogConnector.ZMSZCatalogConnector(id)
      self._setObject(connector.id, connector)
      return getattr(self, connector.id)

    # --------------------------------------------------------------------------
    #   Get adapter's ids & attributes catalog-data.
    # --------------------------------------------------------------------------
    def get_attr_data(self, node, d, lang=None):
      """Return attr data."""
      request = node.REQUEST
      if not lang:
        lang = request['lang'] if 'lang' in request else d.get('lang', node.getPrimaryLanguage())
      if request.get('lang') != lang:
        request.set('lang', lang)
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

    # --------------------------------------------------------------------------
    #  Get catalog objects data for given node.
    # --------------------------------------------------------------------------
    def get_catalog_objects_data(self, node, d, fileparsing=True, lang=None):
      """Return catalog objects data."""
      request = node.REQUEST
      lang = lang or standard.nvl(request.get('lang'), node.getPrimaryLanguage())
      # Additional defaults.
      d['id'] = '%s_%s'%(node.id,lang)
      d['lang'] = lang
      # Get adapter's ids & attributes catalog-data.
      self.get_attr_data(node, d, lang)
      # ZMSFile.file to standard_html?
      if fileparsing and node.meta_id == 'ZMSFile':
        get_file(node, d, fileparsing)
      # Add data via connector.
      return (node, d)
        
    # --------------------------------------------------------------------------
    #  Get catalog objects.
    # --------------------------------------------------------------------------
    def get_catalog_objects(self, node, fileparsing=True, lang=None):
      """Return catalog objects for node in given lang (default: request lang)."""
      objects = []
      with catalog_request_context(node, lang) as lang:
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
              objects.append(self.get_catalog_objects_data(node, data, fileparsing, lang))
          # Catalog only desired typed meta-ids (resolves type(ZMS...)).
          if self.matches_ids_filter(node):
            data = get_default_data(node, lang)
            objects.append(self.get_catalog_objects_data(node, data, fileparsing, lang))
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

