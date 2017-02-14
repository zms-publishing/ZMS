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
from DateTime.DateTime import DateTime
from types import StringTypes
from traceback import format_exception
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
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

security = ModuleSecurityInfo('Products.zms.standard')

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
German umlaute.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
umlautMapping = {
        # German
        u'ä' : 'ae',
        u'ö' : 'oe',
        u'ü' : 'ue',
        u'Ä' : 'Ae',
        u'Ö' : 'Oe',
        u'Ü' : 'Ue',
        u'ß' : 'ss',
        # Cyrillic
        u'а' : 'a',
        u'б' : 'b',
        u'в' : 'v',
        u'г' : 'g',
        u'д' : 'd',
        u'е' : 'e',
        u'ё' : 'e',
        u'ж' : 'zh',
        u'з' : 'z',
        u'и' : 'i',
        u'й' : 'j',
        u'к' : 'k',
        u'л' : 'l',
        u'м' : 'm',
        u'н' : 'n',
        u'о' : 'o',
        u'п' : 'p',
        u'р' : 'r',
        u'с' : 's',
        u'т' : 't',
        u'у' : 'u',
        u'ф' : 'f',
        u'х' : 'h',
        u'ц' : 'c',
        u'ч' : 'ch',
        u'ш' : 'sh',
        u'щ' : 'sch',
        u'ь' : "'",
        u'ы' : 'y',
        u'ь' : "'",
        u'э' : 'e',
        u'ю' : 'ju',
        u'я' : 'ja',
        u'А' : 'A',
        u'Б' : 'B',
        u'В' : 'V',
        u'Г' : 'G',
        u'Д' : 'D',
        u'Е' : 'E',
        u'Ё' : 'E',
        u'Ж' : 'ZH',
        u'З' : 'Z',
        u'И' : 'I',
        u'Й' : 'J',
        u'К' : 'K',
        u'Л' : 'L',
        u'М' : 'M',
        u'Н' : 'N',
        u'О' : 'O',
        u'П' : 'P',
        u'Р' : 'R',
        u'С' : 'S',
        u'Т' : 'T',
        u'У' : 'U',
        u'Ф' : 'F',
        u'Х' : 'H',
        u'Ц' : 'C',
        u'Ч' : 'CH',
        u'Ш' : 'SH',
        u'Щ' : 'SCH',
        u'Ъ' : "'",
        u'Ы' : 'Y',
        u'Ь' : "'",
        u'Э' : 'E',
        u'Ю' : 'JU',
        u'Я' : 'JA',}


security.declarePublic('umlaut_quote')
def umlaut_quote(self, s, mapping={}):
  """
  Replace umlauts in s using given mapping.
  @param s: String
  @type s: C{str}
  @param mapping: Mapping
  @type mapping: C{dict}
  @return: Quoted string
  @rtype: C{str}
  """
  try:
    if type(s) is not unicode:
      s = unicode(s,'utf-8')
    map( lambda x: operator.setitem( mapping, x, umlautMapping[x]), umlautMapping.keys())
    for key in mapping.keys():
      s = s.replace(key,mapping[key])
    s = s.encode('utf-8')
  except:
    writeError(self,'[umlaut_quote]')
  return s


security.declarePublic('string_maxlen')
def string_maxlen(s, maxlen=20, etc='...', encoding=None):
  """
  Returns string with specified maximum-length. If original string exceeds 
  maximum-length '...' is appended at the end.
  @param s: String
  @type s: C{string}
  @param maxlen: Maximum-length
  @type maxlen: C{int}
  @param etc: Characters to be appended if maximum-length is exceeded
  @type etc: C{string}
  @param encoding: Encoding
  @type encoding: C{string}
  @rtype: C{string}
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
  @type m: C{int}
  @return: Integer
  @rtype: C{str}
  """
  return ''.join(map(lambda x: chr(16*int('0x%s'%m[x*2],0)+int('0x%s'%m[x*2+1],0)),range(len(m)/2)))


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.unencode:

Unencodes given parameter.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def unencode( p, enc='utf-8'):
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
  @type s: C{string}
  @return: Id-prefix
  @rtype: C{str}
  """
  return re.findall('^(\\D*)',s)[0]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.map_key_vals:

Maps list of keys and list of values to new dictionary.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def map_key_vals(keys, vals):
  d = {}
  map(operator.setitem, [d]*len(keys), keys, vals)
  return d


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.objectTree:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def objectTree(self, clients=False):
  rtn = [ self]
  try:
    for ob in self.objectValues( self.dGlobalAttrs.keys()):
      rtn.extend( objectTree( ob))
  except:
    writeError( self, '[objectTree]')
  if clients:
    for ob in self.getPortalClients():
      rtn.extend( objectTree( ob, clients))
  return rtn


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.form_quote

Remove <form>-tags for Management Interface.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def form_quote(text, REQUEST):
  rtn = text
  if isManagementInterface(REQUEST):
    rtn = re.sub( '<form(.*?)>', '<noform\\1>', rtn)
    rtn = re.sub( ' name="lang"', ' name="_lang"', rtn)
    rtn = re.sub( '</form(.*?)>', '</noform\\1>', rtn)
  return rtn


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.qs_append:

Append to Query-String.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def qs_append(qs, p, v):
  if len(qs) == 0:
    qs += '?'
  else:
    qs += '&amp;'
  qs += p + '=' + urllib.quote(v)
  return qs


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.nvl:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.get_session:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_session(self):
  return getattr(self, 'session_data_manager', None) and \
    self.session_data_manager.getSessionData(create=0)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.triggerEvent:

Hook for trigger of custom event (if there is one)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def triggerEvent(self, *args, **kwargs):
  l = []
  name = args[0]
  
  # Always call local trigger for global triggers.
  if name.startswith('*.'):
    triggerEvent(self,name[2:]+'Local')
  
  # Pass custom event to zope ObjectModifiedEvent event.
  notify(ObjectModifiedEvent(self, name))
  
  metaObj = self.getMetaobj( self.meta_id)
  if metaObj:
    # Process meta-object-triggers.
    context = self
    v = context.evalMetaobjAttr(name,kwargs)
    writeLog( context, "[triggerEvent]: %s=%s"%(name,str(v)))
    if v is not None:
      l.append(v)
    # Process zope-triggers.
    context = self
    ids = []
    while context is not None:
      for id in context.getHome().objectIds():
        if id not in ids and id.find( name) == 0:
          v = getattr(self,id)(context=context,REQUEST=self.REQUEST)
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.unescape:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def unescape(s):
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
def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
  """
  Send Http-Request and return Response-Body.
  @param url: Remote-URL
  @type url: C{string}
  @param method: Method
  @type method: C{string}, values are GET or POST
  @param auth: Authentication
  @type auth: C{string}
  @param parse_qs: Parse Query-String
  @type parse_qs: C{int}, values are 0 or 1
  @param timeout: Time-Out [s]
  @type timeout: C{int}, values in seconds
  @param headers: Request-Headers
  @type headers: C{dict}
  @return: Response-Body
  @rtype: C{string}
  """
  # Parse URL.
  import urlparse
  u = urlparse.urlparse(url)
  writeLog( self, "[http_import.%s]: %s"%(method,str(u)))
  scheme = u[0]
  netloc = u[1]
  path = u[2]
  query = u[4]
  
  # Get Proxy.
  useproxy = True
  noproxy = ['localhost','127.0.0.1']+filter(lambda x: len(x)>0,map(lambda x: x.strip(),self.getConfProperty('%s.noproxy'%scheme.upper(),'').split(',')))
  for noproxyurl in noproxy:
    if fnmatch.fnmatch(netloc,noproxyurl):
      useproxy = False
      break
  if useproxy:
    proxy = self.getConfProperty('%s.proxy'%scheme.upper(),'')
    if len(proxy) > 0:
      path = '%s://%s%s'%(scheme,netloc,path) 
      netloc = proxy

  # Open HTTP connection.
  import httplib
  writeLog( self, "[http_import.%s]: %sConnection(%s) -> %s"%(method,scheme,netloc,path))
  if scheme == 'http':
    conn = httplib.HTTPConnection(netloc,timeout=timeout)
  else:
    conn = httplib.HTTPSConnection(netloc,timeout=timeout)
  
  # Set request-headers.
  if auth is not None:
    import base64
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
    writeLog( self, "[http_import.error]: %s"%error)
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
        writeError(self,'[http_import]: can\'t parse_qs')
    return data
  else:
    result = '['+str(reply_code)+']: '+str(message)
    writeLog( self, "[http_import.result]: %s"%result)
    return result


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.get_size:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_size(v):
  size = 0
  if v is not None:
    if type(v) in StringTypes:
      size = size + len(v)
    elif type(v) is list:
      size = sum( map( lambda x: get_size(x), v))
    elif type(v) is dict:
      size = sum( map( lambda x: get_size(x) + get_size(v[x]), v.keys()))
    elif type(v) is int or type(v) is float:
      size = size + 4
    elif hasattr(v,'get_real_size') and callable(getattr(v,'get_real_size')):
      try:
        size = size + v.get_real_size()
      except:
        pass
    elif hasattr(v,'get_size') and callable(getattr(v,'get_size')):
      try:
        size = size + v.get_size()
      except:
        pass
  return size


"""
################################################################################
#
#  Logging
#
################################################################################
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.getLog:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def getLog(self):
  request = self.REQUEST
  if request.has_key('ZMSLOG'):
    zms_log = request.get('ZMSLOG')
  else:
    zms_log = getattr(self,'zms_log',None)
    if zms_log is None:
      zms_log = getattr(self.getPortalMaster(),'zms_log',None)
    request.set('ZMSLOG',zms_log)
  return zms_log

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.debug:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def debug(self):
  b = False
  try:
    zms_log = getLog(self)
    severity = logging.DEBUG
    b = zms_log.hasSeverity(severity)
  except:
    pass
  return b

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.writeLog:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def writeLog(self, info):
  try:
    zms_log = self.zms_log
    severity = logging.DEBUG
    if zms_log.hasSeverity(severity):
      info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
      zms_log.LOG( severity, info)
  except:
    pass
  return info

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.writeBlock:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def writeBlock(self, info):
  try:
    zms_log = getLog(self)
    severity = logging.INFO
    if zms_log.hasSeverity(severity):
      info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
      zms_log.LOG( severity, info)
  except:
    pass
  return info

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
standard.writeError:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def writeError(self, info):
  t,v='?','?'
  try:
    t,v,tb = sys.exc_info()
    v = str(v)
    # Strip HTML tags from the error value
    for pattern in [r"<[^<>]*>", r"&[A-Za-z]+;"]:
      v = re_sub(self, pattern,' ', v)
    if info: 
      info += '\n'
    severity = logging.ERROR
    info += ''.join(format_exception(t, v, tb))
    info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
    zms_log = getLog(self)
    if zms_log.hasSeverity(severity):
      zms_log.LOG( severity, info)
    t = t.__name__.upper()
  except:
    pass
  return '%s: %s <!-- %s -->'%(t,v,info)


"""
################################################################################
#
#( Regular Expressions
#
################################################################################
"""

def re_sub( pattern, replacement, subject, ignorecase=False):
  """
  Performs a search-and-replace across subject, replacing all matches of 
  regex in subject with replacement. The result is returned by the sub() 
  function. The subject string you pass is not modified.
  @rtype: C{string}
  """
  if ignorecase:
    return re.compile( pattern, re.IGNORECASE).sub( replacement, subject)
  else:
    return re.compile( pattern).sub( replacement, subject)

def re_search( pattern, subject, ignorecase=False):
  """
  Scan through string looking for a location where the regular expression 
  pattern produces a match, and return a corresponding MatchObject 
  instance. Return None if no position in the string matches the pattern; 
  note that this is different from finding a zero-length match at some
  point in the string.
  @rtype: C{string}
  """
  if ignorecase:
    s = re.compile( pattern, re.IGNORECASE).split( subject)
  else:
    s = re.compile( pattern).split( subject)
  return map( lambda x: s[x*2+1], range(len(s)/2))

def re_findall( pattern, text, ignorecase=False):
  """
  Return all non-overlapping matches of pattern in string, as a list of strings. 
  The string is scanned left-to-right, and matches are returned in the order found. 
  If one or more groups are present in the pattern, return a list of groups; 
  this will be a list of tuples if the pattern has more than one group. 
  Empty matches are included in the result unless they touch the beginning of another match
  @rtype: C{string}
  """
  if ignorecase:
    r = re.compile( pattern, re.IGNORECASE)
  else:
    r = re.compile( pattern)
  return r.findall(text)

#)


"""
################################################################################
#
#{ DateTime
#
################################################################################
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Index  Field  Values  
0  year (for example, 1993) 
1  month range [1,12] 
2  day range [1,31] 
3  hour range [0,23] 
4  minute range [0,59] 
5  second range [0,61]; see (1) in strftime() description 
6  weekday range [0,6], Monday is 0 
7  Julian day range [1,366] 
8  daylight savings flag 0, 1 or -1; see below 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

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
  Parse date in locale-format
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
