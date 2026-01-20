## Script (Python) "test__calendar__get_events"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=TEST get_events
##
# --// test__calendar__get_events //--
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE
zms = context.content
nodes = zms.filteredChildNodes(request,'calendar')
zmscontext = nodes[0]

return zmscontext.attr('get_events')
# --// /test__calendar__get_events //--
