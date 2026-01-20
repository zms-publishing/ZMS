## Script (Python) "ZMSVideo.titlealt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: DC.Title.Alt
##
# --// titlealt //--
return zmscontext.attr('title')
# --// /titlealt //--
