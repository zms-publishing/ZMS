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
from Products.ZCatalog import ZCatalog
import urllib
import zope.interface
# Product Imports.
import _globals
import IZMSCatalogConnector
import ZMSZCatalogAdapter
import ZMSItem


# ------------------------------------------------------------------------------
#  ZMSZCatalogConnector.intValue:
# ------------------------------------------------------------------------------
def intValue(v):
  try:
    i = int(v)
  except:
    i = 0
  return i


# ------------------------------------------------------------------------------
#  ZMSZCatalogConnector.Empty:
# ------------------------------------------------------------------------------
class Empty: 
  pass


# ------------------------------------------------------------------------------
#  ZMSZCatalogConnector.addLexicon:
# ------------------------------------------------------------------------------
def addLexicon( container, cat):
  
  # Remove Lexicon
  ids = cat.objectIds( ['ZCTextIndex Lexicon','ZCTextIndex Unicode Lexicon'])
  if len( ids) > 0:
    cat.manage_delObjects( ids)
  
  # Add Lexicon
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
#  ZMSZCatalogConnector.recreateCatalog:
# ------------------------------------------------------------------------------
def recreateCatalog(self, zcm, lang):
  
  #-- Create catalog
  cat_id = 'catalog_%s'%lang
  if cat_id in self.objectIds():
    self.manage_delObjects([cat_id])
  cat_title = 'Default catalog'
  zcatalog = ZCatalog.ZCatalog(id=cat_id, title=cat_title, container=self)
  self._setObject(zcatalog.id, zcatalog)
  zcatalog = getattr(self,cat_id)
  
  #-- Add lexicon
  addLexicon( self, zcatalog)
  
  #-- Add columns
  for index_name in ['id','meta_id','absolute_url','zcat_column_custom']:
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


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSZCatalogConnector(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSCatalogConnector.IZMSCatalogConnector)

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogConnector'
    icon = "/misc_/ZCatalog/ZCatalog.gif"

    # Management Interface.
    # ---------------------
    manage_input_form = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_zcatalog_connector',globals())

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
    def __init__(self):
      self.id = 'zcatalog_connector'


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.search_xml:
    # --------------------------------------------------------------------------
    def search_xml(self, q, page_index=0, page_size=10, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogConnector.search_xml """
      # Check constraints.
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang',REQUEST.get('lang',self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml;charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      status = 0
      msg = ''
      results = []
      try: 
        results = self.search(q)
      except:
        import sys
        _globals.writeError(self,'[search_xml]')
        t,v,tb = sys.exc_info()
        status = 400
        msg = v
      # Assemble xml.
      xml = self.getXmlHeader()
      xml += '<response>'
      xml += '<lst name="responseHeader">'
      xml += '<int name="status">%i</int>'%status
      xml += '<lst name="params">'
      for key in REQUEST.form.keys():
        xml += '<int name="%s">%s</int>'%(key,str(REQUEST.form[key]))
      xml += '</lst>'
      xml += '</lst>'
      if status > 0:
        xml += '<lst name="error">'
        xml += '<int name="msg">%s</int>'%msg
        xml += '<int name="code">%i</int>'%status
        xml += '</lst>'
      else:
        xml += '<result name="response" numFound="%i" start="%i">'%(len(results),page_index*page_size)
        if len(results) > page_size:
          results = results[page_index*page_size:(page_index+1)*page_size]
        for result in results:
          xml += '<doc>'
          for k in result.keys():
            v = result[k]
            if k == 'absolute_url':
              k = 'loc'
            elif k == 'zcat_column_custom':
              k = 'custom'
            elif k == 'standard_html':
              v = ZMSZCatalogAdapter.remove_tags(self,v)
            xml += '<arr name="%s">'%k
            if k == 'custom':
              xml += '<str>%s</str>'%v 
            else: 
              xml += '<str><![CDATA[%s]]></str>'%v 
            xml += '</arr>'
          xml += '</doc>'
        xml += '</result>'
      xml += '</response>'
      return xml


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.suggest_xml:
    # --------------------------------------------------------------------------
    def suggest_xml(self, q, limit=5, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogConnector.suggest_xml """
      # Check constraints.
      REQUEST.set('lang',REQUEST.get('lang',self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml;charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      status = 0
      msg = ''
      results = []
      try: 
        results = self.suggest(q,limit)
      except:
        import sys
        _globals.writeError(self,'[suggest_xml]')
        t,v,tb = sys.exc_info()
        status = 400
        msg = v
      # Assemble xml.
      xml = self.getXmlHeader()
      xml += '<response>'
      xml += '<lst name="responseHeader">'
      xml += '<int name="status">%i</int>'%status
      xml += '</lst>'
      if status > 0:
        xml += '<lst name="error">'
        xml += '<int name="msg">%s</int>'%msg
        xml += '<int name="code">%i</int>'%status
        xml += '</lst>'
      else:
        xml += '<lst>'
        xml += '<lst name="suggestions">'
        xml += '<int name="numFound">%i</int>'%len(results)
        xml += '<arr name="suggestion">'
        for result in results:
          xml += '<str>%s</str>'%result
        xml += '</arr>'
        xml += '</lst>'
        xml += '</lst>'
      xml += '</response>'
      return xml


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.search:
    # --------------------------------------------------------------------------
    def search(self, qs, order=None):
      rtn = []
      
      # ZCatalog.
      request = self.REQUEST
      lang = request.get('lang',self.getPrimaryLanguage())
      zcatalog = getattr(self,'catalog_%s'%lang)
      
      # Find search-results.
      items = []
      for index in zcatalog.indexes():
        if index.find('zcat_index_')==0:
          query = {index:self.search_encode( qs)}
          qr = zcatalog(query)
          _globals.writeLog( self, "[search]: %s=%i"%(str(query),len(qr)))
          for item in qr:
            if item not in items:
              items.extend( qr)
      
      # Process search-results.
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
      
      # Sort search-results.
      results.sort()
      results.reverse()
      
      # Append search-results.
      rtn.extend(map(lambda ob: ob[1],results))
      
      # Return list of search-results in correct sort-order.
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.suggest:
    # --------------------------------------------------------------------------
    def suggest(self, q, limit=5):
      rtn = []
      
      # ZCatalog.
      request = self.REQUEST
      lang = request.get('lang',self.getPrimaryLanguage())
      zcatalog = getattr(self,'catalog_%s'%lang)
      
      # Lexicon.
      lexicon = zcatalog.Lexicon
      for w in lexicon.words():
        if w[0] not in ['_','0','1','2','3','4','5','6','7','8','9'] and w.lower().find(q) >= 0 and w not in rtn:
          rtn.append(w)
        if len(rtn) >= limit:
          break
      
      # Return list of suggestions.
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector._update:
    # --------------------------------------------------------------------------
    def _update(self, node, d):
      zcm = self.getCatalogAdapter()
      lang = self.REQUEST.get('lang')
      # Prepare object.
      extra_column_ids = ['custom']
      for attr_id in extra_column_ids:
        attr_name = 'zcat_column_%s'%attr_id
        value = d.get(attr_id)
        setattr(node,attr_name,value)
      for attr_id in zcm.getAttrIds():
        attr_name = 'zcat_index_%s'%attr_id
        value = node.attr(attr_id)
        setattr(node,attr_name,value)
      # Reindex object.
      node.default_catalog = 'catalog_%s'%lang
      node.reindex_object()
      # Unprepare object.
      for attr_id in extra_column_ids:
        attr_name = 'zcat_column_%s'%attr_id
        delattr(node,attr_name)
      for attr_id in zcm.getAttrIds():
        attr_name = 'zcat_index_%s'%attr_id
        delattr(node,attr_name)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self):
      zcm = self.getCatalogAdapter()
      request = self.REQUEST
      container = self.getDocumentElement()
      for lang in container.getLangIds():
        request.set('lang',lang)
        # Recreate catalog.
        recreateCatalog(container,self.aq_parent,lang)
        # Reindex items to catalog.
        def cb(node,d):
          self._update(node,d)
        zcm.get_sitemap(cb,container,recursive=True)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_node:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      node.writeLog('[ZMSZCatalogConnector.reindex_node]')
      zcm = self.getCatalogAdapter()
      # Reindex item to catalog.
      def cb(node,d):
        self._update(node,d)
      zcm.get_sitemap(cb,node,recursive=False)


    def get_sitemap(self):
      """
      Returns sitemap.
      @rtype: C{str}
      """
      zcm = self.getCatalogAdapter()
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      RESPONSE.setHeader('Content-Type','text/plain; charset=utf-8')
      l = []
      def cb(node,d):
        l.append(d)
      zcm.get_sitemap(cb,self.getDocumentElement(),recursive=True)
      return self.str_json(l)


    ############################################################################
    #  ZMSZCatalogConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, selected, btn, lang, REQUEST):
        message = ''
        
        # Reindex.
        # --------
        if btn == 'Reindex' and selected:
          reindex = self.reindex_all()
          message += '%s reindexed (%s)\n'%(self.id,str(reindex))
        
        # Remove.
        # -------
        elif btn == 'Remove':
          ids = REQUEST.get('zcatalog_objectIds',[])
          if len(ids) > 0:
            self.getDocumentElement().manage_delObjects(ids)
            message += self.getZMILangStr('MSG_DELETED')%len(ids)
        
        return message

################################################################################
