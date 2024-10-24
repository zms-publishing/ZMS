## Script (Python) "get_targets_json"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=adword=''
##title=Public adword REST endpoint
##
# --// get_targets_json //--

from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE

# IMPORTANT HINT: context must be given as the adword datatable node
# ####################################################################
zmscontext = context
# ####################################################################

# Return targets as json
RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
targets = zmscontext.attr('get_targets')
return standard.str_json(targets)


# --// /get_targets_json //--
