## Script (Python) "ZMSIndexZCatalog.onImportObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Event: onImportObj
##
# --// onImportObjEvt //--

if zmscontext.getConfProperty('ZMSIndexZCatalog.onImportObjEvt',False) == True:
  request = context.REQUEST
  base = list(context.getRootElement().getPhysicalPath())[:-1]
  url = list(context.getDocumentElement().getPhysicalPath())[len(base):-1]
  request.set('url','{$'+['','/'.join(url)+'@'][len(url)>0]+'}')
  zmscontext.ZMSIndexZCatalog_func_(zmscontext,'resync')

# --// /onImportObjEvt //--
