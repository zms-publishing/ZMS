## Script (Python) "ZMSIndexZCatalog.getRefObjPath"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Hook: Get ref object path
##
# --// ZMSIndexZCatalog.getRefObjPath //--

ob = options['ob']
anchor = options['anchor']
ref = ob.get_uid()
if anchor:
  ref += '#'+anchor
return '{$%s}'%ref

# --// /ZMSIndexZCatalog.getRefObjPath //--
