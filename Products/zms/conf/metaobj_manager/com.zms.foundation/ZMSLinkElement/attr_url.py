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
if ref.startswith('{$') and ref.endswith('}'):
  ref_lang = zmscontext.attr('ref_lang')
  if lang != zmscontext.getPrimaryLanguage() and len(ref_lang) > 0:
    ref = zmscontext.re_sub(';lang\\=\\w*','',ref)
    ref = ref[:-1]
    ref += ';lang='+ref_lang+'}'
return ref

# --// /attr_url //--
