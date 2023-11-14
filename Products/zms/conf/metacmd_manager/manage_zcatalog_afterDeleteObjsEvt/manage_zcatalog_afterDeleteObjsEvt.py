from Products.zms import standard

def manage_zcatalog_afterDeleteObjsEvt( self):
  l = []
  def traverse(node):
    standard.writeLog(node, 'manage_zcatalog_afterDeleteObjsEvt')
    l.append(1)
    # Uncatalog object.
    # TODO implement here
    # Traverse.
    for childNode in node.getChildNodes():
      traverse(childNode)
  traverse(self)
  return 'manage_zcatalog_afterDeleteObjsEvt: %i objects uncataloged'%len(l)