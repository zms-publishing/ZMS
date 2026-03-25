def manage_clean_deep_zcatalog_adapters( self):
  def traverse(node):
    rtn = []
    rtn.append('traverse ' + '/'.join(node.getPhysicalPath()))
    if node != node.getRootElement() and 'zcatalog_adapter' in node.objectIds():
      rtn.append('delete ' + '/'.join(list(node.getPhysicalPath())+['zcatalog_adapter']))
      node.manage_delObjects(ids=['zcatalog_adapter'])
    for client in node.getPortalClients():
      rtn.extend(traverse(client))
    return rtn
  return "<br/>".join(traverse(self.getRootElement()))