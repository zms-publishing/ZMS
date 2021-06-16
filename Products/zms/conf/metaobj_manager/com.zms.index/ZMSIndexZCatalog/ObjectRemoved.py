## Script (Python) "ZMSIndexZCatalog.ObjectRemoved"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: Event: object removed
##
# --// ZMSIndexZCatalog.ObjectRemoved //--

def traverse(node):
  # Uncatalog object.
  node.ZMSIndexZCatalog_func_(node,'uncatalog_object',node.getPath())
  # Traverse.
  for childNode in node.getChildNodes():
    traverse(childNode)
traverse(zmscontext)

# --// /ZMSIndexZCatalog.ObjectRemoved //--
