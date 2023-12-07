import sys
from xml.dom import minidom
# Product Imports.
from Products.zms import standard

# --------------------------------------------------------------------------
#  ZMSZCatalogConnector.search_xml:
# --------------------------------------------------------------------------
def search_xml(self, q, page_index=0, page_size=10, debug=0, pretty=0, REQUEST=None, RESPONSE=None):
  """ ZMSZCatalogConnector.search_xml """
  # Check constraints.
  page_index = int(page_index)
  page_size = int(page_size)
  REQUEST.set('lang', REQUEST.get('lang', self.getPrimaryLanguage()))
  RESPONSE = REQUEST.RESPONSE
  content_type = 'text/xml; charset=utf-8'
  if debug!=0:
    content_type = 'text/plain; charset=utf-8'
  RESPONSE.setHeader('Content-Type', content_type)
  RESPONSE.setHeader('Cache-Control', 'no-cache')
  RESPONSE.setHeader('Pragma', 'no-cache')
  RESPONSE.setHeader('Access-Control-Allow-Origin', '*')
  # Execute query.
  status = 0
  msg = ''
  results = []
  try: 
    results = self.search(q, REQUEST.get('fq[]', ''))
  except:
    standard.writeError(self, '[search_xml]')
    t, v, tb = sys.exc_info()
    status = 400
    msg = v
  # Assemble xml.
  xml = self.getXmlHeader()
  xml += '<response>'
  xml += '<lst name="responseHeader">'
  xml += '<int name="status">%i</int>'%status
  xml += '<lst name="params">'
  for key in REQUEST.form.keys():
    xml += '<str name="%s">%s</str>'%(key, standard.html_quote(REQUEST.form[key]))
  xml += '</lst>'
  xml += '</lst>'
  xmlr = ''
  if status <= 0:
    xmlr += '<result name="response" numFound="%i" start="%i">'%(len(results), page_index*page_size)
    if len(results) > page_size:
      results = results[page_index*page_size:(page_index+1)*page_size]
    for result in results:
      xmlr += '<doc>'
      for k in result.keys():
        try:
          v = result[k]
          if k == 'zcat_column_loc':
            k = 'loc'
          elif k == 'zcat_column_index_html':
            k = 'index_html'
          elif k == 'zcat_column_custom':
            k = 'custom'
          elif k == 'standard_html':
            v = standard.remove_tags(v)
          xmlr += '<arr name="%s">'%k
          if isinstance(v,str):
            for x in range(16):
              v = v.replace(chr(x), '')
          if k == 'custom':
            xmlr += '<str>%s</str>'%v
          else:
            xmlr += '<str><![CDATA[%s]]></str>'%v
          xmlr += '</arr>'
        except:
          standard.writeError(self, '[search_xml]: result=%s, k=%s'%(str(result), k))
          t, v, tb = sys.exc_info()
          status = 400
          msg = v
          break
      xmlr += '</doc>'
    xmlr += '</result>'
  if status > 0:
    xmlr = ''
    xmlr += '<lst name="error">'
    xmlr += '<str name="msg">%s</str>'%standard.html_quote(msg)
    xmlr += '<int name="code">%i</int>'%status
    xmlr += '</lst>'
  xml += str(xmlr)
  xml += '</response>'
  if pretty!=0:
    # Prettify xml
    xml = minidom.parseString(xml).toprettyxml(indent='  ')
  return xml
