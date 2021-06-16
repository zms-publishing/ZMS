## Script (Python) "ZMSIndexZCatalog.onCreateObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Event: onCreateObj
##
# --// onCreateObjEvt //--

from Products.zms import standard
request = zmscontext.REQUEST
base = list(context.getRootElement().getPhysicalPath())[:-1]
url = list(context.getDocumentElement().getPhysicalPath())[len(base):-1]
request.set('url','{$'+['','/'.join(url)+'@'][len(url)>0]+'}')
zmscontext.ZMSIndexZCatalog_func_(zmscontext,'reindex')

# --// /onCreateObjEvt //--
