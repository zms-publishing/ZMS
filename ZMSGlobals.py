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
from App.Common import package_home
from DateTime.DateTime import DateTime
from OFS.CopySupport import absattr
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.Expressions import SecureModuleImporter
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
import standard
import _blobfields
import _fileutil
import _filtermanager
import _globals
import _mimetypes
import _pilutil
import _xmllib
import zopeutil

__all__= ['ZMSGlobals']

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
      s = standard.umlaut_quote(self, s, mapping)
      valid = map( lambda x: ord(x[0]), mapping.values()) + [ord('_')] + range(ord('0'),ord('9')+1) + range(ord('A'),ord('Z')+1) + range(ord('a'),ord('z')+1)
      s = filter( lambda x: ord(x) in valid, s)
      while len(s) > 0 and s[0] == '_':
          s = s[1:]
      s = s.lower()
      return s


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
      return standard.writeLog( self, info)

    """
    Log information.
    @param info: Information
    @type info: C{any}
    """
    def writeBlock(self, info):
      return standard.writeBlock( self, info)

    """
    Log error.
    @param info: Information
    @type info: C{any}
    """
    def writeError(self, info):
      return standard.writeError( self, info)

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
      standard.writeLog( self, '[localfs_read]: filename=%s'%filename)
      
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
      standard.writeLog( self, '[localfs_write]: filename=%s'%filename)
      
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
      standard.writeLog( self, '[localfs_remove]: path=%s'%path)
      
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
      standard.writeLog( self, '[localfs_readPath]: filename=%s'%filename)
      
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
    #  Plugins
    #
    ############################################################################

    """
    Returns if given value is executable.
    """
    def dt_executable(self, v):
      if type(v) in StringTypes:
        if v.startswith('##'):
          return 'py'
        elif v.find('<tal:') >= 0:
          return 'zpt'
        elif v.find('<dtml-') >= 0:
          return 'method'
      return False

    """
    Try to execute given value.
    """
    def dt_exec(self, v, o={}):
      if type(v) in StringTypes:
        if v.startswith('##'):
          v = self.dt_py(v,o)
        elif v.find('<tal:') >= 0:
          v = self.dt_tal(v,dict(o))
        elif v.find('<dtml-') >= 0:
          v = self.dt_html(v,self.REQUEST)
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
               'modules': SecureModuleImporter,
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
        rtn = standard.writeError( self, '[getPlugin]')
      return rtn

    def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
      return standard.http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers)
  
    def getLangFmtDate(self, t, lang=None, fmt_str='SHORTDATETIME_FMT'):
      return standard.getLangFmtDate(self, t, lang, fmt_str)
  
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
        #standard.writeBlock( self, "[sendMail]: %s"%mime_msg.as_string())
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
