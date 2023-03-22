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
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import os
import re
import time
from zope.interface import implementer, providedBy
# Product Imports.
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSDaemon
from Products.zms import IZMSRepositoryManager
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem
from Products.zms import _fileutil
from Products.zms import _repositoryutil
from Products.zms import standard
from Products.zms import zopeutil


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSDaemon.IZMSDaemon,
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
    manage_main_diff = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main_diff', globals())

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
    Returns auto-update.
    """
    def get_auto_update(self):
      return getattr(self, 'auto_update', False)


    """
    Returns last-update.
    """
    def get_last_update(self):
      return getattr(self, 'last_update', 0)


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

    """
    @see IZMSDaemon
    """
    def startDaemon(self):
      standard.writeLog(self,"[startDaemon]")
      self.exec_auto_update()


    """
    @see IZMSRepositoryManager
    """
    def exec_auto_commit(self, provider, id):
      if self.get_auto_update():
        ids = [':'.join([provider.id, id])]
        standard.writeLog(self,"[exec_auto_commit]: Run... %s"%str(ids))
        self.commitChanges(ids)


    """
    @see IZMSRepositoryManager
    """
    def exec_auto_update(self):
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'ZMSRepositoryManager.exec_auto_update'
      try: 
        return self.fetchReqBuff(reqBuffId)
      except:
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        self.storeReqBuff(reqBuffId, True)
        # Execute once.
        standard.writeLog(self,"[exec_auto_update]")
        current_time = time.time()
        if self.get_auto_update():
          last_update = self.get_last_update()
          if (not last_update or standard.getDateTime(last_update)<standard.getDateTime(self.Control_Panel.process_start)) and self.getConfProperty('ZMS.debug',0):
            standard.writeLog(self,"[exec_auto_update]: Run...")
            def traverse(path):
              l = []
              if os.path.exists(path):
                for file in os.listdir(path):
                  filepath = os.path.join(path, file)
                  if os.path.isdir(filepath):
                    l.extend(traverse(filepath))
                  else:
                    l.append((os.path.getmtime(filepath), filepath))
              return l
            basepath = self.get_conf_basepath()
            files = traverse(basepath)
            mtime = max([x[0] for x in files]+[0])
            standard.writeLog(self,"[exec_auto_update]: %s - %s < %s"%(str(standard.getDateTime(last_update) < standard.getDateTime(mtime)),standard.format_datetime_iso(standard.getDateTime(last_update)), standard.format_datetime_iso(standard.getDateTime(mtime))))
            if not last_update or standard.getDateTime(last_update) < standard.getDateTime(mtime):
              update_files = [x[1][len(basepath):] for x in files if not last_update or standard.getDateTime(x[0])>standard.getDateTime(last_update)]
              temp_files = [x.split(os.path.sep) for x in update_files]
              temp_files = \
                [[x[0], x[-1].replace('.py', '')] for x in temp_files if len(x)==2] + \
                [[x[0], x[-2]] for x in temp_files if len(x)>2]
              # avoid processing of hidden files, e.g. .DS_Store on macOS
              temp_files = [x for x in temp_files if not x[-1].startswith('.')]
              ids = list(set([':'.join(x) for x in temp_files]))
              standard.writeLog(self,"[exec_auto_update]: %s"%str(ids))
              self.updateChanges(ids, override=True)
            self.last_update = standard.getDateTime(current_time)
        standard.writeLog(self,"[exec_auto_update]: %s seconds needed"%(str(time.time()-current_time)))


    def getDiffs(self, provider, ignore=True):
      standard.writeLog(self,"[getDiffs]: provider=%s"%str(provider))
      diff = []
      local = self.localFiles(provider)
      remote = self.remoteFiles(provider)
      filenames = sorted(set(list(local)+list(remote)))
      for filename in filenames:
        if ignore and filename not in local.keys():
          # ignore orphaned files in filesystem
          # if there are no references in model
          continue
        l = local.get(filename, {})
        l_data = l.get('data')
        r = remote.get(filename, {})
        r_data = r.get('data')
        # Check whether any bytes data are decodeable as utf-8 text
        if isinstance(l_data, bytes):
          try:
            l['data'] = l_data.decode('utf-8')
          except: # data is no text, but image etc.
            pass
        if isinstance(r_data, bytes):
          try:
            r['data'] = r_data.decode('utf-8')
          except:
            pass
        # If text then normalize Windows CR+LF line break to Unix LF
        # and ignore leading/trailing whitespace since Zope removes 
        # and github adds them
        if isinstance(l.get('data'), str):
          l['data'] = l['data'].replace('\r','').strip()
        if isinstance(r.get('data'), str):
          r['data'] = r['data'].replace('\r','').strip()
        # Only if text is not equal add to diff list
        if l.get('data') != r.get('data'):
          data = l_data or r_data
          if isinstance(data, str):
            data = data.encode('utf-8')
          mt, enc = standard.guess_content_type(filename.split('/')[-1], data)
          diff.append((filename, mt, l.get('id', r.get('id', '?')), l, r))
      return diff


    def getRepositoryProviders(self):
      obs = self.getDocumentElement().objectValues()
      return [x for x in obs if IZMSRepositoryProvider.IZMSRepositoryProvider in list(providedBy(x))]


    def localFiles(self, provider, ids=None):
      standard.writeLog(self,"[localFiles]: provider=%s"%str(provider))
      l = {}
      local = provider.provideRepository(ids)
      for id in local:
        o = local[id]
        filename = o.get('__filename__', [id, '__init__.py'])
        # Write python-representation.
        py = []
        py.append('class %s:'%id.replace('.','_').replace('-','_'))
        py.append('\t"""')
        py.append('\tpython-representation of %s'%o['id'])
        py.append('\t"""')
        py.append('')
        e = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
        keys = sorted([x for x in o if not x.startswith('__') and x not in e])
        for k in keys:
          v = o.get(k)
          py.append('\t# %s'%k.capitalize())
          py.append('\t%s = %s'%(standard.id_quote(k), standard.str_json(v, encoding="utf-8", formatted=True, level=2, allow_booleans=False)))
          py.append('')
        for k in e:
          v = o.get(k)
          if v and isinstance(v, list):
            py.append('\t# %s'%k.capitalize())
            py.append('\tclass %s:'%standard.id_quote(k).capitalize())
            # Are there duplicated ids after id-quoting?
            id_list = [ standard.id_quote(i['id']) for i in v if i.get('ob') is None ] 
            id_duplicates =  [ i for i in id_list if id_list.count(i) > 1 ]
            for i in v:
              if 'id' in i:
                ob = i.get('ob')
                if ob is not None:
                  fileexts = {'DTML Method':'.dtml', 'DTML Document':'.dtml', 'External Method':'.py', 'Page Template':'.zpt', 'Script (Python)':'.py', 'Z SQL Method':'.zsql'}
                  fileprefix = i['id'].split('/')[-1]
                  data = zopeutil.readData(ob)
                  version = ''
                  if hasattr(ob,'_p_mtime'):
                    version = standard.getLangFmtDate(DateTime(ob._p_mtime).timeTime(), 'eng')
                  d = {}
                  d['id'] = id
                  d['filename'] = os.path.sep.join(filename[:-1]+['%s%s'%(fileprefix, fileexts.get(ob.meta_type, ''))])
                  d['data'] = data
                  d['version'] = version
                  d['meta_type'] = ob.meta_type
                  l[d['filename']] = d
                if 'ob' in i:
                  del i['ob']
                try:
                  # Prevent id-quoting if duplicates may result
                  id_quoted = ( i['id'].startswith('_') and ( standard.id_quote(i['id']) in id_duplicates) ) and i['id'] or standard.id_quote(i['id'])
                  py.append('\t\t%s = %s'%(id_quoted, standard.str_json(i, encoding="utf-8", formatted=True, level=3, allow_booleans=False)))
                except:
                  py.append('\t\t# ERROR: '+standard.writeError(self,'can\'t localFiles \'%s\''%i['id']))
                py.append('')
        d = {}
        d['__icon__'] = o.get('__icon__')
        d['__description__'] = o.get('__description__')
        d['id'] = id
        d['filename'] = os.path.sep.join(filename)
        d['data'] = '\n'.join(py)
        try:
          d['version'] = [int(x) for x in o.get('revision', '0.0.0').split('.')]
        except:
          # version schmeme 0.0.0 must not contain strings
          d['version'] = list(map(int, re.findall(r'\d+', o.get('revision', '0.0.0'))))
        d['meta_type'] = 'Script (Python)'
        l[d['filename']] = d
      return l


    def remoteFiles(self, provider):
      standard.writeLog(self,"[remoteFiles]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return _repositoryutil.remoteFiles(self, basepath)


    def readRepository(self, provider):
      standard.writeLog(self,"[readRepository]: provider=%s"%str(provider))
      basepath = self.get_conf_basepath(provider.id)
      return _repositoryutil.readRepository(self, basepath)


    """
    Commit ZODB to repository.
    """
    def commitChanges(self, ids):
      standard.writeLog(self,"[commitChanges]: ids=%s"%str(ids))
      standard.triggerEvent(self,'beforeCommitRepositoryEvt')
      success = []
      failure = []
      for provider_id in list(set([x.split(':')[0] for x in ids])):
        provider = getattr(self, provider_id)
        basepath = self.get_conf_basepath(provider.id)
        for id in list(set([x.split(':')[1] for x in ids if x.split(':')[0]==provider_id])):
          try:
            # Read local-files from provider.
            files = self.localFiles(provider, [id])
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
            dir = list(set([os.path.join(basepath,x[:x.rfind(os.path.sep)]) for x in files if x.endswith('__init__.py')]))
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
    Update ZODB from repository.
    """
    def updateChanges(self, ids, override=False):
      standard.writeLog(self,"[updateChanges]: ids=%s"%str(ids))
      standard.triggerEvent(self,'beforeUpdateRepositoryEvt')
      success = []
      failure = []
      repositories = {}
      for i in ids:
        # Initialize.
        provider_id = i[:i.find(':')]
        id = i[i.find(':')+1:]
        provider = getattr(self, provider_id)
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
        self.auto_update = REQUEST.get('auto_update','')!=''
        self.last_update = self.parseLangFmtDate(REQUEST.get('last_update',''))
        self.ignore_orphans = REQUEST.get('ignore_orphans','')!=''
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
