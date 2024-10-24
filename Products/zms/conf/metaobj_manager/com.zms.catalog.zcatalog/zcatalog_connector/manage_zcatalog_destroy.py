id = 'zcatalog_connector'
from Products.zms import standard

def getZCatalog(context, lang):
  cat_id = 'catalog_%s'%lang
  root = context.getRootElement()
  return getattr(root, cat_id, None)

def destroyZCatalog(context, lang):
  cat_id = None
  zcatalog = getZCatalog(context, lang)
  if zcatalog:
    cat_id = zcatalog.id
    parent = zcatalog.aq_parent
    parent.manage_delObjects([zcatalog.id])
  return '%s destroyed'%str(cat_id)

def manage_zcatalog_destroy( self):
  try:
    result = []
    request = self.REQUEST
    for lang in self.getLangIds():
      request.set('lang', lang)
      result.append(destroyZCatalog(self, lang))  
    return "\n".join(result)
  except:
    return standard.writeError(self,"can't manage_zcatalog_destroy")