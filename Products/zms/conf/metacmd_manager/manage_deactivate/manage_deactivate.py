## Script (Python) "manage_deactivate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Deactivate selected content items
##
request = container.REQUEST
RESPONSE =  request.RESPONSE
lang = request['lang']

new_active = 0

ids = request.get('ids',[])
target = context.getSelf(context.PAGES)
for ob in target.getChildNodes(request):
  if ob.id in ids:
    ob.setObjStateModified(request)
    ob.setObjProperty('active',new_active,lang,forced=True)
    ob.onChangeObj(request)
print('%i Objects deactivated'%len(ids))

return target,printed
