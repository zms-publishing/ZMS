################################################################################
# ZMSRepositoryManager.py
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


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSRepositoryManager.IZMSRepositoryManager)
class ZMSRepositoryManager(
        ZMSItem.ZMSItem):

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    meta_type = 'ZMSRepositoryManager'
    zmi_icon = "fas fa-database"
    icon_clazz = zmi_icon

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Options
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      return (
        {'label': 'Repository','action': 'manage_main'},
        )

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Interface
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main', globals())
    manage_main = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main', globals())

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Permissions
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    __administratorPermissions__ = (
        'manage_main',
        'manage_change',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSRepositoryManager.__init__: 
    
    Constructor.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def __init__(self):
      self.id = 'repository_manager'


    """
    Returns direction of copying config files: 
    Loading from file system (coloring ZMS changes) vs.
    Saving to file system (coloring filesystem changes)
    """
    def get_update_direction(self):
      return getattr(self,'update_direction','Loading')


    """
    Returns ignore-orphans.
    """
    def get_ignore_orphans(self):
      return getattr(self, 'ignore_orphans', True)


    """
    Returns conf-basepath.
    """
    def get_conf_basepath(self, id=''):
      basepath = self.get_conf_property('ZMS.conf.path')
      basepath = basepath.replace('$INSTANCE_HOME', standard.getINSTANCE_HOME())
      basepath = basepath.replace('$HOME_ID',"/".join([x.getHome().id for x in self.breadcrumbs_obj_path() if x.meta_id=='ZMS']))
      basepath = basepath.replace("/", os.path.sep)
      basepath = os.path.join(basepath, id)
      return basepath


    def remoteFiles(self, provider):
      standard.writeLog(self,"[remoteFiles]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return repositoryutil.remoteFiles(self, basepath)


    def readRepository(self, provider):
      standard.writeLog(self,"[readRepository]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return repositoryutil.readRepository(self, basepath)


    """
    Export: Commit ZODB to repository.
    """
    def commitChanges(self, ids):
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
            files = repositoryutil.localFiles(self, provider, [id])
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
            dir = list(set([os.path.join(basepath,x[:x.rfind(os.path.sep)]) for x in files if x.split('.')[-2].endswith('__')]))
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

    """
    Import: Update ZODB from repository.
    """
    def updateChanges(self, ids, override=False):
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
          repositories[provider_id] = self.readRepository(provider)
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


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSRepositoryManager.manage_change:
    
    Change.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def manage_change(self, btn, lang, REQUEST=None, RESPONSE=None):
      """ ZMSRepositoryManager.manage_change """
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

################################################################################
