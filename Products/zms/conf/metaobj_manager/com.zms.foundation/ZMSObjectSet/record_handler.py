## Script (Python) "ZMSObjectSet.record_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Record-Handler
##
# --// record_handler //--

request = zmscontext.REQUEST
class EntityRecordHandler():
  def handle_record(self, r):
    id = r['__id__']
    childNode = getattr(zmscontext,id)
    objectset = childNode.attr('objectset')
    if not objectset:
      objectset = '<span class=\042label label-default zmi-info %s\042><a href=\042%s/manage_main?lang=%s\042>%s %s</a></span>'%(['','active'][int(childNode.isActive(request))],childNode.absolute_url(),request['lang'],childNode.display_icon(),childNode.display_type())
    r['objectset'] = objectset
    return r
record_handler = EntityRecordHandler()
return record_handler

# --// /record_handler //--
