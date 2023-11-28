id = 'zcatalog_connector'
from Products.zms import standard
import copy

def umlaut_quote(self, v):
  if int(self.getConfProperty('ZMSZCatalogConnector.umlaut_quote', 0)):
    return standard.umlaut_quote(v)
  return v

def intValue(v):
  try:
    i = int(v)
  except:
    i = 0
  return i

def zcatalog_query( self, q, fq='', order=None):
  # ZCatalog.
  request = self.REQUEST
  lang = standard.nvl(request.get('lang'), self.getPrimaryLanguage())
  root = self.getRootElement()
  zcatalog = getattr(root, 'catalog_%s'%lang)
  
  # Find search-results.
  items = []
  prototype = {}
  for fqs in fq.split(','):
    attr_id = fqs[:fqs.find(':')]
    if attr_id.endswith('_s'):
      attr_id = attr_id[:-2]
    fqk = 'zcat_index_%s'%attr_id
    if fqk in zcatalog.indexes():
      fqv = fqs[fqs.find(':')+1:]
      fqv = umlaut_quote(self, fqv)
      prototype[fqk] = fqv
  for index in zcatalog.indexes():
    if index.find('zcat_index_')==0:
      query = copy.deepcopy(prototype)
      query[index] = umlaut_quote(self, q)
      qr = zcatalog(query)
      standard.writeLog( self, "[zcatalog_query]: %s=%i"%(str(query), len(qr)))
      for item in qr:
        if item not in items:
          items.append( item.aq_base )
  
  # Process search-results.
  results = []
  for item in items:
    data_record_id = item.data_record_id_
    path = zcatalog.getpath(data_record_id)
    # Append to valid results.
    if len([x for x in results if x[1]['path']==path]) == 0:
      result = {}
      result['path'] = path
      result['score'] = intValue(item.data_record_score_)
      result['normscore'] = intValue(item.data_record_normalized_score_)
      for column in zcatalog.schema():
        k = column
        if k.find('zcat_index_')==0:
          k = k[len('zcat_index_'):]
        result[k] = getattr(item, column, None)
      results.append((item.data_record_score_, result))
  
  # Sort search-results.
  results = sorted( results, key=lambda x: x[0])
  results.reverse()
  
  # Return list of search-results in correct sort-order.
  return [x[1] for x in results]

