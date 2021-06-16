## Script (Python) "ZMSFile.attr_url"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Alias: Teaser.Url
##
# --// BO attr_url //--

file = zmscontext.attr('file')
return file.getHref(zmscontext.REQUEST)

# --// EO attr_url //--
