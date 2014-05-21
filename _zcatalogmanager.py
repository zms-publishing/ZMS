################################################################################
# _zcatalogmanager.py
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
from Products.ZCatalog import ZCatalog, CatalogAwareness
from zope.interface import implements
import re
import sys
# Product Imports.
import _globals


# ------------------------------------------------------------------------------
#  _zcatalogmanager.Empty
# ------------------------------------------------------------------------------
class Empty: pass


# ------------------------------------------------------------------------------
#  _zcatalogmanager.zcat_meta_types
# ------------------------------------------------------------------------------
zcat_meta_types = ['ZMS','ZMSCustom']


# ------------------------------------------------------------------------------
#  _zcatalogmanager.intValue:
# ------------------------------------------------------------------------------
def intValue(v):
  try:
    i = int(v)
  except:
    i = 0
  return i


# ------------------------------------------------------------------------------
#  _zcatalogmanager.search_string:
#
#  Search string of given value.
# ------------------------------------------------------------------------------
def search_string(v):
  s = ''
  if v is not None:
    if type(v) is str and len(v) > 0:
      s += v + ' '
    elif type(v) is list:
      for i in v:
        s += search_string(i) + ' '
    elif type(v) is dict:
      for k in v.keys():
        i = v[k]
        s += search_string(i) + ' '
  return s


# ------------------------------------------------------------------------------
#  _zcatalogmanager.search_quote:
#
#  Remove HTML-Tags from given string.
# ------------------------------------------------------------------------------
def search_quote(s, maxlen=255, tag='&middot;'):
  # remove all tags.
  s = re.sub( '<script((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</script>', '', s)
  s = re.sub( '<style((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</style>', '', s)
  s = re.sub( '<((.|\n|\r|\t)*?)>', '', s)
  # limit characters.
  if len(s) > maxlen:
    if s[:maxlen].rfind('&') >= 0 and not s[:maxlen].rfind('&') < s[:maxlen].rfind(';') and \
       s[maxlen:].find(';') >= 0 and not s[maxlen:].find(';') > s[maxlen:].find('&'):
      maxlen = maxlen + s[maxlen:].find(';')
    if s[:maxlen].endswith(chr(195)) and maxlen < len(s):
      maxlen += 1
    s = s[:maxlen] + tag * 3
  # return quoted search string.
  return s

# ------------------------------------------------------------------------------
#  _zcatalogmanager.addLexicon:
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

# --------------------------------------------------------------------------
#  _zcatalogmanager.getCatalog:
# --------------------------------------------------------------------------
def getCatalog(self, lang):
  context = self.getDocumentElement()
  cat_id = 'catalog_%s'%lang
  obs = filter( lambda x: x.id==cat_id, context.objectValues( [ 'ZCatalog']))
  if obs:
    return obs[0]
  else:
    return getattr( self, cat_id, None)


################################################################################
################################################################################
###
###   class ZCatalogItem
###
################################################################################
################################################################################
class ZCatalogItem(CatalogAwareness.CatalogAware):

    """
    TextIndexNG3
    """
    try:
      
      from textindexng.interfaces import IIndexableContent
      implements(IIndexableContent)
      
      def indexableContent(self, fields):
        from textindexng.content import IndexContentCollector as ICC
        icc = ICC()
        default_language = self.REQUEST.get('lang',self.getPrimaryLanguage())
        default_encoding = 'utf-8'
        
        for f in fields:
          v = getattr(self, f, None)
          if not v: continue
          
          if f in ['zcat_data']:
            
            # unpack result triple
            source, mimetype, encoding = v()
            icc.addBinary(f, source, mimetype, encoding, default_language)
            
          elif f in ['zcat_text']:
            v = v()
            
            # accept only a string/unicode string
            if not isinstance(v, basestring):
                raise TypeError('Value returned for field "%s" must be string or unicode (got: %s, %s)' % (f, repr(v), type(v)))
            
            if isinstance(v, str):
                v = unicode(v, default_encoding, 'ignore')
            
            icc.addContent(f, v, default_language)
        
        return icc
      
    except:
      pass

    # --------------------------------------------------------------------------
    #  ZCatalogItem.search_quote:
    #
    #  Remove HTML-Tags.
    # --------------------------------------------------------------------------
    def search_quote(self, s, maxlen=255, tag='&middot;'):
      return search_quote(s,maxlen,tag)


    # --------------------------------------------------------------------------
    #  ZCatalogItem.search_encode:
    #
    #  Encodes given string.
    # --------------------------------------------------------------------------
    def search_encode(self, s):
      return _globals.umlaut_quote(self, s)


    # --------------------------------------------------------------------------
    #  ZCatalogItem.getCatalogNavUrl:
    #
    #  Returns catalog-navigation url.
    # --------------------------------------------------------------------------
    def getCatalogNavUrl(self, REQUEST):
      return self.url_inherit_params(REQUEST['URL'],REQUEST,['qs'])


    # --------------------------------------------------------------------------
    #  ZCatalogItem.catalogText:
    #
    #  Catalog text.
    # --------------------------------------------------------------------------
    def catalogText(self, REQUEST):
      v = ''
      
      # Custom hook (overwrite).
      if 'catalogText' in self.getMetaobjAttrIds(self.meta_id):
        value = self.getObjProperty('catalogText',REQUEST)
        value = search_string(value)
        v += value
      
      else:
        
        ##### Trigger custom catalogText-Contributors (if there is one) ####
        l = _globals.triggerEvent( self, 'catalogTextContrib', REQUEST=REQUEST)
        if l:
          v += ' '.join(l)
        
        # Attributes.
        for key in filter( lambda x: x.find('_') != 0, self.getObjAttrs().keys()):
          obj_attr = self.getObjAttr(key)
          if obj_attr['xml']:
            datatype = obj_attr['datatype_key']
            if datatype in _globals.DT_STRINGS or \
               datatype == _globals.DT_DICT or \
               datatype == _globals.DT_LIST:
              value = self.getObjAttrValue(obj_attr,REQUEST)
              value = search_string(value)
              # Increase weight of attributes!
              if obj_attr['id'].find('title') == 0:
                value = value * 5
              elif obj_attr['id'].find('attr_dc_') == 0:
                value = value * 3
              v += value
      for ob in filter( lambda x: x.isActive(REQUEST), self.getChildNodes()):
        if not ob.isCatalogItem():
          v += ob.catalogText(REQUEST)
      return v


    # --------------------------------------------------------------------------
    #  ZCatalogItem.catalogData:
    #
    #  Catalog data.
    # --------------------------------------------------------------------------
    def catalogData(self, REQUEST):
      source = ''
      mt, enc = 'content/unknown', ''
      key = self.zcat_data_key()
      if key is not None:
        file = self.getObjProperty( key, REQUEST)
        if file is not None:
          source = file.getData()
          mt, enc = file.getContentType(), 'utf-8'
      return source, mt, enc


    ############################################################################
    ###
    ###  Metadate: Indices / Columns
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_data_key:
    # --------------------------------------------------------------------------
    def zcat_data_key(self):
      ids = self.getMetaobjAttrIds(self.meta_id,types=[_globals.DT_FILE])
      if len(ids) == 1:
        return ids[ 0]
      return None

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_data:
    # --------------------------------------------------------------------------
    def zcat_data( self, lang=None):
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      source, mimetype, encoding = self.catalogData( {'lang':lang})
      return source, mimetype, encoding

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_text:
    # --------------------------------------------------------------------------
    def zcat_text( self, lang=None):
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      zcat = self.catalogText( req)
      zcat = self.search_encode( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_date:
    # --------------------------------------------------------------------------
    def zcat_date( self, lang=None): 
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      zcat = self.getObjProperty('attr_dc_date',req)
      if zcat is None or zcat == '':
        zcat = self.getObjProperty('change_dt',req)
        for ob in self.filteredChildNodes( req, self.PAGEELEMENTS):
          ob_change_dt = ob.getObjProperty('change_dt',req)
          if ob_change_dt > zcat:
            zcat = ob_change_dt
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_title:
    # --------------------------------------------------------------------------
    def zcat_title( self, lang=None):
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      zcat = self.getTitle( req)
      zcat = self.search_encode( zcat)
      zcat = self.search_quote( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_summary:
    # --------------------------------------------------------------------------
    def zcat_summary( self, lang=None):
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      zcat = self.getObjProperty( 'attr_dc_description', req)
      zcat = self.search_encode( zcat)
      zcat = self.search_quote( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_url:
    # --------------------------------------------------------------------------
    def zcat_url( self, lang=None):
      if lang is None:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      txng_key = self.zcat_data_key()
      txng_value = None
      if txng_key is not None:
        txng_value = self.getObjProperty( txng_key, req)
      if txng_value is not None:
        zcat = txng_value.getHref( req)
        zcat = '/'.join(zcat.split('/')[-2:])
      else:
        zcat = 'index_%s.html'%lang
      return zcat


    # --------------------------------------------------------------------------
    #  ZCatalogItem.synchronizeSearch:
    # --------------------------------------------------------------------------
    def synchronizeSearch(self, REQUEST, forced=0):
      if self.getConfProperty('ZMS.CatalogAwareness.active',1) or forced:
        _globals.writeLog( self, '[synchronizeSearch]')
        for ref_by in self.getRefByObjs(REQUEST):
          ref_ob = self.getLinkObj(ref_by,REQUEST)
          if ref_ob is not None and \
             ref_ob. meta_type == 'ZMSLinkElement' and \
             ref_ob.isEmbedded( REQUEST) and not \
             ref_ob.isEmbeddedRecursive( REQUEST):
            if not forced or ref_ob.getHome().id != self.getHome().id:
              ref_ob.synchronizeSearch( REQUEST=REQUEST, forced=forced)
        lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
        # Reindex object.
        ob = self.getCatalogItem()
        if ob is not None:
          ob.default_catalog = 'catalog_%s'%lang
          ob.reindex_object()


    # --------------------------------------------------------------------------
    #  ZCatalogItem.isCatalogItem:
    #
    #  Returns true if this is a catalog item.
    # --------------------------------------------------------------------------
    def isCatalogItem(self):
      b = False
      b = b or (self.isPage() or self.meta_id == 'ZMSFile')
      b = b or (self.getConfProperty('ZCatalog.TextIndexNG',0)==1 and self.zcat_data_key() is not None)
      return b


    # --------------------------------------------------------------------------
    #  ZCatalogItem.getCatalogItem:
    # --------------------------------------------------------------------------
    def getCatalogItem(self):
      ob = self
      while ob is not None:
        if ob.isCatalogItem():
          break
        ob = ob.getParentNode()
      return ob


    # --------------------------------------------------------------------------
    #  ZCatalogItem.reindexCatalogItem:
    #
    #  Reindex catalog item.
    # --------------------------------------------------------------------------
    def reindexCatalogItem(self, REQUEST):
      message = ''
      # Process catalog-item.
      if self.isCatalogItem():
        self.synchronizeSearch(REQUEST=REQUEST,forced=1)
      # Recurse.
      for ob in filter( lambda x: x.isActive(REQUEST), self.filteredChildNodes(REQUEST)):
        ob.reindexCatalogItem(REQUEST)
      # Return with message.
      return message


################################################################################
################################################################################
###
###   class ZCatalogManager
###
################################################################################
################################################################################
class ZCatalogManager:

    # --------------------------------------------------------------------------
    #  ZCatalogManager.reindexCatalog:
    #
    #  Reindex catalog.
    # --------------------------------------------------------------------------
    def reindexCatalog(self, REQUEST, clients=False):
      message = ''
      
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
          message += portalClient.reindexCatalog( REQUEST, clients)
      
      # Return with message.
      return message


    # --------------------------------------------------------------------------
    #  ZCatalogManager.recreateCatalog:
    #
    #  Recreates catalog.
    # --------------------------------------------------------------------------
    def recreateCatalog(self, lang):
      message = ''
      context = self.getDocumentElement()
      
      #-- Get catalog
      zcatalog = getCatalog( self, lang)
      if zcatalog is None:
        cat_id = 'catalog_%s'%lang
        cat_title = 'Default catalog'
        vocab_id = 'create_default_catalog_'
        zcatalog = ZCatalog.ZCatalog(cat_id, cat_title, vocab_id, context)
        context._setObject(zcatalog.id, zcatalog)
        zcatalog = getCatalog( self, lang)
      
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


    # --------------------------------------------------------------------------
    #  ZCatalogManager.getCatalogQueryString:
    # --------------------------------------------------------------------------
    def getCatalogQueryString(self, raw, option='AND', only_words=False):
      qs = []
      i = 0
      for si in raw.split('"'):
        si = si.strip()
        if si:
          if i % 2 == 0:
            for raw_item in si.split(' '):
              raw_item = raw_item.strip()
              if len(raw_item) > 1 and not raw_item.upper() in ['AND','OR']:
                raw_item = raw_item.replace('-','* AND *')
                if not only_words and not raw_item.endswith('*'):
                  raw_item += '*'
                if raw_item not in qs:
                  qs.append( raw_item)
          else:
            raw_item = '"%s"'%si
            if raw_item not in qs:
              qs.append( raw_item)
        i += 1
      return (' %s '%option).join(filter( lambda x: len(x.strip())>0, qs))


    # --------------------------------------------------------------------------
    #  ZCatalogManager.getCatalogPathObject:
    #
    #  Returns object from catalog-path.
    # --------------------------------------------------------------------------
    def getCatalogPathObject(self, path):
      ob = self.getHome()
      l = path.split( '/')
      if ob.id not in l:
        docElmnt = self.getDocumentElement()
        if docElmnt.id not in l:
          ob = docElmnt
      else:
        l = l[ l.index(ob.id)+1:]
      for id in l:
         if len( id) > 0 and ob is not None:
          ob = getattr(ob,id,None)
      return ob


    # --------------------------------------------------------------------------
    #  ZCatalogManager.submitCatalogQuery:
    #
    #  Submits query to catalog.
    # --------------------------------------------------------------------------
    def submitCatalogQuery(self, search_query, search_order_by, search_meta_types, search_clients, REQUEST):
      
      #-- Initialize local variables.
      rtn = []
      if search_query == '':
        return rtn
      
      #-- Process clients.
      if self.getConfProperty('ZCatalog.portalClients',1) == 1 and search_clients == 1:
        for portalClient in self.getPortalClients():
          rtn.extend(portalClient.submitCatalogQuery( search_query, search_order_by, search_meta_types, search_clients, REQUEST))
      
      #-- Search catalog.
      lang = REQUEST['lang']
      zcatalog = getCatalog(self,lang)
      if zcatalog is None:
        return rtn
      items = []
      for zcindex in zcatalog.indexes():
        if zcindex.find('zcat_')==0:
          d = {}
          d['meta_type'] = zcat_meta_types
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
        if (len(search_meta_types) == 0 or item.meta_id in search_meta_types) and \
           (len(filter(lambda x: x[1]['path']==path, results)) == 0):
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

################################################################################
