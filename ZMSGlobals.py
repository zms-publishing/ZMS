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
from AccessControl import ClassSecurityInfo
from App.Common import package_home
from DateTime.DateTime import DateTime
from OFS.CopySupport import absattr
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from cStringIO import StringIO
from types import StringTypes
from binascii import b2a_base64, a2b_base64
import Globals
import base64
import copy
import fnmatch
import operator
import os
import re
import tempfile
import time
import urllib
import zExceptions
import zope.interface
# Product Imports.
import _blobfields
import _fileutil
import _filtermanager
import _globals
import _mimetypes
import _pilutil
import _xmllib
import _zopeutil

__all__= ['ZMSGlobals']

# ------------------------------------------------------------------------------
#  MD5:
# ------------------------------------------------------------------------------
import hashlib

class MD5DigestScheme:

  def encrypt(self, pw):
    enc = hashlib.md5(pw)
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
    i = unicode(i,'utf-8')
    mapping = _globals.umlautMapping
    for key in mapping.keys():
      try: i = i.replace(key,mapping[key])
      except: pass
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

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()


    # --------------------------------------------------------------------------
    #  Meta-Type Selectors.
    # --------------------------------------------------------------------------
    PAGES = 0         #: virtual meta_type for all Pages (Containers)
    PAGEELEMENTS = 1  #: virtual meta_type for all Page-Elements
    NOREF = 4         #: virtual meta_type-flag for resolving meta-type of ZMSLinkElement-target-object.
    NORESOLVEREF = 5  #: virtual meta_type-flag for not resolving meta-type of ZMSLinkElement-target-object.


    """
    Returns home-folder of this Product.
    """
    def getPRODUCT_HOME( self):
      PRODUCT_HOME = os.path.dirname(os.path.abspath(__file__))
      return PRODUCT_HOME


    """
    Returns path to lib/site-packages
    """
    def getPACKAGE_HOME( self):
      from distutils.sysconfig import get_python_lib
      return get_python_lib()


    """
    Returns path to Instance
    """
    def getINSTANCE_HOME( self):
      INSTANCE_HOME = self.Control_Panel.getINSTANCE_HOME()
      return INSTANCE_HOME


    """
    Creates a new Zope native-representative (Image/File) of given blob in container.
    @return: New instance of Zope-object.
    @rtype: L{object}
    """
    def createBlobInContext( self, id, blob, container):
      filename = blob.getFilename()
      data = blob.getData()
      if blob.getContentType().startswith('image'):
        container.manage_addImage( id=id, title=filename, file=data)
      else:
        container.manage_addFile( id=id, title=filename, file=data)
      ob = getattr(container,id)
      return ob


    """
    Creates a new instance of a file from given data.
    @param data: File-data (binary)
    @type data: C{string}
    @param filename: Filename
    @type filename: C{string}
    @return: New instance of file.
    @rtype: L{MyFile}
    """
    def FileFromData( self, data, filename='', content_type=None, mediadbStorable=False):
      file = {}
      file['data'] = data
      file['filename'] = filename
      if content_type: file['content_type'] = content_type
      return _blobfields.createBlobField( self, _globals.DT_FILE, file=file, mediadbStorable=mediadbStorable)


    """
    Creates a new instance of an image from given data.
    @param data: Image-data (binary)
    @type data: C{string}
    @param filename: Filename
    @type filename: C{string}
    @return: New instance of image.
    @rtype: L{MyImage}
    """
    def ImageFromData( self, data, filename='', content_type=None, mediadbStorable=False):
      f = _blobfields.createBlobField( self, _globals.DT_IMAGE, file={'data':data,'filename':filename,'content_type':content_type}, mediadbStorable=mediadbStorable)
      f.aq_parent = self
      return f


    """
    Inline condition 
    @param c: condition
    @type c: C{boolean}
    @param t: return value if condition is true
    @type t: C{any}
    @param f: return value if condition is false
    @type f: C{any}
    @rtype: C{any}
    """
    def boolint(self, c, t=1, f=0):
      if c in [1,True,'1','True']:
        return t
      return f


    """
    Returns its first argument if it is not equal to third argument (None), 
    otherwise it returns its second argument.
    @param a1: 1st argument
    @type a1: C{any}
    @param a2: 2nd argument
    @type a2: C{any}
    @rtype: C{any}
    """
    def nvl(self, a1, a2, n=None):
      return _globals.nvl( a1, a2, n)


    """
    Available encryption-schemes.
    @return: list of encryption-scheme ids
    @rtype: C{list}
    """
    def encrypt_schemes(self):
      ids = []
      for id, prefix, scheme in AuthEncoding._schemes:
        ids.append( id)
      return ids


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
    def encrypt_password(self, pw, algorithm='md5', hex=False):
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


    """
    Encrypts given string with entities by random algorithm.
    @param s: String
    @type s: C{string}
    @return: Encrypted string
    @rtype: C{string}
    """
    def encrypt_ordtype(self, s):
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


    """
    Random integer in given range.
    @param n: Range
    @type n: C{int}
    @return: Random integer
    @rtype: C{int}
    """
    def rand_int(self, n):
      from random import randint
      return randint(0,n)


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
    def string_maxlen(self, s, maxlen=20, etc='...', encoding=None):
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


    """
    Replace special characters in string using the %xx escape. Letters, digits, 
    and the characters '_.-' are never quoted. By default, this function is 
    intended for quoting the path section of the URL. The optional safe 
    parameter specifies additional characters that should not be quoted,
    its default value is '/'.
    @return: the quoted string
    @rtype: C{string}
    """
    def url_quote(self, string, safe='/'):
      return urllib.quote(string,safe)


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
    def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
      return _globals.http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers)


    """
    Append params from dict to given url.
    @param url: Url
    @type url: C{string}
    @param dict: dictionary of params (key/value pairs)
    @type dict: C{dict}
    @return: New url
    @rtype: C{string}
    """
    def url_append_params(self, url, dict, sep='&amp;'):
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


    """
    Inerits params from request to given url.
    @param url: Url
    @type url: C{string}
    @param REQUEST: the triggering request
    @type REQUEST: C{ZPublisher.HTTPRequest}
    @return: New url
    @rtype: C{string}
    """
    def url_inherit_params(self, url, REQUEST, exclude=[], sep='&amp;'):
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


    """
    Converts given string to identifier (removes special-characters and 
    replaces German umlauts).
    @param s: String
    @type s: C{string}
    @return: Identifier
    @rtype: C{string}
    """
    def id_quote(self, s, mapping={
            '\x20':'_',
            '-':'_',
            '/':'_',
    }):
      s = _globals.umlaut_quote(self, s, mapping)
      valid = map( lambda x: ord(x[0]), mapping.values()) + [ord('_')] + range(ord('0'),ord('9')+1) + range(ord('A'),ord('Z')+1) + range(ord('a'),ord('z')+1)
      s = filter( lambda x: ord(x) in valid, s)
      while len(s) > 0 and s[0] == '_':
          s = s[1:]
      s = s.lower()
      return s


    """
    Returns prefix from identifier (which is the non-numeric part at the 
    beginning).
    @param s: Identifier
    @type s: C{string}
    @return: Prefix
    @rtype: C{string}
    """
    def get_id_prefix(self, s):
      return _globals.id_prefix(s)


    """
    Replace special characters in string for javascript.
    """
    def js_quote(self, text, charset=None):
      if type(text) is unicode:
        text= text.encode([charset, 'utf-8'][charset==None])
      text = text.replace("\r", "\\r").replace("\n", "\\n")
      text = text.replace('"', '\\"').replace("'", "\\'")
      return text


    """
    Checks if given request is preview.
    @param REQUEST: the triggering request
    @type REQUEST: C{ZPublisher.HTTPRequest}
    @rtype: C{Boolean}
    """
    def isPreviewRequest(self, REQUEST):
      return _globals.isPreviewRequest(REQUEST)


    """
    Returns display string for file-size (KB).
    @param len: length (bytes)
    @type len: C{int}
    @rtype: C{string}
    """
    def getDataSizeStr(self, len):
      return _fileutil.getDataSizeStr(len)


    """
    Returns the absolute-url of an icon representing the specified MIME-type.
    @param mt: MIME-Type (e.g. image/gif, text/xml).
    @type mt: C{string}
    @rtype: C{string}
    """
    def getMimeTypeIconSrc(self, mt):
      return'/misc_/zms/%s'%_mimetypes.dctMimeType.get( mt, _mimetypes.content_unknown)


    ############################################################################
    #
    #( Operators
    #
    ############################################################################

    """
    Returns absolute-attribute of given value.
    @param v: Value
    @type v: C{any}
    @rtype: C{type}
    """
    def operator_absattr(self, v):
      return absattr(v)

    """
    Returns python-type of given value.
    @param v: Value
    @type v: C{any}
    @rtype: C{type}
    """
    def operator_gettype(self, v):
      return type(v)

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
    def operator_setitem(self, a, b, c):
      operator.setitem(a,b,c)
      return a

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
    def operator_getitem(self, a, b, c=None, ignorecase=True):
      if ignorecase and type(b) is str:
        flags = int(self.getConfProperty('operator_getitem.ignorecase.flags',re.IGNORECASE))
        pattern = self.getConfProperty('operator_getitem.ignorecase..pattern','^*$').replace('*',b)
        for key in a.keys():
          if re.search(pattern,key,flags) is not None:
            return operator.getitem(a,key)
      if b in a.keys():
        return operator.getitem(a,b)
      return c

    """
    Delete key from python-dictionary.
    @param a: Dictionary
    @type a: C{dict}
    @param b: Key
    @type b: C{any}
    """
    def operator_delitem(self, a, b):
      operator.delitem(a, b)

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
    def operator_setattr(self, a, b, c):
      setattr(a,b,c)
      return a

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
    def operator_getattr(self, a, b, c=None):
      return getattr(a,b,c)

    """
    Delete key from python-object.
    @param a: Object
    @type a: C{any}
    @param b: Key
    @type b: C{any}
    """
    def operator_delattr(self, a, b):
      return delattr(a,b)

    #)


    ############################################################################
    #
    #( Logging
    #
    ############################################################################

    """
    Write to standard-out (only allowed for development-purposes!).
    @param info: Object
    @type info: C{any}
    """
    def writeStdout(self, info):
      print info


    """
    Log debug-information.
    @param info: Debug-information
    @type info: C{any}
    """
    def writeLog(self, info):
      return _globals.writeLog( self, info)

    """
    Log information.
    @param info: Information
    @type info: C{any}
    """
    def writeBlock(self, info):
      return _globals.writeBlock( self, info)

    """
    Log error.
    @param info: Information
    @type info: C{any}
    """
    def writeError(self, info):
      return _globals.writeError( self, info)

    #)


    ############################################################################
    #
    #( Regular Expressions
    #
    ############################################################################

    """
    Performs a search-and-replace across subject, replacing all matches of 
    regex in subject with replacement. The result is returned by the sub() 
    function. The subject string you pass is not modified.
    @rtype: C{string}
    """
    def re_sub( self, pattern, replacement, subject, ignorecase=False):
      if ignorecase:
        return re.compile( pattern, re.IGNORECASE).sub( replacement, subject)
      else:
        return re.compile( pattern).sub( replacement, subject)


    """
    Scan through string looking for a location where the regular expression 
    pattern produces a match, and return a corresponding MatchObject 
    instance. Return None if no position in the string matches the pattern; 
    note that this is different from finding a zero-length match at some
    point in the string.
    """
    def re_search( self, pattern, subject, ignorecase=False):
      if ignorecase:
        s = re.compile( pattern, re.IGNORECASE).split( subject)
      else:
        s = re.compile( pattern).split( subject)
      return map( lambda x: s[x*2+1], range(len(s)/2))


    """
    Return all non-overlapping matches of pattern in string, as a list of strings. 
    The string is scanned left-to-right, and matches are returned in the order found. 
    If one or more groups are present in the pattern, return a list of groups; 
    this will be a list of tuples if the pattern has more than one group. 
    Empty matches are included in the result unless they touch the beginning of another match
    """
    def re_findall( self, pattern, text, ignorecase=False):
      if ignorecase:
        r = re.compile( pattern, re.IGNORECASE)
      else:
        r = re.compile( pattern)
      return r.findall(text)

    #)


    ############################################################################
    #
    #( Styles / CSS
    #
    ############################################################################

    """
    Parses default-stylesheet and returns elements.
    @deprecated
    @return: Elements
    @rtype: C{dict}
    """
    def parse_stylesheet(self):
      stylesheet = self.getStylesheet()
      if stylesheet.meta_type in ['DTML Document','DTML Method']:
        data = stylesheet.raw
      elif stylesheet.meta_type in ['File']:
        data = stylesheet.data
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
      colormap = {}
      for key in value.keys():
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
      self.setConfProperty('ZMS.colormap',colormap)
      return colormap

    def get_colormap(self):
      colormap = self.getConfProperty('ZMS.colormap',None)
      if colormap is None:
        try:
          colormap = self.parse_stylesheet()
        except:
          # Destroy Colormap on Error
          colormap = {}
          self.setConfProperty('ZMS.colormap',colormap)
      return colormap

    #)


    ############################################################################
    #
    #( Mappings
    #
    ############################################################################

    """
    Intersection of two lists (li & l2).
    @param l1: List #1
    @type l1: C{list}
    @param l2: List #2
    @type l2: C{list}
    @returns: Intersection list
    @rtype: C{list}
    """
    def intersection_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      return filter(lambda x: x in l2, l1)


    """
    Difference of two lists (l1 - l2).
    @param l1: List #1
    @type l1: C{list}
    @param l2: List #2
    @type l2: C{list}
    @returns: Difference list
    @rtype: C{list}
    """
    def difference_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      return filter(lambda x: x not in l2, l1)


    """
    Concatenates two lists (l1 + l2).
    @param l1: List #1
    @type l1: list
    @param l2: List #2
    @type l2: list
    @returns: Concatinated list
    @rtype: C{list}
    """
    def concat_list(self, l1, l2):
      l1 = list(l1)
      l2 = list(l2)
      l = self.copy_list(l1)
      l.extend(filter(lambda x: x not in l1, l2))
      return l


    """
    Converts list to dictionary: key=l[x*2], value=l[x*2+1]
    @param l: List
    @type l: C{list}
    @return: Dictionary
    @rtype: C{dict}
    """
    def dict_list(self, l):
      dict = {}
      for i in range(0,len(l)/2):
        key = l[i*2]
        value = l[i*2+1]
        dict[key] = value
      return dict


    """
    Returns distinct values of given field from list.
    @param l: List
    @type l: C{list}
    @rtype: C{list}
    """
    def distinct_list(self, l, i=None):
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


    """
    Sorts list by given field.
    @return: Sorted list.
    @rtype: C{list}
    """
    def sort_list(self, l, qorder=None, qorderdir='asc', ignorecase=1): 
      if qorder is None:
        sorted = map(lambda x: (x, x), l)
      elif type(qorder) is str:
        sorted = map(lambda x: (sort_item(x.get(qorder,None)),x),l)
      elif type(qorder) is list:
        sorted = map(lambda x: (map(lambda y: sort_item(x[y]), qorder),x),l)
      else:
        sorted = map(lambda x: (sort_item(x[qorder]),x),l)
      if ignorecase==1 and len(sorted) > 0 and type(sorted[0][0]) is str:
        sorted = map(lambda x: (str(x[0]).upper(),x[1]),sorted)
      sorted.sort()
      sorted = map(lambda x: x[1],sorted)
      if qorderdir == 'desc': sorted.reverse()
      return sorted


    """
    Split string by given separator and trim items.
    @rtype: C{list}
    """
    def string_list(self, s, sep='\n'):
      l = []
      for i in s.split(sep):
        i = i.strip()
        while len(i) > 0 and ord(i[-1]) < 32:
          i = i[:-1]
        if len(i) > 0:
          l.append(i)
      return l


    """
    Returns parents for linked list.
    @rtype: C{list}
    """
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


    """
    Returns children for linked list.
    @rtype: C{list}
    """
    def tree_list(self, l, i='id', r='idId', v='', deep=0):
      k = []
      for x in l:
        if x.get(r)==v:
          k.append(x)
          if deep:
            k.extend(self.tree_list(l,i,r,x[i],deep))
      return k


    """
    Returns a json-string representation of the object.
    @rtype: C{string}
    """
    def str_json(self, i, encoding='ascii', errors='xmlcharrefreplace'):
      if type(i) is list or type(i) is tuple:
        return '['+','.join(map(lambda x: self.str_json(x,encoding,errors),i))+']'
      elif type(i) is dict:
        return '{'+','.join(map(lambda x: '"%s":%s'%(x,self.str_json(i[x],encoding,errors)),i.keys()))+'}'
      elif type(i) is time.struct_time:
        try:
          return '"%s"'%self.getLangFmtDate(i)
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


    """
    Returns a string representation of the item.
    @rtype: C{string}
    """
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
    def filter_list(self, l, i, v, o='%'):
      # Full-text scan.
      if i is None or len(str(i))==0:
        str_item = self.str_item
        v = str(v)
        k = []
        if len(v.split(' OR '))>1:
          for s in v.split(' OR '):
            s = s.replace('*','').strip()
            if len( s) > 0:
              s = _globals.umlaut_quote(self, s).lower()
              k.extend(filter(lambda x: x not in k and _globals.umlaut_quote(self, str_item(x)).lower().find(s)>=0, l))
        elif len(v.split(' AND '))>1:
          k = l
          for s in v.split(' AND '):
            s = s.replace('*','').strip()
            if len( s) > 0:
              s = _globals.umlaut_quote(self, s).lower()
              k = filter(lambda x: _globals.umlaut_quote(self, str_item(x)).lower().find(s)>=0, k)
        else:
          v = v.replace('*','').strip().lower()
          if len( v) > 0:
            v = _globals.umlaut_quote(self, v).lower()
            k = filter(lambda x: _globals.umlaut_quote(self, str_item(x)).lower().find(v)>=0, l)
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


    """
    Copies list l.
    @param l: List
    @type l: C{list}
    @return: Copy of list.
    @rtype: C{list}
    """
    def copy_list(self, l):
      try:
        v = copy.deepcopy(l)
      except:
        v = copy.copy(l)
      return v


    """
    Syncronizes list l with new list nl using the column i as identifier.
    """
    def sync_list(self, l, nl, i):
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


    """
    Aggregates given field in list.
    """
    def aggregate_list(self, l, i):
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

    """
    Returns util with PIL functions.
    """
    def pilutil( self):
      return _pilutil.pilutil(self)


    """
    Returns util to handle zms3.extensions
    """
    def extutil(self):
      import _extutil
      return _extutil.ZMSExtensions()


    """
    Extract files from zip-archive and return list of extracted files.
    @return: Extracted files (binary)
    @rtype: C{list}
    """
    def getZipArchive(self, f):
      return _fileutil.getZipArchive(f)


    """
    Extract zip-archive.
    """
    security.declarePrivate('extractZipArchive')
    def extractZipArchive(self, f):
      return _fileutil.extractZipArchive(f)


    """
    Pack zip-archive and return data.
    @return: zip-archive (binary)
    @rtype: C{string}
    """
    def buildZipArchive( self, files, get_data=True):
      return _fileutil.buildZipArchive( files, get_data)


    """
    Returns package_home on local file-system.
    @return: package_home()
    @rtype: C{string}
    """
    def localfs_package_home(self):
      return package_home(globals())


    """
    Creates temp-folder on local file-system.
    @rtype: C{string}
    """
    def localfs_tempfile(self):
      tempfolder = tempfile.mktemp()
      return tempfolder


    security.declareProtected('View', 'localfs_read')
    def localfs_read(self, filename, mode='b', cache='public, max-age=3600', REQUEST=None):
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
      _globals.writeLog( self, '[localfs_read]: filename=%s'%filename)
      
      # Get absolute filename.
      filename = _fileutil.absoluteOSPath(filename)
      
      # Check permissions.
      request = self.REQUEST
      authorized = False
      perms = self.getConfProperty('ZMS.localfs_read','').split(';')
      perms.append(tempfile.gettempdir())
      perms.append(package_home(globals()))
      mediadb = self.getMediaDb()
      if mediadb:
          perms.append(mediadb.getLocation())
      for perm in map(lambda x: x.strip(), perms):
          authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( _fileutil.absoluteOSPath(perm).lower()))
      if not authorized:
          raise zExceptions.Unauthorized
      
      # Read file.
      if type( mode) is dict:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode.get('mode','b'), mode.get('threshold',-1))
      else:
        fdata, mt, enc, fsize = _fileutil.readFile( filename, mode)
      if REQUEST is not None:
        RESPONSE = REQUEST.RESPONSE
        self.set_response_headers( filename, mt)
        RESPONSE.setHeader('Cache-Control', cache)
        RESPONSE.setHeader('Content-Encoding', enc)
        RESPONSE.setHeader('Content-Length', fsize)
      return fdata


    """
    Set content-type and -disposition to response-headers.
    """
    def set_response_headers(self, fn, mt='application/octet-stream'):
      REQUEST = self.REQUEST
      RESPONSE = REQUEST.RESPONSE
      RESPONSE.setHeader('Content-Type', mt)
      if REQUEST.get('HTTP_USER_AGENT','').find('Android') < 0:
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%_fileutil.extractFilename(fn))
      accept_ranges = self.getConfProperty('ZMS.blobfields.accept_ranges','bytes')
      if len( accept_ranges) > 0:
          RESPONSE.setHeader('Accept-Ranges', accept_ranges)


    """
    Writes file to local file-system.
    """
    def localfs_write(self, filename, v, mode='b', REQUEST=None):
      _globals.writeLog( self, '[localfs_write]: filename=%s'%filename)
      
      # Get absolute filename.
      filename = _fileutil.absoluteOSPath(filename)
      
      # Check permissions.
      request = self.REQUEST
      authorized = False
      perms = self.getConfProperty('ZMS.localfs_write','').split(';')
      perms.append(tempfile.gettempdir())
      perms.append(package_home(globals()))
      mediadb = self.getMediaDb()
      if mediadb:
          perms.append(mediadb.getLocation())
      for perm in map(lambda x: x.strip(), perms):
          authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( _fileutil.absoluteOSPath(perm).lower()))
      if not authorized:
          raise zExceptions.Unauthorized
      
      # Write file.
      _fileutil.exportObj( v, filename, mode)


    """
    Removes file from local file-system.
    """
    def localfs_remove(self, path, deep=0):
      _globals.writeLog( self, '[localfs_remove]: path=%s'%path)
      
      # Get absolute filename.
      filename = _fileutil.absoluteOSPath(path)
      
      # Check permissions.
      request = self.REQUEST
      authorized = False
      perms = self.getConfProperty('ZMS.localfs_write','').split(';')
      perms.append(tempfile.gettempdir())
      perms.append(package_home(globals()))
      mediadb = self.getMediaDb()
      if mediadb:
          perms.append(mediadb.getLocation())
      for perm in map(lambda x: x.strip(), perms):
        authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( _fileutil.absoluteOSPath(perm).lower()))
      if not authorized:
        raise zExceptions.Unauthorized
      
      # Remove file.
      _fileutil.remove( path, deep)


    """
    Reads path from local file-system.
    @rtype: C{list}
    """
    def localfs_readPath(self, filename, data=False, recursive=False, REQUEST=None):
      try:
        filename = unicode(filename,'utf-8').encode('latin-1')
      except:
        pass
      _globals.writeLog( self, '[localfs_readPath]: filename=%s'%filename)
      
      # Get absolute filename.
      filename = _fileutil.absoluteOSPath(filename)
      
      # Check permissions.
      request = self.REQUEST
      authorized = False
      perms = self.getConfProperty('ZMS.localfs_read','').split(';')
      perms.append(tempfile.gettempdir())
      perms.append(package_home(globals()))
      mediadb = self.getMediaDb()
      if mediadb:
          perms.append(mediadb.getLocation())
      for perm in map(lambda x: x.strip(), perms):
        authorized = authorized or ( len( perm) > 0 and filename.lower().startswith( _fileutil.absoluteOSPath(perm).lower()))
      if not authorized:
        raise zExceptions.Unauthorized
      
      # Read path.
      return _fileutil.readPath(filename, data, recursive)

    #)


    ############################################################################
    #
    #  XML
    #
    ############################################################################

    """
    Returns XML-Header (encoding=utf-8)
    @param encoding: Encoding
    @type encoding: C{string}
    @rtype: C{string}
    """
    def getXmlHeader(self, encoding='utf-8'):
      return _xmllib.xml_header(encoding)


    """
    Serializes value to ZMS XML-Structure.
    @rtype: C{string}
    """
    def toXmlString(self, v, xhtml=False, encoding='utf-8'):
      return _xmllib.toXml(self, v, xhtml=xhtml, encoding=encoding)


    """
    Parse value from ZMS XML-Structure.
    @return: C{list} or C{dict}
    @rtype: C{any}
    """
    def parseXmlString(self, xml, mediadbStorable=True):
      builder = _xmllib.XmlAttrBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse( xml, mediadbStorable)
      return v


    """
    Process xml with xsl transformation.
    @deprecated: Use ZMSGlobals.processData('xslt') instead.
    """
    def xslProcess(self, xsl, xml):
      return self.processData('xslt', xml, xsl)


    """
    Process data with custom transformation.
    """
    def processData(self, processId, data, trans=None):
      return _filtermanager.processData(self, processId, data, trans)


    """
    Parse arbitrary XML-Structure into dictionary.
    @return: Dictionary of XML-Structure.
    @rtype: C{dict}
    """
    def xmlParse(self, xml):
      builder = _xmllib.XmlBuilder()
      if type(xml) is str:
        xml = StringIO(xml)
      v = builder.parse(xml)
      return v


    """
    Retrieve node-set for given tag-name from dictionary of XML-Node-Structure.
    @return: List of dictionaries of XML-Structure.
    @rtype: C{list}
    """
    def xmlNodeSet(self, mNode, sTagName='', iDeep=0):
      return _xmllib.xmlNodeSet( mNode, sTagName, iDeep)


    ############################################################################
    #
    #  Zope-Util
    #
    ############################################################################

    """
    Read Zope-object from container.
    """
    def readObject(self, ob, default=None):
      data = default
      if ob is not None:
        data= _zopeutil.readObject(ob.aq_parent,absattr(ob.id),default)
      return data


    ############################################################################
    #
    #  Plugins
    #
    ############################################################################

    """
    Try to execute given value.
    """
    def dt_exec(self, v):
      if type(v) in StringTypes:
        if v.find('<dtml-') >= 0:
          v = self.dt_html(v,self.REQUEST)
        elif v.startswith('##'):
          v = self.dt_py(v)
        elif v.find('<tal:') >= 0:
          v = self.dt_tal(v)
      return v

    """
    Execute given DTML-snippet.
    @param value: DTML-snippet
    @type value: C{string}
    @param REQUEST: the triggering request
    @type REQUEST: C{ZPublisher.HTTPRequest}
    @return: Result of the execution or None
    @rtype: C{any}
    """
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
      value = re.sub( '<dtml-sendmail(.*?)>(\r\n|\n)','<dtml-sendmail\\1>',value)
      value = re.sub( '</dtml-var>', '', value)
      dtml = DocumentTemplate.DT_HTML.HTML(value)
      value = dtml( self, REQUEST)
      return value

    """
    Execute given Python-script.
    @param script: Python-script
    @type script: C{string}
    @param kw: additional options
    @type kw: C{dict}
    @return: Result of the execution or None
    @rtype: C{any}
    """
    def dt_py( self, script, kw={}):
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
          'container':self,
          'context':self,
          'script':ps,
        }
      args = ()
      return ps._exec(bound_names,args,kw)

    """
    Execute given TAL-snippet.
    @param value: TAL-snippet
    @type value: C{string}
    @return: Result of the execution or None
    @rtype: C{any}
    """
    def dt_tal(self, text, options={}):
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
               }
          return c
        def _cook_check(self):
          t = 'text/html'
          self.pt_edit(self.text, t)
          self._cook()
      
      pt = StaticPageTemplateFile(filename='None')
      pt.setText(text)
      pt.setEnv(self,options)
      return unicode(pt.pt_render(extra_context={'here':self,'request':self.REQUEST})).encode('utf-8')

    """
    Executes plugin.
    @param path: the plugin path in $ZMS_HOME/plugins/
    @type path: C{string}
    @param options: the options
    @type options: C{dict}
    """
    def getPlugin( self, path, options={}):
      # Check permissions.
      request = self.REQUEST
      authorized = path.find('..') < 0
      if not authorized:
        raise zExceptions.Unauthorized
      # Execute plugin.
      try:
        class StaticPageTemplateFile(PageTemplateFile):
          def setEnv(self,context,options):
            self.context = context
            self.options  = options
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
                 }
            return c
        filename = os.path.join(self.localfs_package_home(),'plugins',path)
        pt = StaticPageTemplateFile(filename)
        pt.setEnv(self,options)
        rtn = pt.pt_render(extra_context={'here':self,'request':self.REQUEST})
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

    """
    Formats date in locale-format
    @param t: Datetime
    @type t: C{struct_time}
    @param lang: Locale
    @type lang: C{string}
    @param fmt_str: Format-String, possible values SHORTDATETIME_FMT (default),
    SHORTDATE_FMT, DATETIME_FMT, DATE_FMT, DateTime, Day, Month, ISO8601, RFC2822
    """
    def getLangFmtDate(self, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
      try:
        if lang is None:
          lang = self.get_manage_lang()
        # Convert to struct_time
        t = _globals.getDateTime(t)
        # Return ModificationTime
        if fmt_str == 'BOBOBASE_MODIFICATION_FMT':
          sdtf = self.getLangFmtDate(t, lang, fmt_str='SHORTDATETIME_FMT')
          if self.daysBetween(t,DateTime()) > self.getConfProperty('ZMS.shortDateFormat.daysBetween',5):
            sdf = self.getLangFmtDate(t, lang, fmt_str='SHORTDATE_FMT')
            return '<span title="%s">%s</span>'%(sdtf,sdf)
          return sdtf
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
        elif fmt_str.replace('-','').replace(' ','') in ['ISO8601','RFC2822']:
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
          colon = ''
          if fmt_str.replace('-','').replace(' ','') in ['ISO8601']:
            colon = ':'
          return time.strftime('%Y-%m-%dT%H:%M:%S',t)+tch+('00%d'%tzh)[-2:]+colon+('00%d'%tzm)[-2:]
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

    """
    Parse date in locale-format
    @rtype: C{struct_time}
    """
    def parseLangFmtDate(self, s, lang=None, fmt_str=None, recflag=None):
      return _globals.parseLangFmtDate(s)

    """
    Compare two dates.
    @rtype: C{int}
    """ 
    def compareDate(self, t0, t1):
      return _globals.compareDate(t0, t1) 

    """
    Calculate days between two dates.
    @rtype: C{int}
    """ 
    def daysBetween(self, t0, t1):
      return _globals.daysBetween(t0, t1) 


    """
    Sends Mail via MailHost.
    """
    def sendMail(self, mto, msubject, mbody, REQUEST=None, mattach=None):
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
        mto['From'] = mto.get('From',self.getUserAttr(auth_user,'email',self.getConfProperty('ZMSAdministrator.email','')))
      
      # Get MailHost.
      mailhost = None
      homeElmnt = self.getHome()
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
            metadata = self.re_search('(^.*[;,])', filedata)
            # extract filename, mimetype and encoding if available
            if (type(metadata)==list and len(metadata)==1):          
              mimetype = self.re_search('data:([^;,]+[;,][^;,]*)', metadata[0])
              filename = self.re_search('filename:([^;,]+)', metadata[0])
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
        #_globals.writeBlock( self, "[sendMail]: %s"%mime_msg.as_string())
        mailhost.send(mime_msg.as_string())
        return 0
      except:
        return -1

    """
    Check if feature toggle is set.
    @rtype: C{boolean}
    """ 
    def isFeatureEnabled(self, feature=''):
    
      # get conf from current client
      confprop = self.breadcrumbs_obj_path(False)[0].getConfProperty('ZMS.Features.enabled','')
      features = confprop.replace(',',';').split(';')
      # get conf from top master if there is no feature toggle set at client
      if len(features)==1 and features[0].strip()=='':
        confprop = self.breadcrumbs_obj_path(True)[0].getConfProperty('ZMS.Features.enabled','')
        features = confprop.replace(',',';').split(';')
    
      if len(filter(lambda ob: ob.strip()==feature.strip(), features))>0:
        return True
      else:
        return False

# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ZMSGlobals)

################################################################################