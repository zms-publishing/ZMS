"""
zms.py - ZMS Root Object and Lifecycle Management

This module provides the core ZMS (Zope Management System) root content object
and lifecycle event handling for the ZMS publishing platform.
The module encapsulates:
  - B{Root Content Object}: The L{ZMS} class serves as the top-level content
    container combining configuration management, content editing capabilities,
    and search indexing functionality.
  - B{Lifecycle Event Handling}: The L{subscriber} function dispatches Zope
    container lifecycle events (object addition, movement, removal) to the
    internal ZMS event framework, enabling custom business logic triggers
    throughout the object hierarchy.
  - B{Site Initialization}: The L{initZMS} function handles creation and
    configuration of new ZMS sites, supporting both standalone master sites
    and client sites that acquire their content model from a portal master.
  - B{Theme Management}: The L{importTheme} function imports or acquires
    configured themes for newly created sites.
  - B{Content Import}: The L{initContent} function imports initial site content
    from bundled archive files.
  - B{Management Interface}: The L{manage_addZMS} function provides the factory
    method for creating top-level ZMS installations through the Zope add form.

The ZMS class inherits from multiple managers providing specific functionality:
  - ZMSCustom: Custom user extensions
  - AccessManager: Permission and role management
  - Builder: XML content model building
  - ConfManager: Configuration property management
  - ObjAttrsManager: Object attribute management
  - ZCatalogManager: Search catalog integration

This module also includes a workaround for zope.browserresource compatibility
to provide ETag adapter functionality required by zope.browserresource 3.11.0+.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""


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

import zope.event
from zope.container.contained import ObjectAddedEvent
from zope.container.contained import ObjectMovedEvent
from zope.container.contained import ObjectRemovedEvent


def subscriber(event):
  """
  Dispatch ZMS object lifecycle events to the internal event framework.

  @param event: Zope container lifecycle event.
  @type event: zope.lifecycleevent.interfaces.IObjectEvent
  """
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


def importTheme(self, theme):
  """
  Import or acquire the configured theme for a newly created site.

  @param self: ZMS site that receives the theme configuration.
  @type self: ZMS
  @param theme: Theme package identifier or import source.
  @type theme: str
  @return: Identifier of the imported theme, or C{None} when the theme is
      acquired from a portal master.
  @rtype: str | None
  """
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


def initZMS(self, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init = False):
  """
  Create and initialize a new ZMS site below the given container.

  A new site can either be initialized as a standalone master site or as a
  client that acquires its content model from a portal master when the request
  variable C{acquire} is set.

  @param self: Container that receives the new ZMS site.
  @type self: OFS.ObjectManager.ObjectManager
  @param id: Identifier of the created ZMS object.
  @type id: str
  @param titlealt: Alternative title shown in the management interface.
  @type titlealt: str
  @param title: Human readable title of the site.
  @type title: str
  @param lang: Primary content language.
  @type lang: str
  @param manage_lang: Management interface language.
  @type manage_lang: str
  @param REQUEST: HTTP request with initialization options.
  @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest
  @param minimal_init: Initialize only the minimal default configuration.
  @type minimal_init: bool
  @return: Newly created and initialized ZMS site.
  @rtype: ZMS
  """

  obj = ZMS()
  obj.id = id
  self._setObject(obj.id, obj)
  obj = getattr(self, obj.id)

  # Add the built-in trashcan used for soft deletion.
  trashcan = ZMSTrashcan()
  obj._setObject(trashcan.id, trashcan)

  # Register the default metamodel, metacmd, and format managers.
  manager = ZMSMetamodelProvider.ZMSMetamodelProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSMetacmdProvider.ZMSMetacmdProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSFormatProvider.ZMSFormatProvider()
  obj._setObject( manager.id, manager)

  obj.setLanguage(lang, REQUEST['lang_label'], '', manage_lang)

  if REQUEST.get('zmslog_init', 0)==1:
    zmslog = ZMSLog( copy_to_stdout=True, logged_entries=[ 'ERROR', 'INFO'])
    obj._setObject(zmslog.id, zmslog)

  if REQUEST.get('http_proxy'):
    obj.setConfProperty('HTTP.proxy', REQUEST.get('http_proxy', ''))
    obj.setConfProperty('HTTPS.proxy', REQUEST.get('http_proxy', ''))
  obj.setConfProperty('ZMS.autocommit', 1)

  if REQUEST.get('acquire', 0) == 0:
    # Initialize the default content model for standalone sites.
    minimal_init = minimal_init == True or REQUEST.get('minimal_init', 0) == 1
    if minimal_init:
      _confmanager.initConf(obj, 'conf:com.zms.foundation')
      _confmanager.initConf(obj, 'conf:com.zms.foundation.theming')
    else:
      _confmanager.initConf(obj, 'conf:com.zms.foundation*')
    if REQUEST.get('zcatalog_init', 0) == 1:
      _confmanager.initConf(obj, 'conf:com.zms.catalog.zcatalog')

  else:
    # Acquire the content model and theme from the portal master.
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

  obj.getZMSIndex()

  # Keep the historic default configuration order so the catalog connector is
  # not initialized implicitly a second time.
  _confmanager.initConf(obj, ':default')

  obj.initRoleDefs()

  obj.setObjStateNew(REQUEST)
  obj.setObjProperty('active', 1, lang)
  obj.setObjProperty('titlealt', titlealt, lang)
  obj.setObjProperty('title', title, lang)
  obj.onChangeObj(REQUEST, forced=1)
  
  # Init Object-Children
  obj.initObjChildren(REQUEST)
  
  return obj

def createZMS(context, id, name, REQUEST):
  # Create the folder that contains the new client root.
  home = Folder(id)
  context._setObject(home.id, home)
  home = [x for x in context.objectValues() if x.id == home.id][0]
  lang = REQUEST['lang ']
  manage_lang = REQUEST['manage_lang']
  titlealt = '%s home'%name
  title = '%s - Python-based Content Management System for Science, Technology and Medicine'%name
  return initZMS(home, 'content', titlealt, title, lang, manage_lang, REQUEST)

def init_content(self, filename, REQUEST):
  """
  Import initial site content from a bundled archive.

  @param self: ZMS site that receives the imported content.
  @type self: ZMS
  @param filename: Name of the import archive below the product import folder.
  @type filename: str
  @param REQUEST: Active HTTP request.
  @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest
  """
  with open(_fileutil.getOSPath(package_home(globals())+'/import/'+filename), 'rb') as file:
    _importable.importFile( self, file, REQUEST, _importable.importContent)

def init_multisite(context, depth, clients, prefix='client', REQUEST=None):
  """
  Initialize a multisite content structure with the given depth and number of clients.

  @param context: ZMS site that receives the multisite content structure.
  @type context: ZMS
  @param depth: Depth of the multisite folder hierarchy.
  @type depth: int
  @param clients: Number of client folders at each level.
  @type clients: int
  @param REQUEST: Active HTTP request.
  @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest
  """
  for i in range(clients):
    id = '%s%i'%(prefix,i)
    name = id.capitalize()
    content = createZMS(context, id, name, REQUEST)
    if REQUEST.get('content_init', 0)==1:
      init_content(content, 'content.default.zip', REQUEST)
    if depth > 0:
      home = content.aq_parent
      init_multisite(home, depth-1, clients, id, REQUEST)

  
manage_addZMSForm = PageTemplateFile('manage_addzmsform', globals())
def manage_addZMS(self, lang, manage_lang, REQUEST, RESPONSE):
  """
  Create the top-level home folder and initial ZMS site from the add form.

  @param self: Container in which the home folder is created.
  @type self: OFS.ObjectManager.ObjectManager
  @param lang: Primary content language.
  @type lang: str
  @param manage_lang: Management interface language.
  @type manage_lang: str
  @param REQUEST: HTTP request containing form input.
  @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest
  @param RESPONSE: HTTP response used for redirects.
  @type RESPONSE: ZPublisher.HTTPResponse.HTTPResponse
  """
  message = ''
  t0 = time.time()

  if REQUEST['btn'] == 'Add':

    # Create the folder that contains the new site root.
    homeElmnt = Folder(REQUEST['folder_id'])
    self._setObject(homeElmnt.id, homeElmnt)
    homeElmnt = [x for x in self.objectValues() if x.id == homeElmnt.id][0]
    
    titlealt = 'ZMS home'
    title = 'ZMS - Python-based Content Management System for Science, Technology and Medicine'
    obj = initZMS(homeElmnt, 'content', titlealt, title, lang, manage_lang, REQUEST)
    
    theme_none = 'conf:acquire'
    if REQUEST.get('theme',theme_none) != 'conf:acquire':
      theme_id = importTheme(obj,REQUEST.get('theme','conf:acquire'))
      # Set theme property: id may not contain dots.
      obj.setConfProperty('ZMS.theme',theme_id.replace('.','_'))

    if REQUEST.get('content_init', 0)==1:
      init_content(obj, 'content.default.zip', REQUEST)

    if REQUEST.get('multisite_init', 0)==1:
      depth = REQUEST.get('multisite_depth')
      clients = REQUEST.get('multisite_clients')
      init_multisite(obj, depth, clients, REQUEST)

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

    # Reindex ZMS index.
    zmsindex = obj.getZMSIndex()
    zmsindex.manage_reindex(regenerate_all=True)

    # Return with message.
    message = obj.getLangStr('MSG_INSERTED', manage_lang)%obj.meta_type
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    RESPONSE.redirect('%s/%s/manage?manage_tabs_message=%s'%(homeElmnt.absolute_url(), obj.id, standard.url_quote(message)))

  else:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


def containerFilter(container):
  """
  Restrict add-dialog containers to plain folders.

  @param container: Candidate container displayed by the add dialog.
  @type container: object
  @return: C{True} when the container is a folder.
  @rtype: bool
  """
  return container.meta_type == 'Folder'


class ZMS(
        ZMSCustom,
        _accessmanager.AccessManager,
        _builder.Builder,
        _confmanager.ConfManager,
        _objattrs.ObjAttrsManager,
        _zcatalogmanager.ZCatalogManager,
        ):
    """
    Root ZMS content object that combines configuration, editing, and indexing.
    """

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

    def __init__(self):
      """Initialize the root object with the default content id."""
      self.id = 'content'


    def initZMS(self, container, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init = False):
      """
      Delegate site initialization to the module-level helper.

      @param container: Container that receives the new ZMS object.
      @type container: OFS.ObjectManager.ObjectManager
      @param id: Identifier of the created object.
      @type id: str
      @param titlealt: Alternative title shown in management views.
      @type titlealt: str
      @param title: Human readable site title.
      @type title: str
      @param lang: Primary content language.
      @type lang: str
      @param manage_lang: Management interface language.
      @type manage_lang: str
      @param REQUEST: HTTP request with initialization options.
      @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest
      @param minimal_init: Initialize only the minimal default configuration.
      @type minimal_init: bool
      @return: Newly created and initialized ZMS site.
      @rtype: ZMS
      """
      return initZMS(container, id, titlealt, title, lang, manage_lang, REQUEST, minimal_init)


    def manage_addMediaDb(self, location, REQUEST=None, RESPONSE=None):
      """
      Add the media database helper object.

      @param location: Filesystem location of the media database.
      @type location: str
      @param REQUEST: Optional HTTP request.
      @type REQUEST: ZPublisher.HTTPRequest.HTTPRequest | None
      @param RESPONSE: Optional HTTP response.
      @type RESPONSE: ZPublisher.HTTPResponse.HTTPResponse | None
      """
      _mediadb.manage_addMediaDb(self, location, REQUEST, RESPONSE)


    def zms_version(self, custom=False):
      """
      Return the product version string, optionally including custom metadata.

      @param custom: Include deployment-specific version decorations.
      @type custom: bool
      @return: Version text for UI rendering.
      @rtype: str
      """
      version_txt = '%s-%s' % (self.getConfProperty('ZMS.product_name'), self.getConfProperty('ZMS.version_txt'))
      zms_custom_version = os.environ.get('ZMS_CUSTOM_VERSION', '')
      if custom and zms_custom_version != '':
        version_txt += f'&nbsp;(<samp id="zms_custom_version">{zms_custom_version}</samp>)'
        # Generate revisions and custom version gathering commit hashes of git submodules
        # see Lines 37-46 unibe-cms/.github/workflows/build-and-push.yml
        revisions = _fileutil.getOSPath('/app/revisions.txt')
        if os.path.exists(revisions):
            with open(revisions, 'r') as file:
                zms_submodule_revisions = file.read()
            version_txt += f"""
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
            return version_txt
      if custom and len(version_txt.split('+'))>1:
        git_hash = version_txt.split('+')[1].strip()
        version_txt = version_txt.split('+')[0].strip()
        version_txt += (f' <a title="ZMS commit on github.com" target="_blank" '
          f'href="https://github.com/zms-publishing/ZMS/commits/{git_hash}">git#{git_hash}</a>')
      return version_txt

    def getDocumentElement(self):
      """Return the document element of the site tree."""
      return self

    def getRootElement(self):
      """Return the topmost portal master in the current site hierarchy."""
      doc_elmnt = self
      while True:
        portal_mstr = doc_elmnt.getPortalMaster()
        if portal_mstr is None:
          break
        doc_elmnt = portal_mstr
      return doc_elmnt

    def getAbsoluteHome(self):
      """Return the home folder of the portal master or the local site."""
      portalMaster = self.getPortalMaster()
      if portalMaster:
        return portalMaster.getAbsoluteHome()
      return self.getHome()

    def getHome(self):
      """Return the folder that contains the document element."""
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

    def getTrashcan(self):
      """Return the site's trashcan object."""
      return self.objectValues(['ZMSTrashcan'])[0]

    def getNewId(self, id_prefix='e'):
      """
      Return a new unique object identifier.

      @param id_prefix: Prefix used for the generated id.
      @type id_prefix: str
      @return: Unique object id.
      @rtype: str
      """
      return '%s%i'%(id_prefix, self.getSequence().nextVal())

    def getDCCoverage(self, REQUEST={}):
      """
      Return the Dublin Core coverage string for the primary language.

      @param REQUEST: Optional request mapping.
      @type REQUEST: dict
      @return: Global coverage identifier.
      @rtype: str
      """
      return 'global.'+self.getPrimaryLanguage()


    # Portal helpers.
    def getPortalMaster(self):
      """Return the configured portal master, or C{None} if absent."""
      v = self.get_conf_properties().get('Portal.Master', '')
      if v:
        try:
          return getattr( self, v).content
        except:
          pass
      return None

    def getPortalClients(self):
      """Return portal clients configured below the site home folder."""
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


    # DOM methods.
    def getParentNode(self):
      """Return C{None} because the site root has no parent node."""
      return None

    # XML builder.
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode):
      """
      Reset root-level import state before XML builder processing starts.

      @param sTagName: Name of the XML start tag.
      @type sTagName: str
      @param dTagAttrs: Attributes of the XML start tag.
      @type dTagAttrs: dict
      @param oParentNode: Parent node passed by the XML builder.
      @type oParentNode: object
      """
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
################################################################################
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