id = 'zcatalog_connector'
from Products.zms import standard

def getZCatalog(context, lang):
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  return getattr(root, cat_id, None)

def manage_zcatalog_objects_clear( self, home_id):
  success, failed = 0, 0
  request = self.REQUEST
  for lang in self.getLangIds():
    request.set('lang', lang)
    zcatalog = getZCatalog(self, lang)
    query = {'zcat_index_home_id':home_id}
    items = zcatalog(query)
    for item in items:
      data_record_id = item.data_record_id_
      path = zcatalog.getpath(data_record_id)
      if zcatalog.getrid(path):
        zcatalog.uncatalog_object(path)
        success += 1
      else:
        failed += 1
  return success, failed