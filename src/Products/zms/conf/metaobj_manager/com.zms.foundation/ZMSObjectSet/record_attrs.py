## Script (Python) "ZMSObjectSet.record_attrs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Record-Attrs
##
# --// record_attrs //--

attrs = []
for x in zmscontext.attr('record_attr_ids').split(','):
  id = x
  type = 'string'
  if x.find(':') > 0:
    id = x[:x.find(':')]
    type = x[x.find(':')+1:]
  name = id.capitalize()
  if id.find('[') < id.find(']'):
    name = id[id.find('[')+1:-1]
    id = id[:id.find('[')]
  attrs.append({'id':id,'name':name,'type':type})
return attrs

# --// /record_attrs //--
