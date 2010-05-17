################################################################################
# _zcatalogmanager.py
#
# $Id: _zcatalogmanager.py,v 1.8 2004/11/30 20:03:17 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.8 $
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
import new
import re
import sys
from Products.ZCatalog import ZCatalog, CatalogAwareness
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
        s += search_string(i)
    elif type(v) is dict:
      for k in v.keys():
        i = v[k]
        s += search_string(i)
  return s


# ------------------------------------------------------------------------------
#  _zcatalogmanager.search_quote:
#
#  Remove HTML-Tags from given string.
# ------------------------------------------------------------------------------
def search_quote(s, maxlen=255, tag='&middot;'):
  # remove all tags.
  s = re.sub( '<(.*?)>', '', s)
  # limit characters.
  if len(s) > maxlen:
    blank = s.find(' ',maxlen)
    s = s[:blank] + tag * 3
  # return quoted search string.
  return s

# ------------------------------------------------------------------------------
#  _zcatalogmanager.addLexicon:
# ------------------------------------------------------------------------------
def addLexicon( self, cat):
  
  #-- Remove Lexicon
  ids = cat.objectIds( ['ZCTextIndex Lexicon'])
  if len( ids) > 0:
    cat.manage_delObjects( ids)
  
  #-- Add Lexicon
  index_type = self.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
  if index_type == 'ZCTextIndex':
    elem = []
    wordSplitter = Empty()
    wordSplitter.group = 'Word Splitter'
    wordSplitter.name = 'HTML aware splitter'
    caseNormalizer = Empty()
    caseNormalizer.group = 'Case Normalizer'
    caseNormalizer.name = 'Case Normalizer'
    stopWords = Empty()
    stopWords.group = 'Stop Words'
    stopWords.name = 'Remove listed and single char words'
    elem.append(wordSplitter)
    elem.append(caseNormalizer)
    elem.append(stopWords)
    try:
      cat.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Default lexicon', elem)
    except:
      pass


# --------------------------------------------------------------------------
#  _zcatalogmanager.getCatalog:
# --------------------------------------------------------------------------
def getCatalog(self, lang):
  context = self.getDocumentElement()
  cat_id = 'catalog_%s'%lang
  obs = filter( lambda x: x.id==cat_id, context.objectValues( [ 'ZCatalog']))
  if len(obs) == 0:
    catalog = getattr( self, cat_id, None)
    if catalog is not None and catalog.meta_type == 'ZCatalog':
      obs = [catalog]
  if len(obs) == 0:
    return self.recreateCatalog(lang)
  return obs[0]


################################################################################
################################################################################
###
###   class ZCatalogItem
###
################################################################################
################################################################################
class ZCatalogItem(CatalogAwareness.CatalogAware): 

    # --------------------------------------------------------------------------
    #  ZCatalogItem.txng_get_key:
    # --------------------------------------------------------------------------
    def txng_get_key(self):
      keys = []
      for key in self.getObjAttrs().keys():
        obj_attr = self.getObjAttr(key)
        datatype = obj_attr['datatype_key']
        if datatype == _globals.DT_FILE:
          keys.append( key)
        if len( keys) == 1:
          return keys[ 0]
      return None
      

    # --------------------------------------------------------------------------
    #  ZCatalogItem.txng_get:
    #
    #  This code provides a hook called txng_get(), when you add a TextIndexNG 
    #  index on SearchableText the indexer 'senses' that you provided your 
    #  content with the hook and automagically uses it.
    # --------------------------------------------------------------------------
    def txng_get(self, attr=('SearchableText',)):
      """Special searchable text source for text indexng2"""
      key = self.txng_get_key()
      if key is not None:
        lang = attr
        if type( lang) is tuple or type( lang) is list:
          lang = lang[0]
        lang = lang[lang.rfind('_')+1:]
        req = {'lang' : lang}
        file = self.getObjProperty( key, req)
        if file is not None:
          source = file.getData()
          mimetype = file.getContentType()
          encoding = 'utf-8'
          return (source, mimetype, encoding)


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
      try:
        s = unicode( s, 'utf-8').encode( 'latin-1')
        # German Umlauts in capital letters.
        mapping = {
          '\xc4':'\xe4', # Ae
          '\xd6':'\xf6', # Oe
          '\xdc':'\xfc', # Ue
        }
        for capital in mapping.keys():
          letter = mapping[ capital]
          while s.find( capital) >= 0:
            s = s.replace( capital, letter)
      except ( UnicodeDecodeError, UnicodeEncodeError):
        _globals.writeError(self,"[search_encode]")
        try:
          v = str(sys.exc_value)
          STR_POSITION = ' position '
          i = v.find(STR_POSITION)
          if i > 0:
            v = v[i+len(STR_POSITION):]
            if v.find('-') > 0:
              l = int( v[:v.find('-')])
              h = int( v[v.find('-')+1:v.find(':')])
            else:
              l = int( v[:v.find(':')])
              h = l
            ln = max( l - 20, 0)
            hn = min( h + 20, len(s))
            print ">>>>>",s[ln:hn]
            print ">>>>>"," "*(l-ln)+"^"*(h-l+1)
        except:
          _globals.writeError(self,"[search_encode]: ignore exception")
      return s


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
      key = self.txng_get_key()
      if key is not None:
        file = self.getObjProperty( key, REQUEST)
        if file is not None:
          source = file.getData()
          mimetype = file.getContentType()
          encoding = 'utf-8'
      return source


    ############################################################################
    ###
    ###  Metadate: Indices / Columns
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_data:
    # --------------------------------------------------------------------------
    def zcat_data( self, lang):
      zcat = self.catalogData( {'lang':lang})
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_text:
    # --------------------------------------------------------------------------
    def zcat_text( self, lang):
      req = {'lang':lang}
      zcat = self.catalogText( req)
      zcat = self.search_encode( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_date:
    # --------------------------------------------------------------------------
    def zcat_date( self, lang): 
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
    def zcat_title( self, lang):
      req = {'lang':lang}
      zcat = self.getTitle( req)
      zcat = self.search_encode( zcat)
      zcat = self.search_quote( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_summary:
    # --------------------------------------------------------------------------
    def zcat_summary( self, lang):
      req = {'lang':lang}
      zcat = self.getObjProperty( 'attr_dc_description', req)
      zcat = self.search_encode( zcat)
      zcat = self.search_quote( zcat)
      return zcat

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_url:
    # --------------------------------------------------------------------------
    def zcat_url( self, lang):
      req = {'lang':lang}
      txng_key = self.txng_get_key()
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
        if _globals.debug( self):
          _globals.writeLog( self, '[synchronizeSearch]')
        for ref_by in self.getRefByObjs(REQUEST):
          ref_ob = self.getLinkObj(ref_by,REQUEST)
          if ref_ob is not None and \
             ref_ob. meta_type == 'ZMSLinkElement' and \
             ref_ob.isEmbedded( REQUEST) and not \
             ref_ob.isEmbeddedRecursive( REQUEST):
            if not forced or ref_ob.getHome().id != self.getHome().id:
              ref_ob.synchronizeSearch( REQUEST=REQUEST, forced=1)
        lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
        ob = self.getCatalogItem()
        if ob is not None:
          if not forced:
            # Recreate object-methods for indices.
            index_name = 'zcat_text'
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_text.func_code, {}, index_name, (lang,)))
            index_name = 'zcat_date'
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_date.func_code, {}, index_name, (lang,)))
            index_name = 'zcat_title'
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_title.func_code, {}, index_name, (lang,)))
            index_name = 'zcat_summary'
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_summary.func_code, {}, index_name, (lang,)))
            index_name = 'zcat_url'
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_url.func_code, {}, index_name, (lang,)))
            if self.getConfProperty('ZCatalog.TextIndexNG',0)==1:
              index_name = 'zcat_data'
              setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_data.func_code, {}, index_name, (lang,)))
          # Reindex object.
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
      b = b or (self.getConfProperty('ZCatalog.TextIndexNG',0)==1 and self.txng_get_key() is not None)
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
      # Recurs.
      for ob in filter( lambda x: x.isActive(REQUEST), self.getChildNodes()):
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
      cat_id = 'catalog_%s'%lang
      obs = filter( lambda x: x.id==cat_id, context.objectValues( [ 'ZCatalog']))
      if len(obs) == 0:
        catalog = getattr( self, cat_id, None)
        if catalog is not None and catalog.meta_type == 'ZCatalog':
          obs = [catalog]
      if len( obs) == 0:
        cat_title = 'Default catalog'
        vocab_id = 'create_default_catalog_'
        zcatalog = ZCatalog.ZCatalog(cat_id, cat_title, vocab_id, context)
        context._setObject(zcatalog.id, zcatalog)
        zcatalog = getCatalog(self,lang)
      else:
        zcatalog = obs[ 0]
      
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
      setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_text.func_code, {}, index_name, (lang,)))
      index_type = self.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
      index_extras = None
      if index_type == 'ZCTextIndex':
        index_extras = Empty()
        index_extras.doc_attr = index_name
        index_extras.index_type = 'Okapi BM25 Rank'
        index_extras.lexicon_id = 'Lexicon'
      zcatalog.manage_addColumn(index_name)
      zcatalog.manage_addIndex(index_name,index_type,index_extras)
      message += ", "+index_name
      # Date (Column)
      index_name = 'zcat_date'
      setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_date.func_code, {}, index_name, (lang,)))
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Title (Column)
      index_name = 'zcat_title'
      setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_title.func_code, {}, index_name, (lang,)))
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Summary (Column)
      index_name = 'zcat_summary'
      setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_summary.func_code, {}, index_name, (lang,)))
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Url (Column)
      index_name = 'zcat_url'
      setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_url.func_code, {}, index_name, (lang,)))
      zcatalog.manage_addColumn(index_name)
      message += ", "+index_name
      # Data (Index)
      index_type = None
      for k in [ 'ZCTextIndex', 'TextIndexNG2', 'TextIndexNG3']:
        if k in index_types: index_type = k
      if self.getConfProperty('ZCatalog.TextIndexNG',0)==1:
        index_name = 'zcat_data'
        setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_data.func_code, {}, index_name, (lang,)))
        index_extras = Empty()
        if index_type == 'ZCTextIndex':
          index_extras.doc_attr = index_name
          index_extras.index_type = 'Okapi BM25 Rank'
          index_extras.lexicon_id = 'Lexicon'
        else:
          index_extras.default_encoding = 'utf-8'
          index_extras.indexed_fields = index_name
          index_extras.near_distance = 5
          index_extras. splitter_casefolding = 1
          index_extras.splitter_max_len = 64
          index_extras.splitter_separators = '.+-_@'
          index_extras.splitter_single_chars = 0
          if index_type == 'TextIndexNG2':
            setattr(index_extras,'use_converters',1)
            setattr(index_extras,'use_normalizer','')
            # setattr(index_extras,'use_stemmer','')
            setattr(index_extras,'use_stopwords','')
          elif index_type == 'TextIndexNG3':
            setattr(index_extras,'use_converters',True)
            setattr(index_extras,'use_normalizer',False)
            setattr(index_extras,'use_stemmer',False)
            setattr(index_extras,'use_stopwords',False)
        zcatalog.manage_addIndex(index_name,index_type,index_extras)
        message += ", "+index_name+"("+index_type+")"
      
      #-- Return message.
      return message


    # --------------------------------------------------------------------------
    #  ZCatalogManager.getCatalogQueryString:
    # --------------------------------------------------------------------------
    def getCatalogQueryString(self, raw, option='AND'):
      qs = []
      i = 0
      for si in raw.split('"'):
        si = si.strip()
        if si:
          if i % 2 == 0:
            for raw_item in si.split(' '):
              raw_item = raw_item.strip()
              if len(raw_item) > 1:
                raw_item = raw_item.replace('-','* AND *')
                if not raw_item.endswith('*'):
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
      items = []
      for zcindex in zcatalog.indexes():
        if zcindex.find('zcat_')==0:
          d = {}
          d['meta_type'] = zcat_meta_types
          if zcindex.find('zcat_data')==0:
            d[zcindex] = search_query
          else:
            d[zcindex] = self.search_encode( search_query)
          if _globals.debug( self):
            _globals.writeLog( self, "[searchCatalog]: %s=%s"%(zcindex,d[zcindex]))
          qr = zcatalog(d)
          if _globals.debug( self):
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
            result['url'] = path + '/' + getattr(item,'zcat_url','')
            results.append((result[order_by],result))
      
      #-- Sort objects.
      results.sort()
      results.reverse()
      
      #-- Append objects.
      rtn.extend(map(lambda ob: ob[1],results))
      
      #-- Return objects in correct sort-order.
      return rtn

################################################################################
