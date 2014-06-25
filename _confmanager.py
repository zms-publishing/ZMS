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
import IZMSMetamodelProvider, IZMSFormatProvider
import _globals
import _exportable
import _fileutil
import _filtermanager
import _mediadb
import _metacmdmanager
import _multilangmanager
import _sequence
import zmslog


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Read system-configuration from $ZMS_HOME/etc/zms.conf
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class ConfDict:

    __confdict__ = None
    __clazzes__ = {}

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
    def set_constructor(cls, key, clazz):
      cls.__clazzes__[key] = clazz

    @classmethod
    def get_constructor(cls, key):
      return cls.__clazzes__[key]


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
def initConf(self, profile, REQUEST):
  _globals.writeBlock( self, '[initConf]: profile='+profile)
  createIfNotExists = True
  files = self.getConfFiles()
  for filename in files.keys():
    label = files[filename]
    if label.startswith(profile + '.'):
      _globals.writeBlock( self, '[initConf]: filename='+filename)
      if filename.find('.zip') > 0:
        self.importConfPackage(filename,REQUEST,createIfNotExists)
      elif filename.find('.xml') > 0:
        self.importConf(filename,REQUEST,createIfNotExists)


# ------------------------------------------------------------------------------
#  _confmanager.updateConf:
# ------------------------------------------------------------------------------
def updateConf(self, REQUEST):
  createIfNotExists = False
  filenames = self.getConfFiles().keys()
  for filename in filenames:
    self.importConf(filename,REQUEST,createIfNotExists)


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ConfManager(
    _multilangmanager.MultiLanguageManager,
    _metacmdmanager.MetacmdManager,
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
    addZMSCustomForm = PageTemplateFile('addzmscustomform',globals()) 
    addZMSLinkElementForm = PageTemplateFile('addzmslinkelementform',globals()) 
    addZMSSqlDbForm = PageTemplateFile('addzmssqldbform',globals()) 
    manage_customize = PageTemplateFile('zpt/ZMS/manage_customize',globals())
    manage_customizeLanguagesForm = PageTemplateFile('zpt/ZMS/manage_customizelanguagesform',globals())
    manage_customizeMetacmdForm = PageTemplateFile('zpt/metacmd/manage_customizeform',globals()) 
    manage_customizeFilterForm = PageTemplateFile('zpt/ZMS/manage_customizefilterform',globals())
    manage_customizeDesignForm = PageTemplateFile('zpt/ZMS/manage_customizedesignform',globals())


    # --------------------------------------------------------------------------
    #  ConfManager.importConfPackage:
    # --------------------------------------------------------------------------
    def importConfPackage(self, file, REQUEST, createIfNotExists=0):
      if type( file) is str:
        if file.startswith('http://'):
          file = StringIO( self.http_import(file))
        else:
          file = open(_fileutil.getOSPath(file),'rb')
      files = _fileutil.getZipArchive( file)
      for f in files:
        if not f.get('isdir'):
          self.importConf(f,REQUEST,createIfNotExists)


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
    def importConf(self, file, REQUEST, createIfNotExists=0):
      message = ''
      filename, xmlfile = self.getConfXmlFile( file)
      if filename.find('.charfmt.') > 0:
        self.format_manager.importCharformatXml(xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.filter.') > 0:
        _filtermanager.importXml(self, xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.metadict.') > 0:
        self.metaobj_manager.importMetadictXml(xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.metaobj.') > 0:
        self.metaobj_manager.importMetaobjXml(xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.metacmd.') > 0:
        _metacmdmanager.importXml(self, xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.langdict.') > 0:
        _multilangmanager.importXml(self, xmlfile, REQUEST, createIfNotExists)
      elif filename.find('.textfmt.') > 0:
        self.format_manager.importTextformatXml(xmlfile, REQUEST, createIfNotExists)
      xmlfile.close()
      self.synchronizeObjAttrs()
      return message


    # --------------------------------------------------------------------------
    #  Returns configuration-files from $ZMS_HOME/import-Folder
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ZMS Administrator')
    def getConfFiles(self, pattern=None, REQUEST=None, RESPONSE=None):
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
    #  ConfManager.getResourceFolders:
    #
    #  Returns list of resource-folders.
    # --------------------------------------------------------------------------
    def getResourceFolders(self):
      obs = []
      ids = self.getConfProperty('ZMS.resourceFolders','instance,common').split(',')
      if '*' in ids:
        ids.extend( map(lambda x: x.id, filter(lambda x: x.id not in ids, self.getHome().objectValues(['Folder']))))
      for id in ids:
        if id == '*':
          obs.append(self.getHome())
        else:
          container = getattr( self, id, None)
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
            for ob in folder.objectValues(['DTML Method', 'DTML Document', 'File']):
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
      l.append({'label':'TAB_METACMD','action':'manage_customizeMetacmdForm'})
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
    def getConfProperties(self):
      return getattr( self, '__attr_conf_dict__', {})


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
    Returns property from request.
    
    @param key: The key.
    @type key: C{string}
    @param default: The default-value.
    @type default: C{any}
    @rtype: C{any}
    """
    def getReqProperty(self, key, default=None, REQUEST=None):
      """ ConfManager.getReqProperty """
      if REQUEST is not None:
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
          authorized = REQUEST['AUTHENTICATED_USER'].has_role('Authenticated')
          if not authorized:
              raise zExceptions.Unauthorized
      if OFS.misc_.misc_.zms['confdict'].has_key(key):
          default = OFS.misc_.misc_.zms['confdict'].get(key)
      return self.getConfProperties().get( key, default)


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
            self.importConfPackage( f, REQUEST, createIfNotExists)
          else:
            filename = REQUEST['init']
            self.importConfPackage( filename, REQUEST, createIfNotExists)
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
          s = REQUEST.get('portal_master','').strip()
          if s != self.getHome().id:
            self.setConfProperty('Portal.Master',s)
          l = []
          for s in REQUEST.get('portal_clients','').split('\n'):
            s = s.strip()
            if s in self.getHome().objectIds(['Folder']):
              l.append(s)
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
          self.setConfProperty('InstalledProducts.pil.thumbnail.max',REQUEST.get('pil_thumbnail_max',100))
          self.setConfProperty('InstalledProducts.pil.hires.thumbnail.max',REQUEST.get('pil_hires_thumbnail_max',600))
          message = self.getZMILangStr('MSG_CHANGED')
      
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
          elif meta_type in ['ZMSWorkflowProvider','ZMSWorkflowProviderAcquired']:
            obj = ConfDict.get_constructor(meta_type)()
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


    """
    ############################################################################
    ###
    ###   Configuration-Design
    ###
    ############################################################################
    """
    
    def get_zmi_logo(self, REQUEST=None, RESPONSE=None):
      """ get_zmi_logo """
      if self.zmi_logo is not None:
        return self.zmi_logo.data
      return ''

    ############################################################################
    #  ConfManager.manage_customizeDesign: 
    #
    #  Customize design properties.
    ############################################################################
    def manage_customizeDesign(self, btn, lang, REQUEST, RESPONSE):
      """ ConfManager.manage_customizeDesign """
      message = ''
      cssId = REQUEST.get('cssId','')
      
      # Ex-/Import.
      # -----------
      if btn in [ self.getZMILangStr('BTN_EXPORT'), self.getZMILangStr('BTN_IMPORT')]:
        #-- Theme.
        home = self.getHome()
        home_id = home.id
        temp_folder = self.temp_folder
        # Init exclude-ids.
        excl_ids = []
        # Add clients-folders to exclude-ids.
        for folder in home.objectValues( ['Folder']):
          if len( folder.objectValues( ['ZMS'])) > 0:
            excl_ids.append( absattr( folder.id))
        # Add content-object artefacts to exclude-ids.
        for metaObjId in self.getMetaobjIds():
          for metaObjAttrId in self.getMetaobjAttrIds( metaObjId):
            metaObjAttr = self.getMetaobjAttr(metaObjId,metaObjAttrId)
            if metaObjAttr['type'] in self.metaobj_manager.valid_zopetypes:
              excl_ids.append( metaObjAttrId)
        # Filter ids.
        ids = filter( lambda x: x not in excl_ids, home.objectIds(self.metaobj_manager.valid_zopetypes))
        if btn == self.getZMILangStr('BTN_EXPORT'):
          if home_id in temp_folder.objectIds():
            temp_folder.manage_delObjects(ids=[home_id])
          temp_folder.manage_addFolder(id=home_id,title=home.title_or_id())
          folder = getattr(temp_folder,home_id)
          home.manage_copyObjects(ids,REQUEST)
          folder.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
          return RESPONSE.redirect( self.url_append_params('%s/manage_exportObject'%temp_folder.absolute_url(),{'id':home_id,'download:int':1}))
        if btn == self.getZMILangStr('BTN_IMPORT'):
          v = REQUEST['theme']
          temp_filename = _fileutil.extractFilename( v.filename)
          temp_id = temp_filename[:temp_filename.rfind('.')]
          filepath = INSTANCE_HOME+'/import/'+temp_filename
          _fileutil.exportObj( v, filepath)
          if temp_id in temp_folder.objectIds():
            temp_folder.manage_delObjects(ids=[temp_id])
          temp_folder.manage_importObject( temp_filename)
          folder = getattr( temp_folder, temp_id)
          home.manage_delObjects(ids=ids)
          folder.manage_copyObjects(folder.objectIds(),REQUEST)
          home.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
          _fileutil.remove( filepath)
          temp_folder.manage_delObjects(ids=[temp_id])
      
      # Save.
      # -----
      if btn == self.getZMILangStr('BTN_SAVE'):
        #-- Stylesheet.
        if REQUEST.has_key('cssId'):
          if REQUEST.get('default'):
            self.setConfProperty('ZMS.stylesheet',REQUEST.get('cssId'))
          css = self.getStylesheet( REQUEST.get('cssId'))
          data = REQUEST.get('stylesheet')
          title = css.title
          css.manage_edit(data,title)
          self.parse_stylesheet()
          message = self.getZMILangStr('MSG_CHANGED')
        #-- Sitemap.
        if REQUEST.has_key('attr_layoutsitemap'):
          if len(REQUEST['attr_layoutsitemap'])>0:
            self.attr_layoutsitemap = int(REQUEST['attr_layoutsitemap'])
          elif hasattr(self,'attr_layoutsitemap'):
            delattr(self,'attr_layoutsitemap')
          message = self.getZMILangStr('MSG_CHANGED')
      
      # Upload.
      # -------
      elif btn == self.getZMILangStr('BTN_UPLOAD'):
        #-- ZMI Logo.
        self.zmi_logo = Image(id='zmi_logo', title='', file='')
        self.zmi_logo.manage_upload(REQUEST['file'],REQUEST)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeDesignForm?lang=%s&manage_tabs_message=%s&cssId=%s'%(lang,message,cssId))


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
      return self.metaobj_manager

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