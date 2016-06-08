#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# _globals.py
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

# Imports.
from App.Common import package_home
from DateTime.DateTime import DateTime
from types import StringTypes
from traceback import format_exception
from zope.contenttype import guess_content_type
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

""" Globals. """

# Datatypes.
DT_UNKNOWN = 0
DT_BOOLEAN = 1
DT_DATE = 2
DT_DATETIME = 3
DT_DICT = 4
DT_FILE = 5
DT_FLOAT = 6
DT_IMAGE = 7
DT_INT = 8
DT_LIST = 9
DT_PASSWORD = 10
DT_STRING = 11
DT_TEXT = 12
DT_TIME = 13
DT_URL = 14
DT_ID = 15
DT_XML = 16
DT_AMOUNT = 17
DT_COLOR = 18
DT_TEXTS = [ DT_STRING, DT_TEXT ]
DT_STRINGS = [ DT_STRING, DT_TEXT, DT_URL, DT_PASSWORD, DT_XML, DT_COLOR ]
DT_BLOBS = [ DT_IMAGE, DT_FILE ]
DT_INTS = [ DT_INT, DT_BOOLEAN ]
DT_NUMBERS = [ DT_INT, DT_FLOAT, DT_AMOUNT ]
DT_DATETIMES = [ DT_DATE, DT_TIME, DT_DATETIME ]

dtMapping = [
  [ 'unknown',''],
  [ 'boolean',0],
  [ 'date',None],
  [ 'datetime',None],
  [ 'dictionary',{}],
  [ 'file',None],
  [ 'float',0.0],
  [ 'image',None],
  [ 'int',0],
  [ 'list',[]],
  [ 'password',''],
  [ 'string',''],
  [ 'text',''],
  [ 'time',None],
  [ 'url',''],
  [ 'identifier',''],
  [ 'xml',''],
  [ 'amount',0.0],
  [ 'color',''],
]

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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.umlaut_quote:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def umlaut_quote(self, s, mapping={}):
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.datatype_key:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def datatype_key(datatype):
  for dtIndex in range(len(dtMapping)):
    if dtMapping[dtIndex][0] == datatype:
      return dtIndex
  else:
    return DT_UNKNOWN


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.url_encode:

All unsafe characters must always be encoded within a URL.
@see: http://www.ietf.org/rfc/rfc1738.txt
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def url_encode(url):
  for ch in ['[',']',' ','(',')']:
    url = url.replace(ch,'%'+bin2hex(ch).upper())
  return url

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.guess_contenttype:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def guess_contenttype(filename, data):
  mt, enc  = guess_content_type( filename, data)
  return mt, enc

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.format_sort_id:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def format_sort_id(i_sort_id):
  sort_id = '0000%i'%i_sort_id
  sort_id = 's' + sort_id[-4:]
  return sort_id


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.html_quote:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def html_quote(v, name='(Unknown name)', md={}):
  return cgi.escape(str(v), 1)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.bin2hex:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def bin2hex(m):
  return ''.join(map(lambda x: hex(ord(x)/16)[-1]+hex(ord(x)%16)[-1],m))


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.hex2bin:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def hex2bin(m):
  return ''.join(map(lambda x: chr(16*int('0x%s'%m[x*2],0)+int('0x%s'%m[x*2+1],0)),range(len(m)/2)))


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.unencode:

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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.strip_int:

Strips numeric part from string.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def strip_int(s):
  i = 0
  while i < len(s) and ord(s[i]) in range(ord('0'),ord('9')+1):
    i = i + 1
  return i


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.id_prefix:

Strips non-numeric part from string.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def id_prefix(s):
  i = len(s)
  while i > 0 and ord(s[i-1]) in range(ord('0'),ord('9')+1):
    i = i - 1
  return s[:i]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.map_key_vals:

Maps list of keys and list of values to new dictionary.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def map_key_vals(keys, vals):
  d = {}
  map(operator.setitem, [d]*len(keys), keys, vals)
  return d


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.objectTree:
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
_globals.form_quote

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
_globals.qs_append:

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
_globals.nvl:
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
_globals.get_session:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_session(self):
  return getattr(self, 'session_data_manager', None) and \
    self.session_data_manager.getSessionData(create=0)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.triggerEvent:

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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.isManagementInterface

Returns true if current context is management-interface, false else.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def isManagementInterface(REQUEST):
  return REQUEST is not None and \
         REQUEST.get('URL','').find('/manage') >= 0 and \
         isPreviewRequest(REQUEST)
     

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.isPreviewRequest:

Returns true if current context is preview-request, false else.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def isPreviewRequest(REQUEST):
  return REQUEST is not None and \
         REQUEST.get('preview','') == 'preview'


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.getPageWithElements:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def getPageWithElements(self, REQUEST):
  if self.isPageContainer():
    obs = self.getChildNodes(REQUEST)
    for ob in obs:
      if ob.isVisible(REQUEST):
        if ob.isPageElement():
          return self
        elif ob.isPage():
          return getPageWithElements(ob,REQUEST)
  return self



"""
################################################################################
#
#  Http
#
################################################################################
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.unescape:
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.http_import:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
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
  if method == 'GET':
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
_globals.get_size:
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
_globals.getLog:
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
_globals.debug:
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
_globals.writeLog:
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
_globals.writeBlock:
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
_globals.writeError:
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.re_sub:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def re_sub( self, pattern, replacement, subject, ignorecase=False):
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.re_search:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def re_search( self, pattern, subject, ignorecase=False):
  """
  Scan through string looking for a location where the regular expression 
  pattern produces a match, and return a corresponding MatchObject 
  instance. Return None if no position in the string matches the pattern; 
  note that this is different from finding a zero-length match at some
  point in the string.
  """
  if ignorecase:
    s = re.compile( pattern, re.IGNORECASE).split( subject)
  else:
    s = re.compile( pattern).split( subject)
  return map( lambda x: s[x*2+1], range(len(s)/2))

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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.getDateTime:

Bei Python 2.2 ist der Typ der Objekte des Moduls "time" nicht
mehr "tuple", sondern "time.struct_time". Es verhaelt sich aber weiterhin
abwaertskompatibel zu einem tuple.
This is no problem for Zope since Zope uses its own, more flexible, type
DateTime. Nevertheless ZMS relies on the datatype "tuple" as DateTime has 
the limitation that no date prior to 1970-01-01 can be used!
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def getDateTime(t):
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.stripDateTime:

Strips time portion from date-time and returns date.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def stripDateTime(t):
  d = None
  if t is not None:
    t = getDateTime(t)
    d = (t[0],t[1],t[2],0,0,0,t[6],t[7],t[8])
  return d

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.daysBetween:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def daysBetween(t0, t1):
  t0 = time.mktime(stripDateTime(getDateTime(t0)))
  t1 = time.mktime(stripDateTime(getDateTime(t1)))
  d = 24.0*60.0*60.0
  return int((t1-t0)/d)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.compareDate:

Compares two dates and returns result.
 +1: t0 < t1
  0: t0 == t1
 -1: t0 > t1
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def compareDate(t0, t1):
  mt0 = time.mktime(stripDateTime(getDateTime(t0)))
  mt1 = time.mktime(stripDateTime(getDateTime(t1)))
  if mt1 > mt0:
    return +1
  elif mt1 < mt0:
    return -1
  else:
    return 0

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
_globals.parseLangFmtDate:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def parseLangFmtDate(s):
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

  def import_instance_home(self, this, url):
    path = this.Control_Panel.getINSTANCE_HOME()+'/etc/zms/'+url
    mode = 'b'
    if os.path.exists(path):
      f = None
      try:
        f = open( path, 'r'+mode)
        data = f.read()
      finally:
        if f is not None:
          f.close()
      return data
    return None

  def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
    return http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers)

  def re_sub( self, pattern, replacement, subject, ignorecase=False):
    return re_sub( self, pattern, replacement, subject, ignorecase=False)

  def re_search( self, pattern, subject, ignorecase=False):
    return re_search( self, pattern, subject, ignorecase)


################################################################################
# Define MyClass.
################################################################################
class MyClass:

  # ----------------------------------------------------------------------------
  #  MyClass.keys:
  # ----------------------------------------------------------------------------
  def keys(self):
    return self.__dict__.keys()


################################################################################
# Define MySectionizer.
################################################################################
class MySectionizer:

    # --------------------------------------------------------------------------
    #  MySectionizer.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self, levelnfc='0'):
      self.levelnfc = levelnfc
      self.sections = []

    # --------------------------------------------------------------------------
    #  MySectionizer.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
      s = ''
      for i in range(len(self.sections)):
        if self.levelnfc == '0':
          s += str(self.sections[i]) + '.'
        elif self.levelnfc == '1':
          s += chr(self.sections[i] - 1 + ord('A')) + '.'
        elif self.levelnfc == '2':
          s += chr(self.sections[i] - 1 + ord('a')) + '.'
      return s

    # --------------------------------------------------------------------------
    #  MySectionizer.clone:
    #
    #  Creates and returns a copy of this object.
    # --------------------------------------------------------------------------
    def clone(self):
      ob = MySectionizer(self.levelnfc)
      ob.sections = copy.deepcopy(self.sections)
      return ob

    # --------------------------------------------------------------------------
    #  MySectionizer.getLevel:
    # --------------------------------------------------------------------------
    def getLevel(self):
      return len(self.sections)

    # --------------------------------------------------------------------------
    #  MySectionizer.processLevel:
    # --------------------------------------------------------------------------
    def processLevel(self, level):
      # Increase section counter on this level.
      if level > 0:
        if level == len(self.sections):
          self.sections[level-1] = self.sections[level-1] + 1
        elif level > len(self.sections):
          for i in range(len(self.sections),level):
            self.sections.append(1)
        elif level < len(self.sections):
          for i in range(level,len(self.sections)):
            del self.sections[len(self.sections)-1]
          self.sections[level-1] = self.sections[level-1] + 1


################################################################################
# Define MyStack.
################################################################################
class MyStack:

    # --------------------------------------------------------------------------
    #  MyStack.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self):
      self.clear()

    # --------------------------------------------------------------------------
    #  MyStack.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
      s = ''
      for el in self._stack:
        s += str(el) + ';'
      return s[:-1]

    def size(self):
      return len(self._stack)

    def clear(self):
      self._stack = []

    def push(self, x):
      self._stack.append(x)

    def pop(self):
      if len(self._stack) > 0:
        return self._stack.pop()
      else:
        return None

    def get_all(self):
      return self._stack

    def get(self, i=0):
      if len(self._stack) > 0 and abs(i) < len(self._stack):
        if i < 0:
          return self._stack[len(self._stack)+i-1]
        else:
          return self._stack[i]
      else:
        return None

    def top(self):
      if len(self._stack) > 0:
        return self._stack[len(self._stack)-1]
      else:
        return None

################################################################################
