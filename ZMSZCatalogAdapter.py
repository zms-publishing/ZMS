################################################################################
# ZMSMetamodelProvider.py
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
def addLexicon( self, cat):
  
  #-- Remove Lexicon
  ids = cat.objectIds( ['ZCTextIndex Lexicon','ZCTextIndex Unicode Lexicon'])
  if len( ids) > 0:
    cat.manage_delObjects( ids)
  
  #-- Add Lexicon
  index_type = self.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
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
    #  ZMSZCatalogAdapter.search:
    # --------------------------------------------------------------------------
    def search(self, qs, order, clients=False):
      rtn = []
      if search_query == '':
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
      for zcindex in zcatalog.indexes():
        if zcindex.find('zcat_')==0:
          d = {}
          d['meta_type'] = ['ZMSCustom']
          if zcindex.find('zcat_data')==0:
            d[zcindex] = search_query
          else:
            d[zcindex] = self.search_encode( search_query)
          _globals.writeLog( self, "[searchCatalog]: %s=%s"%(zcindex,d[zcindex]))
          qr = zcatalog(d)
          _globals.writeLog( self, "[searchCatalog]: qr=%i"%len( qr))
          items.extend( qr)
      
      #-- Sort order.
      if int(search_order_by)==1:
        order_by = 'score'
      else:
        order_by = 'time'
      
      #-- Process results.
      results = []
      for item in items:
        data_record_id = item.data_record_id_
        path = zcatalog.getpath(data_record_id)
        # Append to valid results.
        if len(filter(lambda x: x[1]['path']==path, results)) == 0:
          result = {}
          result['score'] = intValue(item.data_record_score_)
          result['normscore'] = intValue(item.data_record_normalized_score_)
          result['time'] = getattr(item,'zcat_date',None)
          result['path'] = path
          if REQUEST.get('search_ob',True):
            ob = self.getCatalogPathObject( path)
            append = ob is not None
            if append:
              for o in ob.breadcrumbs_obj_path():
                append = append and o.isActive(REQUEST)
            if append:
              result['ob'] = ob
              result['url'] = ob.getDeclUrl(REQUEST) + '/' + ob.zcat_url(lang)
              results.append((result[order_by],result))
          else:
            result['title'] = getattr(item,'zcat_title','')
            result['summary'] = getattr(item,'zcat_summary','')
            result['zcat_url'] = getattr(item,'zcat_url','')
            result['url'] = (path + '/' + getattr(item,'zcat_url','')).replace('//','/')
            results.append((result[order_by],result))
      
      #-- Sort objects.
      results.sort()
      results.reverse()
      
      #-- Append objects.
      rtn.extend(map(lambda ob: ob[1],results))
      
      #-- Return objects in correct sort-order.
      return rtn

    # --------------------------------------------------------------------------
    #  ZMSZCatalogAdapter.reindex:
    # --------------------------------------------------------------------------
    def reindex(self, clients=False):
      message = ''
      
      REQUEST = self.REQUEST
      for lang in self.getLangIds():
        REQUEST.set('lang',lang)
        
        #-- Recreate catalog.
        message += self.recreateCatalog(lang)+'<br/>'
        
        #-- Find items to catalog.
        message += self.reindexCatalogItem(REQUEST)+'<br/>'
      
      message += 'Catalog %s indexed successfully.'%self.getHome().id
      
      #-- Process clients.
      if clients:
        for portalClient in self.getPortalClients():
          for ob in portalClient.objectValues():
            if IZMSCatalogAdapter.IZMSCatalogAdapter in list(zope.interface.providedBy(ob)):
              message += ob.reindex(clients)
      
      # Return with message.
      return message


    # --------------------------------------------------------------------------
    #  ZCatalogManager.recreateCatalog:
    #
    #  Recreates catalog.
    # --------------------------------------------------------------------------
    def recreateCatalog(self, lang):
      message = ''
      
      #-- Get catalog
      cat_id = 'catalog_%s'%lang
      zcatalog = getattr(self,cat_id,None)
      if zcatalog is None:
        cat_title = 'Default catalog'
        vocab_id = 'create_default_catalog_'
        zcatalog = ZCatalog.ZCatalog(cat_id, cat_title, vocab_id, self)
        self._setObject(zcatalog.id, zcatalog)
        zcatalog = getattr(self,cat_id,None)
      
      #-- Add lexicon
      addLexicon( self, zcatalog)
      
      #-- Clear catalog
      zcatalog.manage_catalogClear()
      
      #-- Delete indexes from catalog
      index_names = []
      l = []
      l.extend( zcatalog.schema())
      l.extend( zcatalog.indexes())
      for index_name in l:
        if index_name not in index_names and \
           (index_name.find( 'zcat_') == 0 or index_name == 'meta_id'):
          try:
            zcatalog.manage_delColumn( [ index_name])
          except:
            _globals.writeError(self,"[recreateCatalog]: Can't delete column '%s' from catalog"%index_name)
          try:
            zcatalog.manage_delIndex( [ index_name])
          except:
            _globals.writeError(self,"[recreateCatalog]: Can't delete index '%s' from catalog"%index_name)
          index_names.append( index_name)
      
      #-- Get index types.
      index_types = []
      for index in zcatalog.Indexes.filtered_meta_types():
        index_types.append(index['name'])
      
      #-- (Re-)create indexes on catalog
      message += "Create Index: "
      index_name = 'meta_id'
      zcatalog.manage_addColumn(index_name)
      message += index_name
      # Text (Index & Column)
      index_name = 'zcat_text'
      zcatalog.manage_addColumn(index_name)
      index_type = self.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
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
      zcatalog.manage_addIndex(index_name,index_type,extra)
      message += ", "+index_name+"("+index_type+")"
      # Date (Column)
      index_name = 'zcat_date'
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Title (Column)
      index_name = 'zcat_title'
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Summary (Column)
      index_name = 'zcat_summary'
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Url (Column)
      index_name = 'zcat_url'
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Data (Index)
      index_type = None
      for k in [ 'ZCTextIndex', 'TextIndexNG2', 'TextIndexNG3']:
        if k in index_types:
          index_type = k
      if self.getConfProperty('ZCatalog.TextIndexNG',0)==1:
        index_name = 'zcat_data'
        extra = {}
        if index_type == 'ZCTextIndex':
          extra['doc_attr'] = index_name
          extra['index_type'] = 'Okapi BM25 Rank'
          extra['lexicon_id'] = 'Lexicon'
        else:
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
        zcatalog.manage_addIndex(index_name,index_type,extra)
        message += ", "+index_name+"("+index_type+")"
      
      #-- Return message.
      return message


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
        if btn == 'Change':
          self.setConfProperty('ZMS.CatalogAwareness.active',REQUEST.get('catalog_awareness_active')==1)
          message = self.getZMILangStr('MSG_CHANGED')
        
        # Reindex.
        # -------
        elif btn == 'Reindex':
          clients = 'catalog_portal_clients' in REQUEST.get('options',[])
          message += self.reindex(clients=clients)
        
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
