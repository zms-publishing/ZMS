################################################################################
# zms.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Image import Image
from sys import *
import copy
import os
import shutil
import sys
import time
import transaction
import urllib
import zExceptions
# Product imports.
import _accessmanager
import _builder
import _confmanager
import _enummanager
import _fileutil
import _globals
import _importable
import _objattrs
import _xmllib
import _zcatalogmanager
import _zmsattributecontainer
import ZMSMetamodelProvider, ZMSFormatProvider, ZMSWorkflowProvider, ZMSWorkflowProviderAcquired
from zmscustom import ZMSCustom
from zmslinkcontainer import ZMSLinkContainer
from zmslinkelement import ZMSLinkElement
from zmslog import ZMSLog
from zmssqldb import ZMSSqlDb
from zmstrashcan import ZMSTrashcan

__all__= ['ZMS']


################################################################################
################################################################################
###
###  Common Function(s)
###
################################################################################
################################################################################

# ------------------------------------------------------------------------------
#  ZMS.recurse_cleanArtefacts:
#
#  Clean artefacts.
# ------------------------------------------------------------------------------
def recurse_cleanArtefacts( self, level=0):
  from OFS.CopySupport import absattr
  # Recursion.
  last_id = None
  for ob in self.objectValues():
    if absattr(self.id) == absattr(ob.id):
      print (" "*level)+"recurse_cleanArtefacts", ob.absolute_url(), ob.meta_type
      raise zExceptions.InternalError('InfiniteRecursionError')
    else:
      try:
        recurse_cleanArtefacts( ob, level+1)
      except "InfiniteRecursionError":
        print (" "*level)+"recurse_cleanArtefacts: clean artefact ", ob.absolute_url(), ob.meta_type
        self._delObject(absattr(ob.id), suppress_events=True)


# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionBuild:
#
#  Update version build.
# ------------------------------------------------------------------------------
def recurse_updateVersionBuild(docElmnt, self, REQUEST):
  message = ''

  ##### Build 131a: ZMS Teaser-Elements: Penetrance ####
  if getattr( docElmnt, 'build', '000') < '131':
    try:
      if self.getType() == 'ZMSTeaserElement':
        d = { '0': 'this', '1': 'sub_nav', '2': 'sub_all'}
        for ob_ver in self.getObjVersions():
          key = 'attr_penetrance'
          if hasattr( ob_ver, key):
            try:
              v = getattr( ob_ver, key)
              setattr( ob_ver, key, d.get( str( v), v))
            except:
              pass
    except:
      pass
  
  ##### Build 132a: Rename logo to zmi_logo ####
  if getattr( docElmnt, 'build', '000') < '132':
    try:
      self.zmi_logo = self.logo
      delattr( self, 'logo')
    except:
      pass
  
  ##### Build 133a: Create workflow-managers ####
  if getattr( docElmnt, 'build', '000') < '133':
    if self.meta_type == 'ZMS':
      autocommit = self.getConfProperty('ZMS.autocommit',1)
      nodes = self.getConfProperty('ZMS.workflow.nodes',['{$}'])
      acquired = self.getConfProperty('ZMS.workflow.acquire',0)
      activities = self.getConfProperty('ZMS.workflow.activities',[])
      transitions = self.getConfProperty('ZMS.workflow.transitions',[])
      if acquired or len(activities+transitions)>0:
        if acquired:
          manager = ZMSWorkflowProviderAcquired.ZMSWorkflowProviderAcquired(autocommit,nodes)
        else:
          manager = ZMSWorkflowProvider.ZMSWorkflowProvider(autocommit,nodes,activities,transitions)
        if manager.id in self.objectIds():
          self.manage_delObjects(manager.id)
        self._setObject( manager.id, manager)
      self.delConfProperty('ZMS.autocommit')
      self.delConfProperty('ZMS.workflow.nodes')
      self.delConfProperty('ZMS.workflow.acquire')
      self.delConfProperty('ZMS.workflow.activities')
      self.delConfProperty('ZMS.workflow.transitions')
  
  ##### Build 134c: Store object-state for modified sub-objects in version-container ####
  if getattr( docElmnt, 'build', '000') < '134':
    if not self.getAutocommit() and self.isVersionContainer():
      self.syncObjModifiedChildren( REQUEST)
  
  # Recursion.
  for ob in self.objectValues( self.dGlobalAttrs.keys()):
    recurse_updateVersionBuild(docElmnt, ob, REQUEST)
  
  ##### Build 130a: ZMS Standard-Objects ####
  if getattr( docElmnt, 'build', '000') < '130':
    if self.meta_type == 'ZMS':
      users = self.getConfProperty('ZMS.security.users',{})
      for user in users.keys():
        nodes = users[user].get('nodes',{})
        try:
          for node_ref in nodes.keys():
            node_ob = self.getLinkObj(node_ref)
            node_dict = nodes[node_ref]
            if node_ob:
              self.setLocalUser( user, node_ref, node_dict['roles'], node_dict['langs'])
        except:
          pass

  # Return with message.
  return message


# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionPatch:
#
#  Update version patch.
# ------------------------------------------------------------------------------
def recurse_updateVersionPatch(docElmnt, self, REQUEST):
  message = ''
  _confmanager.updateConf(self,REQUEST)
  self.getSequence()
  self.synchronizeObjAttrs()
  self.initRoleDefs()
  return message


# ------------------------------------------------------------------------------
#  initTheme:
# ------------------------------------------------------------------------------
def initTheme(self, theme, new_id, REQUEST):
  
  filename = _fileutil.extractFilename(theme)
  id = filename[:filename.rfind('.')]
  
  ### Store copy of ZEXP in INSTANCE_HOME/import-folder.
  filepath = INSTANCE_HOME + '/import/' + filename
  if theme.startswith('http://'):
    initutil = _globals.initutil()
    initutil.setConfProperty('HTTP.proxy',REQUEST.get('http_proxy',''))
    zexp = _globals.http_import( initutil, theme)
    _fileutil.exportObj( zexp, filepath)
  else:
    packagepath = package_home(globals()) + '/import/' + filename
    try: 
      os.stat(_fileutil.getOSPath(filepath))
    except OSError:
      shutil.copy( packagepath, filepath)
  
  ### Import theme from ZEXP.
  _fileutil.importZexp( self, filename)
  
  ### Assign folder-id.
  if id != new_id:
    self.manage_renameObject( id=id, new_id=new_id)
  
  ### Return new ZMS home instance.
  return getattr( self, new_id)


# ------------------------------------------------------------------------------
#  initZMS:
# ------------------------------------------------------------------------------
def initZMS(self, id, titlealt, title, lang, manage_lang, REQUEST):
  
  ### Constructor.
  obj = ZMS()
  obj.id = id
  self._setObject(obj.id, obj)
  obj = getattr(self,obj.id)
  
  ### Trashcan.
  trashcan = ZMSTrashcan()
  obj._setObject(trashcan.id, trashcan)
  
  ### Manager.
  manager = ZMSMetamodelProvider.ZMSMetamodelProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSFormatProvider.ZMSFormatProvider()
  obj._setObject( manager.id, manager)
  
  ### Init languages.
  obj.setLanguage(lang,REQUEST['lang_label'],'',manage_lang)
  
  ### Log.
  if REQUEST.get('zmslog'):
    zmslog = ZMSLog( copy_to_stdout=True, logged_entries=[ 'ERROR', 'INFO'])
    obj._setObject(zmslog.id, zmslog)
  
  ### Init Configuration.
  obj.setConfProperty('HTTP.proxy',REQUEST.get('http_proxy',''))
  obj.setConfProperty('ZMS.autocommit',1)
  obj.setConfProperty('ZMS.Version.autopack',2)
  
  ### Init zcatalog.
  obj.recreateCatalog(lang)
  
  ### Init ZMS object-model.
  conf = 'zms'
  if REQUEST.get('initialization',0) == 3:
    conf = 'zms2go'
  _confmanager.initConf(obj, conf, REQUEST)
  
  ### Init default-configuration.
  _confmanager.initConf(obj, 'default', REQUEST)
  
  ### Init Role-Definitions and Permission Settings.
  obj.initRoleDefs()
  
  ### Init Properties: active, titlealt, title.
  obj.setObjStateNew(REQUEST)
  obj.updateVersion(lang,REQUEST)
  obj.setObjProperty('active',1,lang)
  obj.setObjProperty('titlealt',titlealt,lang)
  obj.setObjProperty('title',title,lang)
  obj.onChangeObj(REQUEST,forced=1)
  
  ### Return new ZMS instance.
  return obj


# ------------------------------------------------------------------------------
#  initContent:
# ------------------------------------------------------------------------------
def initContent(self, filename, REQUEST):
  file = open(_fileutil.getOSPath(package_home(globals())+'/import/'+filename),'rb')
  _importable.importFile( self, file, REQUEST, _importable.importContent)
  file.close()


################################################################################
################################################################################
###   
###   Constructor
###   
################################################################################
################################################################################
manage_addZMSForm = PageTemplateFile('manage_addzmsform', globals())
def manage_addZMS(self, lang, manage_lang, REQUEST, RESPONSE):
  """ manage_addZMS """
  message = ''
  t0 = time.time()
  
  if REQUEST['btn'] == 'Add':
  
    ##### Add Theme ####
    homeElmnt = initTheme(self,REQUEST['theme'],REQUEST['folder_id'],REQUEST)
    if REQUEST.get('mobile',0)==1:
      tempId = 'myZMSmobile'
      tempMobile = initTheme(homeElmnt,'myZMSmobile.zexp',tempId,REQUEST)
      cb_copy_data = tempMobile.manage_cutObjects(tempMobile.objectIds())
      homeElmnt.manage_pasteObjects(cb_copy_data=cb_copy_data)
      homeElmnt.manage_delObjects(ids=[tempId])
    
    ##### Add ZMS ####
    titlealt = 'ZMS home'
    title = 'ZMS - ZOPE-based contentmanagement system for science, technology and medicine'
    obj = initZMS(homeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
    
    ##### Default content ####
    if REQUEST.get('initialization',0)==1:
      initContent(obj,'content.default.zip',REQUEST)
    elif REQUEST.get('initialization',0)==3:
      initContent(obj,'zms2go.default.zip',REQUEST)
    
    ##### E-Learning components ####
    if REQUEST.get('initialization',0)==2:
      # Create Home.
      lcmsHomeElmnt = initTheme(homeElmnt,'lcms.zexp','lcms',REQUEST)
      # Create LCMS.
      titlealt = 'LCMS'
      title = 'Learning Content Management System'
      lcms = initZMS(lcmsHomeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
      lcms.setLanguage('eng', 'English', 'ger', 'eng')
      # Init configuration.
      _confmanager.initConf(lcms, 'lcms', REQUEST)
      _confmanager.initConf(obj, 'lms', REQUEST)
      # Register Portal/Client.
      lcms.setConfProperty('Portal.Master',homeElmnt.id)
      obj.setConfProperty('Portal.Clients',[lcmsHomeElmnt.id])
      # Init content.
      initContent(lcms,'lcms.default.xml',REQUEST)
      initContent(obj,'lms.default.zip',REQUEST)
    
    ##### Configuration ####
    
    #-- QUnit
    if REQUEST.get('specobj_qunit',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'com.zms.test', REQUEST)
      # Init content.
      initContent(obj,'com.zms.test.content.xml',REQUEST)
    
    #-- Galleria
    if REQUEST.get('specobj_galleria',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'com.zms.jquery.galleria', REQUEST)
      # Init content.
      initContent(obj,'com.zms.jquery.galleria.content.zip',REQUEST)
    
    #-- Example Database
    if REQUEST.get('specobj_exampledb',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'exampledb', REQUEST)
      # Init content.
      initContent(obj,'exampledb.content.xml',REQUEST)
    
    #-- Bulletin Board
    if REQUEST.get('specobj_discussions',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'discussions', REQUEST)
      # Init content.
      initContent(obj,'discussions.content.xml',REQUEST)
    
    #-- Newsletter
    if REQUEST.get('specobj_newsletter',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'newsletter', REQUEST)
    
    #-- Calendar
    if REQUEST.get('specobj_calendar',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'calendar', REQUEST)

    ##### Access ####
    obj.synchronizePublicAccess()
    
    # Return with message.
    message = obj.getLangStr('MSG_INSERTED',manage_lang)%obj.meta_type
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    RESPONSE.redirect('%s/%s/manage?manage_tabs_message=%s'%(homeElmnt.absolute_url(),obj.id,urllib.quote(message)))
  
  else:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


def containerFilter(container):
  return container.meta_type == 'Folder'


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMS(
        ZMSCustom,
        _accessmanager.AccessManager,
        _builder.Builder,
        _confmanager.ConfManager,
        _objattrs.ObjAttrsManager,
        _zcatalogmanager.ZCatalogManager,
        ):

    # Version-Info.
    # -------------
    zms_build = '134'        # Internal use only, designates object model!
    zms_patch = 'c'          # Internal use only!

    # Properties.
    # -----------
    meta_type = meta_id = "ZMS"

    # Management Options.
    # -------------------
    def manage_options(self):
      pc = self.isPageContainer()
      root = self.getLevel() == 0
      opts = []
      opts.append({'label': 'TAB_EDIT',         'action': 'manage_main'})
      if pc:
        opts.append({'label': 'TAB_PROPERTIES',   'action': 'manage_properties'})
      opts.append({'label': 'TAB_ACCESS',       'action': 'manage_users'})
      opts.append({'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'})
      opts.append({'label': 'TAB_TASKS',        'action': 'manage_tasks'})
      opts.append({'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'})
      if not self.getAutocommit() or self.getHistory():
        opts.append({'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'})
      opts.append({'label': 'TAB_CONFIGURATION','action': 'manage_customize'})
      opts.append({'label': 'TAB_SEARCH',       'action': 'manage_search'})
      opts.append({'label': 'TAB_PREVIEW',      'action': 'preview_html'})
      return tuple(opts)

    # Management Permissions.
    # -----------------------
    zmi_logo__roles__ = None
    __administratorPermissions__ = (
        'manage_customize', 'manage_customizeSystem',
        'manage_changeLanguages', 'manage_customizeLanguagesForm',
        'manage_changeMetacmds', 'manage_customizeMetacmdForm',
        'manage_customizeDesign', 'manage_customizeDesignForm',
        )
    __authorPermissions__ = (
        'manage','manage_main','manage_main_iframe','manage_workspace',
        'manage_addZMSModule',
        'manage_deleteObjs','manage_undoObjs',
        'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
        'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
        'manage_ajaxDragDrop','manage_ajaxZMIActions',
        'manage_properties','manage_changeProperties','manage_changeTempBlobjProperty',
        'manage_search','manage_tasks',
        'manage_wfTransition', 'manage_wfTransitionFinalize',
        'manage_userForm', 'manage_user',
        'manage_importexport', 'manage_import', 'manage_export',
        )
    __userAdministratorPermissions__ = (
        'manage_users', 'manage_userProperties', 'manage_roleProperties', 'userdefined_roles', 
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        ('ZMS Author', __authorPermissions__),
        ('ZMS UserAdministrator', __userAdministratorPermissions__),
        )

    # Globals.
    # --------
    dGlobalAttrs = {
    'ZMS':{
                'obj_class':None},
    'ZMSCustom':{
                'obj_class':ZMSCustom},
    'ZMSLinkContainer':{
                'obj_class':ZMSLinkContainer,
                'constructor':'manage_addZMSLinkContainer'},
    'ZMSLinkElement':{
                'obj_class':ZMSLinkElement,
                'constructor':'manage_addzmslinkelementform'},
    'ZMSSqlDb':{
                'obj_class':ZMSSqlDb,
                'constructor':'manage_addzmssqldbform'},
    }

    # Interface.
    # ----------
    index_html = PageTemplateFile('zpt/ZMS/index', globals()) # index_html
    f_index_html = PageTemplateFile('zpt/ZMS/index', globals()) # index_html
    zmi_bodycontent_inactive = PageTemplateFile('zpt/ZMS/zmi_bodycontent_inactive', globals())
    zmi_body_content_sitemap = PageTemplateFile('zpt/ZMS/zmi_bodycontent_sitemap', globals())
    zmi_body_content_search = PageTemplateFile('zpt/ZMS/zmi_bodycontent_search', globals())
    zmi_body_content_not_found = PageTemplateFile('zpt/ZMS/zmi_bodycontent_not_found', globals())
    f_headDoctype = PageTemplateFile('zpt/ZMS/f_headdoctype', globals()) # Head.DOCTYPE
    f_headTitle = PageTemplateFile('zpt/ZMS/f_headtitle', globals()) # Head.Title
    f_headMeta_DC = PageTemplateFile('zpt/ZMS/f_headmeta_dc', globals()) # Head.Meta.DC (Dublic-Core))
    f_headMeta_Locale = PageTemplateFile('zpt/ZMS/f_headmeta_locale', globals()) # Head.Locale (Content-Type & Charset)
    f_standard_html_header = PageTemplateFile('zpt/ZMS/f_standard_html_header', globals())
    f_standard_html_footer = PageTemplateFile('zpt/ZMS/f_standard_html_footer', globals())
    headScript = PageTemplateFile('zpt/ZMS/headscript', globals()) # Head.Script
    headMeta = PageTemplateFile('zpt/ZMS/headmeta', globals()) # Head.Meta
    headCStyleSheet = PageTemplateFile('zpt/ZMS/headcstylesheet', globals()) # Head.CStyleSheet
    headCSS = PageTemplateFile('zpt/ZMS/headcstylesheet', globals()) # Head.CSS

    # Enumerations.
    # -------------
    enumManager = _enummanager.EnumManager()


    """
    ############################################################################
    ###
    ###   Constructor
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMS.__init__: 
    # --------------------------------------------------------------------------
    """
    Constructor.
    """
    def __init__(self):
      self.id = 'content'
      file = open(_fileutil.getOSPath(package_home(globals())+'/www/spacer.gif'),'rb')
      self.zmi_logo = Image(id='logo', title='', file=file.read())
      file.close()


    # --------------------------------------------------------------------------
    #  ZMS.initZMS: 
    # --------------------------------------------------------------------------
    def initZMS(self, container, id, titlealt, title, lang, manage_lang, REQUEST):
      return initZMS(container, id, titlealt, title, lang, manage_lang, REQUEST)


    # --------------------------------------------------------------------------
    #  ZMS.zms_version:
    #
    #  Get version.
    # --------------------------------------------------------------------------
    def zms_version(self):
      file = open(_fileutil.getOSPath(package_home(globals())+'/version.txt'),'r')
      rtn = file.read()
      file.close()
      return rtn

    # --------------------------------------------------------------------------
    #  ZMS.getDocumentElement
    # --------------------------------------------------------------------------
    """
    The root element of the site.
    """
    def getDocumentElement(self):
      return self

    # --------------------------------------------------------------------------
    #  ZMS.getAbsoluteHome
    # --------------------------------------------------------------------------
    def getAbsoluteHome(self):
      portalMaster = self.getPortalMaster()
      if portalMaster:
        return portalMaster.getAbsoluteHome()
      return self.getHome()

    """
    Returns the home-folder of the site.
    """
    def getHome(self):
      docElmnt = self.getDocumentElement()
      ob = docElmnt
      try:
        depth = 0
        while ob.meta_type != 'Folder': 
          if depth > sys.getrecursionlimit():
            raise zExceptions.InternalError('Maximum recursion depth exceeded')
          depth = depth + 1
          ob = ob.aq_parent
      except:
        try:
          ob = getattr( docElmnt, docElmnt.absolute_url().split( '/')[-2])
        except:
          ob = docElmnt.aq_parent
      return ob

    """
    Returns the trashcan of the site.
    """
    def getTrashcan(self):
      return self.objectValues(['ZMSTrashcan'])[0]

    """
    Returns new (unique) Object-ID.
    """
    def getNewId(self, id_prefix='e'):
      return '%s%i'%(id_prefix,self.getSequence().nextVal())

    """
    Returns Dublin-Core Meta-Attribute Coverage.
    """
    def getDCCoverage(self, REQUEST={}):
      return 'global.'+self.getPrimaryLanguage()



    ############################################################################
    #
    #   ZMS - Portals
    #
    ############################################################################

    """
    Returns portal-master, none if it does not exist.
    """
    def getPortalMaster(self):
      v = self.getConfProperty('Portal.Master','')
      if len(v) > 0:
        try:
          return getattr( self, v).content
        except:
          _globals.writeError(self, '[getPortalMaster]: %s not found!'%str(v))
      return None

    """
    Returns portal-clients, empty list if none exist.
    """
    def getPortalClients(self):
      docElmnts = []
      v = self.getConfProperty('Portal.Clients',[])
      if len(v) > 0:
        thisHome = self.getHome()
        for id in v:
          try:
            docElmnts.append(getattr(thisHome,id).content)
          except:
            _globals.writeError(self, '[getPortalClients]: %s not found!'%str(id))
      return docElmnts


    ############################################################################
    #
    #   ZMS - Versions
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.updateVersion:
    #
    #  Update version.
    # --------------------------------------------------------------------------
    def updateVersion(self, lang, REQUEST, maintenance=True):
      message = ''
      build = getattr( self, 'build', '000')
      patch = getattr( self, 'patch', '000')
      if build != self.zms_build:
        REQUEST.set('recurse_updateVersionBuild',True)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from build #%s%s to #%s%s...'%(build,patch,self.zms_build,self.zms_patch))
        message += recurse_updateVersionBuild( self, self, REQUEST)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from build #%s%s to #%s%s - Finished!'%(build,patch,self.zms_build,self.zms_patch))
        setattr( self, 'build', self.zms_build)
        transaction.commit()
        message += 'Synchronized object-model from build #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if build != self.zms_build or patch != self.zms_patch:
        REQUEST.set('recurse_updateVersionPatch',True)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from patch #%s%s to #%s%s...'%(build,patch,self.zms_build,self.zms_patch))
        message += recurse_updateVersionPatch( self, self, REQUEST)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from patch #%s%s to #%s%s - Finished!'%(build,patch,self.zms_build,self.zms_patch))
        setattr( self, 'patch', self.zms_patch)
        transaction.commit()
        message += 'Synchronized object-model from patch #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if maintenance:
        try:
          self.getTrashcan().run_garbage_collection()
        except:
          _globals.writeError( self, '[updateVersion]: can\'t run garbage collection')
      
      # Process clients.
      if message:
        for portalClient in self.getPortalClients():
          message += portalClient.updateVersion( lang, REQUEST, False)
      
      return message


    ############################################################################
    ###  
    ###   DOM-Methods
    ### 
    ############################################################################

    """
    The parent of this node. 
    All nodes except root may have a parent.
    """
    def getParentNode(self): 
      return None


    ############################################################################
    ###
    ###   XML-Builder
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    # Handler for XML-Builder (_builder.py)
    # --------------------------------------------------------------------------
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode, oRoot):
      _globals.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)
      
      # remove all ZMS-objects.
      self.manage_delObjects(self.objectIds(self.dGlobalAttrs.keys()))
      # remove all languages.
      for s_lang in self.getLangIds():
        self.delLanguage(s_lang)
      
      self.dTagStack = _globals.MyStack()
      self.dValueStack  = _globals.MyStack()
      
      # WORKAROUND! The member variable "aq_parent" does not contain the right 
      # parent object at this stage of the creation process (it will later on!). 
      # Therefore, we introduce a special attribute containing the parent 
      # object, which will be used by xmlGetParent() (see below).
      self.oParent = None

################################################################################