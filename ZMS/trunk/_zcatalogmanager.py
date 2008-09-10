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
#  _zcatalogmanager.addVocabulary:
# ------------------------------------------------------------------------------
def addVocabulary( self, cat):
  from Products.ZCatalog import Vocabulary
  
  #-- Remove Default-Vocabulary
  ids = cat.objectIds( ['Vocabulary'])
  if len( ids) > 0:
    cat.manage_delObjects( ids)
  
  #-- Add ISO 8859-1 Vocabulary
  # see ZCatalogs with Umlauts
  # http://www.zope.org/Members/strobl/HowTos/Iszcatalog
  globbing = 1
  splitter = "ISO_8859_1_Splitter"
  voc = Vocabulary.Vocabulary( "Vocabulary", "Default vocabulary", globbing, splitter)
  cat._setObject( voc.id, voc)

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
    #	ZCatalogItem.search_quote:
    #
    #	Remove HTML-Tags.
    # --------------------------------------------------------------------------
    def search_quote(self, s, maxlen=255, tag='&middot;'):
      return search_quote(s,maxlen,tag)


    # --------------------------------------------------------------------------
    #	ZCatalogItem.search_encode:
    #
    #	Encodes given string.
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
        _globals.writeException(self,"[search_encode]")
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
      # Custom hook.
      if 'catalogText' in self.getMetaobjAttrIds(self.meta_id):
        value = self.getObjProperty('catalogText',REQUEST)
        value = search_string(value)
        v += value
      else:
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
      for ob in self.getChildNodes():
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
      zcat = self.catalogText( {'lang':lang})
      zcat = self.search_encode( zcat)
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
            index_name = 'zcat_text_%s'%lang
            setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_text.func_code, {}, index_name, (lang,)))
            if self.getConfProperty('ZCatalog.TextIndexNG',0)==1:
              index_name = 'zcat_data_%s'%lang
              setattr( ZCatalogItem, index_name, new.function(ZCatalogItem.zcat_data.func_code, {}, index_name, (lang,)))
          # Reindex object.
          ob.default_catalog = 'catalog'
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
      if self.isCatalogItem():
        for lang in self.getLangIds():
          REQUEST.set('lang',lang)
          self.synchronizeSearch(REQUEST=REQUEST,forced=1)
      for ob in self.getChildNodes():
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
    #  ZCatalogManager.getCatalog:
    #
    #  Returns catalog.
    # --------------------------------------------------------------------------
    def getCatalog(self):
      context = self.getDocumentElement()
      obs = context.objectValues(['ZCatalog'])
      if len(obs) == 0:
        return self.recreateCatalog()
      return obs[0]


    # --------------------------------------------------------------------------
    #  ZCatalogManager.recreateCatalog:
    #
    #  Recreates catalog.
    # --------------------------------------------------------------------------
    def recreateCatalog(self):
      message = ''
      context = self.getDocumentElement()
      
      #-- Get catalog
      obs = context.objectValues( [ 'ZCatalog'])
      if len( obs) == 0:
        cat_id = 'catalog'
        cat_title = 'Default catalog'
        vocab_id = 'create_default_catalog_'
        zcatalog = ZCatalog.ZCatalog(cat_id, cat_title, vocab_id, context)
        context._setObject(zcatalog.id, zcatalog)
        zcatalog = self.getCatalog()
      else:
        zcatalog = obs[ 0]
      
      #-- Add vocabulary
      addVocabulary( self, zcatalog)
      
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
           index_name.find( 'zcat_') == 0:
          try:
            zcatalog.manage_delColumn( [ index_name])
          except:
            _globals.writeException(self,"[recreateCatalog]: Can't delete column '%s' from catalog"%index_name)
          try:
            zcatalog.manage_delIndex( [ index_name])
          except:
            _globals.writeException(self,"[recreateCatalog]: Can't delete index '%s' from catalog"%index_name)
          index_names.append( index_name)
      
      #-- (Re-)create indexes on catalog
      index_types = []
      for index in zcatalog.Indexes.filtered_meta_types():
        index_types.append(index['name'])
      for lang in self.getLangIds():
        message += "Index ["
        index_name = 'zcat_text_%s'%lang
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
        message += index_name
        index_type = None
        for k in [ 'ZCTextIndex', 'TextIndexNG2', 'TextIndexNG3']:
          if k in index_types: index_type = k
        if self.getConfProperty('ZCatalog.TextIndexNG',0)==1:
          index_name = 'zcat_data_%s'%lang
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
        message += "] created for language <i>"+self.getLanguageLabel(lang)+'</i><br/>'
      
      #-- Return message.
      return message


    # --------------------------------------------------------------------------
    #  ZCatalogManager.reindexCatalog:
    #
    #  Reindex catalog.
    # --------------------------------------------------------------------------
    def reindexCatalog(self, REQUEST):
      message = ''
      
      #-- Recreate catalog.
      message += self.recreateCatalog()
      
      #-- Find items to catalog.
      message += self.reindexCatalogItem(REQUEST)
      
      # Return with message.
      message += 'Catalog indexed successfully.'
      return message


    # --------------------------------------------------------------------------
    #	ZCatalogManager.getCatalogQueryString:
    # --------------------------------------------------------------------------
    def getCatalogQueryString(self, raw, option='AND'):
      qs = ''
      raw = raw.replace(' and ',' AND ')
      raw = raw.replace(' or ',' OR ')
      if raw.find(' AND ')>=0 and raw.find(' OR ')>=0:
        for raw_item in raw.split(' '):
          if len(raw_item)>0:
            if raw_item in ['AND','OR'] or raw_item[-1]=='*':
              qs += raw_item + ' '
            else:
              qs += raw_item + '* '
      else:
        q = 0
        c = 0
        for raw_item in raw.split(' '):
          if len(raw_item)>0:
            if q==0 and c>0:
              qs += option + ' '
            if raw_item[0]=='*':
              q=1
            if q==1:
              qs += raw_item +' '
            else:
              qs += raw_item + '* '
            if raw_item[-1]=='*':
              q=0
            c=c+1
      qs = qs.replace('-','* AND *')
      qs = qs.strip()
      return qs


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
      message = ''
      rtn = []
      
      #-- Process clients.
      if self.getConfProperty('ZCatalog.portalClients',1) == 1 and search_clients == 1:
        for portalClient in self.getPortalClients():
          rtn.extend(portalClient.submitCatalogQuery( search_query, search_order_by, search_meta_types, search_clients, REQUEST))
      
      #-- Numbers are not cataloged.
      lnum = []
      qs = ''
      lq = search_query.split(' ')
      for i in range(len(lq)):
        try: 
          lnum.append(int(lq[i].strip()))
        except:
          qs += lq[i] + ' '
      
      #-- Search catalog.
      lang = REQUEST['lang']
      zcatalog = self.getCatalog()
      items = []
      for zcindex in zcatalog.indexes():
        if zcindex.find('zcat_')==0 and zcindex.rfind('_'+lang)==len(zcindex)-len('_'+lang):
          d = {}
          d['meta_type'] = zcat_meta_types
          if zcindex.find('zcat_data')==0:
            d[zcindex] = qs
          else:
            d[zcindex] = self.search_encode( qs)
          if _globals.debug( self):
            _globals.writeLog( self, "[submitCatalogQuery]: %s=%s"%(zcindex,d[zcindex]))
          qr = zcatalog(d)
          if _globals.debug( self):
            _globals.writeLog( self, "[submitCatalogQuery]: qr=%i"%len( qr))
          items.extend( qr)
      
      #-- Sort order.
      if int(search_order_by)==1:
        order_by = 'score'
      else:
        order_by = 'time'
      
      #-- Process results.
      abs_url = self.absolute_url()
      aq_abs_url = self.aq_absolute_url()
      results = []
      for item in items:
        # Get object by path.
        data_record_id = item.data_record_id_
        path = zcatalog.getpath(data_record_id)
        ob = self.getCatalogPathObject( path)
        # Uncatalog object.
        uncatalog = ob is None
        append = ob is not None
        if not uncatalog:
          for path_ob in ob.breadcrumbs_obj_path():
            if not uncatalog:
              uncatalog = uncatalog or path_ob == self.getTrashcan()
              append = append and path_ob.isVisible(REQUEST)
        if uncatalog:
          try:
            zcatalog.uncatalog_object(path)
          except:
            pass
          ob = None
        # Check for valid result.
        append = append and ob not in map(lambda x: x[1]['ob'], results)
        if append:
          # Handle Pages.
          append = ob.isCatalogItem()
          # Handle Meta-Types.
          if len(search_meta_types) > 0:
            append = append and ob.meta_id in search_meta_types
          # Handle Numbers.
          zctext = getattr(ob,'zcat_text_%s'%lang,'')
          for num in lnum:
            append = append and zctext.find(str(num))>=0
        # Append to valid results.
        if append:
          sum_time = ob.getObjProperty('attr_dc_date',REQUEST)
          if sum_time is None or len(str(sum_time))==0:
            sum_time = ob.getObjProperty('change_dt',REQUEST)
          try:
            sum_score = int(item.data_record_score_)
          except:
            sum_score = 0
          txng_key = ob.txng_get_key()
          txng_value = None
          if txng_key is not None:
            txng_value = ob.getObjProperty( txng_key, REQUEST)
          if txng_value is not None:
            id = ob.id+'/'
            sum_url = txng_value.getHref(REQUEST)
            sum_url = sum_url[sum_url.find(id)+len(id):]
          else:
            sum_url = 'index_%s.html'%lang
            if REQUEST.get('preview','')=='preview':
              sum_url = self.url_append_params(sum_url,{'preview':'preview'})
          result = {}
          result['ob'] = ob
          result['score'] = sum_score
          result['time'] = sum_time
          result['url'] = ob.getDeclUrl(REQUEST).replace(abs_url,aq_abs_url) + '/' + sum_url
          results.append((result[order_by],result))
      
      #-- Sort objects.
      results.sort()
      results.reverse()
      
      #-- Append objects.
      rtn.extend(map(lambda ob: ob[1],results))
      
      #-- Return objects in correct sort-order.
      return rtn

################################################################################
