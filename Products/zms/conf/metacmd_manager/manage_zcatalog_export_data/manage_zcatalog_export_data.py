# --// manage_zcatalog_export_data //--

import json
from Products.zms import standard
from Products.zms import catalog_analysis

def manage_zcatalog_export_data( self):
  msg = []
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
  zmscontext = self.getLinkObj(request.get('uid','{$}'))
  root_id = zmscontext.getRootElement().getHome().id
  home = zmscontext.getDocumentElement()
  home_id = home.getPhysicalPath()
  home_id = home_id[home_id.index('content')-1]
  inst_home = zmscontext.Control_Panel.getINSTANCE_HOME()
  path = home_id
  node = home
  while True:
    node = node.getPortalMaster()
    if node is None: break
    path = node.getHome().getId() + '/' + path
  
  zmscontext.f_standard_html_request(request)
  data = []
  zca = zmscontext.getCatalogAdapter()
  attrs = zca.getAttrs()
  def cb(node, d):
    if node.meta_id in ['ZMSFile']:
      try:
        text = catalog_analysis.catalog_analysis(node, node.attr('file').getData())
        d['standard_html'] = text
      except:
        standard.writeError(node,"can't catalog_analysis")
        d['standard_html'] = '@@%s:%s'%('/'.join(node.getPhysicalPath()),'file')
    dindex = {"index":{"_index":root_id,"_id":node.get_uid()}}
    for k in ['id','custom']:
      if k in d:
        del d[k]
    data.append(json.dumps(dindex))
    data.append(json.dumps(d))
  zca.get_sitemap(cb, zmscontext, recursive=True)
  data = '\n'.join([standard.pystr(x) for x in data])+'\n'
  data = data.replace(zmscontext.getHref2IndexHtml(request),zmscontext.absolute_url()[len(request['SERVER_URL']):]+'/')
  
  jsonpath = '%s/var/%s/opensearch/%s.json'%(inst_home,path,home_id)
  try:
      bak = standard.localfs_read(jsonpath,mode='b')
      standard.localfs_write('%s.bak'%jsonpath,bak,mode='b')
  except:
      standard.writeError(zmscontext,"can't backup")
  standard.localfs_write(jsonpath,data,mode='b')
  msg.append('%i json-bytes written to %s'%(len(data),jsonpath))
  
  RESPONSE.setHeader('Content-Type','text/plain;charset=utf-8')
  msg.append("Done!")
  return '\n'.join(msg)

# --// /manage_zcatalog_export_data //--