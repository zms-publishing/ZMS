# --// manage_zcatalog_create_sitemap //--

from Products.zms import standard
from Products.zms import content_extraction

def manage_zcatalog_create_sitemap( self):
  msg = []
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
  fileparsing = standard.pybool(request.get('fileparsing'))
  zmscontext = self.getLinkObj(request.get('uid','{$}'))
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
  xml = []
  xml.append('<?xml version="1.0"?>')
  xml.append('<add>')
  zca = zmscontext.getCatalogAdapter()
  attrs = zca.getAttrs()
  def cb(node, d):
    if node.meta_id in ['ZMSFile']:
      try:
        text = content_extraction.extract_content(node, node.attr('file').getData())
        d['standard_html'] = text
      except:
        standard.writeError(node,"can't extract_content")
        d['standard_html'] = '@@%s:%s'%('/'.join(node.getPhysicalPath()),'file')
    doc =  []
    doc.append('<doc>')
    text = []
    for k in d:
      name = k
      boost = 1.0
      v = d[k]
      if k not in ['id']:
        if k in attrs:
          boost = attrs[k]['boost']
          if isinstance(v, str):
            name = '%s_t'%k
            text.append(v)
        else:
          if isinstance(v, str):
            name = '%s_s'%k
      if name.endswith("_t"):
        v = '<![CDATA[%s]]>'%(standard.remove_tags(v))
      doc.append('<field name="%s" boost="%.1f">%s</field>'%(name, boost, v))
    doc.append('<field name="text_t"><![CDATA[%s]]></field>'%(standard.remove_tags(' '.join([x for x in text if x]))))
    doc.append('</doc>')
    xml.extend(doc)
  zca.get_sitemap(cb, zmscontext, recursive=True, fileparsing=fileparsing)
  xml.append('</add>')
  xml = '\n'.join([standard.pystr(x) for x in xml])
  xml = xml.replace(zmscontext.getHref2IndexHtml(request),zmscontext.absolute_url()[len(request['SERVER_URL']):]+'/')
  
  xmlpath = '%s/var/%s/sitemap.xml'%(inst_home,path)
  try:
      bak = standard.localfs_read(xmlpath,mode='b')
      standard.localfs_write('%s.bak'%xmlpath,bak,mode='b')
  except:
      standard.writeError(zmscontext,"can't backup")
  standard.localfs_write(xmlpath,xml,mode='b')
  msg.append('%i xml-bytes written to %s'%(len(xml),xmlpath))
  
  RESPONSE.setHeader('Content-Type','text/plain;charset=utf-8')
  msg.append("Done!")
  return '\n'.join(msg)

# --// /manage_zcatalog_create_sitemap //--