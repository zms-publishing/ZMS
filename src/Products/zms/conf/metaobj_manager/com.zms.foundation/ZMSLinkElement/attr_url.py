## Script (Python) "ZMSLinkElement.attr_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Alias: Url
##
# --// attr_url //--

request = zmscontext.REQUEST
lang = request.get('lang',zmscontext.getPrimaryLanguage())
ref = zmscontext.attr('attr_ref')
return ref

# --// /attr_url //--
