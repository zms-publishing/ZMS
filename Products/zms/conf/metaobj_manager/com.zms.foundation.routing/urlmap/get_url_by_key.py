## Script (Python) "get_url_by_key"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=url_key='',zmscontext=None
##title=Using URL-Map for URL Resolving
##
request = container.REQUEST
response =  request.response

if url_key=='':
    url_key = request.get('URL')
    
# Check both just a final keyword or whole URL is used for redirecting
req_id = url_key.split('/')[-1]
req_url = url_key
new_url = 'url_mapping/error_404?key=%s'%(url_key)

urlmap = container.get_urlmap(zmscontext=zmscontext)

# Test
if req_id == 'get_url_by_key':
    return 'Test executed without parameter url_key: %s'%(req_url)

if urlmap.get(req_id):
    new_url = urlmap.get(req_id)
elif urlmap.get(req_url):
    new_url = urlmap.get(req_url)
# Try adding lost URL-suffix 
elif urlmap.get('%s/index_ger.html'%(req_url)):
    new_url = urlmap.get('%s/index_ger.html'%(req_url))
    
return new_url
