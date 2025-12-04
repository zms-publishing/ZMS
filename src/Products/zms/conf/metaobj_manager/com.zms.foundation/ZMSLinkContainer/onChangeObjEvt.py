## Script (Python) "ZMSLinkContainer.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext
##title=py: Event: onChangeObj
##
# --// BO onChangeObjEvt //--
from Products.zms import standard

def equals(o, d):
  for k in d:
    if o.attr(k) != d[k]:
      return False
  return True

request = zmscontext.REQUEST
lang = request.get('lang')
if request.get('btn') == 'BTN_SAVE':
  align = zmscontext.attr('align')
  # Save.
  for childNode in zmscontext.getChildNodes(request,['ZMSLinkElement']):
    id = childNode.id
    active = int(request.get('active%s'%id,1))
    url = request['url%s'%id].strip()
    title = request['title%s'%id].strip()
    description = request['description%s'%id].strip()
    attr_type = ['new','replace'][int(url.startswith('{$') and url.endswith('}'))]
    d = {'active':active,'title':title,'titlealt':title,'attr_ref':url,'attr_dc_description':description,'attr_type':attr_type,'align':align}
    if not equals(childNode,d):
      childNode.setObjStateModified(request)
      for k in d:
        childNode.setObjProperty(k,d[k],lang)
      childNode.onChangeObj(request)
  # Insert.
  id = '_'
  url = request['url%s'%id].strip()
  if len(url) > 0:
    active = int(request.get('active%s'%id,1))
    title = request['title%s'%id].strip()
    description = request['description%s'%id].strip()
    attr_type = ['new','replace'][int(url.startswith('{$') and url.endswith('}'))]
    d = {'active':active,'title':title,'titlealt':title,'attr_ref':url,'attr_dc_description':description,'attr_type':attr_type,'align':align}
    childNode = standard.addZMSCustom(self=zmscontext, meta_id='ZMSLinkElement', values=d, REQUEST=request)

# --// EO onChangeObjEvt //--
