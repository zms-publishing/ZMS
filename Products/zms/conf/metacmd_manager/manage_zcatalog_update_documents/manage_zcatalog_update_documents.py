# --// manage_zcatalog_update_documents //--

from Products.zms import standard

def manage_zcatalog_update_documents( self):
  msg = []
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
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
  
  xmlpath = '%s/var/%s/sitemap.xml'%(inst_home,path)
  xml = standard.localfs_read(xmlpath,mode={'threshold':-1}).decode('utf-8')
  msg.append('%i xml-bytes read from %s'%(len(xml),xmlpath))
  
  def update(action, xml):
      solr_url = zmscontext.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = zmscontext.getConfProperty('solr.core', home_id)
      url = '%s/%s/update'%(solr_url, solr_core)
      url = '%s?%s'%(url, xml)
      standard.writeLog(zmscontext, "[manage_zcatalog_update_documents.update]: %s=%s"%(action,url))
      result = standard.pystr(standard.http_import(zmscontext, url, method='POST', headers={'Content-Type':'text/xml;charset=UTF-8'}))
      standard.writeLog(zmscontext, "[manage_zcatalog_update_documents.update]: %s=%s"%(action,result))
      return '%s=%s'%(action,result)
  
  def update_extract(action, data):
      solr_url = zmscontext.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = zmscontext.getConfProperty('solr.core', home_id)
      url = '%s/%s/update/extract'%(solr_url, solr_core)
      standard.writeLog(zmscontext, "[manage_zcatalog_update_documents.update]: %s=%s"%(action,url))
      response = standard.pystr(standard.http_request(url, method='POST', data=data, headers={'Content-Type':'multipart/form-data'}))
      standard.writeLog(zmscontext, "[manage_zcatalog_update_documents.update]: %s=%s"%(action,response))
      return '%s=%s'%(action,response)
  
  def get_delete_xml(query='*', attrs={}):
      xml =  []
      xml.append('<?xml version="1.0" encoding="utf-8"?>')
      xml.append('<delete'+' '.join(['']+['%s="%s"'%(x,str(attrs[x])) for x in attrs])+'>')
      xml.append('<query>%s</query>'%query)
      xml.append('</delete>')
      return '\n'.join(xml)
  
  def get_command_xml(command):
      xml =  []
      xml.append('<?xml version="1.0" encoding="utf-8"?>')
      xml.append('<%s/>'%command)
      return '\n'.join(xml)
  
  msg.append(update("delete", get_delete_xml(query='home_id_s:%s'%home_id)))
  msg.append(update("commit", get_command_xml('commit')))
  xml = xml[xml.find('<add>')+len('<add>'):]
  xml = xml[:xml.find('</add>')]
  docs = ['%s</doc>'%x for x in xml.split('</doc>') if x.strip()]
  bins = []
  msg.append("=== [%i]"%len(docs))
  buff = []
  while True:
    if len(buff) == request.get('bufsiz',1) or len(docs) == 0:
      msg.append("--- [%i]"%len(buff))
      try:
        i = '\n'.join(buff)
        i = i.replace('&amp;gt;',' ').replace('&amp;lt;',' ').replace('#','%23')
        i = '<?xml version="1.0" encoding="utf-8"?><add>%s</add>'%i
        msg.append(update("update", i))
      except:
        msg.append("*** except: %s"%str(i))
        msg.append(standard.writeError(zmscontext,"can't update"))
      msg.append("---")
      msg.append(update("commit", get_command_xml('commit')))
      buff = []
    if len(docs) == 0:
      break
    doc = docs[0]
    i = doc.find('">@@')
    if i >= 0:
      body = doc[i+len('">@@'):]
      body = body[:body.find('</field>')]
      id = standard.re_search(r'<field name="id"(.*?)>(.*?)<\/field>', doc)[1]
      bins.append({'id':id,'body':body})
      doc = standard.re_sub(r'<field name="(.*?)_t"(.*?)>@@(.*?)<\/field>','<field name="\\1_t"\\2></field>',doc)
    buff.append(doc)
    docs.remove(docs[0])
  msg.append(update("commit", get_command_xml('commit')))
  for b in bins:
    body = b['body'].split(':')
    ids = body[0].split('/')[1:]
    attr_name = body[1]
    node = home
    while ids:
      node = getattr(node,ids.pop(0))
    d = {'literal.id': b['id'], 'commit': 'true', 'myfile': node.attr(attr_name).getData(request)}
    msg.append(update_extract("extract", d))
  msg.append(update("optimize", get_command_xml('optimize')))
  
  RESPONSE.setHeader('Content-Type','text/plain;charset=utf-8')
  msg.append("Done!")
  return '\n'.join(msg)

# --// /manage_zcatalog_update_documents //--