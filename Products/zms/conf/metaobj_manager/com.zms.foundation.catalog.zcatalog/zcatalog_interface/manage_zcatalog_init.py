id = 'zcatalog_interface'
from Products.zms import standard
from Products.ZCatalog import ZCatalog
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex

class Empty(object): 
  pass

def addLexicon(context, zcatalog):
  
  # Remove Lexicon
  ids = zcatalog.objectIds( ['ZCTextIndex Lexicon', 'ZCTextIndex Unicode Lexicon'])
  if ids:
    zcatalog.manage_delObjects( ids)
  
  # Add Lexicon
  index_type = context.getConfProperty('ZCatalog.TextIndexType', 'ZCTextIndex')
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
      zcatalog.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon', 'Default lexicon', elements)
    except:
      pass

def getZCatalog(context, lang):
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  # remove deprecated local catalog from client
  if root != context and cat_id in context.objectIds():
    context.manage_delObjects([cat_id])
  zcatalog = getattr(root, cat_id, None)
  return zcatalog

def recreateZCatalog(context, lang):
  
  # Create catalog
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  if cat_id in root.objectIds():
    root.manage_delObjects([cat_id])
  cat_title = 'Default catalog'
  zcatalog = ZCatalog.ZCatalog(id=cat_id, title=cat_title, container=root)
  root._setObject(zcatalog.id, zcatalog)
  zcatalog = getZCatalog(context, lang)
  
  # Add lexicon
  addLexicon( context, zcatalog)
  
  # Add columns
  for index_name in ['id', 'meta_id', 'home_id', 'index_html']:
    zcatalog.manage_addColumn(index_name)
  
  # Add Indexes (incl. Columns)
  zca = context.getCatalogAdapter()
  for attr_id in zca._getAttrIds():
    attr_type = 'string'
    for meta_id in context.getMetaobjIds():
      meta_obj_attr = context.getMetaobjAttr(meta_id,attr_id)
      if meta_obj_attr:
        attr_type = meta_obj_attr['type']
        break
    index_name = 'zcat_index_%s'%attr_id
    index_type = context.getConfProperty('ZCatalog.TextIndexType','ZCTextIndex')
    if index_name == 'zcat_index_home_id':
      index_type = KeywordIndex(index_name)
    elif attr_type == 'date':
      index_type = DateIndex(attr_id)
    extra = None
    if index_type == 'ZCTextIndex':
      extra = Empty()
      extra.doc_attr = index_name
      extra.index_type = 'Okapi BM25 Rank'
      extra.lexicon_id = 'Lexicon'
    elif index_type != 'KeywordIndex':
      extra = {}
      extra['default_encoding'] = 'utf-8'
      extra['indexed_fields'] = index_name
      extra['fields'] = [index_name]
      extra['near_distance'] = 5
      extra['splitter_casefolding'] = 1
      extra['splitter_max_len'] = 64
      extra['splitter_separators'] = '.+-_@'
      extra['splitter_single_chars'] = 0
    zcatalog.manage_addColumn(index_name)
    zcatalog.manage_addIndex(index_name, index_type, extra)
  return '%s created'%str(cat_id)

def manage_zcatalog_init( self):
  try:
    result = []
    request = self.REQUEST
    for lang in self.getLangIds():
      request.set('lang', lang)
      result.append(recreateZCatalog(self, lang))  
    return "\n".join(result)
  except:
    return standard.writeError(self,"can't manage_zcatalog_init")
