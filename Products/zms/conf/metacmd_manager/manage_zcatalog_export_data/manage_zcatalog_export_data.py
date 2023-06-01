# --// manage_zcatalog_export_data //--

import json
from Products.zms import standard

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
        # pdfminer.six (https://github.com/pdfminer/pdfminer.six)
        # Pdfminer.six is a community maintained fork of the original PDFMiner. 
        # It is a tool for extracting information from PDF documents. It focuses
        # on getting and analyzing text data. Pdfminer.six extracts the text 
        # from a page directly from the sourcecode of the PDF. 
        # pip install pdfminer.six
        from io import BytesIO, StringIO
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.pdfpage import PDFPage
        from pdfminer.pdfparser import PDFParser
        output_string = StringIO()
        ob_file = node.attr('file')
        in_file = BytesIO(ob_file.getData())
        parser = PDFParser(in_file)
        standard.writeError(node,"pdfminer: doc")
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        v = output_string.getvalue()
        d['standard_html'] = v
      except:
        standard.writeError(node,"can't pdfminer")
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

# --// /manage_zcatalog_create_sitemap //--