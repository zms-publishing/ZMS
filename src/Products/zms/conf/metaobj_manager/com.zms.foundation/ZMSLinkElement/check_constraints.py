## Script (Python) "ZMSLinkElement.check_constraints"
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
try:
  if not request.get('ZMS_INSERT')=='ZMSLinkElement':
    ref = zmscontext.getRef()
    if ref.startswith('{$') and ref.endswith('}'):
      ref_obj = zmscontext.getRefObj()
      if ref_obj is None:
        constraints['ERRORS'] = constraints.get('ERRORS',[])
        constraints['ERRORS'].append(('ref-obj','link-target not found: '+str(ref)))
except:
  constraints['ERRORS'] = constraints.get('ERRORS',[])
  constraints['ERRORS'].append(('ref-obj',zmscontext.writeError('can\'t check_constraints')))
return constraints

# --// /check_constraints //--
