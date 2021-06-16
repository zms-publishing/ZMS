## Script (Python) "ZMSTextarea.check_constraints"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Hook: check constraints
##
# --// check_constraints //--

constraints = {}
request = zmscontext.REQUEST
obj_attr = zmscontext.getObjAttr('text')
text = zmscontext.getObjAttrValue(obj_attr,request)
if text.startswith('##') or text.find('<dtml-')>=0 or text.find('<tal:')>=0:
  constraints['RESTRICTIONS'] = constraints.get('RESTRICTIONS',[])
  constraints['RESTRICTIONS'].append(('restricted-access','text contains executable-code (py, tal, dtml)',['ZMS Administrator']))
return constraints

# --// /check_constraints //--
