## Script (Python) "ZMSObjectSet.record_duplicate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Record-Duplicate
##
# --// record_duplicate //--

request = zmscontext.REQUEST
if request.get('action') == 'record_duplicate':
  before = zmscontext.objectIds()
  ids = [request.get('id')]
  cp = zmscontext.manage_copyObjects(ids)
  zmscontext.manage_pasteObjects(cb_copy_data=cp)
  after = zmscontext.objectIds()
  id = [x for x in after if x not in before][0]
  new_id = zmscontext.getNewId('records')
  zmscontext.manage_renameObject(id=id,new_id=new_id)
  new_ob = [x for x in zmscontext.objectValues() if x.id == new_id][0]
  new_ob.setObjStateNew(request)
  new_ob.setObjProperty('attr_active_start',None,request['lang'])
  new_ob.setObjProperty('attr_active_end',None,request['lang'])
  for attr_id in new_ob.getObjAttrs():
    if attr_id.find('title')>=0:
      new_ob.setObjProperty(attr_id,'Copy of %s'%new_ob.attr(attr_id),request['lang'])
      break
  new_ob.onChangeObj(request)
  return (new_ob,zmscontext.getZMILangStr('MSG_PASTED'))
return None

# --// /record_duplicate //--
