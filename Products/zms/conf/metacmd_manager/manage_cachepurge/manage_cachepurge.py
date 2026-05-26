## Script (Python) "manage_cachepurge"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=*** DO NOT DELETE OR MODIFY ***
##
# ################################################
# IMPORTANT NOTE: 
# 1. This Script needs an External Method
# cache_purge(url) purging the cached data
# 2. Please, modify line 26/27, if your 
# published URLs contain '/content'
# ################################################
request = container.REQUEST
RESPONSE = request.RESPONSE

msg = []
urls = []
ip_or_domain = context.getConfProperty('ASP.ip_or_domain','')
url = context.getHref2IndexHtml({'lang':request['lang'],'preview':''})

if len(ip_or_domain)>0 and url.find('/content')>-1:
	# url = ip_or_domain + url
	if ip_or_domain.find('/content') > 0:
		url = ip_or_domain + url.split('/content')[1]
	else:
		url = ip_or_domain + '/content' + url.split('/content')[1]
else:
	# strip protocol
	url = url.replace('https://','').replace('http://','')

# purge both http/https
for p in ['https://','http://']:
	u = p + url
	try:
		msg.append( context.cache_purge( u ) )
	except:
		msg.append( 'Error: nginx_purge %s' %u )

return '<br />'.join(msg)
