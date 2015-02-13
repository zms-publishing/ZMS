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
from Products.ZCatalog import ZCatalog
import copy
import urllib
import zope.interface
# Product Imports.
import _confmanager
import _globals
import IZMSCatalogAdapter,IZMSConfigurationProvider
import ZMSItem


# ------------------------------------------------------------------------------
#  Empty:
# ------------------------------------------------------------------------------
class Empty: 
  pass


# ------------------------------------------------------------------------------
#  intValue:
# ------------------------------------------------------------------------------
def intValue(v):
  try:
    i = int(v)
  except:
    i = 0
  return i


# ------------------------------------------------------------------------------
#  addLexicon:
# ------------------------------------------------------------------------------
def addLexicon( container, cat):
  
  #-- Remove Lexicon
  ids = cat.objectIds( ['ZCTextIndex Lexicon','ZCTextIndex Unicode Lexicon'])
  if len( ids) > 0:
    cat.manage_delObjects( ids)
  
  #-- Add Lexicon
  index_type = container.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
  if index_type == 'ZCTextIndex':
    elements = []
    wordSplitter = Empty()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'HTML aware splitter'
    elements.append(wordSplitter)
    caseNormalizer = Empty()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Case Normalizer'
    elements.append(caseNormalizer)
    stopWords = Empty()
    stopWords.group = 'Stop Words'
    stopWords.name = 'Remove listed and single char words'
    elements.append(stopWords)
    try:
      cat.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Default lexicon', elements)
    except:
      pass


# ------------------------------------------------------------------------------
#  ZMSZCatalogAdapter.recreateCatalog:
# ------------------------------------------------------------------------------
def recreateCatalog(self, zcm, lang):
  
  #-- Create catalog
  cat_id = 'catalog_%s'%lang
  if cat_id in self.objectIds():
    self.manage_delObjects([cat_id])
  cat_title = 'Default catalog'
  vocab_id = 'create_default_catalog_'
  zcatalog = ZCatalog.ZCatalog(cat_id, cat_title, vocab_id, zcm)
  self._setObject(zcatalog.id, zcatalog)
  zcatalog = getattr(self,cat_id)
  
  #-- Add lexicon
  addLexicon( self, zcatalog)
  
  #-- Add columns
  for index_name in ['id','meta_id','absolute_url','zcat_url','zcat_custom']:
    zcatalog.manage_addColumn(index_name)
  
  #-- Add Indexes (incl. Columns)
  index_type = zcm.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
  for attr_id in zcm.getAttrIds():
    index_name = 'zcat_index_%s'%attr_id
    extra = None
    if index_type == 'ZCTextIndex':
      extra = Empty()
      extra.doc_attr = index_name
      extra.index_type = 'Okapi BM25 Rank'
      extra.lexicon_id = 'Lexicon'
    else:
      extra = {}
      extra['default_encoding'] = 'utf-8'
      extra['indexed_fields'] = index_name
      extra['fields'] = [index_name]
      extra['near_distance'] = 5
      extra['splitter_casefolding'] = 1
      extra['splitter_max_len'] = 64
      extra['splitter_separators'] = '.+-_@'
      extra['splitter_single_chars'] = 0
      if index_type == 'TextIndexNG2':
        extra['use_converters'] = 1
        extra['use_normalizer'] = ''
        # setattr(index_extra,'use_stemmer','')
        extra['use_stopwords'] = ''
      elif index_type == 'TextIndexNG3':
        extra['languages'] = (lang,)
        extra['query_parser'] = 'txng.parsers.en'
        extra['index_unknown_languages'] = True
        extra['dedicated_storage'] = True
        extra['use_stopwords'] = False
        extra['use_normalizer'] = False
        extra['use_converters'] = True
        extra['use_stemmer'] = False
    zcatalog.manage_addColumn(index_name)
    zcatalog.manage_addIndex(index_name,index_type,extra)


# ------------------------------------------------------------------------------
#  ZMSZCatalogAdapter.reindex:
# ------------------------------------------------------------------------------
def reindex(node, zcm, lang=None):
  if lang is not None: node.REQUEST.set('lang',lang)
    
  #-- Prepare object.
  for attr_id in zcm.getAttrIds():
    index_name = 'zcat_index_%s'%attr_id
    value = node.attr(attr_id)
    setattr(node,index_name,value)
  
  #-- Reindex object.
  node.default_catalog = 'catalog_%s'%lang
  node.reindex_object()
  
  #-- Unprepare object.
  for attr_id in zcm.getAttrIds():
    index_name = 'zcat_index_%s'%attr_id
    delattr(node,index_name)


# ------------------------------------------------------------------------------
#  ZMSZCatalogAdapter.reindexObject:
# ------------------------------------------------------------------------------
def reindexObject(node, zcm, lang=None):
  
  #-- Check meta-id.
  if node.meta_id in zcm.getIds():
    reindex(node,zcm,lang)
  
  #-- Handle parent-nodes.
  else:
    parentNode = node.getParentNode()
    if parentNode is not None:
      reindexObject(parentNode,zcm,lang)


# ------------------------------------------------------------------------------
#  ZMSZCatalogAdapter.reindexAll:
# ------------------------------------------------------------------------------
def reindexAll(node, zcm, lang=None):
  if lang is not None: node.REQUEST.set('lang',lang)
  
  #-- Check meta-id.
  if node.meta_id in zcm.getIds():
    reindex(node,zcm,lang)
  
  #-- Handle child-nodes.
  for childNode in node.filteredChildNodes(node.REQUEST):
    reindexAll(childNode,zcm,lang)


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
    def search(self, qs, order=None, clients=False):
      rtn = []
      if qs == '':
        return rtn
      
      #-- Process clients.
      if self.getConfProperty('ZCatalog.portalClients',1) == 1 and clients:
        for portalClient in self.getPortalClients():
          for ob in portalClient.objectValues():
            if IZMSCatalogAdapter.IZMSCatalogAdapter in list(zope.interface.providedBy(ob)):
              rtn.extend(ob.search(qs,order,clients))
      
      #-- Search catalog.
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      zcatalog = getattr(self,'catalog_%s'%lang)
      if zcatalog is None:
        return rtn
      
      #-- Get items.
      items = []
      for index in zcatalog.indexes():
        if index.find('zcat_index_')==0:
          query = {index:self.search_encode( qs)}
          qr = zcatalog(query)
          _globals.writeLog( self, "[searchCatalog]: %s=%i"%(str(query),len(qr)))
          for item in qr:
            if item not in items:
              items.extend( qr)
      
      #-- Process results.
      results = []
      for item in items:
        data_record_id = item.data_record_id_
        path = zcatalog.getpath(data_record_id)
        # Append to valid results.
        if len(filter(lambda x: x[1]['path']==path, results)) == 0:
          result = {}
          result['path'] = path
          result['score'] = intValue(item.data_record_score_)
          result['normscore'] = intValue(item.data_record_normalized_score_)
          for column in zcatalog.schema():
            k = column
            if k.find('zcat_index_')==0:
              k = k[len('zcat_index_'):]
            result[k] = getattr(item,column,None)
          results.append((item.data_record_score_,result))
      
      #-- Sort objects.
      results.sort()
      results.reverse()
      
      #-- Append objects.
      rtn.extend(map(lambda ob: ob[1],results))
      
      #-- Return objects in correct sort-order.
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex_object:
    # --------------------------------------------------------------------------
    def reindex_object(self, o):
      pass


    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self, clients=False):
      message = ''
      
      REQUEST = self.REQUEST
      container = self.getDocumentElement()
      for lang in container.getLangIds():
        REQUEST.set('lang',lang)
        
        #-- Recreate catalog.
        recreateCatalog(container,self,lang)
        
        #-- Find items to catalog.
        reindexAll(container,self,lang)
        
      message += 'Catalog %s indexed successfully.'%container.getHome().id
      
      #-- Process clients.
      if clients:
        for portalClient in container.getPortalClients():
          for adapter in portalClient.getCatalogAdapters():
            message += adapter.reindex_all(clients)
      
      # Return with message.
      return message


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


    ############################################################################
    #  ZMSZCatalogAdapter.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """ ZMSZCatalogAdapter.manage_changeProperties: """
        message = ''
        
        # Change.
        # -------
        if btn == 'Save':
          self.setConfProperty('ZMS.CatalogAwareness.active',REQUEST.get('catalog_awareness_active')==1)
          self._ids = REQUEST.get('ids',[])
          self._attr_ids = REQUEST.get('attr_ids',[])
          message = self.getZMILangStr('MSG_CHANGED')
        
        # Reindex.
        # -------
        elif btn == 'Reindex':
          clients = 'catalog_portal_clients' in REQUEST.get('options',[])
          message += self.reindex_all(clients=clients)
        
        # Remove.
        # -------
        elif btn == 'Remove':
          ids = REQUEST.get('ids',[])
          if len(ids) > 0:
            self.manage_delObjects(ids)
          message = self.getZMILangStr('MSG_DELETED')%len(ids)
        
        # Return with message.
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
