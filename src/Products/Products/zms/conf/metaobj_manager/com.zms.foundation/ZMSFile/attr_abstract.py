## Script (Python) "ZMSFile.attr_abstract"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Alias: Teaser.Abstract
##
# --// BO attr_abstract //--
#
return zmscontext.attr('attr_dc_description')

# --// EO attr_abstract //--
