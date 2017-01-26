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
import inspect
import os
import re
import stat
import time
import urllib
import zope.interface
# Product Imports.
import IZMSConfigurationProvider
import IZMSDaemon
import IZMSRepositoryManager
import IZMSRepositoryProvider
import ZMSItem
import _fileutil
import _globals
import _zopeutil


def get_class(py):
  id = re.findall('class (.*?):',py)[0]
  exec(py)
  return eval(id)


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSRepositoryManager(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSDaemon.IZMSDaemon,
        IZMSRepositoryManager.IZMSRepositoryManager)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Properties
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    meta_type = 'ZMSRepositoryManager'
    icon = "++resource++zms_/img/ZMSRepositoryManager.png"
    icon_clazz = "icon-random"

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Options
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'Repository','action': 'manage_main'},
        )

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Management Interface
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    manage = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main',globals())
    manage_main = PageTemplateFile('zpt/ZMSRepositoryManager/manage_main',globals())

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
    Returns auto-update.
    """
    def get_auto_update(self):
      return getattr(self,'auto_update',False)


    """
    Returns last-update.
    """
    def get_last_update(self):
      return getattr(self,'last_update',None)


    """
    Returns conf-basepath.
    """
    def get_conf_basepath(self, id=''):
      basepath = self.getConfProperty('ZMS.conf.path')
      basepath = basepath.replace("/",os.path.sep)
      basepath = basepath.replace('$INSTANCE_HOME',self.getINSTANCE_HOME())
      basepath = basepath.replace('$HOME_ID',self.getHome().id)
      basepath = os.path.join(basepath,id)
      return basepath

    """
    @see IZMSDaemon
    """
    def startDaemon(self):
      self.writeLog("[startDaemon]")
      self.exec_auto_update()

    """
    @see IZMSRepositoryManager
    """
    def exec_auto_commit(self, provider, id):
      if self.get_auto_update():
        ids = [':'.join([provider.id,id])]
        self.writeLog("[exec_auto_commit]: Run... %s"%str(ids))
        self.commitChanges(ids)


    """
    @see IZMSRepositoryManager
    """
    def exec_auto_update(self):
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'ZMSRepositoryManager.exec_auto_update'
      try: return self.fetchReqBuff(reqBuffId)
      except:
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        self.storeReqBuff(reqBuffId,True)
        # Execute once.
        self.writeLog("[exec_auto_update]")
        current_time = time.time()
        if self.get_auto_update():
          last_update = self.get_last_update()
          if last_update is None or _globals.getDateTime(last_update)<_globals.getDateTime(self.Control_Panel.process_start) or self.getConfProperty('ZMS.debug',0):
            self.writeBlock("[exec_auto_update]: Run...")
            def traverse(path):
              l = []
              if os.path.exists(path):
                for file in os.listdir(path):
                  filepath = os.path.join(path,file)
                  mode = os.stat(filepath)[stat.ST_MODE]
                  if stat.S_ISDIR(mode):
                    l.extend(traverse(filepath))
                  else:
                    l.append((os.path.getmtime(filepath),filepath))
              return l
            basepath = self.get_conf_basepath()
            files = traverse(basepath)
            mtime = max(map(lambda x:x[0],files))
            self.writeBlock("[exec_auto_update]: %s<%s"%(str(last_update),str(mtime)))
            if last_update is None or _globals.getDateTime(last_update)<_globals.getDateTime(mtime):
              update_files = map(lambda x:x[1][len(basepath):],filter(lambda x:last_update is None or _globals.getDateTime(x[0])<_globals.getDateTime(last_update),files))
              ids = list(set(map(lambda x:':'.join(x.split(os.path.sep)[0:2]),update_files)))
              self.writeBlock("[exec_auto_update]: %s"%str(ids))
              self.updateChanges(ids, override=True)
            self.last_update = _globals.getDateTime(current_time)
        self.writeLog("[exec_auto_update]: %s"%str(time.time()-current_time))


    def getDiffs(self, provider):
      self.writeBlock("[getDiffs]: provider=%s"%str(provider))
      diff = []
      local = self.localFiles(provider)
      remote = self.remoteFiles(provider)
      filenames = list(set(local.keys()+remote.keys()))
      filenames.sort()
      for filename in filenames:
        l = local.get(filename,{})
        r = remote.get(filename,{})
        if l.get('data','') != r.get('data',''):
          data = l.get('data',r.get('data',''))
          mt, enc = _globals.guess_contenttype(filename,data)
          diff.append((filename,mt,l.get('id',r.get('id','?')),l,r))
      return diff


    def getRepositoryProviders(self):
      obs = self.getDocumentElement().objectValues()
      return filter(lambda x:IZMSRepositoryProvider.IZMSRepositoryProvider in list(zope.interface.providedBy(x)),obs)


    def localFiles(self, provider, ids=None):
      self.writeBlock("[localFiles]: provider=%s"%str(provider))
      l = {}
      local = provider.provideRepository(ids)
      for id in local.keys():
        o = local[id]
        filename = o.get('__filename__',[id,'__init__.py'])
        # Write python-representation.
        py = []
        py.append('class %s:'%id.replace('.','_'))
        py.append('\t"""')
        py.append('\tpython-representation of %s'%o['id'])
        py.append('\t"""')
        py.append('')
        e = filter(lambda x:not x.startswith('__') and x==x.capitalize() and type(o[x]) is list,o.keys())
        e.sort()
        keys = filter(lambda x:not x.startswith('__') and x not in e,o.keys())
        keys.sort()
        for k in keys:
          v = o.get(k)
          if v:
            py.append('\t# %s'%k.capitalize())
            py.append('\t%s = %s'%(k,self.str_json(v,encoding="utf-8",formatted=True,level=2)))
            py.append('')
        for k in e:
          v = o.get(k)
          if v and type(v) is list:
            py.append('\t# %s'%k.capitalize())
            py.append('\tclass %s:'%k)
            for i in v:
              ob = i.get('ob')
              if ob is not None:
                fileexts = {'DTML Method':'.dtml', 'DTML Document':'.dtml', 'External Method':'.py', 'Page Template':'.zpt', 'Script (Python)':'.py', 'Z SQL Method':'.zsql'}
                fileprefix = i['id'].split('/')[-1]
                d = {}
                d['id'] = id
                d['filename'] = os.path.sep.join(filename[:-1]+['%s%s'%(fileprefix,fileexts.get(ob.meta_type,''))])
                d['data'] = _zopeutil.readData(ob)
                d['version'] = self.getLangFmtDate(ob.bobobase_modification_time().timeTime(),'eng')
                d['meta_type'] = ob.meta_type
                l[d['filename']] = d
              if i.has_key('ob'):
                del i['ob']
              py.append('\t\t%s = %s'%(self.id_quote(i['id']),self.str_json(i,encoding="utf-8",formatted=True,level=3)))
              py.append('')
        d = {}
        d['id'] = id
        d['filename'] = os.path.sep.join(filename)
        d['data'] = '\n'.join(py)
        d['version'] = map(lambda x:int(x),o.get('revision','0.0.0').split('.'))
        d['meta_type'] = 'Script (Python)'
        l[d['filename']] = d
      return l


    def remoteFiles(self, provider):
      self.writeBlock("[remoteFiles]: provider=%s"%str(provider))
      r = {}
      basepath = self.get_conf_basepath(provider.id)
      if os.path.exists(basepath):
        def traverse(base,path):
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path,name)
            mode = os.stat(filepath)[stat.ST_MODE]
            if stat.S_ISDIR(mode):
              traverse(base,filepath)
            elif not name in ['__impl__.py'] and name.startswith('__') and name.endswith('__.py'):
              # Read python-representation of repository-object
              self.writeLog("[remoteFiles]: read %s"%filepath)
              f = open(filepath,"r")
              py = f.read()
              f.close()
              # Analyze python-representation of repository-object
              c = get_class(py)
              d = c.__dict__
              id = d["id"]
              rd = {}
              rd['id'] = id
              rd['filename'] = filepath[len(base)+1:]
              rd['data'] = py
              rd['version'] = d.get("revision",self.getLangFmtDate(os.path.getmtime(filepath),'eng'))
              r[rd['filename']] = rd
              for k in filter(lambda x:not x.startswith('__'),d.keys()):
                v = d[k]
                if inspect.isclass(v):
                  dd = v.__dict__
                  v = []
                  for kk in filter(lambda x:x in ['__impl__'] or not x.startswith("__"),dd.keys()):
                    vv = dd[kk]
                    # Try to read artefact.
                    if vv.has_key('id'):
                      fileprefix = vv['id'].split('/')[-1]
                      for file in filter(lambda x: x==fileprefix or x.startswith('%s.'%fileprefix),names):
                        artefact = os.path.join(path,file)
                        self.writeLog("[remoteFiles]: read artefact %s"%artefact)
                        f = open(artefact,"r")
                        data = f.read()
                        f.close()
                        if artefact.endswith('.zpt'):
                          data = data.decode('utf-8')
                        rd = {}
                        rd['id'] = id
                        rd['filename'] = artefact[len(base)+1:]
                        rd['data'] = data
                        rd['version'] = self.getLangFmtDate(os.path.getmtime(artefact),'eng')
                        r[rd['filename']] = rd
                        break
        traverse(basepath,basepath)
      return r


    def readRepository(self, provider):
      self.writeBlock("[readRepository]: provider=%s"%str(provider))
      r = {}
      basepath = self.get_conf_basepath(provider.id)
      if os.path.exists(basepath):
        def traverse(base,path):
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path,name)
            mode = os.stat(filepath)[stat.ST_MODE]
            if stat.S_ISDIR(mode):
              traverse(base,filepath)
            elif not name in ['__impl__.py'] and name.startswith('__') and name.endswith('__.py'):
              # Read python-representation of repository-object
              self.writeBlock("[readRepository]: read %s"%filepath)
              f = open(filepath,"r")
              py = f.read()
              f.close()
              # Analyze python-representation of repository-object
              c = get_class(py)
              d = c.__dict__
              id = d["id"]
              r[id] = {}
              for k in filter(lambda x:not x.startswith('__'),d.keys()):
                v = d[k]
                if inspect.isclass(v):
                  dd = v.__dict__
                  v = []
                  for kk in filter(lambda x:not x.startswith('__'),dd.keys()):
                    vv = dd[kk]
                    # Try to read artefact.
                    if vv.has_key('id'):
                      fileprefix = vv['id'].split('/')[-1]
                      for file in filter(lambda x: x==fileprefix or x.startswith('%s.'%fileprefix),names):
                        artefact = os.path.join(path,file)
                        self.writeBlock("[readRepository]: read artefact %s"%artefact)
                        f = open(artefact,"r")
                        data = f.read()
                        f.close()
                        if artefact.endswith('.zpt'):
                          data = data.decode('utf-8')
                        vv['data'] = data
                        break
                    v.append((py.find('\t\t%s ='%kk),vv))
                  v.sort()
                  v = map(lambda x:x[1],v)
                r[id][k] = v
        traverse(basepath,basepath)
      return r


    """
    Commit ZODB to repository.
    """
    def commitChanges(self, ids):
      self.writeBlock("[commitChanges]: ids=%s"%str(ids))
      success = []
      for provider_id in list(set(map(lambda x:x.split(':')[0],ids))):
        provider = getattr(self,provider_id)
        for id in list(set(map(lambda x:x.split(':')[1],filter(lambda x:x.split(':')[0]==provider_id,ids)))):
          # Read local-files from provider.
          files = self.localFiles(provider,[id])
          # Recreate folder.
          basepath = self.get_conf_basepath(provider.id)
          if os.path.exists(basepath):
            for name in os.listdir(basepath):
              if name == id or name == '%s.py'%id:
                filepath = os.path.join(basepath,name)
                _fileutil.remove(filepath)
          # Write files.
          for file in files.keys():
            filepath = os.path.join(basepath,file)
            folder = filepath[:filepath.rfind(os.path.sep)]
            self.writeBlock("[commitChanges]: create folder %s if not exists"%folder)
            if not os.path.exists(folder):
              _fileutil.mkDir(folder)
            self.writeBlock("[commitChanges]: write %s"%filepath)
            data = files[file]['data']
            if files[file]['meta_type'] == 'Page Template':
              data = unicode(data).encode('utf-8')
            f = open(filepath,"w")
            f.write(data)
            f.close()
          success.append(id)
      return success

    """
    Update ZODB from repository.
    """
    def updateChanges(self, ids, override=False):
      self.writeBlock("[updateChanges]: ids=%s"%str(ids))
      success = []
      repositories = {}
      for i in ids:
        # Initialize.
        provider_id = i[:i.find(':')]
        id = i[i.find(':')+1:]
        provider = getattr(self,provider_id)
        # Read repositories for provider.
        if not repositories.has_key(provider_id):
          repositories[provider_id] = self.readRepository(provider)
        repository = repositories[provider_id]
        # Update.
        r = repository[id]
        provider.updateRepository(r)
        success.append(id)
      return success


    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ZMSRepositoryManager.manage_change:
    
    Change.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def manage_change(self, btn, lang, REQUEST=None, RESPONSE=None):
      """ ZMSRepositoryManager.manage_change """
      message = ''
      
      if btn == 'save':
        self.auto_update = REQUEST.get('auto_update','')!=''
        self.last_update = self.parseLangFmtDate(REQUEST.get('last_update',''))
        self.setConfProperty('ZMS.conf.path',REQUEST.get('basepath',''))
      
      if btn == 'commit':
        success = self.commitChanges(REQUEST.get('ids',[]))
        message = self.getZMILangStr('MSG_EXPORTED')%('<em>%s</em>'%' '.join(success))
      
      if btn in ['override','update']:
        success = self.updateChanges(REQUEST.get('ids',[]),btn=='override')
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%' '.join(success))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,message))

################################################################################
