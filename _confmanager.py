################################################################################
# _confmanager.py
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
from cStringIO import StringIO
from AccessControl import ClassSecurityInfo
from App.Common import package_home
from DateTime.DateTime import DateTime
from OFS.CopySupport import absattr
from OFS.Image import Image
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
import ConfigParser
import Globals
import OFS.misc_
import os
import stat
import tempfile
import time
import urllib
import zExceptions
import zope.interface
# Product imports.
from IZMSConfigurationProvider import IZMSConfigurationProvider
from IZMSNotificationService import IZMSNotificationService
import IZMSMetamodelProvider, IZMSFormatProvider, IZMSCatalogAdapter, ZMSZCatalogAdapter
import _globals
import _exportable
import _fileutil
import _filtermanager
import _mediadb
import _multilangmanager
import _sequence
import _zopeutil
import zmslog


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Read system-configuration from $ZMS_HOME/etc/zms.conf
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class ConfDict:

    __confdict__ = None

    @classmethod
    def get(cls):
        if cls.__confdict__ is None:
            cls.__confdict__ = {'last_modified':long(DateTime().timeTime())}
            PRODUCT_HOME = os.path.dirname(os.path.abspath(__file__))
            for home in [PRODUCT_HOME,INSTANCE_HOME]:
              fp = os.path.join(home,'etc','zms.conf')
              if os.path.exists(fp):
                cfp = ConfigParser.ConfigParser()
                cfp.readfp(open(fp))
                for section in cfp.sections():
                    for option in cfp.options(section):
                        cls.__confdict__[section+'.'+option] = cfp.get( section, option)
        return cls.__confdict__

    @classmethod
    def forName(cls, name):
      d = name.rfind(".")
      clazzname = name[d+1:len(name)]
      mod = __import__(name[0:d], globals(), locals(), [clazzname])
      clazz = getattr(mod, clazzname)
      return clazz


"""
################################################################################
###
###   Initialization
###
################################################################################
"""

# ------------------------------------------------------------------------------
#  _confmanager.initConf:
# ------------------------------------------------------------------------------
def initConf(self, profile, remote=True):
  _globals.writeBlock( self, '[initConf]: profile='+profile)
  createIfNotExists = True
  files = self.getConfFiles(remote)
  for filename in files.keys():
    label = files[filename]
    if label.startswith(profile + '.') or label.startswith(profile + '-'):
      _globals.writeBlock( self, '[initConf]: filename='+filename)
      if filename.find('.zip') > 0:
        self.importConfPackage(filename,createIfNotExists)
      elif filename.find('.xml') > 0:
        self.importConf(filename,createIfNotExists=createIfNotExists)


# ------------------------------------------------------------------------------
#  _confmanager.updateConf:
# ------------------------------------------------------------------------------
def updateConf(self):
  createIfNotExists = False
  filenames = self.getConfFiles().keys()
  for filename in filenames:
    try:
      self.importConf(filename)
    except:
      pass


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ConfManager(
    _multilangmanager.MultiLanguageManager,
    _filtermanager.FilterManager,
    ):
    zope.interface.implements(
      IZMSMetamodelProvider.IZMSMetamodelProvider,
      IZMSFormatProvider.IZMSFormatProvider)

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Management Interface.
    # ---------------------
    manage_customize = PageTemplateFile('zpt/ZMS/manage_customize',globals())
    manage_customizeLanguagesForm = PageTemplateFile('zpt/ZMS/manage_customizelanguagesform',globals())
    manage_customizeFilterForm = PageTemplateFile('zpt/ZMS/manage_customizefilterform',globals())
    manage_customizeDesignForm = PageTemplateFile('zpt/ZMS/manage_customizedesignform',globals())


    # --------------------------------------------------------------------------
    #  ConfManager.importConfPackage:
    # --------------------------------------------------------------------------
    def importConfPackage(self, file, createIfNotExists=0):
      if type( file) is str:
        if file.startswith('http://'):
          file = StringIO( self.http_import(file))
        else:
          file = open(_fileutil.getOSPath(file),'rb')
      files = _fileutil.getZipArchive( file)
      for f in files:
        if not f.get('isdir'):
          self.importConf(f,createIfNotExists=createIfNotExists)


    # --------------------------------------------------------------------------
    #  ConfManager.getConfXmlFile:
    # --------------------------------------------------------------------------
    def getConfXmlFile(self, file):
      if type(file) is dict:
        filename = file['filename']
        xmlfile = StringIO( file['data'])
      elif type(file) is str and file.startswith('http://'):
        filename = _fileutil.extractFilename(file)
        xmlfile = StringIO( self.http_import(file))
      else:
        filename = _fileutil.extractFilename(file)
        xmlfile = open(_fileutil.getOSPath(file),'rb')
      return filename, xmlfile


    # --------------------------------------------------------------------------
    #  ConfManager.importConf:
    # --------------------------------------------------------------------------
    def importConf(self, file, createIfNotExists=0, syncIfNecessary=True):
      message = ''
      syncNecessary = False
      filename, xmlfile = self.getConfXmlFile( file)
      if not filename.startswith('._'): # ignore hidden files in ZIP created by MacOSX
        if filename.find('.charfmt.') > 0:
          self.format_manager.importCharformatXml(xmlfile, createIfNotExists)
        elif filename.find('.filter.') > 0:
          _filtermanager.importXml(self, xmlfile, createIfNotExists)
        elif filename.find('.metadict.') > 0:
          self.getMetaobjManager().importMetadictXml(xmlfile, createIfNotExists)
          syncNecessary = True
        elif filename.find('.metaobj.') > 0:
          self.getMetaobjManager().importMetaobjXml(xmlfile, createIfNotExists)
          syncNecessary = True
        elif filename.find('.workflow.') > 0:
          self.getWorkflowManager().importXml(xmlfile, createIfNotExists)
        elif filename.find('.metacmd.') > 0:
          self.getMetacmdManager().importXml(xmlfile, createIfNotExists)
        elif filename.find('.langdict.') > 0:
          _multilangmanager.importXml(self, xmlfile, createIfNotExists)
        elif filename.find('.textfmt.') > 0:
          self.format_manager.importTextformatXml(xmlfile, createIfNotExists)
        xmlfile.close()
      if syncIfNecessary and syncNecessary:
        self.synchronizeObjAttrs()
      return message


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.getPluginIds:
    # --------------------------------------------------------------------------
    def getPluginIds(self, path=[]):
      ids = []
      filepath = os.sep.join([package_home(globals()),'plugins']+path)
      for filename in os.listdir(filepath):
        path = os.sep.join([filepath,filename])
        if os.path.isdir(path) and len(os.listdir(path)) > 0:
          ids.append(filename)
      return ids


    # --------------------------------------------------------------------------
    #  Returns configuration-files from $ZMS_HOME/import-Folder
    # --------------------------------------------------------------------------
    security.declareProtected('ZMS Administrator', 'getConfFiles')
    def getConfFiles(self, remote=True, pattern=None, REQUEST=None, RESPONSE=None):
      """
      ConfManager.getConfFiles
      """
      filenames = {}
      filepaths = [
        self.Control_Panel.getINSTANCE_HOME()+'/etc/zms/import/',
        package_home(globals())+'/import/',]
      try:
        conf = open( filepaths[0]+'configure.zcml','r')
        _globals.writeBlock( self, "[getConfFiles]: Read from "+filepaths[0]+"configure.zcml")
      except:
        conf = open( filepaths[1]+'configure.zcml','r')
        _globals.writeBlock( self, "[getConfFiles]: Read from "+filepaths[0]+"configure.zcml")
      conf_xml = self.xmlParse( conf)
      for source in self.xmlNodeSet(conf_xml,'source'):
        location = source['attrs']['location']
        if location.startswith('http://'):
          if remote:
            try:
              remote_conf = self.http_import(location+'configure.zcml')
              remote_conf_xml = self.xmlParse( remote_conf)
              for remote_file in self.xmlNodeSet(remote_conf_xml,'file'):
                filename = remote_file['attrs']['id']
                if filename not in filenames.keys():
                  filenames[location+filename] = filename+' ('+remote_file['attrs']['title']+')'
            except:
              _globals.writeError( self, "[getConfFiles]: can't get conf-files from remote URL=%s"%location)
        else:
          for filepath in filepaths:
            if os.path.exists( filepath):
              for filename in os.listdir(filepath+location):
                path = filepath + filename
                mode = os.stat(path)[stat.ST_MODE]
                if not stat.S_ISDIR(mode):
                  if filename not in filenames:
                    filenames[path] = filename
      conf.close()
      # Filter.
      if pattern is not None:
        for k in filenames.keys():
          if k.find(pattern) < 0:
            del filenames[k]
          else:
            v = filenames[k]
            i = v.find(' ')
            if i < 0:
              i = len(v)
            v = v[:v.find(pattern)]+v[i:]
            filenames[k] = v
      # Return.
      if REQUEST is not None and \
         RESPONSE is not None:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/xml; charset=utf-8'
        filename = 'getConfFiles.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        return self.getXmlHeader() + self.toXmlString( filenames)
      else:
        return filenames


    """
    ############################################################################
    ###
    ###   Configuration-Properties Getters
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.getSequence:
    #
    #  Returns sequence.
    # --------------------------------------------------------------------------
    def getSequence(self):
      id = 'acl_sequence'
      exists = id in self.objectIds(['Sequence'])
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        startvalue = 0
        if exists:
          ob = getattr(self,id)
          startvalue = ob.value
          self.manage_delObjects(ids=[id])
        ob = portalMaster.getSequence()
        if ob.value < startvalue:
          ob.value = startvalue
      else:
        if not exists:
          sequence = _sequence.Sequence()
          self._setObject(sequence.id, sequence)
        ob = getattr(self,id)
      return ob

    # --------------------------------------------------------------------------
    #  ConfManager.getMediaDb:
    #
    #  Returns mediadb.
    # --------------------------------------------------------------------------
    def getMediaDb(self):
      for ob in self.getDocumentElement().objectValues(['MediaDb']):
        return ob
      return None


    # --------------------------------------------------------------------------
    #  ConfManager.getThemes:
    #
    #  Returns list of theme-folders.
    # --------------------------------------------------------------------------
    def getThemes(self):
      obs = []
      for ob in self.getHome().objectValues():
        if isinstance(ob,Folder) and 'standard_html' in ob.objectIds():
          obs.append(ob)
      return obs


    # --------------------------------------------------------------------------
    #  ConfManager.getResourceFolders:
    #
    #  Returns list of resource-folders.
    # --------------------------------------------------------------------------
    def getResourceFolders(self):
      obs = []
      ids = self.getConfProperty('ZMS.resourceFolders','instance,common').split(',')
      home = self.getHome()
      if len(self.getConfProperty('ZMS.theme','')) > 0:
        home = getattr(home,self.getConfProperty('ZMS.theme',''))
      if '*' in ids:
        ids.extend( map(lambda x: x.id, filter(lambda x: x.id not in ids, home.objectValues(['Folder','Filesystem Directory View']))))
      for id in ids:
        if id == '*':
          obs.append(home)
        else:
          container = getattr( home, id, None)
          if container is not None and len(container.objectValues(['ZMS']))==0:
            obs.append(container)
      return obs


    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheet:
    #
    #  Returns stylesheet.
    # --------------------------------------------------------------------------
    def getStylesheet(self, id=None):
      stylesheets = self.getStylesheets()
      if id is None:
        return stylesheets[0]
      else:
        for css in stylesheets:
          if absattr( css.id) == id:
            return css

    # --------------------------------------------------------------------------
    #  ConfManager.getStylesheets:
    #
    #  Returns list of stylesheets.
    # --------------------------------------------------------------------------
    def getStylesheets(self):
      ids = []
      obs = []
      for container in self.getResourceFolders():
        for folder in [ getattr( container, 'css', None), container]:
          if folder is not None:
            for ob in folder.objectValues(['DTML Method', 'DTML Document', 'File', 'Filesystem File']):
              id = absattr( ob.id)
              path = ob.getPhysicalPath()
              if len(filter(lambda x: x.endswith('css'), path)) > 0 and id not in ids:
                ids.append( id)
                if id == self.getConfProperty('ZMS.stylesheet','style.css'):
                  obs.insert( 0, ob)
                else:
                  obs.append( ob)
      return obs


    """
    ############################################################################
    ###
    ###   Configuration-Tab Options
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ConfManager.customize_manage_options:
    # --------------------------------------------------------------------------
    customize_manage_options__roles__ = None
    def customize_manage_options(self):
      l = []
      l.append({'label':'TAB_EDIT','action':'manage_main'})
      l.append({'label':'TAB_SYSTEM','action':'manage_customize'})
      l.append({'label':'TAB_LANGUAGES','action':'manage_customizeLanguagesForm'})
      for ob in self.objectValues():
        if IZMSConfigurationProvider in list(zope.interface.providedBy(ob)):
          for d in ob.manage_sub_options():
            l.append(self.operator_setitem(d.copy(),'action',ob.id+'/'+d['action']))
      l.append({'label':'TAB_FILTER','action':'manage_customizeFilterForm'})
      l.append({'label':'TAB_DESIGN','action':'manage_customizeDesignForm'})
      return l


    ############################################################################
    ###
    ###   Configuration-Properties
    ###
    ############################################################################

    """
    Returns configuration-manager.
    """
    def getConfManager(self):
      return self


    """
    Returns property from configuration.
    @rtype: C{dict}
    """
    def getConfProperties(self, prefix=None, inherited=False, REQUEST=None):
      """ ConfManager.getConfProperties """
      d = getattr( self, '__attr_conf_dict__', {})
      if REQUEST is not None:
        import base64
        prefix = base64.b64decode(prefix)
        r = {}
        for k in filter(lambda x:x.startswith(prefix+'.'),d.keys()):
          r[k] = d[k]
        return self.str_json(r)
      if inherited:
        d = d.keys()
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          d.extend(filter(lambda x:x not in d,portalMaster.getConfProperties(prefix,inherited,REQUEST)))
      return d


    """
    Removes property from configuration.
    
    @param key: The key.
    @type key: C{string}
    @return None
    """
    security.declareProtected('ZMS Administrator', 'delConfProperty')
    def delConfProperty(self, key):
      self.setConfProperty(key,None)


    """
    Returns property from request (used to get zope-request-properties,
    e.g. SERVER_URL oder AUTHENTICATED_USER).
    
    @param key: The key.
    @type key: C{string}
    @param default: The default-value.
    @type default: C{any}
    @rtype: C{any}
    """
    def getReqProperty(self, key, default=None, REQUEST=None):
      """ ConfManager.getReqProperty """
      authorized = REQUEST['AUTHENTICATED_USER'].has_role('Authenticated')
      if not authorized:
        raise zExceptions.Unauthorized
      return REQUEST.get(key,default)


    """
    Returns property from configuration.
    
    @param key: The key.
    @type key: C{string}
    @param default: The default-value.
    @type default: C{any}
    @rtype: C{any}
    """
    def getConfProperty(self, key, default=None, REQUEST=None):
      """ ConfManager.getConfProperty """
      if REQUEST is not None:
        import base64
        key = base64.b64decode(key)
      if OFS.misc_.misc_.zms['confdict'].has_key(key):
        default = OFS.misc_.misc_.zms['confdict'].get(key)
      value = default
      confdict = self.getConfProperties()
      if confdict.has_key(key):
        value = confdict.get(key)
      elif key is not None and not key.startswith('Portal.'):
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          value = portalMaster.getConfProperty( key, default)
      return value 


    """
    Sets property into configuration.
    
    @param key: The key.
    @type key: C{string}
    @param value: The value.
    @type value: C{any}
    @return None
    """
    security.declareProtected('ZMS Administrator', 'setConfProperty')
    def setConfProperty(self, key, value):
      d = self.getConfProperties()
      if value is None:
        if d.has_key(key):
          del d[key]
      else:
        d[key] = value
      self.__attr_conf_dict__ = d
      self.__attr_conf_dict__ = self.__attr_conf_dict__.copy()


    ############################################################################
    # Compile lesscss.
    #
    # Linux: lessc {in} > {out}
    # Win32: "C:\Program Files (x86)\lessc_0\lessc.exe" {in}
    # @see http://digitalpbk.com/less-css/less-css-compiler-windows-lesscexe
    ############################################################################
    security.declareProtected('ZMS Author', 'compile_lesscss')
    def compile_lesscss(self):
      """ ConfManager.compile_lesscss """
      rtn = []
      request = self.REQUEST
      tempfolder = tempfile.mktemp()
      root = self.getHome()
      for id in root.objectIds(['Folder']):
        _exportable.exportFolder( self, root, tempfolder, id, request)
      path = _fileutil.readPath(tempfolder,data=False)
      for file in path:
        filename = file['filename']
        if filename.endswith('.less'):
          filepath = file['local_filename']
          outpath = filepath.replace(filename,filename.replace('.less','.css'))
          physical_path = outpath[len(tempfolder)+1:].split(os.sep)
          container = root
          while container is not None and len(physical_path) > 1:
            container = getattr(container,physical_path[0],None)
            physical_path = physical_path[1:]
          if container is not None:
            context = getattr(container,physical_path[0],None)
            if context is not None:
              t0 = time.time()
              command = self.getConfProperty('InstalledProducts.lesscss','')
              command = command.replace('{in}',filepath)
              command = command.replace('{out}',outpath)
              _globals.writeBlock( self, '[compile_lesscss]: command=%s'%command)
              exitVal = os.system(command)
              if exitVal == 0:
                exitCode = 'OK'
                out = open(outpath,'r')
                filedata = out.read()
                out.close()
                context.manage_edit(title=context.title,content_type=context.content_type,filedata=filedata)
              else:
                exitCode = 'ERROR'
              rtn.append('%s [%s] %.2fsecs.'%(filepath[len(tempfolder):],exitCode,time.time()-t0))
      _fileutil.remove(tempfolder,deep=1)
      return '\n'.join(rtn)


    """
    ############################################################################
    ###
    ###   Configuration-System
    ###
    ############################################################################
    """

    ############################################################################
    #  Customize system properties.
    ############################################################################
    def manage_customizeSystem(self, btn, key, lang, REQUEST, RESPONSE=None):
      """ ConfManager.manage_customizeSystem """
      
      message = ''
      params = []
      
      ##### Import ####
      if key == 'Import':
        if btn == 'Import':
          f = REQUEST['file']
          createIfNotExists = 1
          if f:
            filename = f.filename
            self.importConfPackage( f, createIfNotExists)
          else:
            filename = REQUEST['init']
            self.importConfPackage( filename, createIfNotExists)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      ##### History ####
      elif key == 'History':
        old_active = self.getConfProperty('ZMS.Version.active',0)
        new_active = REQUEST.get('active',0)
        old_nodes = self.getConfProperty('ZMS.Version.nodes',['{$}'])
        new_nodes = self.string_list(REQUEST.get('nodes',''))
        self.setConfProperty('ZMS.Version.active',new_active)
        self.setConfProperty('ZMS.Version.nodes',new_nodes)
        nodes = []
        if old_active == 1 and new_active == 0:
          nodes = old_nodes
        if old_active == 1 and new_active == 1:
          nodes = self.difference_list( old_nodes, self.getConfProperty('ZMS.Version.nodes',['{$}']))
        for node in nodes:
          ob = self.getLinkObj( node)
          if ob is not None:
            message += '[%s: %i]'%(node,ob.packHistory())
        message = self.getZMILangStr('MSG_CHANGED')+message
      
      ##### Clients ####
      elif key == 'Clients':
        if btn == 'Change':
          home = self.getHome()
          s = REQUEST.get('portal_master','').strip()
          if s != home.id:
            self.setConfProperty('Portal.Master',s)
          l = []
          portal_clients = REQUEST.get('portal_clients',[])
          if type(portal_clients) is not list:
            portal_clients  = [portal_clients]
          portal_clients = map(lambda x:(int(x[:x.find(':')]),x[x.find(':')+1:]),portal_clients)
          portal_clients.sort()
          portal_clients = map(lambda x:x[1],portal_clients)
          for id in portal_clients:
            folder = getattr(home,id,None)
            if folder is not None:
              for node in folder.objectValues('ZMS'):
                node.setConfProperty('Portal.Master',home.id)
                l.append(id)
          self.setConfProperty('Portal.Clients',l)
          message = self.getZMILangStr('MSG_CHANGED')
      
      ##### MediaDb ####
      elif key == 'MediaDb':
        if btn == 'Create':
          location = REQUEST['mediadb_location'].strip()
          _mediadb.manage_addMediaDb(self,location)
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Pack':
          message = _mediadb.manage_packMediaDb(self)
        elif btn == 'Remove':
          message = _mediadb.manage_delMediaDb(self)
      
      ##### Custom ####
      elif key == 'Custom':
        k = REQUEST.get( 'conf_key', '')
        if btn == 'Change':
          v = REQUEST.get( 'conf_value', '')
          self.setConfProperty( k, v)
          if REQUEST.get('portal_clients'):
            for portalClient in self.getPortalClients():
              portalClient.setConfProperty( k, v)
          params.append('conf_key')
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Delete':
          self.delConfProperty( k)
          if REQUEST.get('portal_clients'):
            for portalClient in self.getPortalClients():
              portalClient.delConfProperty( k)
          message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      ##### InstalledProducts ####
      elif key == 'InstalledProducts':
        if btn == 'Change':
          self.setConfProperty('InstalledProducts.lesscss',REQUEST.get('lesscss',''))
          self.setConfProperty('InstalledProducts.pil.thumbnail.max',REQUEST.get('pil_thumbnail_max',self.getConfProperty('InstalledProducts.pil.thumbnail.max')))
          self.setConfProperty('InstalledProducts.pil.hires.thumbnail.max',REQUEST.get('pil_hires_thumbnail_max',self.getConfProperty('InstalledProducts.pil.hires.thumbnail.max')))
          message = self.getZMILangStr('MSG_CHANGED')
        elif btn == 'Import':
          zmsext = REQUEST.get('zmsext','')
          # hand over import to Deployment Library if available
          revobj = self.getMetaobjRevision('zms3.deployment')
          revreq = '0.2.0'
          if revobj >= revreq:
            target = 'manage_deployment'
            target = self.url_append_params(target, {'zmsext': zmsext})
            return RESPONSE.redirect(target)
          # otherwise import now
          from _globals import writeError
          target = 'manage_customize'
          isProcessed = False
          try:
            ZMSExtension  = self.extutil()
            filesToImport = ZMSExtension.getFilesToImport(zmsext, self.getDocumentElement())
            if len(filesToImport)>0:
              for f in filesToImport:
                self.importConf(f, createIfNotExists=True, syncIfNecessary=False)
              self.synchronizeObjAttrs()
              isProcessed = True
          except:
            isProcessed = False
          if isProcessed:
            message = self.getZMILangStr('MSG_IMPORTED')%('<code class="alert-success">'+self.str_item(ZMSExtension.getFiles(zmsext))+'</code>')
            target = self.url_append_params(target, {'manage_tabs_message': message})
          else:
            message = self.getZMILangStr('MSG_EXCEPTION') 
            message += ': <code class="alert-danger">%s</code>'%('No conf files found.')
            target = self.url_append_params(target, {'manage_tabs_error_message': message})
            writeError(self, '[ConfManager.manage_customizeSystem] No conf files found.')
          return RESPONSE.redirect(target + '#%s'%key)
        elif btn == 'ImportExample':
          zmsext = REQUEST.get('zmsext','')
          target = 'manage_main'
          ZMSExtension  = self.extutil()
          isProcessed = False
          try:
            if ZMSExtension.getExample(zmsext) is not None:
              destination = self.getLinkObj(self.getConfProperty('ZMS.Examples',{}))
              if destination is None:
                destination = self.getDocumentElement()
              ZMSExtension.importExample(zmsext,destination,REQUEST)
              isProcessed = True
          except:
            isProcessed = False
          if isProcessed:
            return True
          else:
            return False
        elif btn == 'InstallTheme':
          zmsext = REQUEST.get('zmsext','')
          target = 'manage_main'
          ZMSExtension  = self.extutil()
          print "###InstallTheme:", zmsext
          if ZMSExtension.installTheme(self, zmsext):
            return True
          else:
            return False

      ##### Instance ####
      elif key == 'Instance':
        if btn == 'Restart':
          target = 'manage_customize'
          
          if 'ZMANAGED' in os.environ:
            from Lifetime import shutdown
            from cgi import escape
            from _globals import writeBlock
            try:
              user = '"%s"' % REQUEST['AUTHENTICATED_USER']
            except:
              user = 'unknown user'
            writeBlock(self, " Restart requested by %s" % user)
            shutdown(1)
            message = self.getZMILangStr('ZMS3 instance restarted.')
            target = self.url_append_params(target, {'manage_tabs_message': message})
            return """<html>
            <head><meta HTTP-EQUIV=REFRESH CONTENT="10; URL=%s">
            </head>
            <body>Restarting...</body></html>
            """ % escape(target + '#%s'%key, 1)
          else:       
            return "No daemon."
      
      ##### Manager ####
      elif key == 'Manager':
        if btn == 'Add':
          meta_type = REQUEST.get('meta_type','')
          if meta_type == 'Sequence':
            obj = _sequence.Sequence()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
          elif meta_type == 'ZMSLog':
            obj = zmslog.ZMSLog()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
          else:
            obj = ConfDict.forName(meta_type+'.'+meta_type)()
            self._setObject(obj.id, obj)
            message = 'Added '+meta_type
        elif btn == 'Remove':
          ids = REQUEST.get('ids',[])
          if ids:
            message = 'Removed '+', '.join(ids)
            self.manage_delObjects(ids=ids)
      
      # Return with message.
      if RESPONSE:
        d = {'lang': lang,'manage_tabs_message': message}
        for param in params:
          d[param] = REQUEST.get( param, '')
        return RESPONSE.redirect( self.url_append_params( 'manage_customize', d) + '#%s'%key)
      
      return message


    ############################################################################
    #  ConfManager.manage_customizeDesign: 
    #
    #  Customize design properties.
    ############################################################################
    def manage_customizeDesign(self, btn, lang, REQUEST, RESPONSE):
      """ ConfManager.manage_customizeDesign """
      message = ''
      home = self.getHome()
      
      # Save.
      # -----
      if btn == self.getZMILangStr('BTN_SAVE'):
        id = REQUEST.get('id','')
        self.setConfProperty('ZMS.theme',id)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn == self.getZMILangStr('BTN_DELETE'):
        ids = REQUEST.get('ids',[])
        home.manage_delObjects(ids)
        message = self.getZMILangStr('MSG_DELETED')%int(len(ids))
      
      # Import.
      # -------
      elif btn == self.getZMILangStr('BTN_IMPORT'):
        file = REQUEST['file']
        filename = _fileutil.extractFilename(file.filename)
        id = filename[:filename.rfind('.')]
        filepath = INSTANCE_HOME+'/import/'+filename
        _fileutil.exportObj( file, filepath)
        home.manage_importObject(filename)
        _fileutil.remove( filepath)
        message = self.getZMILangStr('MSG_IMPORTED')%('<code class="alert-success">'+filename+'</code>')
      
      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        newId = REQUEST['newId']
        newTitle = REQUEST['newTitle']
        home.manage_addFolder(id=newId,title=newTitle)
        folder = getattr(home,newId)
        _zopeutil.addPageTemplate(folder, id='standard_html', title='', data='<!DOCTYPE html>\n<htmltal:define="zmscontext options/zmscontext">\n</html>')
        message = self.getZMILangStr('MSG_INSERTED')%newId
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeDesignForm?lang=%s&manage_tabs_message=%s'%(lang,message))


    ############################################################################
    ###
    ###   Interface IZMSWorkflowProvider: delegate to workflow_manager
    ###
    ############################################################################

    def getWfActivities(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getActivities()

    def getWfActivitiesIds(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getActivityIds()

    def getWfActivity(self, id):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return None
      return workflow_manager.getActivity(id)

    def getWfTransitions(self):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return []
      return workflow_manager.getTransitions()

    def getWfTransition(self, id):
      workflow_manager = getattr(self,'workflow_manager',None)
      if workflow_manager is None:
        return None
      return workflow_manager.getTransition(id)


    ############################################################################
    ###
    ###   Interface IZMSMetamodelProvider: delegate
    ###
    ############################################################################

    def getMetaobjManager(self):
      manager = getattr(self,'metaobj_manager',None)
      if manager is None:
        class DefaultMetaobjManager:
          def importXml(self, xml): pass
          def getMetaobjId(self, name): return None
          def getMetaobjIds(self, sort=1, excl_ids=[]): return []
          def getMetaobj(self, id): return None
          def getMetaobjAttrIds(self, meta_id, types=[]): return []
          def getMetaobjAttrs(self, meta_id,  types=[]): return []
          def getMetaobjAttr(self, id, attr_id, syncTypes=['resource']): return None
          def getMetaobjAttrIdentifierId(self, meta_id): return None
          def notifyMetaobjAttrAboutValue(self, meta_id, key, value): return None
        manager = DefaultMetaobjManager()
      return manager

    def getMetaobjRevision(self, id):
      return self.getMetaobjManager().getMetaobjRevision( id)
    
    def getMetaobjId(self, name):
      return self.getMetaobjManager().getMetaobjId( name)

    def getMetaobjIds(self, sort=1, excl_ids=[]):
      return self.getMetaobjManager().getMetaobjIds( sort, excl_ids)

    def getMetaobj(self, id):
      return self.getMetaobjManager().getMetaobj( id)

    def getMetaobjAttrIds(self, meta_id, types=[]):
      return self.getMetaobjManager().getMetaobjAttrIds( meta_id, types)

    def getMetaobjAttrs(self, meta_id,  types=[]):
      return self.getMetaobjManager().getMetaobjAttrs( meta_id)

    def getMetaobjAttr(self, id, attr_id, syncTypes=['resource']):
      return self.getMetaobjManager().getMetaobjAttr(id,attr_id,syncTypes)

    def getMetaobjAttrIdentifierId(self, meta_id):
      return self.getMetaobjManager().getMetaobjAttrIdentifierId( meta_id)

    def notifyMetaobjAttrAboutValue(self, meta_id, key, value):
      return self.getMetaobjManager().notifyMetaobjAttrAboutValue( meta_id, key, value)


    ############################################################################
    ###
    ###   Interface IZMSMetacmdProvider: delegate
    ###
    ############################################################################

    def getMetacmdManager(self):
      ### updateVersion
      commands = self.getConfProperty('ZMS.custom.commands',[])
      if len(commands)>0:
        meta_type = 'ZMSMetacmdProvider'
        obj = ConfDict.forName(meta_type+'.'+meta_type)(commands)
        self._setObject( obj.id, obj)
        self.delConfProperty('ZMS.custom.commands')
      ###
      metacmd_manager = getattr(self,'metacmd_manager',None)
      if metacmd_manager is None:
        class DefaultManager:
          def importXml(self, xml): pass
          def getMetaCmdDescription(self, id=None, name=None): return None
          def getMetaCmd(self, id=None, name=None): return None
          def getMetaCmdIds(self, sort=True): return []
          def getMetaCmds(self, context=None, stereotype='', sort=True): return []
        metacmd_manager = DefaultManager()
      return metacmd_manager

    def getMetaCmdDescription(self, id=None, name=None):
       """ getMetaCmdDescription """
       return self.getMetacmdManager().getMetaCmdDescription(id,name)

    def getMetaCmd(self, id=None, name=None):
       return self.getMetacmdManager().getMetaCmd(id,name)

    def getMetaCmdIds(self, sort=1):
       return self.getMetacmdManager().getMetaCmdIds(sort)

    def getMetaCmds(self, context=None, stereotype='', sort=True):
      return self.getMetacmdManager().getMetaCmds(context,stereotype,sort)


    ############################################################################
    ###
    ###   Interface IZMSWorkflowProvider: delegate
    ###
    ############################################################################

    def getWorkflowManager(self):
      manager = filter(lambda x:absattr(x.id)=='workflow_manager',self.getDocumentElement().objectValues())
      if len(manager)==0:
        class DefaultManager:
          def importXml(self, xml): pass
          def writeProtocol(self, log): pass
          def getAutocommit(self): return True
          def getActivities(self): return []
          def getActivityIds(self): return []
          def getActivity(self, id): return None
          def getActivityDetails(self, id): return None
          def getTransitions(self): return []
          def getTransitionIds(self): return []
        manager = [DefaultManager()]
      return manager[0]


    ############################################################################
    ###
    ###   Interface IZMSFormatProvider: delegate
    ###
    ############################################################################

    def getFormatManager(self):
      return self.format_manager

    def getTextFormatDefault(self):
      return self.getFormatManager().getTextFormatDefault()

    def getTextFormat(self, id, REQUEST):
      return self.getFormatManager().getTextFormat(id, REQUEST)

    def getTextFormats(self, REQUEST):
      return self.getFormatManager().getTextFormats(REQUEST)

    def getCharFormats(self):
      return self.getFormatManager().getCharFormats()


    ############################################################################
    ###
    ###   Interface IZMSCatalogAdapter: delegate
    ###
    ############################################################################

    def getCatalogAdapter(self):
      for ob in self.objectValues():
        if IZMSCatalogAdapter.IZMSCatalogAdapter in list(zope.interface.providedBy(ob)):
          return ob
      adapter = ZMSZCatalogAdapter.ZMSZCatalogAdapter()
      self._setObject( adapter.id, adapter)
      adapter = getattr(self,adapter.id)
      adapter.setIds(['ZMSFolder','ZMSDocument','ZMSFile'])
      adapter.setAttrIds(['title','titlealt','attr_dc_description','standard_html'])
      adapter.addConnector('ZMSZCatalogConnector')
      return adapter


    ############################################################################
    ###
    ###   Interface IZMSLocale: delegate
    ###
    ############################################################################

    def getLocale(self):
      return self

    """
    def get_manage_langs(self):
      return self.getLocale().get_manage_langs()

    def get_manage_lang(self):
      return self.getLocale().get_manage_lang()

    def getZMILangStr(self, key, REQUEST=None, RESPONSE=None):
      return self.getLocale().getZMILangStr( key)

    def getLangStr(self, key, lang=None):
      return self.getLocale().getLangStr( key, lang)

    def getPrimaryLanguage(self):
      return self.getLocale().getPrimaryLanguage()
    """


# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ConfManager)

################################################################################