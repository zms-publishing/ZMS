################################################################################
# repositoryutil.py
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

"""ZMS repository utility module

This module provides helpful functions and classes for use in Python
Scripts.  It can be accessed from Python with the statement
"import Products.zms.repository"
"""
# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
from App.Common import package_home
from DateTime import DateTime
from zope.interface import providedBy
import inspect
import os
import re
import sys
# Product Imports.
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSRepositoryProvider
from Products.zms import zopeutil
from Products.zms import standard
from Products.zms import yamlutil
from Products.zms import zopeutil

security = ModuleSecurityInfo('Products.zms.repositoryutil')

"""
Returns system conf-basepath.
"""
security.declarePublic('get_system_conf_basepath')
def get_system_conf_basepath():
    return package_home(globals())+'/conf'


"""
Returns list of repository-providers.
"""
security.declarePublic('get_providers')
def get_providers(self):
  def get_repo_providers(context):
    children = context.objectValues()
    repo_providers = []
    [repo_providers.append(x) for x in children if IZMSRepositoryProvider.IZMSRepositoryProvider in list(providedBy(x))]
    [repo_providers.extend(get_repo_providers(x)) for x in children if IZMSConfigurationProvider.IZMSConfigurationProvider in list(providedBy(x))]
    return repo_providers
  return get_repo_providers(self.getDocumentElement())


"""
Get class from py-string.
"""
def get_class(py):
  id = re.findall('class (.*?):', py)[0]
  if sys.version_info >= (3, 13):
    py = py + "\nglobal c\nc = " + id
    exec(py, globals=globals(), locals=locals())
    return eval("c", globals=globals(), locals=locals())
  else:
    exec(py)
    return eval(id)


"""
Read repository from base-path.
"""
security.declarePublic('remoteFiles')
def remoteFiles(self, basepath, deep=True):
    standard.writeLog(self,"[remoteFiles]: basepath=%s"%basepath)
    r = {}
    if os.path.exists(basepath):
        def traverse(base, path, level=0):
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path, name)
            if os.path.isdir(filepath) and (deep or level == 0):
              traverse(base, filepath, level+1)
            elif name.startswith('__') and name.endswith('__.py'):
              # Read python-representation of repository-object
              standard.writeLog(self,"[remoteFiles]: read %s"%filepath)
              f = open(filepath,"rb")
              py = standard.pystr(f.read())
              f.close()
              # Analyze python-representation of repository-object
              d = {}
              try:
                  c = get_class(py)
                  d = c.__dict__
              except:
                  d['revision'] = standard.writeError(self,"[remoteFiles.traverse]: can't analyze filepath=%s"%filepath)
              id = d.get('id',name)
              ### Different from remoteFiles()
              rd = {}
              rd['id'] = id
              rd['filename'] = filepath[len(base)+1:]
              rd['data'] = py
              rd['version'] = d.get("revision",self.getLangFmtDate(os.path.getmtime(filepath),'eng'))
              r[rd['filename']] = rd
              # Read artefacts and avoid processing of hidden files, e.g. .DS_Store on macOS 
              for file in [x for x in names if x != name and not x.startswith('.')]:
                artefact = os.path.join(path,file)
                if os.path.isfile(artefact):
                    standard.writeLog(self,"[remoteFiles]: read artefact %s"%artefact)
                    f = open(artefact,"rb")
                    data = f.read()
                    f.close()
                    rd = {}
                    rd['id'] = id
                    rd['filename'] = artefact[len(base)+1:]
                    rd['data'] = data
                    rd['version'] = self.getLangFmtDate(os.path.getmtime(artefact),'eng')
                    r[rd['filename']] = rd
        traverse(basepath,basepath)
    return r


"""
Read repository from base-path.
"""
security.declarePublic('readRepository')
def readRepository(self, basepath, deep=True):
    standard.writeLog(self,"[readRepository]: basepath=%s"%basepath)
    r = {}
    if os.path.exists(basepath):
        def traverse(base, path, level=0):
          initialized = False
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path, name)
            if os.path.isdir(filepath) and (deep or level == 0):
                traverse(base, filepath, level+1)
            elif not initialized and name.startswith('__') and name.endswith('__.py'):
              # Read python-representation of repository-object
              py = parseInit(self, filepath)
              # Analyze python-representation of repository-object
              d = {}
              try:
                  c = get_class(py)
                  d = c.__dict__
              except:
                  d['revision'] = standard.writeError(self,"[readRepository.traverse]: can't analyze filepath=%s"%filepath)
              id = d.get('id',name)
              ### Different from remoteFiles()
              r[id] = {}
              for k in [x for x in d if not x.startswith('__')]:
                v = d[k]
                if inspect.isclass(v):
                  dd = v.__dict__
                  v = []
                  for kk in [x for x in dd if not x.startswith('__')]:
                    vv = dd[kk]
                    # Try to read artefact.
                    if 'id' in vv:
                      fileprefix = vv['id'].split('/')[-1]
                      for file in [x for x in names if x==fileprefix or x.startswith('%s.'%fileprefix)]:
                        artefact = os.path.join(path, file)
                        standard.writeLog(self,"[readRepository]: read artefact %s"%artefact)
                        f = open(artefact, "rb")
                        data = f.read()
                        f.close()
                        try:
                            if isinstance(data, bytes):
                                data = data.decode('utf-8')
                        except:
                            pass
                        vv['data'] = data
                        break
                    v.append((py.find('\t\t%s ='%kk), vv))
                  v.sort()
                  v = [x[1] for x in v]
                r[id][k] = v
              initialized = True
            elif not initialized and name.startswith('__') and name.endswith('__.yaml'):
              # Read YAML-representation of repository-object
              data = parseInit(self, filepath)
              # Analyze YAML-representation of repository-object
              yaml = yamlutil.parse_yaml(data)
              id = list(yaml.keys())[0]
              d = yaml[id]
              ### Different from remoteFiles()
              r[id] = d
              for k in [x for x in d if type(d[x]) is list]:
                v = []
                for vv in d[k]:
                  if type(vv) is dict and 'id' in vv:
                    fileprefix = vv['id'].split('/')[-1]
                    for file in [x for x in names if x==fileprefix or x.startswith('%s.'%fileprefix)]:
                      artefact = os.path.join(path, file)
                      standard.writeLog(self,"[readRepository]: read artefact %s"%artefact)
                      f = open(artefact, "rb")
                      data = f.read()
                      f.close()
                      try:
                          if isinstance(data, bytes):
                              data = data.decode('utf-8')
                      except:
                          pass
                      vv['data'] = data
                      break
                  v.append(vv)
                r[id][k] = v
              initialized = True
        traverse(basepath, basepath)
    return r


def parseInit(self, filepath):
    # Read python-representation of repository-object
    standard.writeLog(self,"[parseInit]: read %s"%filepath)
    f = open(filepath, "rb")
    data = standard.pystr(f.read())
    f.close()
    return data


def parseInitPy(filename):
  pass


def parseInitYaml(filename):
  pass


"""
Read repository from ZMS-instance.
"""
security.declarePublic('localFiles')
def localFiles(self, provider, ids=None):
  standard.writeLog(self,"[localFiles]: provider=%s"%str(provider))
  l = {}
  local = provider.provideRepository(ids)
  for id in local:
    o = local[id]
    l.update(getInitArtefacts(self, o, {'py':getInitPy(self, o), 'yaml':getInitYaml(self, o)}))
  return l


def getInitArtefacts(self, o, initFiles):
  """
  Generate a dictionary of initialization artefacts from the given object and initialization files.

  Args:
    self: The instance of the class containing this method.
    o (dict): A dictionary representing the object to process. It may contain:
      - 'id': The identifier of the object.
      - 'acquired': A flag indicating if the object is acquired (0 or 1).
      - '__filename__': A list representing the filename structure.
      - '__icon__': An optional icon for the object.
      - '__description__': An optional description for the object.
      - 'revision': A version string in the format "0.0.0".
      - Other keys representing attributes, where capitalized keys with list values are processed.
    initFiles (dict): A dictionary where keys are formats (e.g., 'py') and values are lists of strings
      representing the initialization data for each format.

  Returns:
    dict: A dictionary where keys are filenames and values are dictionaries containing:
      - 'id': The identifier of the object.
      - 'filename': The full path of the file.
      - 'data': The content of the file.
      - 'version': The version of the file as a list of integers.
      - 'meta_type': The meta type of the object (e.g., 'Script (Python)').
      - '__icon__': The icon of the object (if provided).
      - '__description__': The description of the object (if provided).
  """
  l = {}
  id = o.get('id','?')
  acquired = int(o.get('acquired',0))
  filename = o.get('__filename__', [id, ['__init__.py','__acquired__.py'][acquired]])
  e = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
  for k in e:
    v = o.get(k)
    if v and isinstance(v, list):
      # Are there duplicated ids after id-quoting?
      id_list = [ standard.id_quote(i['id']) for i in v if i.get('ob') is None ] 
      for i in v:
        if 'id' in i:
          ob = i.get('ob')
          if ob is not None:
            d = {}
            # Someone is so kind to pass us a file-like Object with {filename,data,version,meta_type} as dict.
            if type(ob) is dict:
              d = ob
            # Otherwise we have a Zope-Object and determine everything by ourselves.
            else:
              fileexts = {'DTML Method':'.dtml', 'DTML Document':'.dtml', 'External Method':'.py', 'Page Template':'.zpt', 'Script (Python)':'.py', 'Z SQL Method':'.zsql'}
              fileprefix = i['id'].split('/')[-1]
              data = zopeutil.readData(ob)
              version = ''
              if hasattr(ob,'_p_mtime'):
                version = standard.getLangFmtDate(DateTime(ob._p_mtime).timeTime(), 'eng')
              d['filename'] = os.path.sep.join(filename[:-1]+['%s%s'%(fileprefix, fileexts.get(ob.meta_type, ''))])
              d['data'] = data
              d['version'] = version
              d['meta_type'] = ob.meta_type
            d['id'] = id
            l[d['filename']] = d
          if 'ob' in i:
            del i['ob']
  for format in initFiles:
    data = initFiles[format]
    d = {}
    d['__icon__'] = o.get('__icon__')
    d['__description__'] = o.get('__description__')
    d['id'] = id
    d['filename'] = os.path.sep.join(filename).replace('.py', '.%s' % format)
    d['data'] = '\n'.join(data)
    try:
      d['version'] = [int(x) for x in o.get('revision', '0.0.0').split('.')]
    except:
      # version schmeme 0.0.0 must not contain strings
      d['version'] = list(map(int, re.findall(r'\d+', o.get('revision', '0.0.0'))))
    d['meta_type'] = 'Script (Python)'
    l[d['filename']] = d
  return l


def getInitPy(self, o):
  """
  Generate a Python class representation of a given object.

  This function takes an object `o` (typically a dictionary) and generates a Python
  class definition as a list of strings. The generated class includes attributes
  and nested classes based on the structure and content of the input object.

  Args:
    self: The instance of the class calling this method.
    o (dict): The input object containing keys and values to be represented
          as a Python class.

  Returns:
    list: A list of strings representing the Python class definition.
  """
  id = o.get('id','?')
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
      for iv in v:
        if 'id' in iv:
          i = {k: v for k, v in iv.items() if k != 'ob'}
          try:
            # Prevent id-quoting if duplicates may result
            id_quoted = ( i['id'].startswith('_') and ( standard.id_quote(i['id']) in id_duplicates) ) and i['id'] or standard.id_quote(i['id'])
            py.append('\t\t%s = %s'%(id_quoted, standard.str_json(i, encoding="utf-8", formatted=True, level=3, allow_booleans=False)))
          except:
            py.append('\t\t# ERROR: '+standard.writeError(self,'can\'t getInitPy \'%s\''%i['id']))
          py.append('')
  return py


def getInitYaml(self, o):
  """
  Generate a YAML representation of the given object.

  Args:
    self: The instance of the class containing this method.
    o (dict): A dictionary representing the object to be converted to YAML.

  Returns:
    list: A list of strings representing the YAML structure of the input object.
  """
  id = o.get('id','?')
  yaml = []
  yaml.append('%s:'%id.replace('.','_').replace('-','_'))
  e = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
  keys = sorted([x for x in o if not x.startswith('__') and x not in e])
  for k in keys:
    v = o.get(k)
    yaml.append('  %s:%s%s'%(standard.id_quote(k), [' ','\n    '][type(v) is list or type(v) is dict], standard.str_yaml(v, level=1)))
  for k in e:
    v = o.get(k)
    if v and isinstance(v, list):
      yaml.append('  %s:'%standard.id_quote(k).capitalize())
      yaml.append(standard.str_yaml([{k: v for k, v in i.items() if k != 'ob'} for i in v if 'id' in i], level=1))
  return yaml


security.declarePublic('get_diffs')
def get_diffs(local, remote, ignore=True):
  diff = []
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
      l['data'] = l['data'].replace('\\r','').replace('\r','').strip()
    if isinstance(r.get('data'), str):
      r['data'] = r['data'].replace('\\r','').replace('\r','').strip()
    # Only if text is not equal add to diff list
    if l.get('data') != r.get('data'):
      data = l_data or r_data
      if isinstance(data, str):
        data = data.encode('utf-8')
      mt, enc = standard.guess_content_type(filename.split('/')[-1], data)
      diff.append((filename, mt, l.get('id', r.get('id', '?')), l, r))
  return diff

security.apply(globals())