################################################################################
# ZMSGlobals.py
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
from AccessControl import AuthEncoding
from App.Common import package_home
from App.special_dtml import HTMLFile
from DateTime.DateTime import DateTime
from cStringIO import StringIO
from types import StringTypes
from binascii import b2a_base64, a2b_base64
import base64
import copy
import fnmatch
import operator
import os
import re
import tempfile
import time
import urllib
import zope.interface
# Product Imports.
import _blobfields
import _fileutil
import _filtermanager
import _globals
import _mimetypes
import _pilutil
import _xmllib

__all__= ['ZMSGlobals']

# ------------------------------------------------------------------------------
#  MD5:
# ------------------------------------------------------------------------------
try: # Python >= 2.5
  import hashlib

  class MD5DigestScheme:

    def encrypt(self, pw):
      enc = hashlib.md5(pw)
      enc = enc.hexdigest()
      return enc

    def validate(self, reference, attempt):
      compare = self.encrypt(attempt)[:-1]
      return (compare == reference)

except: # Python < 2.5
  import md5

  class MD5DigestScheme:

    def encrypt(self, pw):
      enc = md5.new(pw)
      enc = enc.hexdigest()
      return enc

    def validate(self, reference, attempt):
      compare = self.encrypt(attempt)[:-1]
      return (compare == reference)

AuthEncoding.registerScheme('MD5', MD5DigestScheme())


# ------------------------------------------------------------------------------
#  sort_item:
# ------------------------------------------------------------------------------
def sort_item( i):
  if type( i) is str:
    mapping = _globals.umlautMapping
    for key in mapping.keys():
      i = i.replace(key,mapping[key])
  return i


################################################################################
################################################################################
###
###   class ZMSGlobals:
###
################################################################################
################################################################################
class ZMSGlobals:
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

    # --------------------------------------------------------------------------
    #  Meta-Type Selectors.
    # --------------------------------------------------------------------------
    PAGES = 0         #: virtual meta_type for all Pages (Containers)
    PAGEELEMENTS = 1  #: virtual meta_type for all Page-Elements
    NOREF = 4         #: virtual meta_type-flag for resolving meta-type of ZMSLinkElement-target-object.
    NORESOLVEREF = 5  #: virtual meta_type-flag for not resolving meta-type of ZMSLinkElement-target-object.

    # --------------------------------------------------------------------------
    #  ZMSGlobals.FileFromData:
    # --------------------------------------------------------------------------
    def FileFromData( self, data, filename='', content_type=None):
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
      return _blobfields.createBlobField( self, _globals.DT_FILE, file=file, mediadbStorable=False)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.ImageFromData:
    # --------------------------------------------------------------------------
    def ImageFromData( self, data, filename='', content_type=None):
      """
      Creates a new instance of an image from given data.
      @param data: Image-data (binary)
      @type data: C{string}
      @param filename: Filename
      @type filename: C{string}
      @return: New instance of image.
      @rtype: L{MyImage}
      """
      f = _blobfields.createBlobField( self, _globals.DT_IMAGE, file={'data':data,'filename':filename,'content_type':content_type}, mediadbStorable=False)
      f.aq_parent = self
      return f

    # --------------------------------------------------------------------------
    #  ZMSGlobals.import_zexp:
    # --------------------------------------------------------------------------
    def import_zexp(self, zexp, new_id, id_prefix, _sort_id=0):
      """
      Import zexp.
      @param zexp
      @type L{MyFile}
      """
      return _fileutil.import_zexp(self, zexp, new_id, id_prefix, _sort_id)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.nvl:
    # --------------------------------------------------------------------------
    def nvl(self, a1, a2, n=None):
      """
      Returns its first argument if it is not equal to third argument (None), 
      otherwise it returns its second argument.
      @param a1: 1st argument
      @type a1: C{any}
      @param a2: 2nd argument
      @type a2: C{any}
      @rtype: C{any}
      """
      return _globals.nvl( a1, a2, n)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.zope_interface_providedBy:
    # --------------------------------------------------------------------------
    def zope_interface_providedBy(self, clazz):
      """
      Returns list of interfaces provided by given clazz.
      @param clazz: Class
      @type v: C{any}
      @rtype: C{list}
      """
      return map(lambda x: str(x), list(zope.interface.providedBy(clazz)))


    # --------------------------------------------------------------------------
    #  ZMSGlobals.boolint:
    # --------------------------------------------------------------------------
    def boolint(self, v):
      """
      Returns int (0/1) for Boolean Type new in Python 2.3.
      @param v: Value
      @type v: C{bool}
      @return: New instance of file.
      @rtype: C{int}
      @deprecated: use int instead!
      """
      return int(v)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.dt_html:
    # --------------------------------------------------------------------------
    def dt_html(self, value, REQUEST):
      """
      Execute given DTML-snippet.
      @param value: DTML-snippet
      @type value: C{string}
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Result of the execution or None
      @rtype: C{any}
      """
      return _globals.dt_html(self,value,REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.encrypt_schemes:
    # --------------------------------------------------------------------------
    def encrypt_schemes(self):
      ids = []
      for id, prefix, scheme in AuthEncoding._schemes:
        ids.append( id)
      return ids

    # --------------------------------------------------------------------------
    #  ZMSGlobals.encrypt_password:
    # --------------------------------------------------------------------------
    def encrypt_password(self, pw, algorithm='md5', hex=False):
      """
      Encrypts given password.
      @param pw: Password
      @type pw: C{string}
      @param algorithm: Encryption-algorithm (md5, sha-1, etc.)
      @type algorithm: C{string}
      @param hex: Hexlify
      @type hex: C{bool}
      @return: Encrypted password
      @rtype: C{string}
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.encrypt_ordtype:
    # --------------------------------------------------------------------------
    def encrypt_ordtype(self, s):
      """
      Encrypts given string with entities by random algorithm.
      @param s: String
      @type s: C{string}
      @return: Encrypted string
      @rtype: C{string}
      """
      from binascii import hexlify
      new = ''
      for ch in s:
        whichCode=self.rand_int(2)
        if whichCode==0:
          new += ch
        elif whichCode==1:
          new += '&#%d;'%ord(ch)
        else:
          new += '&#x%s;'%str(hexlify(ch))
      return new

    # --------------------------------------------------------------------------
    #  ZMSGlobals.rand_int:
    # --------------------------------------------------------------------------
    def rand_int(self, n):
      """
      Random integer in given range.
      @param n: Range
      @type n: C{int}
      @return: Random integer
      @rtype: C{int}
      """
      from random import randint
      return randint(0,n)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_diff:
    # --------------------------------------------------------------------------
    def get_diff(self, v1, v2, datatype='string'):
      """
      Renders diff of two values in HTML.
      @param v1: Value #1
      @type v1: C{any}
      @param v2: Value #2
      @type v2: C{any}
      @param datatype: Datatype
      @type datatype: C{string}
      @return: Diff rendered in HTML.
      @rtype: C{string}
      """
      diff = ''
      if v1 == v2:
        return diff
      #-- Lists
      if (type( v1) is list and type( v2) is list) or datatype in [ 'list']:
        for c in range( min( len( v1), len( v2))):
          if v1[c] != v2[c]:
            d1 = self.get_diff(v1[c],v2[c])
            if d1:
              if len( diff) == 0:
                diff += '<table border="0" cellspacing="0" cellpadding="0">'
              diff += '<tr valign="top">'
              diff += '<td class="form-small">[%i]</td>'%(c+1)
              diff += '<td class="form-small">'+d1+'</td>'
              diff += '</tr>'
        if len( diff) > 0:
          diff += '</table>'
      #-- Dictionaries
      elif (type( v1) is dict and type( v2) is dict) or datatype in [ 'dictionary']:
        for k1 in v1.keys():
          if k1 in v2.keys():
            d1 = self.get_diff(v1[k1],v2[k1])
            if d1:
              if len( diff) == 0:
                diff += '<table border="0" cellspacing="0" cellpadding="0">'
              diff += '<tr valign="top">'
              diff += '<td class="form-small">%s=</td>'%k1
              diff += '<td class="form-small">'+d1+'</td>'
              diff += '</tr>'
        if len( diff) > 0:
          diff += '</table>'
      #-- Strings
      elif datatype in [ 'string', 'text']:
        # Untag strings.
        v1 = self.search_quote( v1, len( v1))
        v2 = self.search_quote( v2, len( v2))
        i = 0
        while i < min(len(v1),len(v2)) and v1[i]==v2[i]:
          i += 1
        if v1[:i].rfind('<') >= 0 and v1[:i].rfind('<') > v1[:i].rfind('>') and \
           v1[i:].find('>') >= 0 and v1[i:].find('>') < v1[i:].find('<'):
          i = v1[:i].rfind('<')
        j = 0
        while j < min(len(v1),len(v2))-i and v1[len(v1)-j-1]==v2[len(v2)-j-1]:
          j += 1
        if v1[i:len(v1)-j].find('<') >= 0 and v1[len(v1)-j:].find('<') > v1[len(v1)-j:].find('>') and \
           v2[i:-j].find('<') >= 0 and v2[-j:].find('<') > v2[-j:].find('>'):
          j -= (v2[-j:].find('>') + 1)
        if j == 0:
          red = v2[i:] 
        else:
          red = v2[i:-j]
        diff = v1[:i] + '<ins class="diff">' + v1[i:len(v1)-j] + '</ins><del class="diff">' + red + '</del>' + v1[len(v1)-j:]
      #-- Date/Time
      elif datatype in [ 'date', 'datetime', 'time']:
        v1 = self.getLangFmtDate( v1, 'eng', '%s_FMT'%datatype.upper())
        v2 = self.getLangFmtDate( v1, 'eng', '%s_FMT'%datatype.upper())
        diff = '<ins class="diff">' + v1 + '</ins><del class="diff">' + v2 + '</del>'
      #-- Numbers
      elif datatype in [ 'amount', 'float', 'int']:
        v1 = str( v1)
        v2 = str( v2)
        diff = '<ins class="diff">' + v1 + '</ins><del class="diff">' + v2 + '</del>'
      return diff

    # --------------------------------------------------------------------------
    #  ZMSGlobals.string_maxlen:
    # --------------------------------------------------------------------------
    def string_maxlen(self, s, maxlen=20, etc='...', encoding=None):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_quote:
    # --------------------------------------------------------------------------
    def url_quote(self, s):
      return urllib.quote(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.http_import:
    # --------------------------------------------------------------------------
    def http_import(self, url, method='GET', auth=None, parse_qs=0):
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
      @return: Response-Body
      @rtype: C{string}
      """
      return _globals.http_import( self, url, method, auth, parse_qs)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_append_params:
    # --------------------------------------------------------------------------
    def url_append_params(self, url, dict):
      anchor = ''
      i = url.rfind('#')
      if i > 0:
        anchor = url[i:]
        url = url[:i]
      if url.find( 'http://') < 0 and url.find( '../') < 0:
        try:
          if self.REQUEST.get('ZMS_REDIRECT_PARENT'):
            url = '../' + url
        except:
          pass
      targetdef = ''
      i = url.find('#')
      if i >= 0:
        targetdef = url[i:]
        url = url[:i]
      sep = '?'
      i = url.find(sep)
      if i >= 0:
        sep = '&amp;'
      for key in dict.keys():
        value = dict[key]
        qi = key + '=' + urllib.quote(str(value))
        if url.find( '?' + qi) < 0 and url.find( '&' + qi) < 0 and url.find( '&amp;' + qi) < 0:
          url += sep + qi
        sep = '&amp;'
      url += targetdef
      return url+anchor

    # --------------------------------------------------------------------------
    #  ZMSGlobals.url_inherit_params:
    # --------------------------------------------------------------------------
    def url_inherit_params(self, url, REQUEST, exclude=[]):
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
                url += '&amp;'
              if type(v) is int:
                url += urllib.quote(key+':int') + '=' + urllib.quote(str(v))
              elif type(v) is float:
                url += urllib.quote(key+':float') + '=' + urllib.quote(str(v))
              elif type(v) is list:
                c = 0
                for i in v:
                  if c > 0:
                    url += '&amp;'
                  url += urllib.quote(key+':list') + '=' + urllib.quote(str(i))
                  c = c + 1
              else:
                url += key + '=' + urllib.quote(str(v))
      return url+anchor

    # --------------------------------------------------------------------------
    #  ZMSGlobals.id_quote:
    # --------------------------------------------------------------------------
    def id_quote(self, s):
      """
      Converts given string to identifier (removes special-characters and 
      replaces German umlauts).
      @param s: String
      @type s: C{string}
      @return: Identifier
      @rtype: C{string}
      """
      return _globals.id_quote(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_id_prefix:
    # --------------------------------------------------------------------------
    def get_id_prefix(self, s):
      """
      Returns prefix from identifier (which is the non-numeric part at the 
      beginning).
      @param s: Identifier
      @type s: C{string}
      @return: Prefix
      @rtype: C{string}
      """
      return _globals.id_prefix(s)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.js_quote:
    # --------------------------------------------------------------------------
    def js_quote(self, text, charset=None):
      if type(text) is unicode:
        text= text.encode([charset, 'utf-8'][charset==None])
      text = text.replace("\r", "\\r").replace("\n", "\\n")
      text = text.replace('"', '\\"').replace("'", "\\'")
      return text

    # --------------------------------------------------------------------------
    #  ZMSGlobals.isPreviewRequest:
    # --------------------------------------------------------------------------
    def isPreviewRequest(self, REQUEST):
      return _globals.isPreviewRequest(REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getDataSizeStr: 
    #
    #  Display string for file-size.
    # --------------------------------------------------------------------------
    def getDataSizeStr(self, len):
      """
      Returns display string for file-size (KB).
      @param len: length (bytes)
      @type len: C{int}
      @rtype: C{string}
      """
      return _fileutil.getDataSizeStr(len)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getMimeTypeIconSrc:
    # --------------------------------------------------------------------------
    def getMimeTypeIconSrc(self, mt):
      """
      Returns the absolute-url of an icon representing the specified MIME-type.
      @param mt: MIME-Type (e.g. image/gif, text/xml).
      @type mt: C{string}
      @rtype: C{string}
      """
      return self.MISC_ZMS + _mimetypes.dctMimeType.get( mt, _mimetypes.content_unknown)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.nodes2html:
    # --------------------------------------------------------------------------
    def nodes2html( self, nodes):
      REQUEST = self.REQUEST
      breadcrumbs_ids = REQUEST['ZMS_THIS'].absolute_url().split( '/')
      html = []
      html.append( '<ul>')
      for node in nodes:
        css = node.meta_id
        if node.getParentNode() in nodes:
          css = css + ' parent'
        else:
          if node.id in breadcrumbs_ids: 
            css = css + ' active'
        html.append( '<li class="%s">'%( css))
        html.append( '<a href="%s" title="%s">%s</a>'%( node.getHref2IndexHtml(REQUEST), node.getTitle(REQUEST), node.getTitlealt(REQUEST)))
        html.append( '</li>')
      html.append( '</ul>')
      return ''.join( html)


    ############################################################################
    #
    #( Operators
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_gettype:
    # --------------------------------------------------------------------------
    def operator_gettype(self, v):
      """
      Returns python-type of given value.
      @param v: Value
      @type v: C{any}
      @rtype: C{type}
      """
      return type(v)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_setitem:
    # --------------------------------------------------------------------------
    def operator_setitem(self, a, b, c):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_getitem:
    # --------------------------------------------------------------------------
    def operator_getitem(self, a, b):
      """
      Retrieves value for key from python-dictionary.
      @param a: Dictionary
      @type a: C{dict}
      @param b: Key
      @type b: C{any}
      @rtype: C{any}
      """
      return operator.getitem(a,b)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_delitem:
    # --------------------------------------------------------------------------
    def operator_delitem(self, a, b):
      """
      Delete key from python-dictionary.
      @param a: Dictionary
      @type a: C{dict}
      @param b: Key
      @type b: C{any}
      """
      operator.delitem(a, b)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_setattr:
    # --------------------------------------------------------------------------
    def operator_setattr(self, a, b, c):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_getattr:
    # --------------------------------------------------------------------------
    def operator_getattr(self, a, b, c=None):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.operator_delattr:
    # --------------------------------------------------------------------------
    def operator_delattr(self, a, b):
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
    #( Logging
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.writeStdout:
    # --------------------------------------------------------------------------
    def writeStdout(self, info):
      """
      Write to standard-out (only allowed for development-purposes!).
      @param info: Object
      @type info: C{any}
      """
      print info


    # --------------------------------------------------------------------------
    #  ZMSGlobals.writeLog:
    # --------------------------------------------------------------------------
    def writeLog(self, info):
      """
      Log debug-information.
      @param info: Debug-information
      @type info: C{any}
      """
      if _globals.debug( self):
        _globals.writeLog( self, info)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.writeBlock:
    # --------------------------------------------------------------------------
    def writeBlock(self, info):
      """
      Log information.
      @param info: Information
      @type info: C{any}
      """
      _globals.writeBlock( self, info)

    #)


    ############################################################################
    #
    #( Regular Expressions
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.re_sub:
    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.re_search:
    # --------------------------------------------------------------------------
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


    ############################################################################
    #
    #( Styles / CSS
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.parse_stylesheet
    # --------------------------------------------------------------------------
    def parse_stylesheet(self):
      """
      Parses default-stylesheet and returns elements.
      @return: Elements
      @rtype: C{dict}
      """
      REQUEST = self.REQUEST
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'parse_stylesheet'
      try:
        value = self.fetchReqBuff( reqBuffId, REQUEST)
        return value
      except:
        
        stylesheet = self.getStylesheet()
        data = stylesheet.raw
        data = re.sub( '/\*(.*?)\*/', '', data)
        value = {}
        for elmnt in data.split('}'):
          i = elmnt.find('{')
          keys = elmnt[:i].strip()
          v = elmnt[i+1:].strip()
          for key in keys.split(','):
            key = key.strip()
            if len(key) > 0:
              value[key] = value.get(key,'') + v
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.get_colormap:
    # --------------------------------------------------------------------------
    def get_colormap(self):
      """
      Parses default-stylesheet and returns color-map.
      @return: Color-map
      @rtype: C{dict}
      """
      REQUEST = self.REQUEST
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'get_colormap'
      try:
        forced = True
        value = self.fetchReqBuff( reqBuffId, REQUEST, forced)
        return value
      except:
        stylesheet = self.parse_stylesheet()
        value = {}
        for key in stylesheet.keys():
          if key.find('.') == 0 and \
             key.find('Color') > 0 and \
             key.find('.cms') < 0 and \
             key.find('.zmi') < 0:
            for elmnt in stylesheet[key].split(';'):
              i = elmnt.find(':')
              if i > 0:
                elmntKey = elmnt[:i].strip().lower()
                elmntValue = elmnt[i+1:].strip().lower()
                if elmntKey == 'color' or elmntKey == 'background-color':
                  value[key[1:]] = elmntValue
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)

    #)


    ############################################################################
    #
    #( Mappings
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.intersection_list:
    # --------------------------------------------------------------------------
    def intersection_list(self, l1, l2):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.difference_list:
    # --------------------------------------------------------------------------
    def difference_list(self, l1, l2):
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.concat_list:
    # --------------------------------------------------------------------------
    def concat_list(self, l1, l2):
      """
      Concatinates two lists (l1 + l2).
      @param l1: List #1
      @type l1: list
      @param l2: List #2
      @type l2: list
      @returns: Concatinated list
      @rtype: C{list}
      """
      l1 = list(l1)
      l2 = list(l2)
      l = self.copy_list(l1)
      l.extend(filter(lambda x: x not in l1, l2))
      return l

    # --------------------------------------------------------------------------
    #  ZMSGlobals.dict_list:
    # --------------------------------------------------------------------------
    def dict_list(self, l):
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


    # --------------------------------------------------------------------------
    #  ZMSGlobals.distinct_list:
    # --------------------------------------------------------------------------
    def distinct_list(self, l, i):
      """
      Returns distinct values of given field from list.
      @param l: List
      @type l: C{list}
      @rtype: C{list}
      """
      k = []
      for x in l:
        if type(i) is str:
          v = x.get(i,None)
        else:
          v = x[i]
        if not v in k:
          k.append(v)
      return k
    # --------------------------------------------------------------------------
    #  ZMSGlobals.sort_list:
    #
    #  Sorts list by given field.
    # --------------------------------------------------------------------------
    def sort_list(self, l, qorder, qorderdir='asc', ignorecase=1):
      """
      Sorts list by given field.
      @return: Sorted list.
      @rtype: C{list}
      """
      if type(qorder) is str:
        sorted = map(lambda x: (sort_item(x.get(qorder,None)),x),l)
      elif type(qorder) is list:
        sorted = map(lambda x: (','.join(map(lambda y: sort_item(x[y]), qorder)),x),l)
      else:
        sorted = map(lambda x: (sort_item(x[qorder]),x),l)
      if ignorecase==1 and len(sorted) > 0 and type(sorted[0][0]) is str:
        sorted = map(lambda x: (str(x[0]).upper(),x[1]),sorted)
      sorted.sort()
      sorted = map(lambda x: x[1],sorted)
      if qorderdir == 'desc': sorted.reverse()
      return sorted

    # --------------------------------------------------------------------------
    #  ZMSGlobals.string_list:
    # --------------------------------------------------------------------------
    def string_list(self, s, sep='\n'):
      """
      @rtype: C{list}
      """
      l = []
      for i in s.split(sep):
        i = i.strip()
        while len(i) > 0 and ord(i[-1]) < 32:
          i = i[:-1]
        if len(i) > 0:
          l.append(i)
      return l

    # --------------------------------------------------------------------------
    #  ZMSGlobals.tree_parents:
    #
    #  Returns parents for linked list.
    # --------------------------------------------------------------------------
    def tree_parents(self, l, i='id', r='idId', v='', deep=1, reverse=1):
      k = []
      for x in l:
        if x.get(i)==v:
          k.append(x)
          if deep:
            k.extend(self.tree_parents(l,i,r,x[r],deep,0))
      if reverse:
        k.reverse()
      return k

    # --------------------------------------------------------------------------
    #  ZMSGlobals.tree_list:
    #
    #  Returns children for linked list.
    # --------------------------------------------------------------------------
    def tree_list(self, l, i='id', r='idId', v='', deep=0):
      k = []
      for x in l:
        if x.get(r)==v:
          k.append(x)
          if deep:
            k.extend(self.tree_list(l,i,r,x[i],deep))
      return k

    # --------------------------------------------------------------------------
    #  ZMSGlobals.str_json:
    # --------------------------------------------------------------------------
    def str_json(self, i):
      if type(i) is list or type(i) is tuple:
        return '['+','.join(map(lambda x: self.str_json(x),i))+']'
      elif type(i) is dict:
        return '{'+','.join(map(lambda x: '\'%s\':%s'%(x,self.str_json(i[x])),i.keys()))+'}'
      elif type(i) is time.struct_time:
        try:
          return '\'%s\''%self.getLangFmtDate(i)
        except:
          pass
      elif type(i) is int or type(i) is float:
        return str(i)
      elif i is not None:
        return '\'%s\''%(str(i).replace('\\','\\\\').replace('\'','\\\'').replace('\n','\\n').replace('\r','\\r'))
      return '\'\''

    # --------------------------------------------------------------------------
    #  ZMSGlobals.str_item:
    # --------------------------------------------------------------------------
    def str_item(self, i):
      if type(i) is list or type(i) is tuple:
        return '\n'.join(map(lambda x: self.str_item(x),i))
      elif type(i) is dict:
        return '\n'.join(map(lambda x: self.str_item(i[x]),i.keys()))
      elif type(i) is time.struct_time:
        try:
          return self.getLangFmtDate(i)
        except:
          pass
      if i is not None:
        return str(i)
      return ''

    # --------------------------------------------------------------------------
    #  ZMSGlobals.filter_list:
    # --------------------------------------------------------------------------
    def filter_list(self, l, i, v, o='%'):
      """
      Filters list by given field.
      @param l: List
      @type l: C{list}
      @param i: Field-name or -index
      @type i: C{string} or C{int}
      @param v: Field-value
      @type v: C{any}
      @param v: Match-operator
      @type v: C{string}, values are '%' (full-text), '=', '==', '>', '<', '>=', '<=', '!=', '<>'
      @return: Filtered list.
      @rtype: C{list}
      """
      # Full-text scan.
      if i is None or len(str(i))==0:
        str_item = self.str_item
        v = str(v)
        k = []
        if len(v.split(' OR '))>1:
          for s in v.split(' OR '):
            s = s.replace('*','').strip()
            if len( s) > 0:
              s = _globals.umlaut_quote(s).lower()
              k.extend(filter(lambda x: x not in k and _globals.umlaut_quote(str_item(x)).lower().find(s)>=0, l))
        elif len(v.split(' AND '))>1:
          k = l
          for s in v.split(' AND '):
            s = s.replace('*','').strip()
            if len( s) > 0:
              s = _globals.umlaut_quote(s).lower()
              k = filter(lambda x: _globals.umlaut_quote(str_item(x)).lower().find(s)>=0, k)
        else:
          v = v.replace('*','').strip().lower()
          if len( v) > 0:
            v = _globals.umlaut_quote(v).lower()
            k = filter(lambda x: _globals.umlaut_quote(str_item(x)).lower().find(v)>=0, l)
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
        str_item = self.str_item
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
        dt = _globals.getDateTime
        k=filter(lambda x: x[0] is not None, k)
        k=map(lambda x: (dt(x[0]),x[1]), k)
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.copy_list:
    # --------------------------------------------------------------------------
    def copy_list(self, l):
      """
      Copies list l.
      """
      if _globals.debug( self):
        _globals.writeLog( self, '[copy_list]: %i records'%len(l))
      try:
        v = copy.deepcopy(l)
      except:
        v = copy.copy(l)
      return v

    # --------------------------------------------------------------------------
    #  ZMSGlobals.sync_list:
    # --------------------------------------------------------------------------
    def sync_list(self, l, nl, i):
      """
      Syncronizes list l with new list nl using the column i as identifier.
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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.aggregate_list:
    # --------------------------------------------------------------------------
    def aggregate_list(self, l, i):
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
    #() Local File-System
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.pilutil:
    # --------------------------------------------------------------------------
    def pilutil( self):
      return _pilutil.pilutil(self)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.getZipArchive:
    # --------------------------------------------------------------------------
    def getZipArchive(self, f):
      """
      Extract files from zip-archive and return list of extracted files.
      @return: Extracted files (binary)
      @rtype: C{list}
      """
      return _fileutil.getZipArchive(f)

    # ------------------------------------------------------------------------------
    #  ZMSGlobals.extractZipArchive:
    # ------------------------------------------------------------------------------
    def extractZipArchive(self, f):
      return _fileutil.extractZipArchive(f)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.buildZipArchive:
    # --------------------------------------------------------------------------
    def buildZipArchive( self, files, get_data=True):
      """
      Pack ZIP-Archive and return data.
      @return: ZIP-archive (binary)
      @rtype: C{string}
      """
      return _fileutil.buildZipArchive( files, get_data)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_package_home:
    # --------------------------------------------------------------------------
    def localfs_package_home(self):
      """
      Returns package_home on local file-system.
      @return: package_home()
      @rtype: C{string}
      """
      return package_home(globals())

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_tempfile:
    # --------------------------------------------------------------------------
    def localfs_tempfile(self):
      """
      Creates temp-folder on local file-system.
      """
      tempfolder = tempfile.mktemp()
      return tempfolder

    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_read:
    # --------------------------------------------------------------------------
    def localfs_read(self, filename, mode='b', REQUEST=None):
      """
      Reads file from local file-system.
      You must grant permissions for reading from local file-system to
      directories in Config-Tab / Miscelleaneous-Section.
      @param filename: Filepath
      @type filename: C{string}
      @param filename: Access mode
      @type filename: C{string}, values are 'b' - binary
      @var REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Contents of file
      @rtype: C{string} or C{filestream_iterator}
      """
      try:
        filename = unicode(filename,'utf-8').encode('latin-1')
      except:
        pass
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_read]: filename=%s'%filename)
      
      # Check permissions.
      if REQUEST is not None:
        authorized = False
        for perm in self.getConfProperty('ZMS.localfs_read','').split(';')+[package_home(globals())]:
          authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( perm.lower()))
        if not authorized:
          RESPONSE = REQUEST.RESPONSE
          raise RESPONSE.unauthorized()
      
      # Read file.
      if type( mode) is dict:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode.get('mode','b'), mode.get('threshold',-1))
      else:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode)
      if REQUEST is not None:
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', mt)
        RESPONSE.setHeader('Content-Encoding', enc)
        RESPONSE.setHeader('Content-Length', fsize)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%_fileutil.extractFilename(filename))
        RESPONSE.setHeader('Accept-Ranges', 'bytes')
      return fdata


    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_write:
    # --------------------------------------------------------------------------
    def localfs_write(self, filename, v, mode='b', REQUEST=None):
      """
      Writes file to local file-system.
      """
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_write]: filename=%s'%filename)
      
      # Check permissions.
      if REQUEST is not None:
        authorized = False
        for perm in self.getConfProperty('ZMS.localfs_write','').split(';')+[package_home(globals())]:
          authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( perm.lower()))
        if not authorized:
          RESPONSE = REQUEST.RESPONSE
          raise RESPONSE.unauthorized()
      
      # Write file.
      _fileutil.exportObj( v, filename, mode)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_remove:
    # --------------------------------------------------------------------------
    def localfs_remove(self, path, deep=0):
      """
      Removes file from local file-system.
      """
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_remove]: path=%s'%path)
      _fileutil.remove( path, deep)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_readPath:
    # --------------------------------------------------------------------------
    def localfs_readPath(self, filename, data=False, recursive=False, REQUEST=None):
      """
      Reads path from local file-system.
      @rtype: C{list}
      """
      try:
        filename = unicode(filename,'utf-8').encode('latin-1')
      except:
        pass
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_readPath]: filename=%s'%filename)
      
      # Check permissions.
      if REQUEST is not None:
        authorized = False
        for perm in self.getConfProperty('ZMS.localfs_read','').split(';')+[package_home(globals())]:
          authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( perm.lower()))
        if not authorized:
          RESPONSE = REQUEST.RESPONSE
          raise RESPONSE.unauthorized()
      
      # Read path.
      return _fileutil.readPath(filename, data, recursive)


    # --------------------------------------------------------------------------
    #  ZMSGlobals.localfs_command:
    # --------------------------------------------------------------------------
    def localfs_command(self, command, REQUEST=None):
      """
      Executes command in local file-system.
      """
      if _globals.debug( self):
        _globals.writeLog( self, '[localfs_command]: command=%s'%command)
      
      # Check permissions.
      if REQUEST is not None:
        authorized = False
        if not authorized:
          RESPONSE = REQUEST.RESPONSE
          raise RESPONSE.unauthorized()
      
      # Execute command.
      os.system(command)

    #)


    ############################################################################
    #
    #  XML
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getXmlHeader:
    # --------------------------------------------------------------------------
    def getXmlHeader(self, encoding='utf-8'):
      """
      Returns XML-Header (encoding=utf-8)
      @param encoding: Encoding
      @type encoding: C{string}
      @rtype: C{string}
      """
      return _xmllib.xml_header(encoding)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.toXmlString:
    # --------------------------------------------------------------------------
    def toXmlString(self, v, xhtml=False, encoding='utf-8'):
      """
      Serializes value to ZMS XML-Structure.
      @rtype: C{string}
      """
      return _xmllib.toXml(self, v, xhtml=xhtml, encoding=encoding)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.parseXmlString:
    # --------------------------------------------------------------------------
    def parseXmlString(self, xml, mediadbStorable=True):
      """
      Parse value from ZMS XML-Structure.
      @return: C{list} or C{dict}
      @rtype: C{any}
      """
      builder = _xmllib.XmlAttrBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse( xml, mediadbStorable)
      return v

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xslProcess:
    # --------------------------------------------------------------------------
    def xslProcess(self, xsl, xml):
      """
      Process xml with xsl transformation.
      @deprecated: Use ZMSGlobals.processData('xslt') instead.
      """
      return self.processData('xslt', xml, xsl)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.processData:
    # --------------------------------------------------------------------------
    def processData(self, processId, data, trans=None):
      """
      Process data with custom transformation.
      """
      return _filtermanager.processData(self, processId, data, trans)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xmlParse:
    # --------------------------------------------------------------------------
    def xmlParse(self, xml):
      """
      Parse arbitrary XML-Structure into dictionary.
      @return: Dictionary of XML-Structure.
      @rtype: C{dict}
      """
      builder = _xmllib.XmlBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse(xml)
      return v

    # --------------------------------------------------------------------------
    #  ZMSGlobals.xmlNodeSet:
    # --------------------------------------------------------------------------
    def xmlNodeSet(self, mNode, sTagName='', iDeep=0):
      """
      Retrieve node-set for given tag-name from dictionary of XML-Node-Structure.
      @return: List of dictionaries of XML-Structure.
      @rtype: C{list}
      """
      return _xmllib.xmlNodeSet( mNode, sTagName, iDeep)


    ############################################################################
    #
    #  PLUGINS
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getPlugin:
    # --------------------------------------------------------------------------
    def getPlugin( self, path, REQUEST, pars={}):
      """
      Executes plugin.
      @param path: the plugin path in $ZMS_HOME/plugins/
      @type path: C{string}
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param pars: the request parameters
      @type pars: C{dict}
      @return: Result of the execution or error-message
      """
      try:
        # Set request-parameters.
        for k in pars.keys():
          v = REQUEST.get( k, None)
          REQUEST.set( k, pars[k])
          pars[k] = v
        # Execute plugin.
        rtn = self.dt_html( self.localfs_read( self.localfs_package_home()+'/plugins/'+path), REQUEST)
        # Restore request-parameters.
        for k in pars.keys():
          REQUEST.set( k, pars[k])
      except:
        rtn = _globals.writeError( self, '[getPlugin]')
      return rtn


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

    # --------------------------------------------------------------------------
    #  ZMSGlobals.getLangFmtDate:
    # --------------------------------------------------------------------------
    def getLangFmtDate(self, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
      try:
        if lang is None:
          lang = self.get_manage_lang()
        # Convert to struct_time
        t = _globals.getDateTime(t)
        # Return DateTime
        if fmt_str == 'DateTime':
          dt = DateTime('%4d/%2d/%2d'%(t[0],t[1],t[2]))
          return dt
        # Return name of weekday
        elif fmt_str == 'Day':
          dt = DateTime('%4d/%2d/%2d'%(t[0],t[1],t[2]))
          return self.getLangStr('DAYOFWEEK%i'%(dt.dow()%7),lang)
        # Return name of month
        elif fmt_str == 'Month':
          return self.getLangStr('MONTH%i'%t[1],lang)
        elif fmt_str == 'ISO-8601':
          # DST in t[8] ! -1 (unknown), 0 (off), 1 (on)
          if t[8] == 1:
            tz = time.altzone
          elif t[8] == 0:
            tz = time.timezone
          else:
            tz = 0
          tch = '+'
          if tz < 0:
            tch = '-'
          tz = abs(tz)
          tzh = tz/60/60
          tzm = (tz-tzh*60*60)/60
          return time.strftime('%Y-%m-%dT%H:%M:%S',t)+tch+('00%d'%tzh)[-2:]+':'+('00%d'%tzm)[-2:]
        # Return date/time
        fmt = self.getLangStr(fmt_str,lang)
        time_fmt = self.getLangStr('TIME_FMT',lang)
        date_fmt = self.getLangStr('DATE_FMT',lang)
        if fmt.find(time_fmt) >= 0:
          if t[3] == 0 and \
             t[4] == 0 and \
             t[5]== 0:
            fmt = fmt[:-len(time_fmt)]
        fmt = fmt.strip()
        return time.strftime(fmt,t)
      except:
        #-- _globals.writeError(self,"[getLangFmtDate]: t=%s"%str(t))
        return str(t)

    # --------------------------------------------------------------------------
    #  ZMSGlobals.parseLangFmtDate:
    # --------------------------------------------------------------------------
    def parseLangFmtDate(self, s, lang=None, fmt_str=None, recflag=None):
      return _globals.parseLangFmtDate(s)

    # -------------------------------------------------------------------------- 
    #  ZMSGlobals.compareDate: 
    # -------------------------------------------------------------------------- 
    def compareDate(self, t0, t1): 
      return _globals.compareDate(t0, t1) 

################################################################################