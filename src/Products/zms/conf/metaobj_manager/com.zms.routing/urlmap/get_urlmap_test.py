## Script (Python) "test_urlmap"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Testing an URL target provided by content.urlmap ZMSDatatable
##
request = container.REQUEST
response =  request.response

d = {}
zmscontext = context.content
urlmap = zmscontext.urlmap
res = urlmap.attr('records')
for i in res:
    if zmscontext.getLinkObj(i['url']):
        d.update({i['key']:zmscontext.getLinkObj(i['url'],request).absolute_url()})
    else:
        d.update({i['key']:i['url']})

# TEST
url_key='%s/test_urlmap.html'%(context.content.absolute_url())
return d.get(url_key,'KeyError: %s not found in urlmap'%(url_key))
