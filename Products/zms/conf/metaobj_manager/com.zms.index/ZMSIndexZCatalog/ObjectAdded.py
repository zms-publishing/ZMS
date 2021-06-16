## Script (Python) "ZMSIndexZCatalog.ObjectAdded"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: Event: object added
##
# --// ObjectAdded //--

def traverse(node):
  # Create new uid.
  node.get_uid(True)
  # Catalog object.
  node.ZMSIndexZCatalog_func_(node,'catalog_object')
  # Traverse.
  for childNode in node.getChildNodes():
    traverse(childNode)
traverse(zmscontext)
return True

# --// /ObjectAdded //--
