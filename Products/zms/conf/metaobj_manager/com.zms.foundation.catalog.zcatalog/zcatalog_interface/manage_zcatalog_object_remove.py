id = 'zcatalog_interface'
from Products.zms import standard

def getZCatalog(context, lang):
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  return getattr(root, cat_id, None)

def manage_zcatalog_object_remove( self, nodes):
  request = self.REQUEST
  lang = standard.nvl(request.get('lang'), self.getPrimaryLanguage())
  if 'ZMS_ENV_ZCATALOG' not in request:
    request['ZMS_ENV_ZCATALOG'] = getZCatalog(self, lang)
  zcatalog = request['ZMS_ENV_ZCATALOG']
  for node in nodes:
    path = node.getPath()
    if zcatalog.getrid(path):
      zcatalog.uncatalog_object(path)
  return "%i cataloged"%len(nodes)
