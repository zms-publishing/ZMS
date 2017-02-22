#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# standard.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

"""ZMS standard utility module

This module provides helpful functions and classes for use in Python
Scripts.  It can be accessed from Python with the statement
"import Products.zms.standard"
"""

# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
from App.Common import package_home
from App.config import getConfiguration
from DateTime.DateTime import DateTime
from OFS.CopySupport import absattr
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from cStringIO import StringIO
from types import StringTypes
from traceback import format_exception
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import base64
import cgi
import copy
import fnmatch
import logging
import operator
import os
import re
import sys
import time
import urllib
import zExceptions
# Product Imports.
import _blobfields
import _globals
import _fileutil
import _filtermanager
import _mimetypes
import _xmllib

security = ModuleSecurityInfo('Products.zms.standard')

"""
@group PIL (Python Imaging Library): pil_img_*
@group Local File-System: localfs_*
@group Logging: writeBlock, writeLog
@group Mappings: *_list
@group Operators: operator_*
@group Styles / CSS: parse_stylesheet, get_colormap
@group Regular Expressions: re_*
@group: XML: getXmlHeader, toXmlString, parseXmlString, xslProcess, processData, xmlParse, xmlNodeSet
"""

security.declarePublic('getPRODUCT_HOME')
def getPRODUCT_HOME():
  """
  Returns home-folder of this Product.
  @rtype: C{str}
  """
  PRODUCT_HOME = os.path.dirname(os.path.abspath(__file__))
  return PRODUCT_HOME


security.declarePublic('getPACKAGE_HOME')
def getPACKAGE_HOME():
  """
  Returns path to lib/site-packages.
  @rtype: C{str}
  """
  from distutils.sysconfig import get_python_lib
  return get_python_lib()


security.declarePublic('getINSTANCE_HOME')
def getINSTANCE_HOME():
  """
  Returns path to Instance
  @rtype: C{str}
  """
  return getConfiguration().instancehome


security.declarePublic('FileFromData')
def FileFromData( context, data, filename='', content_type=None):
  """
  Creates a new instance of a file from given data.
  @param data: File-data (binary)
  @type data: C{string}
  @param filename: Filename
  @type filename: C{string}
  @return: New instance of file.
  @rtype: L{MyFile}
  """
  file = {}
  file['data'] = data
  file['filename'] = filename
  if content_type: file['content_type'] = content_type
  return _blobfields.createBlobField( context, _blobfields.MyFile, file=file)


security.declarePublic('ImageFromData')
def ImageFromData( context, data, filename='', content_type=None):
  """
  Creates a new instance of an image from given data.
  @param data: Image-data (binary)
  @type data: C{string}
  @param filename: Filename
  @type filename: C{string}
  @return: New instance of image.
  @rtype: L{MyImage}
  """
  file = {}
  file['data'] = data
  file['filename'] = filename
  if content_type: file['content_type'] = content_type
  return _blobfields.createBlobField( context, _blobfields.MyImage, file=file)


security.declarePublic('set_response_headers')
def set_response_headers(fn, mt='application/octet-stream', size=None, request=None):
  """
  Set content-type and -disposition to response-headers.
  """
  RESPONSE = request.RESPONSE
  RESPONSE.setHeader('Content-Type', mt)
  if request.get('HTTP_USER_AGENT','').find('Android') < 0:
    RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%_fileutil.extractFilename(fn))
  if size:
    RESPONSE.setHeader('Content-Length',size)
  RESPONSE.setHeader('Accept-Ranges','bytes')


security.declarePublic('umlaut_quote')
def umlaut_quote(s, mapping={}):
  """
  Replace umlauts in s using given mapping.
  @param s: String
  @type s: C{str}
  @param mapping: Mapping
  @type mapping: C{dict}
  @return: Quoted string
  @rtype: C{str}
  """
  if type(s) is not unicode:
    s = unicode(s,'utf-8')
  map( lambda x: operator.setitem( mapping, x, _globals.umlaut_map[x]), _globals.umlaut_map.keys())
  for key in mapping.keys():
    s = s.replace(key,mapping[key])
  s = s.encode('utf-8')
  return s


security.declarePublic('url_append_params')
def url_append_params(url, dict, sep='&amp;'):
  """
  Append params from dict to given url.
  @param url: Url
  @type url: C{str}
  @param dict: dictionary of params (key/value pairs)
  @type dict: C{dict}
  @return: New url
  @rtype: C{str}
  """
  anchor = ''
  i = url.rfind('#')
  if i > 0:
    anchor = url[i:]
    url = url[:i]
  targetdef = ''
  i = url.find('#')
  if i >= 0:
    targetdef = url[i:]
    url = url[:i]
  qs = '?'
  i = url.find(qs)
  if i >= 0:
    qs = sep
  for key in dict.keys():
    value = dict[key]
    if type(value) is list:
      for item in value:
        qi = key + ':list=' + urllib.quote(str(item))
        url += qs + qi
        qs = sep
    else:
      qi = key + '=' + urllib.quote(str(value))
      if url.find( '?' + qi) < 0 and url.find( '&' + qi) < 0 and url.find( '&amp;' + qi) < 0:
        url += qs + qi
      qs = sep
  url += targetdef
  return url+anchor


security.declarePublic('url_inherit_params')
def url_inherit_params(url, REQUEST, exclude=[], sep='&amp;'):
  """
  Inerits params from request to given url.
  @param url: Url
  @type url: C{str}
  @param REQUEST: the triggering request
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: New url
  @rtype: C{str}
  """
  anchor = ''
  i = url.rfind('#')
  if i > 0:
    anchor = url[i:]
    url = url[:i]
  if REQUEST.form:
    for key in REQUEST.form.keys():
      if not key in exclude:
        v = REQUEST.form.get( key, None )
        if key is not None:
          if url.find('?') < 0:
            url += '?'
          else:
            url += sep
          if type(v) is int:
            url += urllib.quote(key+':int') + '=' + urllib.quote(str(v))
          elif type(v) is float:
            url += urllib.quote(key+':float') + '=' + urllib.quote(str(v))
          elif type(v) is list:
            c = 0
            for i in v:
              if c > 0:
                url += sep
              url += urllib.quote(key+':list') + '=' + urllib.quote(str(i))
              c = c + 1
          else:
            url += key + '=' + urllib.quote(str(v))
  return url+anchor


security.declarePublic('string_maxlen')
def string_maxlen(s, maxlen=20, etc='...', encoding=None):
  """
  Returns string with specified maximum-length. If original string exceeds 
  maximum-length '...' is appended at the end.
  @param s: String
  @type s: C{str}
  @param maxlen: Maximum-length
  @type maxlen: C{int}
  @param etc: Characters to be appended if maximum-length is exceeded
  @type etc: C{str}
  @param encoding: Encoding
  @type encoding: C{str}
  @rtype: C{str}
  """
  if encoding is not None:
    s = unicode( s, encoding)
  # remove all tags.
  s = re.sub( '<!--(.*?)-->', '', s)
  s = re.sub( '<script((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</script>', '', s)
  s = re.sub( '<style((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</style>', '', s)
  s = re.sub( '<((.|\n|\r|\t)*?)>', '', s)
  if len(s) > maxlen:
    if s[:maxlen].rfind('&') >= 0 and not s[:maxlen].rfind('&') < s[:maxlen].rfind(';') and \
       s[maxlen:].find(';') >= 0 and not s[maxlen:].find(';') > s[maxlen:].find('&'):
      maxlen = maxlen + s[maxlen:].find(';')
    if s[:maxlen].endswith(chr(195)) and maxlen < len(s):
      maxlen += 1
    s = s[:maxlen] + etc
  return s


security.declarePublic('url_encode')
def url_encode(url):
  """
  All unsafe characters must always be encoded within a URL.
  @see: http://www.ietf.org/rfc/rfc1738.txt
  @param url: Url
  @type s: C{str}
  @return: Encoded string
  @rtype: C{str}
  """
  for ch in ['[',']',' ','(',')']:
    url = url.replace(ch,'%'+bin2hex(ch).upper())
  return url


security.declarePublic('guess_content_type')
def guess_content_type(filename, data):
  """
  Guess the type of a file based on its filename and the data.
  @param filename: Filename
  @type filename: C{str}
  @param data: Data
  @type data: C{str}
  @return: Tuple of MIME-type and encoding.
  @rtype: C{tuple}
  """
  import zope.contenttype
  mt, enc  = zope.contenttype.guess_content_type( filename, data)
  return mt, enc


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.html_quote:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def html_quote(v, name='(Unknown name)', md={}):
  if not type(v) in StringTypes:
    v = str(v)
  return cgi.escape(v, 1)


def bin2hex(m):
  """
  Returns a string with the hexadecimal representation of integer m.
  @param m: Binary
  @type m: C{int}
  @return: String
  @rtype: C{str}
  """
  return ''.join(map(lambda x: hex(ord(x)/16)[-1]+hex(ord(x)%16)[-1],m))


def hex2bin(m):
  """
  Converts a hexadecimal-string m to an integer.
  @param m: Hexadecimal.
  @type m: C{str}
  @return: Integer
  @rtype: C{str}
  """
  return ''.join(map(lambda x: chr(16*int('0x%s'%m[x*2],0)+int('0x%s'%m[x*2+1],0)),range(len(m)/2)))


security.declarePublic('encrypt_schemes')
def encrypt_schemes():
  """
  Available encryption-schemes.
  @return: list of encryption-scheme ids
  @rtype: C{list}
  """
  ids = []
  for id, prefix, scheme in AuthEncoding._schemes:
    ids.append( id)
  return ids


security.declarePublic('encrypt_password')
def encrypt_password(pw, algorithm='md5', hex=False):
  """
  Encrypts given password.
  @param pw: Password
  @type pw: C{str}
  @param algorithm: Encryption-algorithm (md5, sha-1, etc.)
  @type algorithm: C{str}
  @param hex: Hexlify
  @type hex: C{bool}
  @return: Encrypted password
  @rtype: C{str}
  """
  enc = None
  if algorithm.upper() == 'SHA-1':
    import sha
    enc = sha.new(pw)
    if hex:
      enc = enc.hexdigest()
    else:
      enc = enc.digest()
  else:
    for id, prefix, scheme in AuthEncoding._schemes:
      if algorithm.upper() == id:
        enc = scheme.encrypt(pw)
  return enc


security.declarePublic('encrypt_ordtype')
def encrypt_ordtype(s):
  """
  Encrypts given string with entities by random algorithm.
  @param s: String
  @type s: C{str}
  @return: Encrypted string
  @rtype: C{str}
  """
  from binascii import hexlify
  new = ''
  for ch in s:
    whichCode=rand_int(2)
    if whichCode==0:
      new += ch
    elif whichCode==1:
      new += '&#%d;'%ord(ch)
    else:
      new += '&#x%s;'%str(hexlify(ch))
  return new


security.declarePublic('rand_int')
def rand_int(n):
  """
  Random integer in given range.
  @param n: Range
  @type n: C{int}
  @return: Random integer
  @rtype: C{int}
  """
  from random import randint
  return randint(0,n)


security.declarePublic('getDataSizeStr')
def getDataSizeStr(len):
  """
  Returns display string for file-size (KB).
  @param len: length (bytes)
  @type len: C{int}
  @rtype: C{str}
  """
  return _fileutil.getDataSizeStr(len)


security.declarePublic('getMimeTypeIconSrc')
def getMimeTypeIconSrc(mt):
  """
  Returns the absolute-url of an icon representing the specified MIME-type.
  @param mt: MIME-Type (e.g. image/gif, text/xml).
  @type mt: C{str}
  @rtype: C{str}
  """
  return'/misc_/zms/%s'%_mimetypes.dctMimeType.get( mt, _mimetypes.content_unknown)


security.declarePublic('unencode')
def unencode( p, enc='utf-8'):
  """
  Unencodes given parameter.
  """
  if type( p) is dict:
    for key in p.keys():
      if type( p[ key]) is unicode:
        p[ key] = p[ key].encode( enc)
  elif type( p) is list:
    l = []
    for i in p:
      if type( i) is unicode:
        l.append( i.encode( enc))
      else:
        l.append( i)
    p = l
  elif type( p) is unicode:
    p = p.encode( enc)
  return p


security.declarePublic('id_prefix')
def id_prefix(s):
  """
  Returns prefix from identifier (which is the non-numeric part at the beginning).
  @param s: Identifier
  @type s: C{str}
  @return: Id-prefix
  @rtype: C{str}
  """
  return re.findall('^(\\D*)',s)[0]


security.declarePublic('id_quote')
def id_quote(s, mapping={
        '\x20':'_',
        '-':'_',
        '/':'_',
}):
  """
  Converts given string to identifier (removes special-characters and 
  replaces German umlauts).
  @param s: String
  @type s: C{str}
  @return: Identifier
  @rtype: C{str}
  """
  s = umlaut_quote(s, mapping)
  valid = map( lambda x: ord(x[0]), mapping.values()) + [ord('_')] + range(ord('0'),ord('9')+1) + range(ord('A'),ord('Z')+1) + range(ord('a'),ord('z')+1)
  s = filter( lambda x: ord(x) in valid, s)
  while len(s) > 0 and s[0] == '_':
      s = s[1:]
  s = s.lower()
  return s


security.declarePublic('form_quote')
def form_quote(text, REQUEST):
  """
  Remove <form>-tags for Management Interface.
  """
  rtn = text
  if isManagementInterface(REQUEST):
    rtn = re.sub( '<form(.*?)>', '<noform\\1>', rtn)
    rtn = re.sub( ' name="lang"', ' name="_lang"', rtn)
    rtn = re.sub( '</form(.*?)>', '</noform\\1>', rtn)
  return rtn


def qs_append(qs, p, v):
  """
    Append to query-string.
  """
  if len(qs) == 0:
    qs += '?'
  else:
    qs += '&amp;'
  qs += p + '=' + urllib.quote(v)
  return qs



security.declarePublic('nvl')
def nvl(a1, a2, n=None):
  """
  Returns its first argument if it is not equal to third argument (None), 
  otherwise it returns its second argument.
  @param a1: 1st argument
  @type a1: C{any}
  @param a2: 2nd argument
  @type a2: C{any}
  @rtype: C{any}
  """
  if (n is None and a1 is not None) or (type(n) is str and a1 != n) or (type(n) is list and a1 not in n):
    return a1
  else:
    return a2


def get_session(context):
  """
  Get http-session.
  """
  return getattr(context, 'session_data_manager', None) and \
    context.session_data_manager.getSessionData(create=0)


def triggerEvent(context, *args, **kwargs):
  """
  Hook for trigger of custom event (if there is one)
  """
  l = []
  name = args[0]
  
  # Always call local trigger for global triggers.
  if name.startswith('*.'):
    triggerEvent(context,name[2:]+'Local')
  
  # Pass custom event to zope ObjectModifiedEvent event.
  notify(ObjectModifiedEvent(context, name))
  
  metaObj = context.getMetaobj( context.meta_id)
  if metaObj:
    # Process meta-object-triggers.
    context = context
    v = context.evalMetaobjAttr(name,kwargs)
    writeLog( context, "[triggerEvent]: %s=%s"%(name,str(v)))
    if v is not None:
      l.append(v)
    # Process zope-triggers.
    context = context
    ids = []
    while context is not None:
      for id in context.getHome().objectIds():
        if id not in ids and id.find( name) == 0:
          v = getattr(context,id)(context=context,REQUEST=context.REQUEST)
          if v is not None:
            l.append(v)
          ids.append(id)
      context = context.getPortalMaster()
  return l


security.declarePublic('isManagementInterface')
def isManagementInterface(REQUEST):
  """
  Returns true if current context is management-interface, false else.
  @rtype: C{Bool}
  """
  return REQUEST is not None and \
         REQUEST.get('URL','').find('/manage') >= 0 and \
         isPreviewRequest(REQUEST)
     


security.declarePublic('isPreviewRequest')
def isPreviewRequest(REQUEST):
  """
  Returns true if current context is preview-request, false else.
  @rtype: C{Bool}
  """
  return REQUEST is not None and \
         REQUEST.get('preview','') == 'preview'


"""
################################################################################
#
#  Http
#
################################################################################
"""

security.declarePublic('unescape')
def unescape(s):
  """
  Unescape
  @rtype: C{str}
  """
  while True:
    i = s.find('%')
    if i < 0: break
    if s[i+1] == 'u':
      old = s[i:i+6]
      if old == '%u21B5':
        new = '&crarr;'
      else:
        new = ''
    else:
      old = s[i:i+3]
      new = chr(int('0x'+s[i+1:i+3],0))
    s = s.replace(old,new)
  return s


security.declarePublic('http_import')
def http_import(context, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
  """
  Send Http-Request and return Response-Body.
  @param url: Remote-URL
  @type url: C{str}
  @param method: Method
  @type method: C{str}, values are GET or POST
  @param auth: Authentication
  @type auth: C{str}
  @param parse_qs: Parse Query-String
  @type parse_qs: C{int}, values are 0 or 1
  @param timeout: Time-Out [s]
  @type timeout: C{int}, values in seconds
  @param headers: Request-Headers
  @type headers: C{dict}
  @return: Response-Body
  @rtype: C{str}
  """
  # Parse URL.
  import urlparse
  u = urlparse.urlparse(url)
  writeLog( context, "[http_import.%s]: %s"%(method,str(u)))
  scheme = u[0]
  netloc = u[1]
  path = u[2]
  query = u[4]
  
  # Get Proxy.
  useproxy = True
  noproxy = ['localhost','127.0.0.1']+filter(lambda x: len(x)>0,map(lambda x: x.strip(),context.getConfProperty('%s.noproxy'%scheme.upper(),'').split(',')))
  for noproxyurl in noproxy:
    if fnmatch.fnmatch(netloc,noproxyurl):
      useproxy = False
      break
  if useproxy:
    proxy = context.getConfProperty('%s.proxy'%scheme.upper(),'')
    if len(proxy) > 0:
      path = '%s://%s%s'%(scheme,netloc,path) 
      netloc = proxy

  # Open HTTP connection.
  import httplib
  writeLog( context, "[http_import.%s]: %sConnection(%s) -> %s"%(method,scheme,netloc,path))
  if scheme == 'http':
    conn = httplib.HTTPConnection(netloc,timeout=timeout)
  else:
    conn = httplib.HTTPSConnection(netloc,timeout=timeout)
  
  # Set request-headers.
  if auth is not None:
    userpass = auth['username']+':'+auth['password']
    userpass = base64.encodestring(urllib.unquote(userpass)).strip()
    headers['Authorization'] =  'Basic '+userpass
  if method == 'GET' and query:
    path += '?' + query
    query = ''
  conn.request(method, path, query, headers)
  response = conn.getresponse()
  reply_code = response.status
  message = response.reason
  
  #### get parameter from content
  if reply_code == 404 or reply_code >= 500:
    error = "[%i]: %s at %s [%s]"%(reply_code,message,url,method)
    writeLog( context, "[http_import.error]: %s"%error)
    raise zExceptions.InternalError(error)
  elif reply_code==200:
    # get content
    data = response.read()
    rtn = None
    if parse_qs:
      try:
        # return dictionary of value lists
        data = cgi.parse_qs(data, keep_blank_values=1, strict_parsing=1)
      except:
        writeError(context,'[http_import]: can\'t parse_qs')
    return data
  else:
    result = '['+str(reply_code)+']: '+str(message)
    writeLog( context, "[http_import.result]: %s"%result)
    return result


################################################################################
#
#{ Logging
#
################################################################################

def getLog(context):
  """
  Get zms_log.
  """
  request = context.REQUEST
  if request.has_key('ZMSLOG'):
    zms_log = request.get('ZMSLOG')
  else:
    zms_log = getattr(context,'zms_log',None)
    if zms_log is None:
      zms_log = getattr(context.getPortalMaster(),'zms_log',None)
    request.set('ZMSLOG',zms_log)
  return zms_log

def writeStdout(context, info):
  """
  Write to standard-out (only allowed for development-purposes!).
  @param info: Object
  @type info: C{any}
  @rtype: C{str}
  """
  print info
  return info

security.declarePublic('writeLog')
def writeLog(context, info):
  """
  Log debug-information.
  @param info: Debug-information
  @type info: C{any}
  @rtype: C{str}
  """
  try:
    zms_log = getLog(context)
    severity = logging.DEBUG
    if zms_log.hasSeverity(severity):
      info = "[%s@%s]"%(context.meta_id,'/'.join(context.getPhysicalPath())) + info
      zms_log.LOG( severity, info)
  except:
    pass
  return info

security.declarePublic('writeBlock')
def writeBlock(context, info):
  """
  Log information.
  @param info: Information
  @type info: C{any}
  @rtype: C{str}
  """
  try:
    zms_log = getLog(context)
    severity = logging.INFO
    if zms_log.hasSeverity(severity):
      info = "[%s@%s]"%(context.meta_id,'/'.join(context.getPhysicalPath())) + info
      zms_log.LOG( severity, info)
  except:
    pass
  return info

security.declarePublic('writeError')
def writeError(context, info):
  """
  Log error.
  @param info: Information
  @type info: C{any}
  @rtype: C{str}
  """
  t,v='?','?'
  try:
    t,v,tb = sys.exc_info()
    v = str(v)
    # Strip HTML tags from the error value
    for pattern in [r"<[^<>]*>", r"&[A-Za-z]+;"]:
      v = re_sub(pattern,' ', v)
    if info: 
      info += '\n'
    severity = logging.ERROR
    info += ''.join(format_exception(t, v, tb))
    info = "[%s@%s]"%(context.meta_id,'/'.join(context.getPhysicalPath())) + info
    zms_log = getLog(context)
    if zms_log.hasSeverity(severity):
      zms_log.LOG( severity, info)
    t = t.__name__.upper()
  except:
    pass
  return '%s: %s <!-- %s -->'%(t,v,info)

#)


################################################################################
#
#( Regular Expressions
#
################################################################################

security.declarePublic('re_sub')
def re_sub( pattern, replacement, subject, ignorecase=False):
  """
  Performs a search-and-replace across subject, replacing all matches of 
  regex in subject with replacement. The result is returned by the sub() 
  function. The subject string you pass is not modified.
  @rtype: C{str}
  """
  if ignorecase:
    return re.compile( pattern, re.IGNORECASE).sub( replacement, subject)
  else:
    return re.compile( pattern).sub( replacement, subject)

security.declarePublic('re_search')
def re_search( pattern, subject, ignorecase=False):
  """
  Scan through string looking for a location where the regular expression 
  pattern produces a match, and return a corresponding MatchObject 
  instance. Return None if no position in the string matches the pattern; 
  note that this is different from finding a zero-length match at some
  point in the string.
  @rtype: C{str}
  """
  if ignorecase:
    s = re.compile( pattern, re.IGNORECASE).split( subject)
  else:
    s = re.compile( pattern).split( subject)
  return map( lambda x: s[x*2+1], range(len(s)/2))

security.declarePublic('re_findall')
def re_findall( pattern, text, ignorecase=False):
  """
  Return all non-overlapping matches of pattern in string, as a list of strings. 
  The string is scanned left-to-right, and matches are returned in the order found. 
  If one or more groups are present in the pattern, return a list of groups; 
  this will be a list of tuples if the pattern has more than one group. 
  Empty matches are included in the result unless they touch the beginning of another match
  @rtype: C{str}
  """
  if ignorecase:
    r = re.compile( pattern, re.IGNORECASE)
  else:
    r = re.compile( pattern)
  return r.findall(text)

#)


############################################################################
#
#  DATE TIME
#
############################################################################

# ==========================================================================
# Index  Field  Values  
# 0  year (for example, 1993) 
# 1  month range [1,12] 
# 2  day range [1,31] 
# 3  hour range [0,23] 
# 4  minute range [0,59] 
# 5  second range [0,61]; see (1) in strftime() description 
# 6  weekday range [0,6], Monday is 0 
# 7  Julian day range [1,366] 
# 8  daylight savings flag 0, 1 or -1; see below 
# ==========================================================================

security.declarePublic('format_datetime_iso')
def format_datetime_iso(t):
  # DST is Daylight Saving Time, an adjustment of the timezone by 
  # (usually) one hour during part of the year. DST rules are magic 
  # (determined by local law) and can change from year to year.
  # 
  # DST in t[8] ! -1 (unknown), 0 (off), 1 (on)
  if t[8] == 1:
    tz = time.altzone
  elif t[8] == 0:
    tz = time.timezone
  else:
    tz = 0
  #  The offset of the local (non-DST) timezone, in seconds west of UTC
  # (negative in most of Western Europe, positive in the US, zero in the
  # UK).
  #
  # ==> quite the opposite to the usual definition as eg in RFC 822.
  tch = '-'
  if tz < 0:
    tch = '+'
  tz = abs(tz)
  tzh = tz/60/60
  tzm = (tz-tzh*60*60)/60
  return time.strftime('%Y-%m-%dT%H:%M:%S',t)+tch+('00%d'%tzh)[-2:]+':'+('00%d'%tzm)[-2:]

def getLangFmtDate(context, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
  """
  Formats date in locale-format
  @param t: Datetime
  @type t: C{struct_time}
  @param lang: Locale
  @type lang: C{str}
  @param fmt_str: Format-String, possible values SHORTDATETIME_FMT (default),
  SHORTDATE_FMT, DATETIME_FMT, DATE_FMT, DateTime, Day, Month, ISO8601, RFC2822
  """
  try:
    if lang is None:
      lang = context.get_manage_lang()
    # Convert to struct_time
    t = getDateTime(t)
    # Return ModificationTime
    if fmt_str == 'BOBOBASE_MODIFICATION_FMT':
      sdtf = context.getLangFmtDate(t, lang, fmt_str='SHORTDATETIME_FMT')
      if context.daysBetween(t,DateTime()) > context.getConfProperty('ZMS.shortDateFormat.daysBetween',5):
        sdf = context.getLangFmtDate(t, lang, fmt_str='SHORTDATE_FMT')
        return '<span title="%s">%s</span>'%(sdtf,sdf)
      return sdtf
    # Return DateTime
    if fmt_str == 'DateTime':
      dt = DateTime('%4d/%2d/%2d'%(t[0],t[1],t[2]))
      return dt
    # Return name of weekday
    elif fmt_str == 'Day':
      dt = DateTime('%4d/%2d/%2d'%(t[0],t[1],t[2]))
      return context.getLangStr('DAYOFWEEK%i'%(dt.dow()%7),lang)
    # Return name of month
    elif fmt_str == 'Month':
      return context.getLangStr('MONTH%i'%t[1],lang)
    elif fmt_str.replace('-','').replace(' ','') in ['ISO8601','RFC2822']:
      return format_datetime_iso(t)
    # Return date/time
    fmt = context.getLangStr(fmt_str,lang)
    time_fmt = context.getLangStr('TIME_FMT',lang)
    date_fmt = context.getLangStr('DATE_FMT',lang)
    if fmt.find(time_fmt) >= 0:
      if t[3] == 0 and \
         t[4] == 0 and \
         t[5]== 0:
        fmt = fmt[:-len(time_fmt)]
    fmt = fmt.strip()
    return time.strftime(fmt,t)
  except:
    #-- writeError(context,"[getLangFmtDate]: t=%s"%str(t))
    return str(t)


security.declarePublic('getDateTime')
def getDateTime(t):
  """
  Bei Python 2.2 ist der Typ der Objekte des Moduls "time" nicht
  mehr "tuple", sondern "time.struct_time". Es verhaelt sich aber weiterhin
  abwaertskompatibel zu einem tuple.
  This is no problem for Zope since Zope uses its own, more flexible, type
  DateTime. Nevertheless ZMS relies on the datatype "tuple" as DateTime has 
  the limitation that no date prior to 1970-01-01 can be used!
  """
  if t is not None:
    try:
      if isinstance( t, DateTime):
        f = '%Y/%m/%d %H:%M:%S'
        st = str(t)
        if st.rfind(' ')>0:
          st = st[:st.rfind(' ')]
        else:
          f = f[:f.rfind(' ')]
        if st.rfind('.')>0:
          st = st[:st.rfind('.')]
        t = time.strptime( st, f)
      if type(t) is tuple:
        t = time.mktime( t)
      if type(t) is not time.struct_time:
        t = time.localtime( t)
    except:
      pass
  return t

security.declarePublic('stripDateTime')
def stripDateTime(t):
  """
  Strips time portion from date-time and returns date.
  """
  d = None
  if t is not None:
    t = getDateTime(t)
    d = (t[0],t[1],t[2],0,0,0,t[6],t[7],t[8])
  return d

security.declarePublic('daysBetween')
def daysBetween(t0, t1):
  """
  Returns number of days between date t0 and t1.
  @rtype: C{int}
  """
  t0 = time.mktime(stripDateTime(getDateTime(t0)))
  t1 = time.mktime(stripDateTime(getDateTime(t1)))
  d = 24.0*60.0*60.0
  return int((t1-t0)/d)

security.declarePublic('compareDate')
def compareDate(t0, t1):
  """
  Compares two dates t0 and t1 and returns result.
   +1: t0 < t1
    0: t0 == t1
   -1: t0 > t1
  @returns: A negative number if date t0 is before t1, zero if they are equal, or positive if t0 is after t1.
  @rtype: C{int}
  """
  mt0 = time.mktime(stripDateTime(getDateTime(t0)))
  mt1 = time.mktime(stripDateTime(getDateTime(t1)))
  if mt1 > mt0:
    return +1
  elif mt1 < mt0:
    return -1
  else:
    return 0

security.declarePublic('parseLangFmtDate')
def parseLangFmtDate(s):
  """
  Parses a string representing a date by trying a variety of different parsers.
  The parse will try each parse pattern in turn. A parse is only deemed successful if it parses the whole of the input string. If no parse patterns match, None is returned.
  @param s: the date to parse
  @type s:C{s}
  @return: the parsed date.
  @rtype: C{struct_time}
  """
  def strip_int(s):
    i = 0
    while i < len(s) and ord(s[i]) in range(ord('0'),ord('9')+1):
      i = i + 1
    return i
  value = None
  for fmt in ['%d.%m.%Y %H:%M:%S','%Y/%m/%d %H:%M:%S','%Y-%m-%d %H:%M:%S','%H:%M:%S']:
    if value is None:
      try:
        if isinstance(s,DateTime):
          s = s.strftime( fmt)
        if s is not None and len(str(s)) > 0:
          dctTime = {'Y':0,'m':0,'d':0,'H':0,'M':0,'S':0}
          v = str(s)
          while True:
            i = fmt.find('%')+1
            if i == 0:
              break
            dirkey = fmt[i]
            fmt = fmt[i+1:]
            j = strip_int(v)
            if j == 0:
              break
            dirval = int(v[:j])
            v = v[j:]
            dctTime[dirkey] = dirval
            if len(v) == 0:
              break
            if fmt[0] != v[0]:
              raise zExceptions.InternalError
            fmt = fmt[1:]
            v = v[1:]
          if dctTime['Y'] + dctTime['m'] + dctTime['d'] == 0:
            dctTime['Y'] = 1980
            dctTime['m'] = 1
            dctTime['d'] = 1
          if dctTime['Y'] in range( 0, 50): 
            dctTime['Y'] = dctTime['Y'] + 2000 
          if dctTime['Y'] in range( 50, 100): 
            dctTime['Y'] = dctTime['Y'] + 1900 
          if len(v.strip())>0 or \
             (dctTime['Y']+dctTime['m']+dctTime['d']!=0 and dctTime['Y']-1 not in range(1900,2100)) or \
             (dctTime['Y']+dctTime['m']+dctTime['d']!=0 and dctTime['m']-1 not in range(12)) or \
             (dctTime['Y']+dctTime['m']+dctTime['d']!=0 and dctTime['d']-1 not in range(31)) or \
             (dctTime['H']!=0 and dctTime['H']-1 not in range(24)) or \
             (dctTime['M']!=0 and dctTime['M']-1 not in range(60)) or \
             (dctTime['S']!=0 and dctTime['S']-1 not in range(60)):
            raise zExceptions.InternalError
          value = getDateTime((dctTime['Y'],dctTime['m'],dctTime['d'],dctTime['H'],dctTime['M'],dctTime['S'],0,1,-1))
      except:
        pass
  return value

#)


############################################################################
#
#( Operators
#
############################################################################

security.declarePublic('operator_absattr')
def operator_absattr(v):
  """
  Returns absolute-attribute of given value.
  @param v: Value
  @type v: C{any}
  @return: the absolute-attribute of the value
  @rtype: C{type}
  """
  return absattr(v)

security.declarePublic('operator_gettype')
def operator_gettype(v):
  """
  Returns python-type of given value.
  @param v: Value
  @type v: C{any}
  @return: the type of the value
  @rtype: C{type}
  """
  return type(v)

security.declarePublic('operator_setitem')
def operator_setitem(a, b, c):
  """
  Applies value for key in python-dictionary.
  This is a convenience-function since it is not possible to use expressions
  like a[b]=c in DTML.
  @param a: Dictionary
  @type a: C{dict}
  @param b: Key
  @type b: C{any}
  @param c: Value
  @type c: C{any}
  @rtype: C{dict}
  """
  operator.setitem(a,b,c)
  return a

security.declarePublic('operator_getitem')
def operator_getitem(a, b, c=None, ignorecase=True):
  """
  Retrieves value for key from python-dictionary.
  @param a: Dictionary
  @type a: C{dict}
  @param b: Key
  @type b: C{any}
  @param c: Default-Value
  @type c: C{any}
  @rtype: C{any}
  """
  if ignorecase and type(b) in StringTypes:
    flags = re.IGNORECASE
    pattern = '^%s$'%b
    for key in a.keys():
      if re.search(pattern,key,flags) is not None:
        return operator.getitem(a,key)
  if b in a.keys():
    return operator.getitem(a,b)
  return c

security.declarePublic('operator_delitem')
def operator_delitem(a, b):
  """
  Delete key from python-dictionary.
  @param a: Dictionary
  @type a: C{dict}
  @param b: Key
  @type b: C{any}
  """
  operator.delitem(a, b)

security.declarePublic('operator_setattr')
def operator_setattr(a, b, c):
  """
  Applies value for key to python-object.
  This is a convenience-function since the use expressions like
  setattr(a,b,c) is restricted in DTML.
  @param a: Object
  @type a: C{any}
  @param b: Key
  @type b: C{string}
  @param c: Value
  @type c: C{any}
  @rtype: C{object}
  """
  setattr(a,b,c)
  return a

security.declarePublic('operator_getattr')
def operator_getattr(a, b, c=None):
  """
  Retrieves value for key from python-object.
  This is a convenience-function since the use expressions like
  getattr(a,b,c) is restricted in DTML.
  @param a: Object
  @type a: C{any}
  @param b: Key
  @type b: C{any}
  @param c: Default-Value
  @type c: C{any}
  @rtype: C{any}
  """
  return getattr(a,b,c)

security.declarePublic('operator_delattr')
def operator_delattr(a, b):
  """
  Delete key from python-object.
  @param a: Object
  @type a: C{any}
  @param b: Key
  @type b: C{any}
  """
  return delattr(a,b)

#)


############################################################################
#
#() Local File-System
#
############################################################################

security.declarePublic('localfs_read')
def localfs_read(filename, mode='b', cache='public, max-age=3600', REQUEST=None):
  """
  Reads file from local file-system.
  You must grant permissions for reading from local file-system to
  directories in Config-Tab / Miscelleaneous-Section.
  @param filename: Filepath
  @type filename: C{string}
  @param filename: Access mode
  @type filename: C{string}, values are 'b' - binary
  @param cache Cache-Headers
  @type cache C{bool}
  @param REQUEST: the triggering request
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Contents of file
  @rtype: C{string} or C{filestream_iterator}
  """
  try:
    filename = unicode(filename,'utf-8').encode('latin-1')
  except:
    pass
  # Get absolute filename.
  filename = _fileutil.absoluteOSPath(filename)
  # Read file.
  if type( mode) is dict:
    fdata, mt, enc, fsize = _fileutil.readFile( filename, mode.get('mode','b'), mode.get('threshold',-1))
  else:
    fdata, mt, enc, fsize = _fileutil.readFile( filename, mode)
  if REQUEST is not None:
    RESPONSE = REQUEST.RESPONSE
    standard.set_response_headers(filename,mt,fsize,REQUEST)
    RESPONSE.setHeader('Cache-Control', cache)
    RESPONSE.setHeader('Content-Encoding', enc)
  return fdata


security.declarePublic('localfs_write')
def localfs_write(filename, v, mode='b', REQUEST=None):
  """
  Writes file to local file-system.
  """
  # Get absolute filename.
  filename = _fileutil.absoluteOSPath(filename)
  # Write file.
  _fileutil.exportObj( v, filename, mode)


security.declarePublic('localfs_remove')
def localfs_remove(path, deep=0):
  """
  Removes file from local file-system.
  """
  # Get absolute filename.
  filename = _fileutil.absoluteOSPath(path)
  # Remove file.
  _fileutil.remove( path, deep)


security.declarePublic('localfs_readPath')
def localfs_readPath(filename, data=False, recursive=False, REQUEST=None):
  """
  Reads path from local file-system.
  @rtype: C{list}
  """
  try:
    filename = unicode(filename,'utf-8').encode('latin-1')
  except:
    pass
  # Get absolute filename.
  filename = _fileutil.absoluteOSPath(filename)
  # Read path.
  return _fileutil.readPath(filename, data, recursive)

#)


############################################################################
#
#( Mappings
#
############################################################################

security.declarePublic('intersection_list')
def intersection_list(l1, l2):
  """
  Intersection of two lists (li & l2).
  @param l1: List #1
  @type l1: C{list}
  @param l2: List #2
  @type l2: C{list}
  @returns: Intersection list
  @rtype: C{list}
  """
  l1 = list(l1)
  l2 = list(l2)
  return filter(lambda x: x in l2, l1)


security.declarePublic('difference_list')
def difference_list(l1, l2):
  """
  Difference of two lists (l1 - l2).
  @param l1: List #1
  @type l1: C{list}
  @param l2: List #2
  @type l2: C{list}
  @returns: Difference list
  @rtype: C{list}
  """
  l1 = list(l1)
  l2 = list(l2)
  return filter(lambda x: x not in l2, l1)


security.declarePublic('concat_list')
def concat_list(l1, l2):
  """
  Concatenates two lists (l1 + l2).
  @param l1: List #1
  @type l1: list
  @param l2: List #2
  @type l2: list
  @returns: Concatinated list
  @rtype: C{list}
  """
  l1 = list(l1)
  l2 = list(l2)
  l = copy_list(l1)
  l.extend(filter(lambda x: x not in l1, l2))
  return l


security.declarePublic('dict_list')
def dict_list(l):
  """
  Converts list to dictionary: key=l[x*2], value=l[x*2+1]
  @param l: List
  @type l: C{list}
  @return: Dictionary
  @rtype: C{dict}
  """
  dict = {}
  for i in range(0,len(l)/2):
    key = l[i*2]
    value = l[i*2+1]
    dict[key] = value
  return dict


security.declarePublic('distinct_list')
def distinct_list(l, i=None):
  """
  Returns distinct values of given field from list.
  @param l: List
  @type l: C{list}
  @rtype: C{list}
  """
  k = []
  for x in l:
    if i is None:
      v = x
    elif type(i) is str:
      v = x.get(i,None)
    else:
      v = x[i]
    if not v in k:
      k.append(v)
  return k


security.declarePublic('sort_list')
def sort_list(l, qorder=None, qorderdir='asc', ignorecase=1): 
  """
  Sorts list by given field.
  @return: Sorted list.
  @rtype: C{list}
  """
  if qorder is None:
    sorted = map(lambda x: (x, x), l)
  elif type(qorder) is str:
    sorted = map(lambda x: (_globals.sort_item(x.get(qorder,None)),x),l)
  elif type(qorder) is list:
    sorted = map(lambda x: (map(lambda y: _globals.sort_item(x[y]), qorder),x),l)
  else:
    sorted = map(lambda x: (_globals.sort_item(x[qorder]),x),l)
  if ignorecase==1 and len(sorted) > 0 and type(sorted[0][0]) is str:
    sorted = map(lambda x: (str(x[0]).upper(),x[1]),sorted)
  sorted.sort()
  sorted = map(lambda x: x[1],sorted)
  if qorderdir == 'desc': sorted.reverse()
  return sorted


security.declarePublic('string_list')
def string_list(s, sep='\n', trim=True):
  """
  Split string by given separator and trim items.
  @rtype: C{list}
  """
  l = []
  for i in s.split(sep):
    if trim:
      i = i.strip()
    while len(i) > 0 and ord(i[-1]) < 32:
      i = i[:-1]
    if len(i) > 0:
      l.append(i)
  return l


security.declarePublic('str_json')
def str_json(i, encoding='ascii', errors='xmlcharrefreplace', formatted=False, level=0):
  """
  Returns a json-string representation of the object.
  @rtype: C{str}
  """
  if type(i) is list or type(i) is tuple:
    return '[' \
        + (['','\n'][formatted]+(['','\t'][formatted]*level)+',').join(map(lambda x: str_json(x,encoding,errors,formatted,level+1),i)) \
        + ']'
  elif type(i) is dict:
    k = i.keys()
    k.sort()
    return '{' \
        + (['','\n'][formatted]+(['','\t'][formatted]*level)+',').join(map(lambda x: '"%s":%s'%(x,str_json(i[x],encoding,errors,formatted,level+1)),k)) \
        + '}'
  elif type(i) is time.struct_time:
    try:
      return '"%s"'%format_datetime_iso(i)
    except:
      pass
  elif type(i) is int or type(i) is float:
    return str(i)
  elif type(i) is bool:
    return str(i).lower()
  elif i is not None:
    if type(i) is unicode:
      if not (i.strip().startswith('<') and i.strip().endswith('>')):
        import cgi
        i = cgi.escape(i).encode(encoding, errors)
      else:
        i = i.encode(encoding, errors)
    else:
      i = str(i)
    if i in ['true','false']:
      return i
    else:
      return '"%s"'%(i.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\r','\\r'))
  return '""'


security.declarePublic('str_item')
def str_item(i):
  """
  Returns a string representation of the item.
  @rtype: C{str}
  """
  if type(i) is list or type(i) is tuple:
    return '\n'.join(map(lambda x: str_item(x),i))
  elif type(i) is dict:
    return '\n'.join(map(lambda x: str_item(i[x]),i.keys()))
  elif type(i) is time.struct_time:
    try:
      return format_datetime_iso(i)
    except:
      pass
  if i is not None:
    return str(i)
  return ''


security.declarePublic('filter_list')
def filter_list(l, i, v, o='%'):
  """
  Filters list by given field.
  @param l: List
  @type l: C{list}
  @param i: Field-name or -index
  @type i: C{str} or C{int}
  @param v: Field-value
  @type v: C{any}
  @param v: Match-operator
  @type v: C{str}, values are '%' (full-text), '=', '==', '>', '<', '>=', '<=', '!=', '<>'
  @return: Filtered list.
  @rtype: C{list}
  """
  # Full-text scan.
  if i is None or len(str(i))==0:
    v = str(v)
    k = []
    if len(v.split(' OR '))>1:
      for s in v.split(' OR '):
        s = s.replace('*','').strip()
        if len( s) > 0:
          s = umlaut_quote(s).lower()
          k.extend(filter(lambda x: x not in k and umlaut_quote(str_item(x)).lower().find(s)>=0, l))
    elif len(v.split(' AND '))>1:
      k = l
      for s in v.split(' AND '):
        s = s.replace('*','').strip()
        if len( s) > 0:
          s = umlaut_quote(s).lower()
          k = filter(lambda x: umlaut_quote(str_item(x)).lower().find(s)>=0, k)
    else:
      v = v.replace('*','').strip().lower()
      if len( v) > 0:
        v = umlaut_quote(v).lower()
        k = filter(lambda x: umlaut_quote(str_item(x)).lower().find(v)>=0, l)
    return k
  # Extract Items.
  if type(i) is str:
    k=map(lambda x: (x.get(i,None),x), l)
  else:
    k=map(lambda x: (x[i],x), l)
  # Filter Date-Tuples
  if type(v) is tuple or type(v) is time.struct_time:
    v = DateTime('%4d/%2d/%2d'%(v[0],v[1],v[2]))
  # Filter Strings.
  if type(v) is str or o=='%':
    if o=='=' or o=='==':
      k=filter(lambda x: str_item(x[0])==v, k)
    elif o=='<>' or o=='!=':
      k=filter(lambda x: str_item(x[0])!=v, k)
    else:
      v = str_item(v).lower()
      if v.find('*')>=0 or v.find('?')>=0:
        k=filter(lambda x: fnmatch.fnmatch(str_item(x[0]).lower(),v), k)
      else:
        k=filter(lambda x: str_item(x[0]).lower().find(v)>=0, k)
  # Filter Numbers.
  elif type(v) is int or type(v) is float:
    if o=='=' or o=='==':
      k=filter(lambda x: x[0]==v, k)
    elif o=='<':
      k=filter(lambda x: x[0]<v, k)
    elif o=='>':
      k=filter(lambda x: x[0]>v, k)
    elif o=='<=':
      k=filter(lambda x: x[0]<=v, k)
    elif o=='>=':
      k=filter(lambda x: x[0]>=v, k)
    elif o=='<>' or o=='!=':
      k=filter(lambda x: x[0]!=v, k)
  # Filter Lists.
  elif type(v) is list:
    if o=='=' or o=='==':
      k=filter(lambda x: x[0]==v, k)
    elif o=='in':
      k=filter(lambda x: x[0] in v, k)
  # Filter DateTimes.
  elif isinstance(v,DateTime):
    k=filter(lambda x: x[0] is not None, k)
    k=map(lambda x: (getDateTime(x[0]),x[1]), k)
    k=map(lambda x: (DateTime('%4d/%2d/%2d'%(x[0][0],x[0][1],x[0][2])),x[1]), k)
    if o=='=' or o=='==':
      k=filter(lambda x: x[0].equalTo(v), k)
    elif o=='<':
      k=filter(lambda x: x[0].lessThan(v), k)
    elif o=='>':
      k=filter(lambda x: x[0].greaterThan(v), k)
    elif o=='<=':
      k=filter(lambda x: x[0].lessThanEqualTo(v), k)
    elif o=='>=':
      k=filter(lambda x: x[0].greaterThanEqualTo(v), k)
    elif o=='<>':
      k=filter(lambda x: not x[0].equalTo(v), k)
  return map(lambda x: x[1], k)


security.declarePublic('copy_list')
def copy_list(l):
  """
  Copies list l.
  @param l: List
  @type l: C{list}
  @return: Copy of list.
  @rtype: C{list}
  """
  try:
    v = copy.deepcopy(l)
  except:
    v = copy.copy(l)
  return v


security.declarePublic('sync_list')
def sync_list(l, nl, i):
  """
  Synchronizes list l with new list nl using the column i as identifier.
  """
  k = []
  for x in l:
    k.extend([x[i],x])
  for x in nl:
    if x[i] in k:
      j = k.index(x[i])+1
      if type(x) is dict:
        v = k[j]
        for xk in x.keys():
          v[xk] = x[xk]
        x = v
      k[j] = x
    else:
      k.extend([x[i],x])
  return map(lambda x: k[x*2+1], range(0,len(k)/2))


security.declarePublic('aggregate_list')
def aggregate_list(l, i):
  """
  Aggregates given field in list.
  """
  k = []
  for li in copy.deepcopy(l):
    del li[i]
    if li not in k:
      k.append(li)
  m = []
  for ki in k:
    mi = copy.deepcopy(ki)
    mi[i] = []
    ks = ki.keys()
    for li in l:
      if len(ks) == len(filter(lambda x: x==i or ki[x]==li[x],ks)):
        mi[i].append(li[i])
    m.append(mi)
  return m

#)


############################################################################
#
#{ XML
#
############################################################################

security.declarePublic('getXmlHeader')
def getXmlHeader(encoding='utf-8'):
  """
  Returns XML-Header (encoding=utf-8)
  @param encoding: Encoding
  @type encoding: C{str}
  @rtype: C{str}
  """
  return _xmllib.xml_header(encoding)


security.declarePublic('toXmlString')
def toXmlString(context, v, xhtml=False, encoding='utf-8'):
  """
  Serializes value to ZMS XML-Structure.
  @param context
  @type context
  @param v
  @type v
  @param xhtml
  @type xhtml
  @param encoding
  @type encoding
  @rtype: C{string}
  """
  return _xmllib.toXml(context, v, xhtml=xhtml, encoding=encoding)


security.declarePublic('parseXmlString')
def parseXmlString(xml):
  """
  Parse value from ZMS XML-Structure.
  @param xml
  @type xml: C{str} or C{StringIO}
  @return: C{list} or C{dict}
  @rtype: C{any}
  """
  builder = _xmllib.XmlAttrBuilder()
  if type(xml) is str:
    xml = StringIO(xml)
  v = builder.parse(xml)
  return v


security.declarePublic('processData')
def processData(context, processId, data, trans=None):
  """
  Process data with custom transformation.
  @param context
  @type context: C{ZMSObject}
  @param processId: the process-id
  @type processId: C{str}
  @param data: the xml-data
  @type data: C{str} or C{StringIO}
  @param trans: the transformation
  @type trans: C{str}
  @return: the transformed data
  @rtype: C{str}
  """
  return _filtermanager.processData(context, processId, data, trans)


############################################################################
#
#{  Executable
#
############################################################################

security.declarePublic('dt_executable')
def dt_executable(context, v):
  """
  Returns if given value is executable.
  @param context: the context
  @type context: C{ZMSObject}
  @param v: the executable code
  @type v: C{str}
  @return: 
  @rtype: C{Bool}
  """
  if type(v) in StringTypes:
    if v.startswith('##'):
      return 'py'
    elif v.find('<tal:') >= 0:
      return 'zpt'
    elif v.find('<dtml-') >= 0:
      return 'method'
  return False

security.declarePublic('dt_exec')
def dt_exec(context, v, o={}):
  """
  Try to execute given value.
  @param context: the context
  @type context: C{ZMSObject}
  @param v: the executable code
  @type v: C{str}
  @param o: the options
  @type o: C{dict}
  @return:
  @rtype: C{any}
  """
  if type(v) in StringTypes:
    if v.startswith('##'):
      v = dt_py(context,v,o)
    elif v.find('<tal:') >= 0:
      v = dt_tal(context,v,dict(o))
    elif v.find('<dtml-') >= 0:
      v = dt_html(context,v,context.REQUEST)
  return v

def dt_html(context, value, REQUEST):
  """
  Execute given DTML-snippet.
  @param context: the context
  @type context: C{ZMSObject}
  @param value: DTML-snippet
  @type value: C{string}
  @param REQUEST: the triggering request
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Result of the execution or None
  @rtype: C{any}
  """
  import DocumentTemplate.DT_HTML
  i = 0
  while True:
    i = value.find( '<dtml-', i)
    if i < 0:
      break
    j = value.find( '>', i)
    if j < 0:
      break
    if value[ j-1] == '/':
      value = value[ :j-1] + value[ j:]
    i = j
  value = re.sub( '<dtml-sendmail(.*?)>(\r\n|\n)','<dtml-sendmail\\1>',value)
  value = re.sub( '</dtml-var>', '', value)
  dtml = DocumentTemplate.DT_HTML.HTML(value)
  value = dtml( context, REQUEST)
  return value

def dt_py( context, script, kw={}):
  """
  Execute given Python-script.
  @param context: the context
  @type context: C{ZMSObject}
  @param script: the Python-script
  @type script: C{string}
  @param kw: additional options
  @type kw: C{dict}
  @return: Result of the execution or None
  @rtype: C{any}
  """
  from Products.PythonScripts.PythonScript import PythonScript
  id = '~temp'
  header = []
  header.append('## Script (Python) "%s"'%id)
  header.append('##bind container=container')
  header.append('##bind context=context')
  header.append('##bind namespace=')
  header.append('##bind script=script')
  header.append('##bind subpath=traverse_subpath')
  header.append('##parameters='+','.join(kw.keys()))
  header.append('##title=')
  header.append('##')
  header.append('')
  data = '\n'.join(header)+script
  ps = PythonScript("~temp")
  ps.write(data)
  bound_names = {
      'traverse_subpath':[],
      'container':context,
      'context':context,
      'script':ps,
    }
  args = ()
  return ps._exec(bound_names,args,kw)

def dt_tal(context, text, options={}):
  """
  Execute given TAL-snippet.
  @param context: the context
  @type context: C{ZMSObject}
  @param value: TAL-snippet
  @type value: C{string}
  @return: Result of the execution or None
  @rtype: C{any}
  """
  class StaticPageTemplateFile(PageTemplateFile):
    def setText(self,text):
      self.text = text
    def setEnv(self,context,options):
      self.context = context
      self.options = options
    def pt_getContext(self):
      root = self.context.getPhysicalRoot()
      context = self.context
      options = self.options
      c = {'template': self,
           'here': context,
           'context': context,
           'options': options,
           'root': root,
           'request': getattr(root, 'REQUEST', None),
           'modules': SecureModuleImporter,
           }
      return c
    def _cook_check(self):
      t = 'text/html'
      self.pt_edit(self.text, t)
      self._cook()
  pt = StaticPageTemplateFile(filename='None')
  pt.setText(text)
  pt.setEnv(context,options)
  request = context.REQUEST
  return unicode(pt.pt_render(extra_context={'here':context,'request':request})).encode('utf-8')

#}


def sendMail(context, mto, msubject, mbody, REQUEST=None, mattach=None):
  """
  Sends Mail via MailHost.
  @param context: the context
  @type context: C{ZMSObject}
  @param mto: the recipient(s)
  @type mto: C{str} or C{dict}
  @param msubject: the subject
  @type mto: C{str}
  @param mbody: the body
  @type mbody: C{str} or C{dict}
  @rtype: C{Bool}
  """
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
  from email.mime.image import MIMEImage
  from email.mime.audio import MIMEAudio
  from email.mime.application import MIMEApplication
  
  # Check constraints.
  if type(mto) is str:
    mto = {'To':mto}
  if type(mbody) is str:
    mbody = [{'text':mbody}]
  
  # Get sender.
  if REQUEST is not None:
    auth_user = REQUEST['AUTHENTICATED_USER']
    mto['From'] = mto.get('From',context.getUserAttr(auth_user,'email',context.getConfProperty('ZMSAdministrator.email','')))
  
  # Get MailHost.
  mailhost = None
  homeElmnt = context.getHome()
  if len(homeElmnt.objectValues(['Mail Host'])) == 1:
    mailhost = homeElmnt.objectValues(['Mail Host'])[0]
  elif getattr(homeElmnt,'MailHost',None) is not None:
    mailhost = getattr(homeElmnt,'MailHost',None)
  
  # Assemble MIME object.
  #mime_msg = MIMEMultipart('related') # => attachments do not show up in iOS Mail (just as paperclip indicator)
  mime_msg = MIMEMultipart()
  mime_msg['Subject'] = msubject
  for k in mto.keys():
    mime_msg[k] = mto[k]
  mime_msg.preamble = 'This is a multi-part message in MIME format.'
  
  # Encapsulate the plain and HTML versions of the message body 
  # in an 'alternative' part, so message agents can decide 
  # which they want to display.
  msgAlternative = MIMEMultipart('alternative')
  mime_msg.attach(msgAlternative)
  for ibody in mbody:
    msg = MIMEText(ibody['text'], _subtype=ibody.get('subtype','plain'), _charset=ibody.get('charset','unicode-1-1-utf-8'))
    msgAlternative.attach(msg)

  # Handle attachments
  if mattach is not None:
    if not isinstance(mattach, list):
      mattach = [mattach]
    for filedata in mattach:
      # Send base64-encoded data stream
      # Give optional prefix naming filename, mimetype and encoding 
      # Example: 'filename:MyImageFile.png;data:image/png;base64,......'
      if isinstance(filedata, str):
        mimetype = 'unknown'
        maintype = 'unknown'
        encoding = 'unknown'
        filename = 'unknown'
        filetype = 'attachment'
        fileextn = 'dat'
        metadata = standard.re_search('(^.*[;,])', filedata)
        # extract filename, mimetype and encoding if available
        if (type(metadata)==list and len(metadata)==1):          
          mimetype = standard.re_search('data:([^;,]+[;,][^;,]*)', metadata[0])
          filename = standard.re_search('filename:([^;,]+)', metadata[0])
          filedata = filedata.replace(metadata[0], '')           
        if (type(mimetype)==list and len(mimetype)==1): 
          mimetype = mimetype[0].split(';')
          if type(mimetype)==list and len(mimetype)==2:
            maintype = mimetype[0]
            encoding = mimetype[1]
        if (type(filename)==list and len(filename)==1):
          filename = filename[0]
        else:
          subtypes = maintype.split('/')
          if (type(subtypes)==list and len(subtypes)==2):
            filetype = subtypes[0]
            fileextn = subtypes[1]            
          filename = '%s.%s'%(filetype,fileextn)
        # decode if already encoded because MIME* is encoding by default
        if encoding=='base64':
          filedata = base64.b64decode(filedata)
        # create mime attachment
        if (filetype=='image'):
          part = MIMEImage(filedata, fileextn)                
        elif (filetype=='audio'):
          part = MIMEAudio(filedata, fileextn)              
        else:
          part = MIMEApplication(filedata)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'%filename)
        mime_msg.attach(part)
        
      # TODO: Handle data from filesystem or other sources
      elif isinstance(filedata, file):
        raise NotImplementedError
  
  # Send mail.
  try:
    #standard.writeBlock( context, "[sendMail]: %s"%mime_msg.as_string())
    mailhost.send(mime_msg.as_string())
    return 0
  except:
    return -1


################################################################################
# Define the initialize() util.
################################################################################
class initutil:

  def __init__(self):
    self.__attr_conf_dict__ = {}

  def setConfProperty(self, key, value):
    self.__attr_conf_dict__[key] = value

  def getConfProperty(self, key, default=None):
    return self.__attr_conf_dict__.get(key,default)

  def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
    return http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers)

security.apply(globals())

################################################################################
