id = 'zcatalog_connector'
from Products.zms import standard

def getZCatalog(context, lang):
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  return getattr(root, cat_id, None)

def catalog_object(zcatalog, adapter, node, data):
  attr_ids = adapter._getAttrIds()
  # Prepare object.
  for attr_id in attr_ids:
    attr_name = 'zcat_index_%s'%attr_id
    value = data.get(attr_id)
    if value == 'None':
      value = None
    setattr(node, attr_name, value)
  # (Re-)Catalog object.
  path = node.getPath()
  if zcatalog.getrid(path):
    zcatalog.uncatalog_object(path)
  zcatalog.catalog_object(node, path)
  # Unprepare object.
  for attr_id in attr_ids:
    attr_name = 'zcat_index_%s'%attr_id
    delattr(node, attr_name)
  return 1

def manage_zcatalog_objects_add( self, objects):
  request = self.REQUEST
  lang = standard.nvl(request.get('lang'), self.getPrimaryLanguage())
  if 'ZMS_ENV_ZCATALOG' not in request:
    request['ZMS_ENV_ZCATALOG'] = getZCatalog(self, lang)
  zcatalog = request['ZMS_ENV_ZCATALOG']
  adapter = self.getCatalogAdapter()
  success, failed = 0, 0
  for (node, data) in objects:
    success += catalog_object(zcatalog, adapter, node, data)
  return success, failed
