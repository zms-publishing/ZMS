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
from OFS.Folder import Folder
import collections
import os
import sys
import time
import zExceptions
# Product imports.
from Products.zms import standard
from Products.zms import _accessmanager
from Products.zms import _builder
from Products.zms import _confmanager
from Products.zms import _enummanager
from Products.zms import _fileutil
from Products.zms import _importable
from Products.zms import _mediadb
from Products.zms import _objattrs
from Products.zms import _zcatalogmanager
from Products.zms import ZMSMetacmdProvider, ZMSMetamodelProvider, ZMSFormatProvider
from Products.zms.zmscustom import ZMSCustom
from Products.zms.zmslinkelement import ZMSLinkElement
from Products.zms.zmslog import ZMSLog
from Products.zms.zmsobject import ZMSObject
from Products.zms.zmssqldb import ZMSSqlDb
from Products.zms.zmstrashcan import ZMSTrashcan

__all__= ['ZMS']


################################################################################
#
# ZMS Object Index
#
################################################################################

import zope.event
from zope.container.contained import ObjectAddedEvent
from zope.container.contained import ObjectMovedEvent
from zope.container.contained import ObjectRemovedEvent

def subscriber(event):
  if isinstance(event, ObjectAddedEvent):
    if isinstance(event.object, ZMSObject):
      if isinstance(event.newParent, ZMSObject):
        # trigger object-added event
        standard.triggerEvent(event.object, "*.ObjectAdded")
  elif isinstance(event, ObjectMovedEvent):
    if isinstance(event.object, ZMSObject):
      if isinstance(event.newParent, ZMSObject):
        # trigger object-moved event
        standard.triggerEvent(event.object, "*.ObjectMoved")
      elif event.newParent is None:
        standard.triggerEvent(event.object, "*.ObjectRemoved")
  elif isinstance(event, ObjectRemovedEvent):
    if isinstance(event.object, ZMSObject):
      # trigger object-removed event
      standard.triggerEvent(event.object, "*.ObjectRemoved")
zope.event.subscribers.append(subscriber)


################################################################################
#
# Common Function(s)
#
################################################################################

# ------------------------------------------------------------------------------
#  importTheme:
# ------------------------------------------------------------------------------
def importTheme(self, theme):
  if not theme or theme == 'conf:acquire':
    return None
  if theme.startswith('conf:'):
    id = theme.split('/').pop()
    _confmanager.initConf(self, theme)
  else:
    filename = _fileutil.extractFilename(theme)
    id = filename[:filename.rfind('-')]
    filepath = package_home(globals()) + '/import/'
    path = filepath + filename
    self.importConf(path)
  return id


# ------------------------------------------------------------------------------
#  initZMS:
# ------------------------------------------------------------------------------
# A new ZMS node can be initalized as a stand-alone client (master) or 
# as subordinated client acquiring content models and sharing the zmsindex.
# Use a request variable 'acquire' =  1 to initalize ZMS as a client
def initZMS(self, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init = False):

  ### Constructor.
  obj = ZMS()
  obj.id = id
  self._setObject(obj.id, obj)
  obj = getattr(self, obj.id)

  ### Trashcan.
  trashcan = ZMSTrashcan()
  obj._setObject(trashcan.id, trashcan)

  ### Manager.
  manager = ZMSMetamodelProvider.ZMSMetamodelProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSMetacmdProvider.ZMSMetacmdProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSFormatProvider.ZMSFormatProvider()
  obj._setObject( manager.id, manager)

  ### Init languages.
  obj.setLanguage(lang, REQUEST['lang_label'], '', manage_lang)

  ### Log.
  if REQUEST.get('zmslog_init', 0)==1:
    zmslog = ZMSLog( copy_to_stdout=True, logged_entries=[ 'ERROR', 'INFO'])
    obj._setObject(zmslog.id, zmslog)

  ### Init Configuration.
  if REQUEST.get('http_proxy'):
    obj.setConfProperty('HTTP.proxy', REQUEST.get('http_proxy', ''))
    obj.setConfProperty('HTTPS.proxy', REQUEST.get('http_proxy', ''))
  obj.setConfProperty('ZMS.autocommit', 1)

  if REQUEST.get('acquire', 0) == 0:
    ### Init ZMS default content-model.
    minimal_init = minimal_init == True or REQUEST.get('minimal_init', 0) == 1
    if minimal_init:
      _confmanager.initConf(obj, 'conf:com.zms.foundation')
      _confmanager.initConf(obj, 'conf:com.zms.foundation.theming')
    else:
      _confmanager.initConf(obj, 'conf:com.zms.foundation*')
    if REQUEST.get('zcatalog_init', 0) == 1:
      _confmanager.initConf(obj, 'conf:com.zms.catalog.zcatalog')

  else:
    ### Acquire content-model from master.
    master = hasattr(self.aq_parent,'content') and (self.aq_parent.content or self.aq_parent.content.getPortalMaster()) or None
    if master:
      obj.setConfProperty('Portal.Master',master.getHome().id)
      masterMetaObjIds_ignore = ['ZMSIndexZCatalog','com.zms.index'] # Ignore obsolete object classes.
      if REQUEST.get('zcatalog_init', 0) == 0:
        masterMetaObjIds_ignore.extend(['com.zms.catalog.zcatalog','zcatalog_connector','zcatalog_page'])
      masterMetaObjIds = [id for id in master.getMetaobjIds() if id not in masterMetaObjIds_ignore and id is not None]
      masterMetaObjs = map(lambda x: master.getMetaobj(x), masterMetaObjIds)
      masterMetaObjPackages = obj.sort_list(obj.distinct_list(map(lambda x: x.get('package'), masterMetaObjs)))
      if len(obj.breadcrumbs_obj_path(True))>1:
        for client in obj.breadcrumbs_obj_path(True)[1:]:
          for id in masterMetaObjPackages:
            if id and id.strip():
              client.metaobj_manager.acquireMetaobj(id)
        client.synchronizeObjAttrs()
      obj.setConfProperty('ZMS.theme', master.getConfProperty('ZMS.theme'))

  ### Init ZMS index.
  obj.getZMSIndex()

  ### Init ZMS default actions.
  _confmanager.initConf(obj, 'conf:manage_tab_*')

  ### Init default-configuration.
  ### ###################################
  ### CAVE: 
  ### zcatalog-connecter shall not 
  ### get initialized by default again.
  ### ###################################
  _confmanager.initConf(obj, ':default')

  ### Init Role-Definitions and Permission Settings.
  obj.initRoleDefs()

  ### Init Properties: active, titlealt, title.
  obj.setObjStateNew(REQUEST)
  obj.setObjProperty('active', 1, lang)
  obj.setObjProperty('titlealt', titlealt, lang)
  obj.setObjProperty('title', title, lang)
  obj.onChangeObj(REQUEST, forced=1)
  
  # Init Object-Children
  obj.initObjChildren(REQUEST)
  
  ### Return new ZMS instance.
  return obj


# ------------------------------------------------------------------------------
#  initContent:
# ------------------------------------------------------------------------------
def initContent(self, filename, REQUEST):
  file = open(_fileutil.getOSPath(package_home(globals())+'/import/'+filename), 'rb')
  _importable.importFile( self, file, REQUEST, _importable.importContent)
  file.close()


################################################################################
#
# Constructor
#
################################################################################
manage_addZMSForm = PageTemplateFile('manage_addzmsform', globals())
def manage_addZMS(self, lang, manage_lang, REQUEST, RESPONSE):
  """ manage_addZMS """
  message = ''
  t0 = time.time()

  if REQUEST['btn'] == 'Add':

    ##### Add Home ####
    homeElmnt = Folder(REQUEST['folder_id'])
    self._setObject(homeElmnt.id, homeElmnt)
    homeElmnt = [x for x in self.objectValues() if x.id == homeElmnt.id][0]
    
    ##### Add ZMS ####
    titlealt = 'ZMS home'
    title = 'ZMS - Python-based Content Management System for Science, Technology and Medicine'
    obj = initZMS(homeElmnt, 'content', titlealt, title, lang, manage_lang, REQUEST)
    
    ##### Add Theme ####
    theme_none = 'conf:acquire'
    if REQUEST.get('theme',theme_none) != 'conf:acquire':
      theme_id = importTheme(obj,REQUEST.get('theme','conf:acquire'))
      # Set theme property: id may not contain dots.
      obj.setConfProperty('ZMS.theme',theme_id.replace('.','_'))

    ##### Default content ####
    if REQUEST.get('content_init', 0)==1:
      initContent(obj, 'content.default.zip', REQUEST)

    ##### Configuration ####

    # Initialize catalog adapter / connector.
    if REQUEST.get('zcatalog_init', 0)==1:
      #-- Search GUI
      _confmanager.initConf(obj, 'conf:com.zms.catalog.zcatalog')
      catalog_adapter = obj.getCatalogAdapter() 
      catalog_connector = catalog_adapter.add_connector('zcatalog_connector')
      catalog_connector.manage_init()
      try:
        catalog_adapter.reindex(catalog_connector, obj, recursive=True)
      except:
        standard.writeBlock( self, '[catalog_adapter]: : \'RequestContainer\' object has no \'attribute reindex\'')

    # Initialize access.
    obj.synchronizePublicAccess()

    # Return with message.
    message = obj.getLangStr('MSG_INSERTED', manage_lang)%obj.meta_type
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    RESPONSE.redirect('%s/%s/manage?manage_tabs_message=%s'%(homeElmnt.absolute_url(), obj.id, standard.url_quote(message)))

  else:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


def containerFilter(container):
  return container.meta_type == 'Folder'


################################################################################
#
#  Class
#
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
    meta_type = meta_id = 'ZMS'

    # Management Permissions.
    # -----------------------
    __viewPermissions__ = (
        'manage', 'manage_main', 'manage_container', 'manage_workspace', 'manage_menu',
        )
    __administratorPermissions__ = (
        'manage_customize',
        'manage_customizeInstalledProducts',
        'manage_customizeSystem',
        'manage_changeLanguages', 'manage_customizeLanguagesForm',
        'manage_customizeDesign', 'manage_customizeDesignForm',
        'manage_change_refs'
        )
    __authorPermissions__ = (
        'preview_html', 'preview_top_html',
        'manage_addZMSModule',
        'manage_deleteObjs', 'manage_undoObjs',
        'manage_moveObjUp', 'manage_moveObjDown', 'manage_moveObjToPos',
        'manage_cutObjects', 'manage_copyObjects', 'manage_pasteObjs',
        'manage_ajaxDragDrop', 'manage_ajaxZMIActions',
        'manage_properties', 'manage_changeProperties', 'manage_changeTempBlobjProperty',
        'manage_wfTransition', 'manage_wfTransitionFinalize',
        'manage_RefForm',
        'manage_userForm', 'manage_user',
        'manage_importexport', 'manage_import', 'manage_export',
        'manage_executeMetacmd',
        )
    __userAdministratorPermissions__ = (
        'manage_users', 'manage_users_sitemap', 'manage_userProperties', 'manage_roleProperties', 'userdefined_roles',
        )
    __ac_permissions__=(
        ('View', __viewPermissions__),
        ('ZMS Administrator', __administratorPermissions__),
        ('ZMS Author', __authorPermissions__),
        ('ZMS UserAdministrator', __userAdministratorPermissions__),
        )

    # Globals.
    # --------
    dGlobalAttrs = {
    'ZMS': {
                'obj_class':None},
    'ZMSCustom': {
                'obj_class':ZMSCustom},
    'ZMSLinkContainer': {
                },
    'ZMSLinkElement': {
                'obj_class':ZMSLinkElement},
    'ZMSSqlDb': {
                'obj_class':ZMSSqlDb,
                'constructor':'manage_addzmssqldbform'},
    }

    # Interface.
    # ----------
    swagger_ui = PageTemplateFile('zpt/ZMS/swagger-ui', globals()) # swagger-ui
    openapi_yaml = PageTemplateFile('zpt/ZMS/openapi_yaml', globals()) # openapi.yaml
    index_html = PageTemplateFile('zpt/ZMS/index', globals()) # index_html
    f_index_html = PageTemplateFile('zpt/ZMS/index', globals()) # index_html
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


    # --------------------------------------------------------------------------
    #  ZMS.initZMS:
    # --------------------------------------------------------------------------
    def initZMS(self, container, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init = False):
      return initZMS(container, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init)


    # --------------------------------------------------------------------------
    #  ZMS.manage_addMediaDb:
    # --------------------------------------------------------------------------
    def manage_addMediaDb(self, location, REQUEST=None, RESPONSE=None):
      _mediadb.manage_addMediaDb(self, location, REQUEST, RESPONSE)


    # --------------------------------------------------------------------------
    #  ZMS.zms_version:
    #
    #  Get version.
    # --------------------------------------------------------------------------
    def zms_version(self, custom=False):
      file = open(_fileutil.getOSPath(package_home(globals())+'/version.txt'),'r')
      rtn = file.read()
      file.close()
      zms_custom_version = os.environ.get('ZMS_CUSTOM_VERSION', '')
      if custom and zms_custom_version != '':
        rtn += f'&nbsp;(<samp id="zms_custom_version">{zms_custom_version}</samp>)'
        # Generate revisions and custom version gathering commit hashes of git submodules
        # see Lines 37-46 unibe-cms/.github/workflows/build-and-push.yml
        revisions = _fileutil.getOSPath('/app/revisions.txt')
        if os.path.exists(revisions):
            file = open(revisions, 'r')
            zms_submodule_revisions = file.read()
            file.close()
            rtn += f"""
                <span class="d-inline-block" data-toggle="popover"
                    title="Git revisions"
                    data-content="{zms_submodule_revisions}">
                    <i class="fab fa-git-square fa-lg"></i>
                </span>
                <script>
                    $(function () {{
                        $('[data-toggle="popover"]').popover();
                        // CAVEAT: Slicing below relies on commit hashes at https://github.com/idasm-unibe-ch/unibe-cms/tree/...
                        const zms_custom_version = $('#zms_custom_version').text().replaceAll('(', '').replaceAll(')', '');
                        const github_link = zms_custom_version.substr(zms_custom_version.indexOf('https://github.com'), zms_custom_version.length);
                        const version_str = zms_custom_version.substr(0, zms_custom_version.indexOf('https://github.com')).trim();
                        if (github_link.indexOf('https://github.com') == 0) {{
                            $('#zms_custom_version').html('<a href="'+github_link+'" title="'+github_link.slice(0, 58)+'" target="_blank">'+version_str+'</a>');
                        }}
                    }})
                </script>
                <style>
                    .popover {{
                        max-width: unset !important;
                    }}
                    .popover-body {{
                        white-space: pre-line;
                        width: auto;
                        max-width:fit-content;
                        font-size: smaller;
                    }}
                </style>
                """
      if custom and os.path.exists(_fileutil.getOSPath(package_home(globals())+'/../../.git/FETCH_HEAD')):
        file = open(_fileutil.getOSPath(package_home(globals())+'/../../.git/FETCH_HEAD'),'r')
        FETCH_HEAD = file.read()
        file.close()
        FETCH_HEAD = FETCH_HEAD[0:7]
        rtn += (f'<a title="ZMS commits on github.com" target="_blank" '
                f'href="https://github.com/zms-publishing/ZMS/commits/main"> git#{FETCH_HEAD}</a>')
      return rtn

    # --------------------------------------------------------------------------
    #  ZMS.getDocumentElement
    # --------------------------------------------------------------------------
    """
    The document-element of the site.
    """
    def getDocumentElement(self):
      return self

    # --------------------------------------------------------------------------
    #  ZMS.getRootElement
    # --------------------------------------------------------------------------
    """
    The root element of the site.
    """
    def getRootElement(self):
      doc_elmnt = self
      while True:
        portal_mstr = doc_elmnt.getPortalMaster()
        if portal_mstr is None:
          break
        doc_elmnt = portal_mstr
      return doc_elmnt

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
      return '%s%i'%(id_prefix, self.getSequence().nextVal())

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
      v = self.get_conf_properties().get('Portal.Master', '')
      if v:
        try:
          return getattr( self, v).content
        except:
          pass
      return None

    """
    Returns portal-clients, empty list if none exist.
    """
    def getPortalClients(self):
      docElmnts = []
      v = self.get_conf_properties().get('Portal.Clients', [])
      if v:
        home = self.getHome()
        for id in v:
          try:
            docElmnts.append(getattr(home, id).content)
          except:
            pass
      return docElmnts


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
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode):
      standard.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)

      # remove all ZMS-objects.
      ids = self.objectIds(list(self.dGlobalAttrs))
      if ids:
        self.manage_delObjects(ids=ids)

      # initialize stacks.
      self.dTagStack = collections.deque()
      self.dValueStack  = collections.deque()

      # WORKAROUND! The member variable "aq_parent" does not contain the right
      # parent object at this stage of the creation process (it will later on!).
      # Therefore, we introduce a special attribute containing the parent
      # object, which will be used by xmlGetParent() (see below).
      self.oParent = None

    # Hook: ZMS.mode.maintenance
    def __before_publishing_traverse__(self, object, request):
      """
      Maintenance mode can be set by adding the ZMS configuration
      key ZMS.mode.maintenance=1. The maintenance mode prevents 
      editing content and returns an error: 503 Service Unavailable.
      To show a specific message the Zope object standard_error_message 
      should be customized, e.g. like this::

        <tal:block
            tal:define="
              errtype python:options.get('error_type',None);
              errvalue python:options.get('error_value',None)"
            tal:condition="python:errtype=='HTTPServiceUnavailable' and str(errvalue)=='Maintenance'">
            <h2>ZMS Maintenance active</h2>
            <button onclick="history.back()">Go Back</button>
        </tal:block>
      """
      path = request.path
      maintenance_conf_key = 'ZMS.mode.maintenance'
      maintenance_mode = bool(self.getConfProperty(maintenance_conf_key, False))
      is_maintenance_mode_change = 'manage_customizeSystem' in path and request.get('conf_key') == maintenance_conf_key
      # Only allow ZMS.mode.maintenance changes in maintenance mode.
      if maintenance_mode and not is_maintenance_mode_change:
        import transaction
        import ZODB.Connection
        t = transaction.get()
        def maintenance_hook():
          # Check if there are ZODB changes - if there is a ZODB.Connection.Connection resource manager.
          # Transaction._resources contains all resource managers which commit their changes sequentially:
          # https://github.com/zopefoundation/transaction/blob/6d4785159c277067f2ec95158884870a92660220/src/transaction/_transaction.py#L421
          for resource in t._resources:
            if isinstance(resource, ZODB.Connection.Connection):
              # Reset response content type (WGSIPublisher sets it to "text/plain" per default if unset)
              # and lock status (the zException does not get mapped correctly)
              request.response.setHeader('Content-Type', 'text/html;charset=utf-8')
              request.response.setStatus(503, lock=True)
              raise zExceptions.HTTPServiceUnavailable('Maintenance')
        t.addBeforeCommitHook(maintenance_hook)

################################################################################


# Workaround for an incompatibility with zope.browserresource 3.11.0 and newer
# which requires an ETagAdapter to be provided by the application.
# Sent a patch upstream to lift this requirement, at which point this
# workaround could be removed:
#  https://github.com/zopefoundation/zope.browserresource/pull/1
try:
    from zope.browserresource.interfaces import IFileResource, IETag
    from zope.publisher.interfaces.browser import IBrowserRequest
    from zope.interface import implementer

    from zope.component import adapter, provideAdapter

    @adapter(IFileResource, IBrowserRequest)
    @implementer(IETag)
    class NoETagAdapter(object):

        def __init__(self, context, request):
            pass

        def __call__(self, mtime, content):
            return None

        @classmethod
        def register(cls):
            provideAdapter(cls)

except ImportError:
    # zope.browserresource before 3.11.0
    class NoETagAdapter(object):
        @classmethod
        def register(cls):
            pass
