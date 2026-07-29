"""
ZMSRepositoryManager.py - ZMS Repository Manager

The ZMSRepositoryManager Module is comprehensive repository management system for ZMS 
that handles synchronization, configuration management, and bi-directional data exchange
between ZODB (Zope Object Database) and the (versioning) file system (e.g., Git).

Core Responsibilities:

  - Repository Synchronization: Manages bidirectional synchronization between ZODB and 
    file system repositories, allowing ZMS to maintain consistency across storage backends.
  - Configuration Management: Handles reading, writing, and validation of ZMS configuration
    files stored in the repository with support for environment variable substitution
    ($INSTANCE_HOME, $HOME_ID).
  - Import/Export Operations: Facilitates exporting ZMS objects and configurations to the
    file system (ZODB -> repository) and importing updates back into ZODB 
    (repository -> ZODB).
  - Model Exchange: Provides mechanisms to exchange model definitions and configurations
    between multiple providers/repositories, supporting distributed ZMS deployments.
  - Multi-Provider Support: Supports multiple repository providers, allowing organizations
    to manage different configuration sets across separate storage locations.

Key Features:
  - Directional Control: Configurable update direction determines whether changes are
    highlighted from the file system (Loading mode) or the ZODB (Saving mode).
  - Orphan Management: Optional handling of orphaned configuration files to maintain
    clean repository states.
  - Event Triggering: Emits repository lifecycle events (beforeCommitRepositoryEvt,
    afterCommitRepositoryEvt, beforeUpdateRepositoryEvt, afterUpdateRepositoryEvt)
    for integration with other ZMS plugins.
  - Transaction Safety: Provides rollback capability through success/failure tracking
    during batch operations.

Use Cases in ZMS:
  - Configuration Backup and Recovery
  - Multi-environment Deployment (development, staging, production)
  - Team Collaboration on ZMS Models and Content Structures
  - Version Control Integration for ZMS Configurations
  - Migration and Data Exchange Between ZMS Instances

Implements:
  - IZMSConfigurationProvider: Configuration retrieval and management
  - IZMSRepositoryManager: Repository operations and synchronization


License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import os
import time
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSRepositoryManager
from Products.zms import ZMSItem
from Products.zms import _fileutil
from Products.zms import repositoryutil
from Products.zms import standard


@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSRepositoryManager.IZMSRepositoryManager)
class ZMSRepositoryManager(
        ZMSItem.ZMSItem):

    #Properties
    meta_type = 'ZMSRepositoryManager'
    zmi_icon = "fas fa-database"
    icon_clazz = zmi_icon

    # Management Options
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      """Handle the ZMI action 'manage_options'."""
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      """Handle the ZMI action 'manage_sub_options'."""
      return (
        {'label': 'Repository','action': 'manage_main'},
        )

    # Management Interface
    manage = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main', globals())
    manage_main = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main', globals())

    # Management Permissions
    __administratorPermissions__ = (
        'manage_main',
        'manage_change',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )


    # Constructor
    def __init__(self):
      """Initialize the instance state."""
      self.id = 'repository_manager'


    def get_update_direction(self):
      """
      Returns direction of copying config files: 
      Loading from file system (coloring ZMS changes) vs.
      Saving to file system (coloring filesystem changes)
      """
      return getattr(self,'update_direction','Loading')


    def get_ignore_orphans(self):
      """Return ignore orphans."""
      return getattr(self, 'ignore_orphans', True)


    def get_conf_basepath(self, id=''):
      """Return conf basepath."""
      basepath = self.get_conf_property('ZMS.conf.path')
      basepath = basepath.replace('$INSTANCE_HOME', standard.getINSTANCE_HOME())
      basepath = basepath.replace('$HOME_ID',"/".join([x.getHome().id for x in self.breadcrumbs_obj_path() if x.meta_id=='ZMS']))
      basepath = basepath.replace("/", os.path.sep)
      basepath = os.path.join(basepath, id)
      return basepath


    def get_modelfileset_from_disk(self, provider):
      """
      Retrieve remote files from a repository provider.

      This method retrieves a list of remote files from the specified provider
      by constructing the base path configuration and delegating to the
      repository utility function.

      @param provider: The repository provider object containing configuration
               and connection details for accessing remote files
      @type provider: object

      @return: A list of remote files available from the provider
      @rtype: list

      @see: L{repositoryutil.get_modelfileset_from_disk}
      @see: L{get_conf_basepath}
      """
      standard.writeLog(self,"[get_modelfileset_from_disk]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return repositoryutil.get_modelfileset_from_disk(self, basepath)


    def get_models_from_disk(self, provider):
      """
      Read repository data from a provider.
      
      Implements the 'get_models_from_disk' interface. This method retrieves repository
      information from the specified provider by reading the repository structure
      from the configured base path.
      
      @param provider: The provider object from which to read the repository.
          Must have an 'id' attribute.
      @type provider: Provider
      
      @return: Repository data read from the provider's base path.
      @rtype: dict
    
      @see: repositoryutil.get_models_from_disk()
      """
      standard.writeLog(self,"[get_models_from_disk]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return repositoryutil.get_models_from_disk(self, basepath)


    def commitChanges(self, ids):
      """Export: Commit ZODB to repository."""
      standard.writeLog(self,"[commitChanges]: ids=%s"%str(ids))
      standard.triggerEvent(self,'beforeCommitRepositoryEvt')
      success = []
      failure = []
      providers = repositoryutil.get_providers(self)
      for provider_id in list(set([x.split(':')[0] for x in ids])):
        provider = [x for x in providers if x.id == provider_id][0]
        basepath = self.get_conf_basepath(provider.id)
        for id in list(set([x.split(':')[1] for x in ids if x.split(':')[0]==provider_id])):
          try:
            # Read local-files from provider.
            files = repositoryutil.get_modelfileset_from_zodb(self, provider, [id])
            # Recreate folder.
            if os.path.exists(basepath):
              for name in os.listdir(basepath):
                filepath = os.path.join(basepath, name)
                if os.path.isdir(filepath) and name == id:
                  standard.writeLog(self,"[commitChanges]: clear dir %s"%filepath)
                  dir = [os.path.join(filepath, x) for x in os.listdir(filepath)]
                  [_fileutil.remove(x) for x in dir if os.path.isfile(x)]
                elif os.path.isfile(filepath) and name == '%s.py'%id:
                  standard.writeLog(self,"[commitChanges]: remove file %s"%filepath)
                  _fileutil.remove(filepath)
            # Clear folders.
            dir = list(set([os.path.join(basepath,x[:x.rfind(os.path.sep)]) for x in files if x.split('.') and len(x.split('.')) > 1 and x.split('.')[-2].endswith('__')]))
            dir = [x for x in dir if x.split(os.path.sep)[-1] in [y.split(':')[-1] for y in ids]]
            [[os.remove(z) for z in [os.path.join(x,y) for y in os.listdir(x)] if os.path.isfile(z)] for x in dir if os.path.isdir(x)]
            # Write files.
            for file in files:
              filepath = os.path.join(basepath,file)
              folder = filepath[:filepath.rfind(os.path.sep)]
              standard.writeLog(self,"[commitChanges]: exists folder %s %s"%(folder,str(os.path.exists(folder))))
              if not os.path.exists(folder):
                standard.writeLog(self,"[commitChanges]: create folder %s"%folder)
                _fileutil.mkDir(folder)
              standard.writeLog(self,"[commitChanges]: write %s"%filepath)
              data = files[file]['data']
              if data is not None:
                f = open(filepath,"wb")
                if isinstance(data,str):
                  try:
                    data = data.encode("utf-8")
                  except:
                    pass
                f.write(data)
                f.close()
              else:
                failure.append('%s is None'%file)
            success.append(id)
          except:
            standard.writeError(self,"[commitChanges]: can't %s"%id)
            failure.append(id)
      standard.triggerEvent(self,'afterCommitRepositoryEvt')
      return success,failure


    def updateChanges(self, ids, override=False):
      """ 
      Import: Update ZODB from repository.
        - If override is False, only update if there are changes in the repository compared to ZODB (highlighted filesystem changes)
        - If override is True, update regardless of changes (highlighted ZMS changes)
      """
      standard.writeLog(self,"[updateChanges]: ids=%s"%str(ids))
      standard.triggerEvent(self,'beforeUpdateRepositoryEvt')
      success = []
      failure = []
      repositories = {}
      providers = repositoryutil.get_providers(self)
      for i in ids:
        # Initialize.
        provider_id = i[:i.find(':')]
        id = i[i.find(':')+1:]
        provider = [x for x in providers if x.id == provider_id][0]
        # Read repositories for provider.
        if provider_id not in repositories:
          repositories[provider_id] = self.get_models_from_disk(provider)
        repository = repositories[provider_id]
        # Update.
        try:
          r = repository[id]
          provider.updateRepository(r)
          success.append(id)
        except:
          standard.writeError(self,"[updateChanges]: can't %s"%id)
          failure.append(id)
      standard.triggerEvent(self,'afterUpdateRepositoryEvt')
      return success,failure


    def manage_change(self, btn, lang, REQUEST=None, RESPONSE=None):
      """ 
      Manage changes in the ZMS repository.

        - For 'save': Save current settings (ignore orphans, update direction) and return with confirmation message.
        - For 'commit': Commit changes from ZODB to repository and return with success/failure messages.
        - For 'override'/'update': Update ZODB from repository (with or without override) and return with success/failure messages.
        - Redirect to manage_main with appropriate messages in query parameters.
        - Messages are localized using getZMILangStr and include lists of successfully processed and failed items.
        - Events 'beforeCommitRepositoryEvt', 'afterCommitRepositoryEvt', 'beforeUpdateRepositoryEvt', and 'afterUpdateRepositoryEvt' are triggered at appropriate stages of processing.

      @param btn: Action button clicked ('save', 'commit', 'override', 'update')
      @type btn: str
      @param lang: Language code for messages
      @type lang: str
      @param REQUEST: Current request object
      @type REQUEST: ZPublisher.HTTPRequest
      @param RESPONSE: Current response object
      @type RESPONSE: ZPublisher.HTTPResponse 
      """
      message = ''
      error_message = ''
      
      if btn == 'save':
        self.ignore_orphans = REQUEST.get('ignore_orphans','')!=''
        self.setConfProperty('ZMS.conf.ignore.sys_conf',REQUEST.get('ignore_sys_conf',0))
        self.setConfProperty('ZMS.conf.path',REQUEST.get('basepath',''))
        self.update_direction = REQUEST.get('update_direction','Loading')
        message = self.getZMILangStr('MSG_CHANGED')
      
      elif btn == 'commit':
        success,failure = self.commitChanges(REQUEST.get('ids',[]))
        message = self.getZMILangStr('MSG_EXPORTED')%('<em>%s</em>'%', '.join(success))
        if failure:
          error_message = '<em>%s</em>'%', '.join(failure)
      
      elif btn in ['override','update']:
        success,failure = self.updateChanges(REQUEST.get('ids',[]),btn=='override')
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%', '.join(success))
        if failure:
          error_message = '<em>%s</em>'%', '.join(failure)
      
      # Return with message.
      target = standard.url_append_params('manage_main',{'lang':lang})
      if message:
        target = standard.url_append_params(target,{'manage_tabs_message':message})
      if error_message:
        target = standard.url_append_params(target,{'manage_tabs_error_message':error_message})
      return RESPONSE.redirect(target)

