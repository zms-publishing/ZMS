################################################################################
# _globals.py
#
# $Id: _globals.py,v 1.12 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.12 $
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
from httplib import HTTP
from types import StringTypes
from traceback import format_exception
import cgi
import copy
import logging
import operator
import os
import re
import sys
import time
import urllib


""" Globals. """

# Constants.
# ----------

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

# German umlaute.
umlautMapping = {
	unicode('\xe4','latin-1').encode('utf-8'):'ae',
	unicode('\xf6','latin-1').encode('utf-8'):'oe',
	unicode('\xfc','latin-1').encode('utf-8'):'ue',
	unicode('\xc4','latin-1').encode('utf-8'):'Ae',
	unicode('\xd6','latin-1').encode('utf-8'):'Oe',
	unicode('\xdc','latin-1').encode('utf-8'):'Ue',
	unicode('\xdf','latin-1').encode('utf-8'):'ss',
}


# ------------------------------------------------------------------------------
#  _globals.umlaut_quote:
# ------------------------------------------------------------------------------
def umlaut_quote(s, mapping={}):
  map( lambda x: operator.setitem( mapping, x, umlautMapping[x]), umlautMapping.keys())
  for key in mapping.keys():
    s = s.replace(key,mapping[key])
  return s


# ------------------------------------------------------------------------------
#  _globals.datatype_key:
# ------------------------------------------------------------------------------
def datatype_key(datatype):
  for dtIndex in range(len(dtMapping)):
    if dtMapping[dtIndex][0] == datatype:
      return dtIndex
  else:
    return DT_UNKNOWN


# ------------------------------------------------------------------------------
#  _globals.format_sort_id:
# ------------------------------------------------------------------------------
def format_sort_id(i_sort_id):
  sort_id = '0000%i'%i_sort_id
  sort_id = 's' + sort_id[-4:]
  return sort_id


# ------------------------------------------------------------------------------
#  _globals.html_quote:
# ------------------------------------------------------------------------------
def html_quote(v, name='(Unknown name)', md={}):
  return cgi.escape(str(v), 1)


# ------------------------------------------------------------------------------
#  _globals.bin2hex:
# ------------------------------------------------------------------------------
def bin2hex(m):
  return ''.join(map(lambda x: hex(ord(x)/16)[-1]+hex(ord(x)%16)[-1],m))


# ------------------------------------------------------------------------------
#  _globals.hex2bin:
# ------------------------------------------------------------------------------
def hex2bin(m):
  return ''.join(map(lambda x: chr(16*int('0x%s'%m[x*2],0)+int('0x%s'%m[x*2+1],0)),range(len(m)/2)))


# ------------------------------------------------------------------------------
#  _globals.unencode:
#
#  Unencodes given parameter.
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
#  _globals.id_quote:
# ------------------------------------------------------------------------------
def id_quote(s, mapping={
		'\x20':'_',
		'-':'_',
		'/':'_',
}):
  s = umlaut_quote(s,mapping)
  valid = map( lambda x: ord(x[0]), mapping.values()) + [ord('_')] + range(ord('0'),ord('9')+1) + range(ord('A'),ord('Z')+1) + range(ord('a'),ord('z')+1)
  s = filter( lambda x: ord(x) in valid, s)
  while len(s) > 0 and s[0] == '_':
    s = s[1:]
  s = s.lower()
  return s


# ------------------------------------------------------------------------------
#  _globals.strip_int:
#
#  Strips numeric part from string.
# ------------------------------------------------------------------------------
def strip_int(s):
  i = 0
  while i < len(s) and ord(s[i]) in range(ord('0'),ord('9')+1):
    i = i + 1
  return i


# ------------------------------------------------------------------------------
#  _globals.id_prefix:
#
#  Strips non-numeric part from string.
# ------------------------------------------------------------------------------
def id_prefix(s):
  i = len(s)
  while i > 0 and ord(s[i-1]) in range(ord('0'),ord('9')+1):
    i = i - 1
  return s[:i]


# ------------------------------------------------------------------------------
#  _globals.map_key_vals:
#
#  Maps list of keys and list of values to new dictionary.
# ------------------------------------------------------------------------------
def map_key_vals(keys, vals):
  d = {}
  map(operator.setitem, [d]*len(keys), keys, vals)
  return d


# ------------------------------------------------------------------------------
#  _globals.objectTree:
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
#  _globals.dt_html:
#
#  Process dtml.
# ------------------------------------------------------------------------------
def dt_html(self, value, REQUEST): 
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
  value = re.sub( '</dtml-var>', '', value)
  dtml = DocumentTemplate.DT_HTML.HTML(value)
  value = dtml( self, REQUEST)
  return value


# ------------------------------------------------------------------------------
#  _globals.dt_parse:
#
#  Parse and validate dtml.
# ------------------------------------------------------------------------------
def dt_parse(self, value):
  message = ''
  try:
    import DocumentTemplate.DT_HTML
    dtml = DocumentTemplate.DT_HTML.HTML(value)
    dtml.cook()
  except:
    message += sys.exc_value
  return message


# ------------------------------------------------------------------------------
#  _globals.form_quote
#
#  Remove <form>-tags for Management Interface.
# ------------------------------------------------------------------------------
def form_quote(text, REQUEST):
  rtn = text
  if isManagementInterface(REQUEST):
    rtn = re.sub( '<form(.*?)>', '<noform\\1>', rtn)
    rtn = re.sub( ' name="lang"', ' name="_lang"', rtn)
    rtn = re.sub( '</form(.*?)>', '</noform\\1>', rtn)
  return rtn

  
# ------------------------------------------------------------------------------
#  _globals.qs_append:
#
#  Append to Query-String.
# ------------------------------------------------------------------------------
def qs_append(qs, p, v):
  if len(qs) == 0:
    qs += '?'
  else:
    qs += '&amp;'
  qs += p + '=' + urllib.quote(v)
  return qs


# ------------------------------------------------------------------------------
#  _globals.nvl:
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
#  _globals.isManagementInterface
#
#  Returns true if current context is management-interface, false else.
# ------------------------------------------------------------------------------
def isManagementInterface(REQUEST):
  return REQUEST is not None and \
         REQUEST.get('URL','').find('/manage') >= 0 and \
         isPreviewRequest(REQUEST)
     

# ------------------------------------------------------------------------------
#  _globals.isPreviewRequest:
#
#  Returns true if current context is preview-request, false else.
# ------------------------------------------------------------------------------
def isPreviewRequest(REQUEST):
  return REQUEST is not None and \
         REQUEST.get('preview','') == 'preview' and \
         REQUEST.get('live','') == ''


# ------------------------------------------------------------------------------
#  _globals.getPageWithElements:
# ------------------------------------------------------------------------------
def getPageWithElements(self, REQUEST):
  obs = self.getChildNodes(REQUEST)
  for ob in obs:
    if ob.isVisible(REQUEST):
      if ob.isPageElement() or ob.getObjProperty('getPageWithElements',REQUEST) in ['1','True',1,True]:
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

# ------------------------------------------------------------------------------
#  _globals.unescape:
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
#  _globals.authtobasic:
#
#  Basic Authentication
# ------------------------------------------------------------------------------
def authtobasic(auth, h): 
 """Converts basic auth data into an HTTP header."""
 import base64
 if auth is not None:
   userpass = auth['username']+':'+auth['password']
   userpass = base64.encodestring(urllib.unquote(userpass)).strip()
   h.putheader('Authorization', 'Basic '+userpass)


# ------------------------------------------------------------------------------
#  _globals.http_import:
# ------------------------------------------------------------------------------
def http_import(self, url, method='GET', auth=None, parse_qs=0):

  # Remove HTTP-Prefix.
  http_prefix = 'http://'
  if url.startswith( http_prefix):
    url = url[ len( http_prefix):]

  # Get Query-String.
  qs = ''
  i = url.find('?')
  if i > 0:
    qs = url[i+1:]
    url = url[:i]
  
  # Get Host and Port.
  i = url.find('/')
  if i > 0:
    host = url[:i]
    url = url[i:]
  else:
    host = url
    url = '/'
  i = host.find(':',max(0,host.find('@')))
  port = 80
  if i > 0:
    port = int(host[i+1:])
    host = host[:i]
  
  # Open HTTP connection.
  writeBlock( self, "[http_import.%s]: %s:%i%s?%s"%(method,host,port,url,qs))
  req = HTTP(host,port)
  
  # Set request-headers.
  if method.upper() == 'GET':
    if len( qs) > 0:
      qs = '?' + qs
    req.putrequest( method, url + qs)
    req.putheader('Host', host)
    authtobasic(auth,req)
    req.putheader('Accept', '*/*')
    req.endheaders()
  elif method.upper() == 'POST':
    req.putrequest(method,url)
    req.putheader('Host', host)
    authtobasic(auth,req)
    req.putheader('Accept', '*/*')
    req.putheader('Content-type', 'application/x-www-form-urlencoded')
    req.putheader('Content-length', '%d' % len(qs))
    req.endheaders()
    # Send query string
    req.send(qs)
  
  # Send request.
  reply_code, message, headers = req.getreply()
  
  #### get parameter from content
  if reply_code == 404 or reply_code >= 500:
    error = "[%i]: %s at %s [%s]"%(reply_code,message,url,method)
    writeBlock( self, "[http_import.error]: %s"%error)
    raise error
  elif reply_code==200:
    # get content
    f = req.getfile()
    content = f.read()
    f.close()
    rtn = None
    if parse_qs:
      try:
        # return dictionary of value lists
        rtn = cgi.parse_qs(content, keep_blank_values=1, strict_parsing=1)
      except:
        # return string
        rtn = content
    else:
      # return string
      rtn = content
      if port != 80:
        rtn = rtn.replace( '%s%s/'%(http_prefix,host), '%s%s:%i/'%(http_prefix,host,port))
    return rtn
  else:
    result = '['+str(reply_code)+']: '+str(message)
    writeBlock( self, "[http_import.result]: %s"%result)
    return result


# ------------------------------------------------------------------------------
#  _globals.get_size:
# ------------------------------------------------------------------------------
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
#  Traces
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _globals.debug:
# ------------------------------------------------------------------------------
def debug(self):
  has_zms_log = False
  try:
    zms_log = getattr( self, 'zms_log', None)
    has_zms_log = \
      zms_log is not None and \
      zms_log.meta_type == 'ZMS Log' and \
      'DEBUG' in zms_log.logged_entries
  except:
    pass
  return has_zms_log

# ------------------------------------------------------------------------------
#  _globals.writeLog:
# ------------------------------------------------------------------------------
def writeLog(self, info):
  try:
    zms_log = getattr( self, 'zms_log', None)
    if 'DEBUG' in zms_log.logged_entries:
      severity = logging.DEBUG
      info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
      zms_log.LOG( severity, info)
  except:
    pass

# ------------------------------------------------------------------------------
#  _globals.writeBlock:
# ------------------------------------------------------------------------------
def writeBlock(self, info):
  try:
    zms_log = getattr( self, 'zms_log', None)
    if 'INFO' in zms_log.logged_entries:
      severity = logging.INFO
      info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
      zms_log.LOG( severity, info)
  except:
    pass

# ------------------------------------------------------------------------------
#  _globals.writeError:
# ------------------------------------------------------------------------------
def writeError(self, etc=''):
  info = '?'
  try:
    t,v,tb = sys.exc_info()
    v = str(v)
    # Strip HTML tags from the error value
    import re
    remove = [r"<[^<>]*>", r"&[A-Za-z]+;"]
    for pat in remove:
      v = re.sub(pat,' ', v)
    if etc: etc += '\n'
    severity = logging.ERROR
    info = etc+''.join(format_exception(t, v, tb))
    info = "[%s@%s]"%(self.meta_id,self.absolute_url()[len(self.REQUEST['SERVER_URL']):]) + info
    zms_log = getattr( self, 'zms_log', None)
    if 'ERROR' in zms_log.logged_entries:
      zms_log.LOG( severity, info)
  except:
    pass
  return info


"""
################################################################################
#
#  DateTime
#
################################################################################
"""

# ==============================================================================
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
# ==============================================================================

# ------------------------------------------------------------------------------
#  _globals.getDateTime:
#
#  Bei Python 2.2 ist der Typ der Objekte des Moduls "time" nicht
#  mehr "tuple", sondern "time.struct_time". Es verhaelt sich aber weiterhin
#  abwaertskompatibel zu einem tuple.
#  This is no problem for Zope since Zope uses its own, more flexible, type
#  DateTime. Nevertheless ZMS relies on the datatype "tuple" as DateTime has 
#  the limitation that no date prior to 1970-01-01 can be used!
# ------------------------------------------------------------------------------
def getDateTime(t):
  if t is not None:
    try:
      if type(t) is tuple:
        t = time.mktime( t)
      if type(t) is not time.struct_time:
        t = time.localtime( t)
    except:
      pass
  return t

# ------------------------------------------------------------------------------
#  _globals.stripDateTime:
#
#  Strips time portion from date-time and returns date.
# ------------------------------------------------------------------------------
def stripDateTime(t):
  d = None
  if t is not None:
    t = getDateTime(t)
    d = (t[0],t[1],t[2],0,0,0,t[6],t[7],t[8])
  return d

# ------------------------------------------------------------------------------
#  _globals.daysBetween:
# ------------------------------------------------------------------------------
def daysBetween(t0, t1):
  t0 = time.mktime(stripDateTime(getDateTime(t0)))
  t1 = time.mktime(stripDateTime(getDateTime(t1)))
  d = 24.0*60.0*60.0
  return int((t1-t0)/d)

# ------------------------------------------------------------------------------
#  _globals.compareDate:
#
#  Compares two dates and returns result.
#   +1: t0 < t1
#    0: t0 == t1
#   -1: t0 > t1
# ------------------------------------------------------------------------------
def compareDate(t0, t1, accuracy_time=1):
  YEAR = 0
  MONTH = 1
  DAY = 2
  HOURS = 3
  MINUTES = 4
  SECONDS = 5
  t0 = getDateTime(t0)
  y0 = t0[YEAR]
  m0 = t0[MONTH]
  d0 = t0[DAY]
  H0 = t0[HOURS]
  M0 = t0[MINUTES]
  S0 = t0[SECONDS]
  t1 = getDateTime(t1)
  y1 = t1[YEAR]
  m1 = t1[MONTH]
  d1 = t1[DAY]
  H1 = t1[HOURS]
  M1 = t1[MINUTES]
  S1 = t1[SECONDS]
  if (y1 > y0) or \
     (y1 == y0 and m1 > m0) or \
     (y1 == y0 and m1 == m0 and d1 > d0) or \
     (accuracy_time == 1 and y1 == y0 and m1 == m0 and d1 == d0 and H1 > H0) or \
     (accuracy_time == 1 and y1 == y0 and m1 == m0 and d1 == d0 and H1 == H0 and M1 > M0) or \
     (accuracy_time == 1 and y1 == y0 and m1 == m0 and d1 == d0 and H1 == H0 and M1 == M0 and S1 > S0):
    return +1
  elif (accuracy_time == 0 and y1 == y0 and m1 == m0 and d1 == d0) or \
       (accuracy_time == 1 and y1 == y0 and m1 == m0 and d1 == d0 and H1 == H0 and M1 == M0 and S1 == S0):
    return 0
  else:
    return -1

# ------------------------------------------------------------------------------
#  _globals.parseLangFmtDate:
# ------------------------------------------------------------------------------
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
              raise "Exception"
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
            raise 'Exception'
          value = getDateTime((dctTime['Y'],dctTime['m'],dctTime['d'],dctTime['H'],dctTime['M'],dctTime['S'],0,1,-1))
      except:
        pass
  return value


################################################################################
################################################################################
###
###   class MyClass:
###
################################################################################
################################################################################
class MyClass:

  # ----------------------------------------------------------------------------
  #  MyClass.keys:
  # ----------------------------------------------------------------------------
  def keys(self):
    return self.__dict__.keys()


################################################################################
################################################################################
###
###   class MySectionizer
###
################################################################################
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

    def getLevel(self):
      return len(self.sections)

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
################################################################################
###
###   class MyStack
###
################################################################################
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
