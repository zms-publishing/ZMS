## Script (Python) "get_path_by_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='e1', zmscontext=None
##title=Getting an URL by Requesting an UID/ID on ZMSIndex
##
from Products.zms import standard
request = container.REQUEST
response =  request.response
zmscontext = zmscontext or context.content
domain = zmscontext.getConfProperty('ASP.ip_or_domain','')
home_id = zmscontext.getHome().id

domain = domain!='' and 'https://%s'%(domain) or domain
domain = domain.split('/content')[0]
cat_attr_name = id.startswith('uid') and 'get_uid' or 'id'
catalog = zmscontext.getZMSIndex().get_catalog()
q = catalog({ cat_attr_name : str(id) })
log = []
for r in q:
    pth = str(r['getPath'])
    log.append(pth)
    if str(home_id + '/content') not in pth:
        # Different ZMS client
        zmsclient = r.getObject().getDocumentElement()
        home_id = zmsclient.getHome().id
        domain = zmsclient.getConfProperty('ASP.ip_or_domain','')
    # Always return 1st catalog hit
    pth = pth.split('/content/')[1]
    return ('%s/content/%s/'%(domain, pth))        

return (domain + '?info=No Valid Document ID')
