## Script (Python) "ZMSTable.titlealt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: DC.Title.Alt
##
# --// BO titlealt //--

titlealt = zmscontext.attr('caption')
if titlealt:
    return titlealt
return zmscontext.display_type(zmscontext.REQUEST)

# --// EO titlealt //--
