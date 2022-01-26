# --// manage_zcatalog_create_sitemap //--

from Products.zms import standard

def manage_zcatalog_create_sitemap( self):
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
  
  zmscontext.f_standard_html_request(request)
  xml = []
  xml.append('<?xml version="1.0"?>')
  xml.append('<add>')
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
  zca.get_sitemap(cb, zmscontext, recursive=True)
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