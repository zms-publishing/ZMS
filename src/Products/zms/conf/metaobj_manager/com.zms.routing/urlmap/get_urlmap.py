## Script (Python) "get_urlmap"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=Getting URL-Map from content.urlmap ZMSDatatable
##
request = container.REQUEST
response =  request.response

d = {}
try:
	if zmscontext:
		urlmap = zmscontext.urlmap
	else:
		zmscontext = context.content
		urlmap = zmscontext.urlmap
	res = urlmap.attr('records')
	for i in res:
		if zmscontext.getLinkObj(i['url']):
			d.update({i['key']:zmscontext.getLinkObj(i['url'],request).absolute_url()})
		else:
			d.update({i['key']:i['url']})
except:
	pass
return d
