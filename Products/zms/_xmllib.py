"""
_xmllib.py - ZMS XML Parsing and Serialization Utilities

Provides functions for converting ZMS objects to/from XML representation,
including support for complex data types (dictionaries, lists, blobs),
multilingual attributes, and CDATA handling. Contains the L{XmlAttrBuilder}
parser for complex Python attributes and the L{XmlBuilder} parser for custom
XML structures.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""


# Imports.
from io import StringIO
from DateTime import DateTime
from OFS.Image import File
import collections
import pyexpat
import re
import time
import xml.dom
# Product Imports
from Products.zms import standard
from Products.zms import _blobfields
from Products.zms import _globals
from Products.zms import zopeutil


# Product Imports.
INDENTSTR = '  '


# ------------------------------------------------------------------------------
#  Datatype Functions
# ------------------------------------------------------------------------------

def serialize(node):
  """
  Serialize a DOM node to an XML string.

  @param node: DOM node to serialize
  @type node: C{xml.dom.Node}
  @return: XML string representation
  @rtype: C{str}
  """
  xml = ''
  if node.nodeType == node.ELEMENT_NODE:
    xml += '<' + node.nodeName
    for attribute in node.attributes:
      xml += ' ' + attribute + '="' + node.attributes[attribute].value + '"'
    xml += '>'
    for childNode in node.childNodes:
      xml += serialize(childNode)
    xml += '</' + node.nodeName
    xml += '>'
  return xml


def getText(nodelist, encoding='utf-8'):
  """
  Extract text content from a list of DOM nodes.

  @param nodelist: DOM node or list of DOM nodes
  @param encoding: Character encoding (unused, kept for compatibility)
  @type encoding: C{str}
  @return: Concatenated text content
  @rtype: C{str}
  """
  rc = []
  if not isinstance(nodelist, list):
    nodelist = [nodelist]
  for node in nodelist:
    for childNode in node.childNodes:
      if childNode.nodeType == childNode.TEXT_NODE:
        rc.append(childNode.data)
  return ''.join(rc)


def parseString(s):
  """
  Parse an XML string into a DOM document.

  @param s: XML string to parse
  @type s: C{str}
  @return: Parsed DOM document
  @rtype: C{xml.dom.minidom.Document}
  """
  return xml.dom.minidom.parseString(s)


def getXmlType(v):
  """
  Return an XML type attribute string for a Python value.

  @param v: Python value to determine XML type for
  @return: XML type attribute (e.g. ' type="int"') or empty string
  @rtype: C{str}
  """
  t = ''
  if isinstance(v, float):
    t = ' type="float"'
  elif isinstance(v, int):
    t = ' type="int"'
  elif isinstance(v, dict):
    t = ' type="dictionary"'
  elif isinstance(v, list):
    t = ' type="list"'
  elif isinstance(v, tuple) or isinstance(v, time.struct_time) or isinstance(v, DateTime):
    t = ' type="datetime"'
  elif isinstance(v, _blobfields.MyImage):
    t = ' type="image"'
  elif isinstance(v, _blobfields.MyFile):
    t = ' type="file"'
  return t


def getXmlTypeSaveValue(v, attrs):
  """
  Convert a string value to the appropriate Python type based on XML attrs.

  @param v: Value to convert (typically a string from XML parsing)
  @type v: C{str}
  @param attrs: Dictionary of XML attributes, expects 'type' key
  @type attrs: C{dict}
  @return: Converted value (int, float, datetime, or stripped string)
  """
  # Strip.
  if isinstance(v, str):
    while len(v) > 0 and v[0] <= ' ' and v[0] != '\t':
      v = v[1:]
    while len(v) > 0 and v[-1] <= ' ' and v[-1] != '\t':
      v = v[:-1]
  # Type.
  t = attrs.get('type', '?')
  if t == 'float':
    v = float(v)
  elif t == 'int':
    if v == 'False':
      v = 0
    elif v == 'True':
      v = 1
    else:
      v = int(v)
  elif t == 'datetime':
    new = standard.parseLangFmtDate(v)
    if new is not None:
      v = new
  # Return value.
  return v


def xmlParse(xml):
  """
  Parse arbitrary XML-Structure into dictionary.

  @param xml: xml data
  @type xml: C{str} or C{StringIO}
  @return: Dictionary of XML-Structure.
  @rtype: C{dict}
  """
  builder = XmlBuilder()
  if isinstance(xml, str):
    xml = StringIO(xml)
  v = builder.parse(xml)
  return v


# ------------------------------------------------------------------------------
#  XML-Encoding Functions
# ------------------------------------------------------------------------------

def xml_header(encoding='utf-8'):
  """
  Return an XML declaration header.

  @param encoding: Character encoding for the header
  @type encoding: C{str}
  @return: XML declaration string
  @rtype: C{str}
  """
  return '<?xml version="1.0" encoding="%s"?>\n' % encoding


# ------------------------------------------------------------------------------
#  Import Functions
# ------------------------------------------------------------------------------

def xmlInitObjProperty(self, key, value, lang=None):
  """
  Initialize a ZMS object property with a value during XML import.

  Handles type conversion for date, integer, float, and string fields.

  @param self: ZMS object being imported
  @param key: Property key/attribute name
  @type key: C{str}
  @param value: Property value to set
  @param lang: Language identifier (optional)
  @type lang: C{str} or C{None}
  """

  # -- DEFINITION
  obj_attr = self.getObjAttr(key)

  # -- ATTR
  attr = self.getObjAttrName(obj_attr, lang)

  # -- DATATYPE
  datatype = obj_attr['datatype_key']

  if value is not None:
    if isinstance(value, str):
      value = value.strip()
    # -- Date-Fields
    if datatype in _globals.DT_DATETIMES:
      if isinstance(value, str) and len(value) > 0:
        value = standard.parseLangFmtDate(value)
    # -- Integer-Fields
    elif datatype in _globals.DT_INTS:
      if isinstance(value, str) and len(value) > 0:
        value = int(value)
    # -- Float-Fields
    elif datatype == _globals.DT_FLOAT:
      if isinstance(value, str) and len(value) > 0:
        value = float(value)
    # -- String-Fields
    elif datatype in _globals.DT_STRINGS:
      value = value

  # -- INIT
  for ob in self.objectValues(['ZMSAttributeContainer']):
    setattr(ob, attr, value)


def xmlOnCharacterData(self, sData, bInCData):
    """
    Handle character data during XML import parsing.

    Appends character data to the current tag on the tag stack.

    @param self: ZMS object being imported
    @param sData: Character data string
    @type sData: C{str}
    @param bInCData: Whether data is inside a CDATA section
    @type bInCData: C{bool}
    @return: 1 to accept any character data
    @rtype: C{int}
    """
    # -- TAG-STACK
    if len(self.dTagStack) > 0:
      tag = self.dTagStack.pop()
      tag['cdata'] += sData
      self.dTagStack.append(tag)

    # -- Return
    return 1  # accept any character data


def xmlOnUnknownStartTag(self, sTagName, dTagAttrs):
    """
    Handle unknown start tags during ZMS XML import.

    Manages the tag stack and value stack for nested XML elements
    including dictionaries, lists, data blobs, and language variants.

    @param self: ZMS object being imported
    @param sTagName: XML element name
    @type sTagName: C{str}
    @param dTagAttrs: Dictionary of element attributes
    @type dTagAttrs: C{dict}
    @return: 1 to accept any unknown tag
    @rtype: C{int}
    """
    # -- TAG-STACK
    tag = {}
    tag['name'] = sTagName
    tag['attrs'] = dTagAttrs
    tag['cdata'] = ''
    tag['dValueStack'] = len(self.dValueStack)
    self.dTagStack.append(tag)

    # -- VALUE-STACK

    # ITEM (DICTIONARY|LIST)
    if sTagName in ['dict', 'dictionary']:
      self.dValueStack.append({})
    elif sTagName == 'list':
      self.dValueStack.append([])
    elif sTagName == 'item':
      pass

    # DATA (IMAGE|FILE)
    elif sTagName == 'data':
      pass

    # LANGUAGE
    elif sTagName == 'lang':
      if len(self.dValueStack) == 0:
        self.dValueStack.append({})

    # PASS OBJECT-ATTRIBUTES
    elif sTagName in self.getObjAttrs():
      pass

    # SKIP OTHERS
    else:
      tag['skip'] = True

    # -- Return
    return 1  # accept any unknown tag


def xmlOnUnknownEndTag(self, sTagName):
    """
    Handle unknown end tags during ZMS XML import.

    Processes the completed element by popping it from the tag stack
    and handling its data according to element type (dict/list items,
    data blobs, language variants, conf-properties, or object attributes).

    @param self: ZMS object being imported
    @param sTagName: XML element name
    @type sTagName: C{str}
    @return: 1 to accept matching end tag, 0 on mismatch
    @rtype: C{int}
    """
    # -- TAG-STACK
    tag = self.dTagStack.pop()
    skip = len([x for x in self.oCurrNode.dTagStack if x.get('skip')]) > 0
    name = standard.unencode(tag['name'])
    if name != sTagName: return 0  # don't accept any unknown tag
    attrs = standard.unencode(tag['attrs'])
    cdata = standard.unencode(tag['cdata'])

    # -- ITEM (DICTIONARY|LIST) --
    #----------------------------
    if sTagName in ['dict', 'dictionary']:
      pass
    elif sTagName == 'list':
      pass
    elif sTagName == 'item':
      item = cdata
      if tag['dValueStack'] < len(self.dValueStack):
        item = self.dValueStack.pop()
      else:
        item = cdata
      item = getXmlTypeSaveValue(item, attrs)
      value = self.dValueStack.pop()
      if isinstance(value, dict):
        key = attrs.get('key')
        value[key] = item
      if isinstance(value, list):
        value.append(item)
      self.dValueStack.append(value)

    # -- DATA (IMAGE|FILE) --
    #-----------------------
    elif sTagName == 'data':
      value = attrs
      if cdata is not None and len(cdata) > 0:
        filename = attrs.get('filename')
        content_type = attrs.get('content_type')
        try:
          import binascii
          data = binascii.unhexlify(cdata)
        except:
          data = bytes(cdata,'utf-8')
        value['data'] = data
      self.dValueStack.append(value)

    # -- LANGUAGE --
    #--------------
    elif sTagName == 'lang':
      lang = attrs.get('id', self.getPrimaryLanguage())
      if len(self.dValueStack) == 1:
        item = cdata
      else:
        item = self.dValueStack.pop()
      values = self.dValueStack.pop()
      try:
        values[lang] = item
      except:
        # empty values
        standard.writeBlock(self, "[values]: WARNING Importing xml may not match to ZMS client's content model - Skip lang %s for %s" %(lang, str(values)))
        values = {}
        values[lang] = item
      self.dValueStack.append(values)

    # -- COMF-PROPERTY --
    #--------------------
    elif sTagName.startswith('conf:'):
      key = sTagName[len('conf:'):]
      self.setConfProperty(key,cdata)
      self.dValueStack.clear()

    # -- OBJECT-ATTRIBUTES --
    #-----------------------
    elif sTagName in self.getObjAttrs():
      if not skip:
        obj_attr = self.getObjAttr(sTagName)

        # -- DATATYPE
        datatype = obj_attr['datatype_key']

        # -- Multi-Language Attributes.
        if obj_attr['multilang']:
          item = None
          if len(self.dValueStack) > 0:
            item = self.dValueStack.pop()
          if item is not None:
            if not isinstance(item, dict):
              item = {self.getPrimaryLanguage():item}
            for s_lang in item:
              value = item[s_lang]
              # Data
              if datatype in _globals.DT_BLOBS:
                if isinstance(value, dict) and len(value.keys()) > 0:
                  ob = _blobfields.createBlobField(self, datatype)
                  for key in value:
                    setattr(ob, key, value[key])
                  xmlInitObjProperty(self, sTagName, ob, s_lang)
              # Others
              else:
                # -- Init Properties.
                xmlInitObjProperty(self, sTagName, value, s_lang)

        else:
          # -- Complex Attributes (Blob|Dictionary|List).
          value = None
          if len(self.dValueStack) > 0:
            value = self.dValueStack.pop()
          if value is not None and \
             (datatype in _globals.DT_BLOBS or \
               datatype == _globals.DT_LIST or \
               datatype == _globals.DT_DICT):
            # Data
            if datatype in _globals.DT_BLOBS:
              if isinstance(value, dict) and len(value.keys()) > 0:
                ob = _blobfields.createBlobField(self, datatype)
                for key in value:
                  setattr(ob, key, value[key])
                xmlInitObjProperty(self, sTagName, ob)
            # Others
            else: 
              if self.getType() == 'ZMSRecordSet':
                if isinstance(value, list):
                  for item in value:
                    if isinstance(item, dict):
                      for key in item:
                        item_obj_attr = self.getObjAttr(key)
                        item_datatype = item_obj_attr['datatype_key']
                        if item_datatype in _globals.DT_BLOBS:
                          item_data = item[ key]
                          if isinstance(item_data, dict):
                            blob = _blobfields.createBlobField(self, item_datatype, item_data)
                            blob.on_setobjattr()
                            item[ key] = blob
              # -- Convert multilingual to monolingual attributes.
              if obj_attr['multilang'] == 0 and \
                 isinstance(value, dict) and \
                 len(value.keys()) == 1 and \
                 list(value.keys())[0] == self.getPrimaryLanguage():
                value = value[self.getPrimaryLanguage()]
              xmlInitObjProperty(self, sTagName, value)
            if len(self.dValueStack) > 0:
              raise "Items on self.dValueStack=%s" % self.dValueStack

          # -- Simple Attributes (String, Integer, etc.)
          else:
            if value is not None:
              standard.writeBlock(self, "[xmlOnUnknownEndTag]: WARNING - Skip %s" % sTagName)
            value = cdata
            # -- OPTIONS
            if 'options' in obj_attr:
              options = obj_attr['options']
              if isinstance(options, list):
                try:
                  i = options.index(int(value))
                  if i % 2 == 1: value = options[i - 1]
                except:
                  try:
                    i = options.index(value)
                    if i % 2 == 1: value = options[i - 1]
                  except:
                    pass
            xmlInitObjProperty(self, sTagName, value)

        # Clear value stack.
        self.dValueStack.clear()

    # -- OTHERS --
    #------------                            
    else:
      value = None
      if len(self.dTagStack): value = self.dTagStack.pop()
      if value is None: value = {'cdata':''}
      cdata = value.get('cdata', '')
      cdata += '<' + tag['name']
      for attr_name in attrs:
        attr_value = attrs.get(attr_name)
        cdata += ' ' + attr_name + '="' + attr_value + '"'
      cdata += '>' + tag['cdata']
      cdata += '</' + tag['name'] + '>'
      value['cdata'] = cdata
      self.dTagStack.append(value)

    return 1  # accept matching end tag


# ------------------------------------------------------------------------------
#  Export Functions
# ------------------------------------------------------------------------------

def toCdata(self, s, xhtml=False):
  """
  Wrap a string value in a CDATA section for safe XML embedding.

  Returns the string as-is if it contains no special characters,
  otherwise wraps it in C{<![CDATA[...]]>}.

  @param self: ZMS context object
  @param s: String value to wrap
  @type s: C{str} or C{bytes}
  @param xhtml: Whether output is XHTML (unused)
  @type xhtml: C{bool}
  @return: CDATA-wrapped string or original string
  @rtype: C{str}
  """
  rtn = ''

  # Return Text.
  if isinstance(s, str) and s.find(' ') < 0 and s.find('<') < 0 and s.find('&') < 0:
    rtn = s

  # Return Text in CDATA.
  elif s is not None:
    try:
      if isinstance(s, bytes):
        s = s.decode('utf-8')
      # Hack for invalid characters
      s = s.replace(chr(30), '')
      # Hack for nested CDATA
      s = re.compile(r'\<\!\[CDATA\[(.*?)\]\]\>').sub(r'<!{CDATA{\1}}>', s)
    except:
      standard.writeBlock(self, "[toCdata]: WARNING - Cannot create file/image object from binary data")
      pass
    # Wrap with CDATA
    rtn = '<![CDATA[%s]]>'%s

  # Return.
  return rtn


def toXml(self, value, indentlevel=0, xhtml=False, encoding='utf-8'):
  """
  Convert a Python value to its XML string representation.

  Handles images, files, dictionaries, lists, datetime tuples,
  numbers, and string values.

  @param self: ZMS context object
  @param value: Python value to convert
  @param indentlevel: Current XML indentation level
  @type indentlevel: C{int}
  @param xhtml: Whether output is XHTML
  @type xhtml: C{bool}
  @param encoding: Character encoding
  @type encoding: C{str}
  @return: XML string representation
  @rtype: C{str}
  """
  xml = []
  if value is not None:

    # Image
    if isinstance(value, _blobfields.MyImage):
      xml.append('\n' + indentlevel * INDENTSTR + value.toXml(self))

    # File
    elif isinstance(value, _blobfields.MyFile):
      xml.append('\n' + indentlevel * INDENTSTR + value.toXml(self))

    # File (Zope-native)
    elif isinstance(value, File):
      tagname = 'data'
      content_type = value.content_type
      xml.append('\n' + indentlevel * INDENTSTR)
      xml.append('<%s' % tagname)
      xml.append(' content_type="%s"' % content_type)
      xml.append(' filename="%s"' % value.title)
      xml.append(' type="file"')
      xml.append('>')
      data = zopeutil.readData(value)
      cdata = None
      if [x for x in ['text/','application/css','application/javascript','image/svg'] if content_type.startswith(x)]:
        try:
          # Ensure CDATA is valid.
          s = '<![CDATA[%s]]>'%data.decode('utf-8')
          p = pyexpat.ParserCreate()
          rv = p.Parse('<?xml version="1.0" encoding="utf-8"?><%s>%s</%s>'%(tagname,s,tagname), 1)
          cdata = s
        except:
          pass
      # Otherwise hexlify
      if cdata is None:
        cdata = _blobfields.bytes_hex(data)
      xml.append(cdata)
      xml.append('</%s>' % tagname)

    # Dictionaries
    elif isinstance(value, dict):
      keys = sorted(value)
      xml.append('\n' + indentlevel * INDENTSTR)
      xml.append('<dictionary>')
      indentstr = '\n' + (indentlevel + 1) * INDENTSTR
      for x in keys:
        k = ' key="%s"' % x
        xv = value[x]
        tv = getXmlType(xv)
        sv = toXml(self, xv, indentlevel + 2, xhtml, encoding)
        xml.append(indentstr)
        xml.append('<item%s%s>' % (k, tv))
        xml.append(sv)
        if sv.find('\n') >= 0:
          xml.append(indentstr)
        xml.append('</item>')
      xml.append('\n' + indentlevel * INDENTSTR)
      xml.append('</dictionary>')

    # Lists
    elif isinstance(value, list):
      xml.append('\n' + indentlevel * INDENTSTR)
      xml.append('<list>')
      indentstr = '\n' + (indentlevel + 1) * INDENTSTR
      for xv in value:
        k = ''
        tv = getXmlType(xv)
        sv = toXml(self, xv, indentlevel + 2, xhtml, encoding)
        xml.append(indentstr)
        xml.append('<item%s%s>' % (k, tv))
        xml.append(sv)
        if sv.startswith('\n'):
          xml.append(indentstr)
        xml.append('</item>')
      xml.append('\n' + indentlevel * INDENTSTR)
      xml.append('</list>')

    # Tuples (DateTime)
    elif isinstance(value, tuple) or isinstance(value, time.struct_time) or isinstance(value, DateTime):
      try:
        s_value = self.getLangFmtDate(value, fmt_str='ISO8601')
        if len(s_value) > 0:
          xml.append('\n' + indentlevel * INDENTSTR)
          xml.append(toCdata(self, s_value, -1))
      except:
        pass

    # Numbers
    elif isinstance(value, int) or isinstance(value, float):
      xml.append(value)

    else:
      # Zope-Objects
      try: meta_type = value.meta_type
      except: meta_type = None
      if meta_type is not None:
        value = zopeutil.readData(value)
      if value:
        xml.append(toCdata(self, value, xhtml))

  # Return xml.
  return ''.join([str(x) for x in xml])


def getAttrToXml(self, base_path, data2hex, obj_attr, REQUEST):
  """
  Convert a single ZMS object attribute to its XML representation.

  @param self: ZMS object
  @param base_path: Base path for resolving blob references
  @type base_path: C{str}
  @param data2hex: Whether to hex-encode binary data
  @type data2hex: C{bool}
  @param obj_attr: Object attribute definition dict
  @type obj_attr: C{dict}
  @param REQUEST: Zope request object
  @return: XML string for the attribute value
  @rtype: C{str}
  """
  xml = ''

  # -- DATATYPE
  datatype = obj_attr['datatype_key']

  # -- VALUE
  obj_vers = self.getObjVersion(REQUEST)
  value = self._getObjAttrValue(obj_attr, obj_vers, REQUEST.get('lang', self.getPrimaryLanguage()))

  if value is not None:

    # Retrieve value from options.
    if 'options' in obj_attr:
      options = obj_attr['options']
      try:
        i = options.index(int(value))
        if i % 2 == 0: value = options[i + 1]
      except:
        try:
          i = options.index(str(value))
          if i % 2 == 0: value = options[i + 1]
        except:
          pass

    #-- Blob-Fields
    if datatype in _globals.DT_BLOBS:
      xml += value.toXml(self, base_path, data2hex)

    #-- Text-Fields
    elif datatype in _globals.DT_TEXTS:
      value = self.validateInlineLinkObj(value)
      xml += toXml(self, value)
      
    #-- Url-Fields
    elif datatype == _globals.DT_URL:
      value = self.validateLinkObj(value)
      xml += toXml(self, value)
    
    # XML.
    elif datatype == _globals.DT_XML or \
         datatype == _globals.DT_BOOLEAN or \
         datatype in _globals.DT_NUMBERS:
      xml += toXml(self, value, -1)

    # Others.
    else:
      xml += toXml(self, value)

  # Return xml.
  return xml


def getObjPropertyToXml(self, REQUEST, base_path='', data2hex=False, obj_attr={}, multilang=True):
  """
  Convert a ZMS object property to XML, handling multilingual attributes.

  @param self: ZMS object
  @param REQUEST: Zope request object
  @param base_path: Base path for resolving references
  @type base_path: C{str}
  @param data2hex: Whether to hex-encode binary data
  @type data2hex: C{bool}
  @param obj_attr: Object attribute definition dict
  @type obj_attr: C{dict}
  @param multilang: Whether to export all language variants
  @type multilang: C{bool}
  @return: XML string for the property
  @rtype: C{str}
  """
  xml = ''
  # Multi-Language Attributes.
  indentlevel = len(base_path.split('/'))
  if obj_attr['multilang'] and multilang==True:
    lang = REQUEST.get('lang')
    langIds = self.getLangIds()
    for langId in langIds:
      REQUEST.set('lang', langId)
      s_attr_xml = getAttrToXml(self, base_path, data2hex, obj_attr, REQUEST)
      if len(s_attr_xml) > 0:
        xml += '<lang%s>%s</lang>' % ( [ '' , ' id="%s"'%langId ][ int(len(langIds)>1) ] , s_attr_xml )
    REQUEST.set('lang', lang)
  # Simple Attributes.
  else:
    xml += getAttrToXml(self, base_path, data2hex, obj_attr, REQUEST)
  # Return xml.
  return xml


def getObjToXml(self, REQUEST, deep=True, base_path='', data2hex=False, multilang=True):
  """
  Export a ZMS object and optionally its children to XML.

  @param self: ZMS object to export
  @param REQUEST: Zope request object
  @param deep: Whether to recursively export child nodes
  @type deep: C{bool}
  @param base_path: Base path for resolving references
  @type base_path: C{str}
  @param data2hex: Whether to hex-encode binary data
  @type data2hex: C{bool}
  @param multilang: Whether to export all language variants
  @type multilang: C{bool}
  @return: XML string for the object tree
  @rtype: C{str}
  """
  # Check Constraints.
  root = getattr(self, '__root__', None)
  if root is not None:
    return ''
  xml = []
  # Start tag.
  indentlevel = len(base_path.split('/'))
  xml.append('%s<%s' % ( indentlevel * INDENTSTR, self.meta_id ) )
  xml.append(' uid="%s"' % self.get_uid() )
  id = self.id 
  prefix = standard.id_prefix(id)
  if id == prefix:
    xml.append(' id_fix="%s"' % id)
  else:
    xml.append(' id="%s"' % id)
    xml.append(' id_prefix="%s"' % standard.id_prefix(id))
  xml.append('>\n')
  # [Issue-219] Special content-like conf-properties edited in interfaces (ZMS.interface_permalinks).
  if self.meta_id == 'ZMS':
    attr_ids = [re.sub(r'^interface_(.*?)(s)','\\1',x) for x in self.getMetaobjAttrIds(self.meta_id,types=['interface'])]
    d = self.get_conf_properties()
    for k in d:
      if [x for x in attr_ids if k.startswith('%s.%s'%(self.meta_id,x))]:
        xml.append('%s<conf:%s>%s</conf:%s>\n'%(((indentlevel+1)*INDENTSTR),k,d[k],k))
  # Attributes.
  keys = self.getObjAttrs().keys()
  if self.getType() == 'ZMSRecordSet':
    keys = ['active', self.getMetaobjAttrIds(self.meta_id,types=['list'])[0]]
  for key in keys:
    obj_attr = self.getObjAttr(key)
    if obj_attr['xml'] or key in ['change_dt','change_uid','created_dt','created_uid']:
      ob_prop = getObjPropertyToXml(self, REQUEST, base_path, data2hex, obj_attr, multilang)
      if len(ob_prop) > 0:
        xml.append('%s<%s>%s</%s>\n' % ( (indentlevel+1) * INDENTSTR, key, ob_prop, key ) )
  # Process children.
  if deep:
    xml.extend([getObjToXml(x, REQUEST, deep, base_path + x.id + '/', data2hex, multilang) for x in self.getChildNodes()])
  # End tag.
  xml.append('%s</%s>\n' % ( indentlevel * INDENTSTR, self.meta_id ) )
  # Return xml.
  return ''.join(xml)


################################################################################
# CLASS ParseError(Exception):
################################################################################

class ParseError(Exception):
    """Exception class to indicate XML parsing errors."""
    pass



################################################################################
# CLASS XmlAttrBuilder:
################################################################################

class XmlAttrBuilder(object):
    """
    XML parser for complex Python attributes (dictionaries, lists, blobs).

    Parses XML documents into Python data structures using expat.
    Used internally by ZMS for importing attribute values.
    """

    # Class variables
    iBufferSize = 1028 * 32  # buffer size for XML file parsing

    def __init__(self):
      """Constructor."""
      pass


    def parse(self, input):
      """
      Parse a given XML document into Python data structures.

      @param input: XML document as string or file object
      @type input: C{bytes} or file-like
      @return: Parsed value (dict, list, or blob), or None if nothing was parsed
      @raise ParseError: If the XML document contains syntax errors
      """

      # prepare builder
      self.dValueStack = collections.deque()
      self.dTagStack = collections.deque()

      # create parser object
      p = pyexpat.ParserCreate()

      # connect parser object with handler methods
      p.StartElementHandler = self.OnStartElement
      p.EndElementHandler = self.OnEndElement
      p.CharacterDataHandler = self.OnCharacterData
      p.StartCdataSectionHandler = self.OnStartCData
      p.EndCdataSectionHandler = self.OnEndCData
      p.ProcessingInstructionHandler = self.OnProcessingInstruction
      p.CommentHandler = self.OnComment
      p.StartNamespaceDeclHandler = self.OnStartNamespaceDecl
      p.EndNamespaceDeclHandler = self.OnEndNamespaceDecl

      #### parsing ####
      if isinstance(input,bytes):
        # input is a string!
        rv = p.Parse(input, 1)
      else:
        # input is a file object!
        while True:

          v = input.read(self.iBufferSize)
          if len(v) == 0:
            rv = 1
            break

          rv = p.Parse(v, 0)
          if not rv:
            break

      # raise parser exception
      if not rv:
        raise ParseError('%s at line %s' % (pyexpat.ErrorString(p.ErrorCode), p.ErrorLineNumber))

      return self.dValueStack.pop()


    def OnStartElement(self, sTagName, dTagAttrs):
      """
      Handle the start of an XML element.

      Called by the expat parser on occurrence of an XML start tag.
      Pushes a new tag onto the tag stack and, for container elements
      (C{data}, C{dictionary}, C{list}), pushes an initial value
      onto the value stack.

      @param sTagName: Element (tag) name
      @type sTagName: C{str}
      @param dTagAttrs: Dictionary of element attributes
      @type dTagAttrs: C{dict}
      """

      # -- TAG-STACK
      tag = {'name':sTagName, 'attrs':dTagAttrs, 'cdata':''}
      tag['dValueStack'] = len(self.dValueStack)
      self.dTagStack.append(tag)

      # -- VALUE-STACK
      if sTagName == 'data':
        self.dValueStack.append(None)
      elif sTagName == 'dictionary':
        self.dValueStack.append({})
      elif sTagName == 'list':
        self.dValueStack.append([])


    def OnEndElement(self, sTagName):
      """
      Handle the end of an XML element.

      Pops the current tag from the stack, processes its content
      depending on element type (C{data} or C{item}), and updates
      the value stack accordingly.

      @param sTagName: Element (tag) name
      @type sTagName: C{str}
      @raise ParseError: If end tag does not match the expected start tag
      """

      # -- TAG-STACK
      tag = self.dTagStack.pop()
      name = standard.unencode(tag['name'])
      attrs = standard.unencode(tag['attrs'])
      cdata = standard.unencode(tag['cdata'])
      # Hack for nested CDATA
      cdata = re.compile(r'\<\!\{CDATA\{(.*?)\}\}\>').sub(r'<![CDATA[\1]]>',cdata)

      if name != sTagName:
        raise ParseError("Unmatching end tag (" + str(sTagName) + ") expected (" + str(name) + ")")

      # -- DATA
      if sTagName in ['data']:
        filename = attrs.get('filename')
        content_type = attrs.get('content_type')
        try:
          import binascii
          data = binascii.unhexlify(cdata)
        except:
          data = bytes(cdata,'utf-8')
        file = {'data':data, 'filename':filename, 'content_type':content_type}
        objtype = attrs.get('type')
        item = _blobfields.createBlobField(None, objtype, file)
        for key in attrs:
          value = attrs.get(key)
          setattr(item, key, value)
        self.dValueStack.pop()
        self.dValueStack.append(item)

      # -- ITEM
      elif sTagName in ['item']:
        if tag['dValueStack'] < len(self.dValueStack):
          item = self.dValueStack.pop()
        else:
          item = cdata
        item = getXmlTypeSaveValue(item, attrs)
        value = self.dValueStack.pop()
        if isinstance(value, dict):
          key = attrs.get('key')
          value[key] = item
        if isinstance(value, list):
          value.append(item)
        self.dValueStack.append(value)


    def OnCharacterData(self, sData):
      """
      Handle character data from the XML parser.

      Appends character data to the current tag's cdata buffer.

      @param sData: Character data string
      @type sData: C{str}
      """

      # -- TAG-STACK
      if len(self.dTagStack) > 0:
        tag = self.dTagStack.pop()
        tag['cdata'] += sData
        self.dTagStack.append(tag)


    def OnStartCData(self):
      """Handle start of a CDATA section."""
      self.bInCData = 1


    def OnEndCData(self):
      """Handle end of a CDATA section."""
      self.bInCData = 0


    def OnProcessingInstruction(self, target, data):
      """
      Handle a processing instruction (ignored).

      @param target: Processing instruction target
      @type target: C{str}
      @param data: Processing instruction data
      @type data: C{str}
      """
      pass  # ignored


    def OnComment(self, data):
      """
      Handle an XML comment (ignored).

      @param data: Comment string
      @type data: C{str}
      """
      pass  # ignored


    def OnStartNamespaceDecl(self, prefix, uri):
      """
      Handle start of a namespace declaration (ignored).

      @param prefix: Namespace prefix
      @type prefix: C{str}
      @param uri: Namespace URI
      @type uri: C{str}
      """
      pass  # ignored


    def OnEndNamespaceDecl(self, prefix):
      """
      Handle end of a namespace declaration (ignored).

      @param prefix: Namespace prefix
      @type prefix: C{str}
      """
      pass  # ignored


def xmlNodeSet(mNode, sTagName='', iDeep=0):
  """
  Retrieve node-set for given tag-name from dictionary of XML-Node-Structure.
  @return: List of dictionaries of XML-Structure.
  @rtype: C{list}
  """
  lNodeSet = []
  lNode = mNode
  if isinstance(mNode, list) and len(mNode) == 2:
    lNode = mNode[1]
  lTags = lNode.get('tags', [])
  for i in range(0, len(lTags) // 2):
    lTagName = lTags[i * 2]
    lNode = lTags[i * 2 + 1]
    if sTagName in [lTagName, '']:
      lNodeSet.append(lNode)
    if iDeep == 1:
      lNodeSet.extend(xmlNodeSet(lNode, sTagName, iDeep))
  return lNodeSet



################################################################################
# CLASS XmlBuilder:
################################################################################

class XmlBuilder(object):
    """
    XML parser for custom XML structures.

    Parses arbitrary XML into a nested dictionary/list structure
    with tag names, attributes, cdata, and child tags.
    """

    ######## class variables ########
    iBufferSize = 1028 * 32  # buffer size for XML file parsing

    def __init__(self):
      """Constructor."""
      pass


    def parse(self, input):
        """
        Parse a given XML document into a nested tag structure.

        @param input: XML document as string or file object
        @type input: C{bytes} or file-like
        @return: List of parsed tags
        @rtype: C{list}
        @raise ParseError: If the XML document contains syntax errors
        """

        # prepare builder
        self.dTagStack = collections.deque()
        self.dTagStack.append({'tags':[]})

        # create parser object
        p = pyexpat.ParserCreate()

        # connect parser object with handler methods
        p.StartElementHandler = self.OnStartElement
        p.EndElementHandler = self.OnEndElement
        p.CharacterDataHandler = self.OnCharacterData
        p.StartCdataSectionHandler = self.OnStartCData
        p.EndCdataSectionHandler = self.OnEndCData
        p.ProcessingInstructionHandler = self.OnProcessingInstruction
        p.CommentHandler = self.OnComment
        p.StartNamespaceDeclHandler = self.OnStartNamespaceDecl
        p.EndNamespaceDeclHandler = self.OnEndNamespaceDecl

        #### parsing ####
        if isinstance(input, bytes):
          # input is a string!
          rv = p.Parse(input, 1)
        else:
          # input is a file object!
          while True:

            v = input.read(self.iBufferSize)
            if len(v) == 0:
              rv = 1
              break

            rv = p.Parse(v, 0)
            if not rv:
              break

        # raise parser exception
        if not rv:
          raise ParseError('%s at line %s' % (pyexpat.ErrorString(p.ErrorCode), p.ErrorLineNumber))

        return self.dTagStack.pop()['tags']


    def OnStartElement(self, sTagName, dTagAttrs):
      """
      Handle the start of an XML element.

      Pushes a new tag dictionary onto the tag stack.

      @param sTagName: Element (tag) name
      @type sTagName: C{str}
      @param dTagAttrs: Dictionary of element attributes
      @type dTagAttrs: C{dict}
      """
      tag = {'name':sTagName, 'attrs':dTagAttrs, 'cdata':'', 'tags':[]}
      self.dTagStack.append(tag)


    def OnEndElement(self, sTagName):
      """
      Handle the end of an XML element.

      Pops the current tag, assembles it into a structured dict,
      and appends it to the parent tag's children.

      @param sTagName: Element (tag) name
      @type sTagName: C{str}
      @raise ParseError: If end tag does not match the expected start tag
      """
      
      lTag = self.dTagStack.pop()
      name = standard.unencode(lTag['name'])
      attrs = standard.unencode(lTag['attrs'])
      lCdata = standard.unencode(lTag['cdata'])
      lTags = standard.unencode(lTag['tags'])

      if name != sTagName:
        raise ParseError("Unmatching end tag (" + sTagName + ")")

      lTag = {}
      lTag['level'] = len(self.dTagStack)
      lTag['name'] = name
      lTag['attrs'] = attrs
      lCdata = lCdata.strip()
      if len(lCdata) > 0:
        lTag['cdata'] = lCdata
      if len(lTags) > 0:
        lTag['tags'] = lTags
      parent = self.dTagStack.pop()
      parent['tags'].append(name)
      parent['tags'].append(lTag)
      self.dTagStack.append(parent)


    def OnCharacterData(self, sData):
      """
      Handle character data from the XML parser.

      Appends character data to the current tag's cdata buffer.

      @param sData: Character data string
      @type sData: C{str}
      """
      tag = self.dTagStack.pop()
      tag['cdata'] = tag['cdata'] + sData
      self.dTagStack.append(tag)


    def OnStartCData(self):
      """Handle start of a CDATA section."""
      self.bInCData = 1


    def OnEndCData(self):
      """Handle end of a CDATA section."""
      self.bInCData = 0


    def OnProcessingInstruction(self, target, data):
      """
      Handle a processing instruction (ignored).

      @param target: Processing instruction target
      @type target: C{str}
      @param data: Processing instruction data
      @type data: C{str}
      """
      pass  # ignored


    def OnComment(self, data):
      """
      Handle an XML comment (ignored).

      @param data: Comment string
      @type data: C{str}
      """
      pass  # ignored


    def OnStartNamespaceDecl(self, prefix, uri):
      """
      Handle start of a namespace declaration (ignored).

      @param prefix: Namespace prefix
      @type prefix: C{str}
      @param uri: Namespace URI
      @type uri: C{str}
      """
      pass  # ignored


    def OnEndNamespaceDecl(self, prefix):
      """
      Handle end of a namespace declaration (ignored).

      @param prefix: Namespace prefix
      @type prefix: C{str}
      """
      pass  # ignored

