## Script (Python) "ZMSFile.attr_img_src"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Alias: Teaser.Image
##
# --// BO attr_img_src //--

file = zmscontext.attr('file')
mt = file.getContentType()
return zmscontext.getMimeTypeIconSrc(mt)

# --// EO attr_img_src //--
