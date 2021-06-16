## Script (Python) "ZMSFile.getHref2IndexHtml"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Function: index_html
##
# --// BO getHref2IndexHtml //--

file = zmscontext.attr('file')
if file:
    return file.getHref(zmscontext.REQUEST)
return ''

# --// EO getHref2IndexHtml //--
