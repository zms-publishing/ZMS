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
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from cStringIO import StringIO
from types import StringTypes
import Globals
import base64
import copy
import fnmatch
import operator
import os
import re
import tempfile
import time
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


    # --------------------------------------------------------------------------
    #  Meta-Type Selectors.
    # --------------------------------------------------------------------------
    PAGES = 0         #: virtual meta_type for all Pages (Containers)
    PAGEELEMENTS = 1  #: virtual meta_type for all Page-Elements
    NOREF = 4         #: virtual meta_type-flag for resolving meta-type of ZMSLinkElement-target-object.
    NORESOLVEREF = 5  #: virtual meta_type-flag for not resolving meta-type of ZMSLinkElement-target-object.


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
      s = standard.umlaut_quote(s, mapping)
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

    def writeLog(self, info):
      return standard.writeLog( self, info)

    def writeBlock(self, info):
      return standard.writeBlock( self, info)

    def writeError(self, info):
      return standard.writeError( self, info)

    #)


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
        filename = os.path.join(package_home(globals()),'plugins',path)
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
