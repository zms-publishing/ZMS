"""
_deprecatedapi.py

Defines DeprecatedAPI for REST API endpoints and HTTP protocol handling.
It exposes content via JSON/XML, handles authentication, and implements HTTP semantics.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
import re
# Product Imports.
from Products.zms import _fileutil, _globals
from Products.zms import _xmllib
from Products.zms import standard


def warn(self,old,new=None):
  """Implement 'warn'."""
  import warnings
  warnings.warn('Using <%s@%s>.%s() is deprecated.'
               ' Use %s() instead.'%(self.meta_id, self.absolute_url(), old, [old, new][new is not None]),
                 DeprecationWarning, 
                 stacklevel=2)

class DeprecatedAPI(object):

  # Create a SecurityInfo for this class. We will use this
  # in the rest of our class definition to make security
  # assertions.
  """Provide helpers for DeprecatedAPI."""
  security = ClassSecurityInfo()

  f_bo_area = '' 
  f_eo_area = '' 
  f_submitBtn = '' 

  def f_bodyContent(self, *args, **kwargs):
    """Implement 'f_bodyContent'."""
    warn(self, 'f_bodyContent', 'None')
    request = self.REQUEST 
    response = request.RESPONSE
    return self.getBodyContent(request)

  def zmi_form_section_begin(self, *args, **kwargs):
    """Implement 'zmi_form_section_begin'."""
    warn(self, 'zmi_form_section_begin', 'None')
    return ''

  def zmi_form_section_end(self, *args, **kwargs):
    """Implement 'zmi_form_section_end'."""
    warn(self, 'zmi_form_section_end', 'None')
    return ''

  def f_selectInput(self, *args, **kwargs):
    """Implement 'f_selectInput'."""
    warn(self, 'f_selectInput', 'getSelect')
    return self.getSelect(fmName=kwargs['fmName'], elName=kwargs['elName'], value=kwargs['value'], inputtype=kwargs['inputtype'], lang_str=kwargs['lang_str'], required=kwargs['required'], optpl=kwargs['optpl'], enabled=kwargs['enabled'])

  def f_headline(self, *args, **kwargs):
    """Implement 'f_headline'."""
    warn(self, 'f_headline', 'None')
    return '<h2>%s</h2><div>%s</div>'%(kwargs.get('headline', ''), kwargs.get('extra', '')) 

  def getTitleimage( self, REQUEST): 
    """Return titleimage."""
    warn(self, 'getTitleimage(REQUEST)', 'attr(\'titleimage\')')
    return self.getObjProperty('titleimage', REQUEST) 

  def getImage(self, REQUEST):
    """Return image."""
    warn(self, 'getImage(REQUEST)', 'attr(\'img\')')
    return self.getObjProperty('img', REQUEST)

  def getFile(self, REQUEST):
    """Return file."""
    warn(self, 'getFile(REQUEST)', 'attr(\'file\')')
    return self.getObjProperty('file', REQUEST)

  def getFormat(self, REQUEST):
    """Return format."""
    warn("[getFormat]: @deprecated: returns \"getObjProperty('format',REQUEST)\" for compatibility reasons!")
    return self.getObjProperty('format', REQUEST)

  def meta_id_or_type(self):
    """Implement 'meta_id_or_type'."""
    warn(self, 'meta_id_or_type', 'meta_id')
    return self.meta_id

  def absolute_obj_path(self):
    """Implement 'absolute_obj_path'."""
    warn(self, 'absolute_obj_path', 'None')
    ob = self.getDocumentElement()
    return '%s/%s/'%(ob.aq_parent.id, self.absolute_url()[len(ob.aq_parent.absolute_url())+1:])

  """
  Resolves internal/external links and returns Html. 
  """
  def getLinkHtml( self, url, html='<a href="%s">&raquo;</a>', REQUEST=None): 
    """Return linkhtml."""
    warn(self, 'getLinkHtml', '@deprecated: use own implementation!')
    REQUEST = standard.nvl( REQUEST, self.REQUEST) 
    s = '' 
    ob = self 
    while ob is not None: 
      if html in ob.getMetaobjIds() and 'getLinkHtml' in ob.getMetaobjAttrIds(html):
        REQUEST.set( 'ref_id', url) 
        return ob.evalMetaobjAttr('%s.getLinkHtml'%html,ref_id=url)
      ob = ob.getPortalMaster() 
    ob = self.getLinkObj(url) 
    if ob is not None: 
      if ob.isVisible(REQUEST): 
        url = ob.getHref2IndexHtml(REQUEST) 
        s = html%url 
    return s 


  # --------------------------------------------------------------------------
  #  DeprecatedAPI.ZCatalogItem:
  # --------------------------------------------------------------------------
  def search_quote(self, s, maxlen=255, tag='&middot;'):
    """Implement 'search_quote'."""
    warn(self, 'search_quote', 'Products.zms.standard.string_maxlen')
    return standard.string_maxlen(s, maxlen, etc=tag*3)

  def search_encode(self, s):
    """Implement 'search_encode'."""
    warn(self, 'search_encode', 'Products.zms.standard.umlaut_quote')
    return standard.umlaut_quote(s)

  def getCatalogNavUrl(self, REQUEST):
    """Return catalognavurl."""
    warn(self, 'getCatalogNavUrl', 'None')
    return self.url_inherit_params(REQUEST['URL'], REQUEST, ['qs'])


  # --------------------------------------------------------------------------
  #  DeprecatedAPI.ZMSGlobals:
  # --------------------------------------------------------------------------
  """
  Replace special characters in string for javascript.
  """
  def js_quote(self, text, charset=None):
    """Implement 'js_quote'."""
    warn(self, 'js_quote', 'None')
    text = standard.pystr(text)
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    text = text.replace('"', '\\"').replace("'", "\\'")
    return text

  def zmi_manage_css(self, *args, **kwargs):
    """ ZMSItem.zmi_manage_css """
    warn(self, 'zmi_manage_css', 'None')
    request = self.REQUEST
    response = request.RESPONSE
    response.setHeader('Content-Type', 'text/css')
    css = []
    for stylesheet in self.getStylesheets():
      try:
        s = stylesheet(self)
      except:
        s = standard.pystr(stylesheet)
      css.append("/* ######################################################################")
      css.append("   ### %s"%stylesheet.absolute_url())
      css.append("   ###################################################################### */")
      css.append(s)
    return '\n'.join(css)

  """
  Parses default-stylesheet and returns elements.
  @deprecated
  @return: Elements
  @rtype: C{dict}
  """
  def parse_stylesheet(self):
    """Implement 'parse_stylesheet'."""
    warn(self, 'parse_stylesheet', 'None')
    stylesheet = self.getStylesheet()
    if stylesheet.meta_type in ['DTML Document', 'DTML Method']:
      data = stylesheet.raw
    elif stylesheet.meta_type in ['File']:
      data = stylesheet.data
    data = re.sub(r'/\*(.*?)\*/', '', data)
    value = {}
    for elmnt in data.split('}'):
      i = elmnt.find('{')
      keys = elmnt[:i].strip()
      v = elmnt[i+1:].strip()
      for key in keys.split(','):
        key = key.strip()
        if len(key) > 0:
          value[key] = value.get(key, '') + v
    colormap = {}
    for key in value:
      if key.startswith('.') and \
         key.find('Color') > 0 and \
         key.find('.cms') < 0 and \
         key.find('.zmi') < 0:
        for elmnt in value[key].split(';'):
          i = elmnt.find(':')
          if i > 0:
            elmntKey = elmnt[:i].strip().lower()
            elmntValue = elmnt[i+1:].strip().lower()
            if elmntKey == 'color' or elmntKey == 'background-color':
              colormap[key[1:]] = elmntValue
    self.setConfProperty('ZMS.colormap', colormap)
    return colormap

  def get_colormap(self):
    """Return colormap."""
    warn(self, 'get_colormap', 'None')
    colormap = self.getConfProperty('ZMS.colormap', None)
    if colormap is None:
      try:
        colormap = self.parse_stylesheet()
      except:
        # Destroy Colormap on Error
        colormap = {}
        self.setConfProperty('ZMS.colormap', colormap)
    return colormap

  """
  Returns parents for linked list.
  @rtype: C{list}
  """
  def tree_parents(self, l, i='id', r='idId', v='', deep=1, reverse=1):
    """Implement 'tree_parents'."""
    warn(self, 'tree_parents', 'None')
    k = []
    for x in l:
      if x.get(i)==v:
        k.append(x)
        if deep:
          k.extend(self.tree_parents(l, i, r, x[r], deep, 0))
    if reverse:
      k.reverse()
    return k

  """
  Returns children for linked list.
  @rtype: C{list}
  """
  def tree_list(self, l, i='id', r='idId', v='', deep=0):
    """Implement 'tree_list'."""
    warn(self, 'tree_list', 'None')
    k = []
    for x in l:
      if x.get(r)==v:
        k.append(x)
        if deep:
          k.extend(self.tree_list(l, i, r, x[i], deep))
    return k

  def string_maxlen(self, s, maxlen=20, etc='...', encoding=None):
    """Implement 'string_maxlen'."""
    warn(self, 'string_maxlen', 'Products.zms.standard.string_maxlen')
    return standard.string_maxlen(s, maxlen, etc, encoding)

  def get_id_prefix(self, s):
    """Return id prefix."""
    warn(self, 'get_id_prefix', 'Products.zms.standard.id_prefix')
    return standard.id_prefix(s)

  def id_quote(self, s, mapping={'\x20': '_', '-': '_', '/': '_',}):
    """Implement 'id_quote'."""
    warn(self, 'id_quote', 'Products.zms.standard.id_quote')
    return standard.id_quote(s, mapping)

  def parseLangFmtDate(self, s, lang=None, fmt_str=None, recflag=None):
    """Implement 'parseLangFmtDate'."""
    warn(self, 'parseLangFmtDate', 'Products.zms.standard.parseLangFmtDate')
    return standard.parseLangFmtDate(s)

  def compareDate(self, t0, t1):
    """Implement 'compareDate'."""
    warn(self, 'compareDate', 'Products.zms.standard.compareDate')
    return standard.compareDate(t0, t1) 

  def daysBetween(self, t0, t1):
    """Implement 'daysBetween'."""
    warn(self, 'daysBetween', 'Products.zms.standard.daysBetween')
    return standard.daysBetween(t0, t1) 

  def encrypt_ordtype(self, s):
    """Implement 'encrypt_ordtype'."""
    warn(self, 'encrypt_ordtype', 'Products.zms.standard.encrypt_ordtype')
    return standard.encrypt_ordtype(s)

  def encrypt_password(self, pw, algorithm='md5', hex=False):
    """Implement 'encrypt_password'."""
    warn(self, 'encrypt_password', 'Products.zms.encrypt_password')
    return standard.encrypt_password(pw, algorithm, hex)

  def encrypt_schemes(self):
    """Implement 'encrypt_schemes'."""
    warn(self, 'encrypt_schemes', 'Products.zms.encrypt_schemes')
    return standard.encrypt_schemes()

  def nvl(self, a1, a2, n=None):
    """Implement 'nvl'."""
    warn(self, 'nvl', 'Products.zms.standard.nvl')
    return standard.nvl( a1, a2, n)

  def rand_int(self, n):
    """Implement 'rand_int'."""
    warn(self, 'rand_int', 'Products.zms.standard.rand_int')
    return standard.rand_int(n)

  def re_findall( self, pattern, text, ignorecase=False):
    """Implement 're_findall'."""
    warn(self, 're_findall', 'Products.zms.standard.re_findall')
    return standard.re_findall(pattern, text, ignorecase)

  def re_search( self, pattern, subject, ignorecase=False):
    """Implement 're_search'."""
    warn(self, 're_search', 'Products.zms.standard.re_search')
    return standard.re_search(pattern, subject, ignorecase)

  def re_sub( self, pattern, replacement, subject, ignorecase=False):
    """Implement 're_sub'."""
    warn(self, 're_sub', 'Products.zms.standard.re_sub')
    return standard.re_sub(pattern, replacement, subject, ignorecase)

  def operator_gettype(self, v):
    """Implement 'operator_gettype'."""
    warn(self, 'operator_gettype', 'Products.zms.standard.operator_gettype')
    return standard.operator_gettype(v)
  
  def operator_setitem(self, a, b, c):
    """Implement 'operator_setitem'."""
    warn(self, 'operator_setitem', 'Products.zms.standard.operator_setitem')
    return standard.operator_setitem(a, b, c)
  
  def operator_getitem(self, a, b, c=None, ignorecase=True):
    """Implement 'operator_getitem'."""
    warn(self, 'operator_getitem', 'Products.zms.standard.operator_getitem')
    return standard.operator_getitem(a, b, c, ignorecase)
  
  def operator_delitem(self, a, b):
    """Implement 'operator_delitem'."""
    warn(self, 'operator_delitem', 'Products.zms.standard.operator_delitem')
    return standard.operator_delitem(a, b)
  
  def operator_setattr(self, a, b, c):
    """Implement 'operator_setattr'."""
    warn(self, 'operator_setattr', 'Products.zms.standard.operator_setattr')
    return standard.operator_setattr(a, b, c)
  
  def operator_getattr(self, a, b, c=None):
    """Implement 'operator_getattr'."""
    warn(self, 'operator_getattr', 'Products.zms.standard.operator_getattr')
    return standard.operator_getattr(a, b, c)
  
  def operator_delattr(self, a, b):
    """Implement 'operator_delattr'."""
    warn(self, 'operator_delattr', 'Products.zms.standard.operator_delattr')
    return standard.operator_delattr(a, b)
  
  def intersection_list(self, l1, l2):
    """Implement 'intersection_list'."""
    warn(self, 'intersection_list', 'Products.zms.standard.intersection_list')
    return standard.intersection_list(l1, l2)

  def difference_list(self, l1, l2):
    """Implement 'difference_list'."""
    warn(self, 'difference_list', 'Products.zms.standard.difference_list')
    return standard.difference_list(l1, l2)

  def concat_list(self, l1, l2):
    """Implement 'concat_list'."""
    warn(self, 'concat_list', 'Products.zms.standard.concat_list')
    return standard.concat_list(l1, l2)

  def dict_list(self, l):
    """Implement 'dict_list'."""
    warn(self, 'dict_list', 'Products.zms.standard.dict_list')
    return standard.dict_list(l)

  def distinct_list(self, l, i=None):
    """Implement 'distinct_list'."""
    warn(self, 'distinct_list', 'Products.zms.standard.distinct_list')
    return standard.distinct_list(l, i)

  def sort_list(self, l, qorder=None, qorderdir='asc', ignorecase=1): 
    """Implement 'sort_list'."""
    warn(self, 'sort_list', 'Products.zms.standard.sort_list')
    return standard.sort_list(l, qorder, qorderdir, ignorecase)

  def string_list(self, s, sep='\n', trim=True):
    """Implement 'string_list'."""
    warn(self, 'string_list', 'Products.zms.standard.string_list')
    return standard.string_list(s, sep, trim)

  def str_json(self, i, encoding='ascii', errors='xmlcharrefreplace', formatted=False, level=0):
    """Implement 'str_json'."""
    warn(self,'str_json','Products.zms.standard.str_json')
    import json
    return json.dumps(i)

  def str_item(self, i):
    """Implement 'str_item'."""
    warn(self, 'str_item', 'Products.zms.standard.str_item')
    return standard.str_item(i)

  def filter_list(self, l, i, v, o='%'):
    """Implement 'filter_list'."""
    warn(self, 'filter_list', 'Products.zms.standard.filter_list')
    return standard.filter_list(l, i, v, o)

  def copy_list(self, l):
    """Implement 'copy_list'."""
    warn(self, 'copy_list', 'Products.zms.standard.copy_list')
    return standard.copy_list(l)

  def sync_list(self, l, nl, i):
    """Implement 'sync_list'."""
    warn(self, 'sync_list', 'Products.zms.standard.sync_list')
    return standard.sync_list(l, nl, i)

  def aggregate_list(self, l, i):
    """Implement 'aggregate_list'."""
    warn(self, 'aggregate_list', 'Products.zms.standard.aggregate_list')
    return standard.aggregate_list(l, i)

  def url_append_params(self, url, dict, sep='&'):
    """Implement 'url_append_params'."""
    warn(self, 'url_append_params', 'Products.zms.standard.url_append_params')
    return standard.url_append_params(url, dict, sep)

  def url_inherit_params(self, url, REQUEST, exclude=[], sep='&amp;'):
    """Implement 'url_inherit_params'."""
    warn(self, 'url_inherit_params', 'Products.zms.standard.url_inherit_params')
    return standard.url_inherit_params(url, REQUEST, exclude, sep)

  def getZipArchive(self, f):
    """Return ziparchive."""
    warn(self, 'getZipArchive', 'None')
    return _fileutil.getZipArchive(f)

  def extractZipArchive(self, f):
    """Implement 'extractZipArchive'."""
    warn(self, 'extractZipArchive', 'None')
    return _fileutil.extractZipArchive(f)

  def buildZipArchive( self, files, get_data=True):
    """Implement 'buildZipArchive'."""
    warn(self, 'buildZipArchive', 'None')
    return _fileutil.buildZipArchive( files, get_data)

  def getXmlHeader(self, encoding='utf-8'):
    """Return xmlheader."""
    warn(self, 'getXmlHeader', 'Products.zms.standard.getXmlHeader')
    return standard.getXmlHeader(encoding)

  def toXmlString(self, v, xhtml=False, encoding='utf-8'):
    """Implement 'toXmlString'."""
    warn(self, 'toXmlString', 'Products.zms.standard.toXmlString')
    return standard.toXmlString(self, v, xhtml, encoding)

  def parseXmlString(self, xml):
    """Implement 'parseXmlString'."""
    warn(self, 'parseXmlString', 'Products.zms.standard.parseXmlString')
    return standard.parseXmlString(xml)

  def xslProcess(self, xsl, xml):
    """Implement 'xslProcess'."""
    warn(self, 'xslProcess', 'None')
    return self.processData('xslt', xml, xsl)

  def processData(self, processId, data, trans=None):
    """Implement 'processData'."""
    warn(self, 'processData', 'Products.zms.standard.processData')
    return standard.processData(self, processId, data, trans)

  def xmlParse(self, xml):
    """Implement 'xmlParse'."""
    warn(self, 'xmlParse', 'None')
    return _xmllib.xmlParse(xml)

  def xmlNodeSet(self, mNode, sTagName='', iDeep=0):
    """Implement 'xmlNodeSet'."""
    warn(self, 'xmlNodeSet', 'Products.zms.standard.xmlNodeSet')
    return _xmllib.xmlNodeSet( mNode, sTagName, iDeep)

  def dt_executable(self, v):
    """Implement 'dt_executable'."""
    warn(self, 'dt_executable', 'Products.zms.standard.dt_executable')
    return standard.dt_executable(v)

  def dt_exec(self, v, o={}):
    """Implement 'dt_exec'."""
    warn(self, 'dt_exec', 'Products.zms.standard.dt_exec')
    return standard.dt_exec(self, v, o)

  def sendMail(self, mto, msubject, mbody, REQUEST=None, mattach=None):
    """Implement 'sendMail'."""
    warn(self, 'sendMail', 'Products.zms.standard.sendMail')
    return standard.sendMail(self, mto, msubject, mbody, REQUEST, mattach)

  def getPRODUCT_HOME(self):
    """Return product home."""
    warn(self, 'getPRODUCT_HOME', 'Products.zms.standard.getPRODUCT_HOME')
    return standard.getPRODUCT_HOME()

  def getPACKAGE_HOME(self):
    """Return package home."""
    warn(self, 'getPACKAGE_HOME', 'Products.zms.standard.getPACKAGE_HOME')
    return standard.getPACKAGE_HOME()

  def getINSTANCE_HOME(self):
    """Return instance home."""
    warn(self, 'getINSTANCE_HOME', 'Products.zms.standard.getINSTANCE_HOME')
    return standard.getINSTANCE_HOME()

  def writeLog(self, info):
    """Implement 'writeLog'."""
    warn(self, 'writeLog', 'Products.zms.standard.writeLog')
    return standard.writeLog( self, info)

  def writeBlock(self, info):
    """Implement 'writeBlock'."""
    warn(self, 'writeBlock', 'Products.zms.standard.writeBlock')
    return standard.writeBlock( self, info)

  def writeError(self, info):
    """Implement 'writeError'."""
    warn(self, 'writeError', 'Products.zms.standard.writeError')
    return standard.writeError( self, info)

  def getDataSizeStr(self, len):
    """Return datasizestr."""
    warn(self, 'getDataSizeStr', 'Products.zms.standard.getDataSizeStr')
    return standard.getDataSizeStr(len)

  def getMimeTypeIconSrc(self, mt):
    """Return mimetypeiconsrc."""
    warn(self, 'getMimeTypeIconSrc', 'Products.zms.standard.getMimeTypeIconSrc')
    return standard.getMimeTypeIconSrc(mt)
    
  def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}, debug=0 ):
    """Implement 'http_import'."""
    warn(self, 'http_import', 'Products.zms.standard.http_import')
    return standard.http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers, debug=int(debug) )

  def getLangFmtDate(self, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
    """Return langfmtdate."""
    warn(self, 'getLangFmtDate', 'Products.zms.standard.getLangFmtDate')
    return standard.getLangFmtDate(self, t, lang, fmt_str)

  def isFeatureEnabled(self, feature=''):
    """Return whether featureenabled."""
    warn(self, 'isFeatureEnabled', 'Products.zms.standard.is_conf_enabled')
    return standard.is_conf_enabled(self, feature)

  # --------------------------------------------------------------------------
  #  ZMSObject.ajaxGetNodes:
  # --------------------------------------------------------------------------
  security.declareProtected('View', 'ajaxGetNodes')
  def ajaxGetNodes(self, context=None, lang=None, xml_header=True, REQUEST=None):
    """ ZMSObject.ajaxGetNodes """
    warn(self, 'ajaxGetNodes', '++rest_api')
    context = standard.nvl(context, self)
    refs = REQUEST.get('refs', [])
    if len(refs)==0:
      for key in REQUEST.keys():
        if key.startswith('ref') and key[3:].isdigit():
          refs.append((int(key[3:]), REQUEST[key]))
      refs.sort()
      refs = [x[1] for x in refs]
    # Build xml.
    xml = ''
    if xml_header:
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/plain; charset=utf-8'
      filename = 'ajaxGetNodes.xml'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml += self.getXmlHeader()
    xml += '<pages>'
    for ref in refs:
      ob = self.getLinkObj(ref)
      if ob is None:
        xml += '<page ref="%s" not_found="1"/>'%ref
      else:
        xml += ob.ajaxGetNode(context=context, lang=lang, xml_header=False, REQUEST=REQUEST)
    xml += "</pages>"
    return xml


  security.declareProtected('View', 'ajaxGetNode')
  def ajaxGetNode(self, context=None, lang=None, xml_header=True, meta_types=None, REQUEST=None):
    """
    Generate an XML representation of the node with its properties and attributes.
    
    This method constructs an XML document containing detailed information about the current
    ZMS object, including its URL, physical path, access permissions, and optionally its
    attributes based on configuration parameters.
    
    @param context: Context object used for generating absolute URLs and index_html references.
            If not provided, defaults to self.
    @type context: C{ZMSObject} or C{None}
    @param lang: Language identifier for retrieving localized title and titlealt values.
           If not provided, uses the current language context.
    @type lang: C{str} or C{None}
    @param xml_header: Flag to determine whether to include XML declaration header and set
               appropriate HTTP response headers. When True, sets Content-Type to
               'text/xml; charset=utf-8' and cache control headers.
    @type xml_header: C{bool}
    @param meta_types: Filter criteria for meta types. Currently defined but not actively used
               in filtering logic.
    @type meta_types: C{list} or C{None}
    @param REQUEST: HTTP request object containing form data and response object for setting
            headers. Required for proper functioning of this method.
    @type REQUEST: C{HTTPRequest}
    @return: XML string representation of the node containing element properties, attributes,
         and optional attribute values based on request parameters.
    @note: Deprecated - Use the REST API instead. This method is deprecated in favor of modern
           REST API endpoints (++rest_api).
    """

    warn(self, 'ajaxGetNode', '++rest_api')
    # Build xml.
    xml = ''
    if xml_header:
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxGetNode.xml'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml += self.getXmlHeader()
    xml += '<page'
    xml += " absolute_url=\"%s\""%str(self.getAbsoluteUrlInContext(context))
    xml += " physical_path=\"%s\""%('/'.join(self.getPhysicalPath()))
    xml += " access=\"%s\""%str(int(self.hasAccess(REQUEST)))
    xml += " active=\"%s\""%str(int(self.isActive(REQUEST)))
    try:
      xml += " zmi_icon=\"%s\""%self.zmi_icon()
    except:
      xml += " zmi_icon=\"%s\""%self.zmi_icon
    xml += " display_type=\"%s\""%str(self.display_type())
    xml += " uid=\"{$%s}\""%(self.get_uid())
    xml += " id=\"%s_%s\""%(self.getHome().id, self.id)
    xml += " home_id=\"%s\""%(self.getHome().id)
    xml += " index_html=\"%s\""%standard.html_quote(self.getHref2IndexHtmlInContext(context,REQUEST=REQUEST))
    xml += " is_page=\"%s\""%str(int(self.isPage()))
    xml += " is_pageelement=\"%s\""%str(int(self.isPageElement()))
    xml += " meta_id=\"%s\""%(self.meta_id)
    xml += " title=\"%s\""%standard.html_quote(self.getTitle(REQUEST))
    xml += " titlealt=\"%s\""%standard.html_quote(self.getTitlealt(REQUEST))
    xml += " restricted=\"%s\""%str(self.hasRestrictedAccess())
    xml += " attr_dc_type=\"%s\""%(self.attr('attr_dc_type'))
    xml += ">"
    if REQUEST.form.get('get_attrs', 0):
      obj_attrs = self.getObjAttrs()
      for key in [x for x in obj_attrs if x not in ['title', 'titlealt', 'change_dt', 'change_uid', 'change_history', 'created_dt', 'created_uid', 'attr_dc_coverage', 'attr_cacheable', 'work_dt', 'work_uid']]:
        obj_attr = obj_attrs[ key]
        if obj_attr['datatype_key'] in _globals.DT_TEXTS or \
            obj_attr['datatype_key'] in _globals.DT_NUMBERS or \
            obj_attr['datatype_key'] in _globals.DT_DATETIMES:
          v = self.attr(key)
          if v:
            xml += "<%s>%s</%s>"%(key, standard.toXmlString(self,v).encode('utf-8'), key)
        elif obj_attr['datatype_key'] in _globals.DT_BLOBS:
          v = self.attr(key)
          if v:
            xml += "<%s>"%key
            xml += "<href>%s</href>"%standard.html_quote(v.getHref(REQUEST))
            xml += "<filename>%s</filename>"%standard.html_quote(v.getFilename())
            xml += "<content_type>%s</content_type>"%standard.html_quote(v.getContentType())
            xml += "<size>%s</size>"%standard.getDataSizeStr(v.get_size())
            xml += "<icon>%s</icon>"%standard.getMimeTypeIconSrc(v.getContentType())
            xml += "</%s>"%key
    xml += "</page>"
    return xml

  # --------------------------------------------------------------------------
  #  ZMSObject.ajaxGetParentNodes:
  # --------------------------------------------------------------------------
  security.declareProtected('View', 'ajaxGetParentNodes')
  def ajaxGetParentNodes(self, lang, xml_header=True, meta_types=None, REQUEST=None):
    """ ZMSObject.ajaxGetParentNodes """
    warn(self, 'ajaxGetParentNodes', '++rest_api')
    # Get context.
    context = self
    for id in REQUEST.get('physical_path', '').split('/'):
      if id and context is not None:
        context = getattr(context, id, None)
        if context is None:
          context = self
          break
    # Build xml.
    xml = ''
    if xml_header:
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxGetParentNodes.xml'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml += self.getXmlHeader()
    # Start-tag.
    xml += "<pages"
    for key in REQUEST.form.keys():
      if key.find('get_') < 0 and key not in ['lang', 'preview', 'http_referer', 'meta_types']:
        xml += " %s=\"%s\""%(key, str(REQUEST.form.get(key)))
    xml += " level=\"%i\""%self.getLevel()
    xml += ">\n"
    # Process nodes.
    for node in self.breadcrumbs_obj_path():
      nodexml = node.ajaxGetNode( context=context, lang=lang, xml_header=False, meta_types=meta_types, REQUEST=REQUEST)
      try:
        xml += str(nodexml, 'utf-8', errors='ignore')
      except:
        xml += nodexml
    # End-tag.
    xml += "</pages>"
    # Return xml.
    return xml

  security.declareProtected('View', 'ajaxGetChildNodes')
  def ajaxGetChildNodes(self, lang, xml_header=True, meta_types=None, REQUEST=None):
    """ ZMSObject.ajaxGetChildNodes """
    warn(self, 'ajaxGetChildNodes', '++rest_api')
    # Get context.
    context = self
    for id in REQUEST.get('physical_path', '').split('/'):
      if id and context is not None:
        context = getattr(context, id, None)
        if context is None:
          context = self
          break
    # Build xml.
    xml = ''
    if xml_header:
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxGetChildNodes.xml'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml += self.getXmlHeader()
    xml += "<pages"
    for key in REQUEST.form.keys():
      if key.find('get_') < 0 and key not in ['lang', 'preview', 'http_referer', 'meta_types']:
        xml += " %s=\"%s\""%(key, str(REQUEST.form.get(key)))
    xml += " level=\"%i\""%self.getLevel()
    xml += ">\n"
    if isinstance(meta_types, str) and meta_types.find(',') > 0:
      meta_types = meta_types.split(',')
    if isinstance(meta_types, list):
      new_meta_types = []
      for meta_type in meta_types:
        try:
          new_meta_types.append( int( meta_type))
        except:
          new_meta_types.append( meta_type)
      meta_types = new_meta_types
    if REQUEST.form.get('http_referer'):
      REQUEST.set('URL', REQUEST.form.get('http_referer'))
    # Add child-nodes.
    obs = []
    childNodes = self.getChildNodes(REQUEST, meta_types)
    # Exclude meta-ids.
    excludeMetaIds = self.getConfProperty('ZMS.ajaxGetChildNodes.excludeMetaIds','').split(',')
    childNodes = [x for x in childNodes if x.meta_id not in excludeMetaIds]
    # Sort.
    sortedChildNodes = self.evalMetaobjAttr('sortChildNodes',childNodes=childNodes)
    if isinstance(sortedChildNodes,list):
      childNodes = sortedChildNodes
    obs.extend(childNodes)
    # Add trashcan.
    if ( self.meta_type == 'ZMS') and \
        ( ( isinstance(meta_types, list) and 'ZMSTrashcan' in meta_types) or \
          ( isinstance(meta_types, str) and 'ZMSTrashcan' == meta_types)):
      obs.append( self.getTrashcan())
    if self.meta_type == 'ZMS':
      obs.extend( self.getPortalClients())
    for ob in obs:
      xml += ob.ajaxGetNode( context=context, lang=lang, xml_header=False, meta_types=meta_types, REQUEST=REQUEST)
    xml += "</pages>"
    if REQUEST.RESPONSE.getHeader('Location'):
      del REQUEST.RESPONSE.headers['location']
    return xml  

# call this to initialize framework classes, which
# does the right thing with the security assertions.
InitializeClass(DeprecatedAPI)

