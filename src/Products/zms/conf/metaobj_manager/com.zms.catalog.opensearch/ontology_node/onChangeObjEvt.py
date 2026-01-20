## Script (Python) "ontology_node.onChangeObjEvt"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Event: onChange
##
# --// onChangeObjEvt //--
# ------------------------
# If attr('key') has got no 
# value, create a unique one
# ------------------------
from Products.zms import standard
request = container.REQUEST
RESPONSE =  request.RESPONSE


if zmscontext.attr('key')=='':
    lang = request.get('lang','ger')
    id = zmscontext.getId()
    suffix = id
    try:
        if id.startswith('e'):
            suffix = int(id[1:])
    except:
        pass
    v = request.get('title_%s'%(lang))
    v = standard.re_sub(r'[^a-zA-Z]', '', v)
    v = v.upper()
    v += str(suffix) # unifiy string
    zmscontext.attr('key',v)

return None

# --// /onChangeObjEvt //--
