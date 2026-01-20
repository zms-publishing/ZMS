## Script (Python) "ZMSTeaserElement.attr_img_src"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Alias: Image
##
# --// BO attr_img_src //--

img = zmscontext.attr('attr_img')
if img:
    return img.getHref(zmscontext.REQUEST)
return ''

# --// EO attr_img_src //--
