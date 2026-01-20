## Script (Python) "ZMSFigure.getHref2IndexHtml"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Function: index_html
##
# --// getHref2IndexHtml //--

img = zmscontext.attr('img')
if img:
    return img.getHref(zmscontext.REQUEST)
return ''

# --// /getHref2IndexHtml //--
