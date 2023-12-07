import sys
from xml.dom import minidom
# Product Imports.
from Products.zms import standard

# --------------------------------------------------------------------------
#  ZMSZCatalogConnector.suggest_xml:
# --------------------------------------------------------------------------
def suggest_xml(self, q, fq='', limit=5, debug=0, pretty=0, REQUEST=None, RESPONSE=None):
  """ ZMSZCatalogConnector.suggest_xml """
  # Check constraints.
  REQUEST.set('lang', REQUEST.get('lang', self.getPrimaryLanguage()))
  RESPONSE = REQUEST.RESPONSE
  content_type = 'text/xml;charset=utf-8'
  if debug!=0:
    content_type = 'text/plain; charset=utf-8'
  RESPONSE.setHeader('Content-Type', content_type)
  RESPONSE.setHeader('Cache-Control', 'no-cache')
  RESPONSE.setHeader('Pragma', 'no-cache')
  # Execute query.
  status = 0
  msg = ''
  results = []
  try: 
    results = self.suggest(q, limit)
  except:
    standard.writeError(self, '[suggest_xml]')
    t, v, tb = sys.exc_info()
    status = 400
    msg = v
  # Assemble xml.
  xml = self.getXmlHeader()
  xml += '<response>'
  xml += '<lst name="responseHeader">'
  xml += '<int name="status">%i</int>'%status
  xml += '</lst>'
  if status > 0:
    xml += '<lst name="error">'
    xml += '<int name="msg">%s</int>'%msg
    xml += '<int name="code">%i</int>'%status
    xml += '</lst>'
  else:
    xml += '<lst>'
    xml += '<lst name="suggestions">'
    xml += '<int name="numFound">%i</int>'%len(results)
    xml += '<arr name="suggestion">'
    for result in results:
      xml += '<str>%s</str>'%result
    xml += '</arr>'
    xml += '</lst>'
    xml += '</lst>'
  xml += '</response>'
  if pretty!=0:
    # Prettify xml
    xml = minidom.parseString(xml).toprettyxml(indent='  ')
  return xml
