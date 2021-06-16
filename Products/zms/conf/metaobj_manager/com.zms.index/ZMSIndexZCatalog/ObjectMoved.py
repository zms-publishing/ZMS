## Script (Python) "ZMSIndexZCatalog.ObjectMoved"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None
##title=py: Event: object moved
##
# --// ZMSIndexZCatalog.ObjectMoved //--

zmsindex = getattr(zmscontext.getRootElement(),'zmsindex',None)
if zmsindex is not None and zmsindex.meta_id=='ZMSIndexZCatalog':
  catalog = getattr(zmscontext,'zcatalog_index',None)
  if catalog is not None:
    def traverse(node):
      # Refresh index: add and remove.
      query = {'get_uid':node.get_uid()}
      row = catalog(query)
      for r in row:
        node.ZMSIndexZCatalog_func_(node,'uncatalog_object',r['getPath'])
      node.ZMSIndexZCatalog_func_(node,'catalog_object')
      # Traverse.
      for childNode in node.getChildNodes():
        traverse(childNode)
    traverse(zmscontext)

# --// /ZMSIndexZCatalog.ObjectMoved //--
