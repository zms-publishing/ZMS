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
import urllib
import zope.interface
# Product Imports.
import IZMSConfigurationProvider
import IZMSRepositoryManager
import IZMSRepositoryProvider
import ZMSItem
import _fileutil
import _globals
import _zopeutil


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

    def getDiffs(self, provider):
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


    def localFiles(self, provider):
      l = {}
      local = provider.provideRepository()
      for id in local.keys():
        o = local[id]
        # Write python-representation.
        py = []
        py.append('class %s:'%self.id_quote(id.replace('.','_')))
        py.append('\t"""')
        py.append('\tpython-representation of content-object %s'%o['id'])
        py.append('\t"""')
        py.append('')
        e = ['attrs']
        keys = filter(lambda x:x not in e,o.keys())
        keys.sort()
        # TODO: get e dynamically
        for k in keys:
          v = o.get(k)
          if v and type(v) is list:
            pass
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
                d['filename'] = os.path.join(id,'%s%s'%(fileprefix,fileexts.get(ob.meta_type,'')))
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
        d['filename'] = os.path.join(id,'__init__.py')
        d['data'] = '\n'.join(py)
        d['version'] = o.get('revision','0.0.0')
        d['meta_type'] = 'Script (Python)'
        l[d['filename']] = d
      return l


    def remoteFiles(self, provider):
      r = {}
      basepath = self.get_conf_basepath(provider.id)
      if os.path.exists(basepath):
        for id in os.listdir(basepath):
          filepath = os.path.join(basepath,id)
          mode = os.stat(filepath)[stat.ST_MODE]
          if stat.S_ISDIR(mode):
            for file in os.listdir(filepath):
              filename = os.path.join(filepath,file)
              f = open(filename,"r")
              data = f.read()
              f.close()
              version = None
              revision = re.findall('revision = "(.*?)"',data)
              if revision:
                version = revision[0]
              else:
                version = self.getLangFmtDate(os.path.getmtime(filename),'eng')
              d = {}
              d['id'] = id
              d['filename'] = os.path.join(id,file)
              d['data'] = data
              d['version'] = version
              r[d['filename']] = d
      return r


    def readRepository(self, provider):
      r = {}
      basepath = self.get_conf_basepath(provider.id)
      if os.path.exists(basepath):
        for id in os.listdir(basepath):
          filepath = os.path.join(basepath,id)
          mode = os.stat(filepath)[stat.ST_MODE]
          if stat.S_ISDIR(mode):
            filename = os.path.join(filepath,'__init__.py')
            if os.path.exists(filename):
              # Read python-representation of content-object
              f = open(filename,"r")
              py = f.read()
              f.close()
              # Analyze python-representation of content-object
              exec(py)
              d = eval("%s.__dict__"%self.id_quote(id.replace('.','_')))
              r[id] = {}
              for k in filter(lambda x:not x.startswith('__'),d.keys()):
                v = d[k]
                if inspect.isclass(v):
                  dd = eval("%s.%s.__dict__"%(self.id_quote(id.replace('.','_')),k))
                  v = []
                  for kk in filter(lambda x:x in ['__impl__'] or not x.startswith("__"),dd.keys()):
                    vv = dd[kk]
                    # Try to read artefact.
                    if vv.has_key('id'):
                      fileprefix = vv['id'].split('/')[-1]
                      for file in os.listdir(filepath):
                        if file.startswith('%s.'%fileprefix):
                          artefact = os.path.join(filepath,file)
                          f = open(artefact,"r")
                          data = f.read()
                          f.close()
                          vv['data'] = data
                          vv['mtime'] = os.path.getmtime(artefact)
                          break
                    v.append((py.find('\t\t%s ='%kk),vv))
                  v.sort()
                  v = map(lambda x:x[1],v)
                r[id][k] = v
      return r


    """
    Commit ZODB to repository.
    """
    def commitChanges(self, ids):
      success = []
      files = {}
      for i in ids:
        # Initialize.
        provider_id = i[:i.find(':')]
        id = i[i.find(':')+1:]
        provider = getattr(self,provider_id)
        # Read local-files from provider.
        if not files.has_key(provider_id):
          files[provider_id] = self.localFiles(provider)
        providerFiles = files[provider_id]
        # Recreate folder.
        basepath = self.get_conf_basepath(provider.id)
        filepath = os.path.join(basepath,id)
        if os.path.exists(filepath):
          _fileutil.remove(filepath)
        _fileutil.mkDir(filepath)
        # Write artefacts.
        for file in filter(lambda x:providerFiles[x]['id']==id,providerFiles.keys()):
          artefact = os.path.join(basepath,file)
          f = open(artefact,"w")
          f.write(providerFiles[file]['data'])
          f.close()
        success.append(id)
      return success

    """
    Update ZODB from repository.
    """
    def updateChanges(self, ids, override=False):
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
