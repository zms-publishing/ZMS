"""
repositoryutil.py - ZMS repository utility module.

This module provides helper functions and classes for repository access from
Python scripts and other ZMS internals.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
from App.Common import package_home
from DateTime import DateTime
from zope.interface import providedBy
import Acquisition
import inspect
import os
import re
import sys
import io

# Product Imports.
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSRepositoryProvider
from Products.zms import zopeutil
from Products.zms import standard

# Conditional import of yamlutil
yamlutil = None
try:
    from ruamel.yaml import YAML
    from Products.zms import yamlutil
except ImportError:
    standard.writeError(None, "[repositoryutil]: Import error - Python-package ruamel.yaml is required for YAML serialization")
    pass

security = ModuleSecurityInfo('Products.zms.repositoryutil')

security.declarePublic('get_system_conf_basepath')
def get_system_conf_basepath():
    """
    Returns system conf-basepath.
    """
    return package_home(globals())+'/conf'


security.declarePublic('get_providers')
def get_providers(self):
  """
  Returns list of repository-providers.
  @param self: The object context.
  @type self: C{object}
  @return: List of repository-providers.
  @rtype: C{list}
  """
  def get_repo_providers(context):
    children = context.objectValues()
    repo_providers = []
    [repo_providers.append(x) for x in children if IZMSRepositoryProvider.IZMSRepositoryProvider in list(providedBy(x))]
    [repo_providers.extend(get_repo_providers(x)) for x in children if IZMSConfigurationProvider.IZMSConfigurationProvider in list(providedBy(x))]
    return repo_providers
  return get_repo_providers(self.getDocumentElement())



def get_class(py):
  """
  Get class from py-string.

  This function extracts the class definition from a given Python code string 
  and executes it to return the defined class object. It uses regular expressions 
  to identify the class name and then executes the code to obtain the class object.
  """
  id = re.findall(r'class (.*?):', py)[0]
  if sys.version_info >= (3, 13):
    py = py + "\nglobal c\nc = " + id
    exec(py, globals=globals(), locals=locals())
    return eval("c", globals=globals(), locals=locals())
  else:
    exec(py)
    return eval(id)


def parseInit(self, filepath):
    """
    Read file and return data as string.
    @param self: The object context.
    @type self: C{object}
    @param filepath: The path to the file to be read.
    @type filepath: C{str}
    @return: The content of the file as a string.
    @rtype: C{str}
    @note: Logging is performed via L{standard.writeLog()} for debugging purposes.
    @raise IOError: If the file cannot be read.
    """
    standard.writeLog(self,"[parseInit]: read %s"%filepath)
    with open(filepath, "rb") as f:
        data = standard.pystr(f.read())
    return data


security.declarePublic('remoteFiles')
def remoteFiles(self, basepath, deep=True):
    """
    Read configuration data from filesystem base-path.

    This function recursively traverses a directory structure to locate and parse
    repository object definitions stored as YAML or Python files. Files matching
    the pattern C{__*.(__yaml|.py)} are treated as repository object definitions.
    Associated artefacts (non-hidden files in the same directory) are collected
    as related resources.
    @param basepath: The root filesystem path to scan for repository objects.
      Must be an existing directory.
    @type basepath: C{str}
    @param deep: If C{True}, recursively traverse subdirectories. If C{False},
      only scan the root basepath directory. Defaults to C{True}.
    @type deep: C{bool}
    @return: Dictionary mapping relative file paths to metadata dictionaries.
      Each metadata dictionary contains:
        - C{id}: Object identifier from repository definition or filename
        - C{filename}: Relative path from basepath
        - C{data}: File content as string (for .yaml/.py) or bytes (for artefacts)
        - C{version}: Revision from repository definition or file modification time
    @rtype: C{dict}
    @note: Logging is performed via L{standard.writeLog()} for debugging purposes.
    @note: Hidden files (starting with '.') such as C{.DS_Store} are excluded
      from artefact processing.
    @raise IOError: If file read operations fail during traversal.
    """

    standard.writeLog(self,"[remoteFiles]: basepath=%s"%basepath)
    r = {}
    if os.path.exists(basepath):
        def traverse(base, path, level=0):
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path, name)
            if os.path.isdir(filepath) and (deep or level == 0):
              traverse(base, filepath, level+1)
            elif name.startswith('__') and name.split('.')[-2].endswith('__'):
              # Read python-representation of repository-object
              standard.writeLog(self,"[remoteFiles]: read %s"%filepath)
              with open(filepath,"rb") as f:
                  filedata = standard.pystr(f.read())
              # Python-representation of repository-object
              d = {}
              if name.endswith('.yaml'):
                # Parse.yaml
                d = yamlutil.parse(filedata)
              elif name.endswith('.py'):
                try:
                    c = get_class(filedata)
                    d = c.__dict__
                except:
                    d['revision'] = standard.writeError(self,"[remoteFiles.traverse]: can't analyze filepath=%s"%filepath)
              id = d.get('id',name)
              # Different from remoteFiles()
              rd = {}
              rd['id'] = id
              rd['filename'] = filepath[len(base)+1:]
              rd['data'] = filedata
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


security.declarePublic('readRepository')
def readRepository(self, basepath, deep=True):
    """
    Read repository from filesystem base-path.

    Read repository structure from filesystem and parse repository objects.
    This function traverses a filesystem directory structure to discover and parse
    repository object definitions. It supports both Python-style (__init__.py) and
    YAML-style (__init__.yaml) repository object representations.
    @param basepath: The root filesystem path from which to read the repository.
    Must be an existing directory.
    @type basepath: C{str}
    @param deep: If C{True}, recursively traverse subdirectories. If C{False},
    only process the top-level directory (level 0). Defaults to C{True}.
    @type deep: C{bool}
    @return: Dictionary mapping repository object IDs to their parsed metadata.
    Each entry contains:
      - For Python objects: class attributes (excluding those starting with '__')
        with nested class definitions converted to sorted lists of attribute dicts
      - For YAML objects: parsed YAML structure with resolved 'id' field
      - Both formats: 'data' field populated for artefacts (binary files) matching
        object IDs, and 'readme' field if readme.md exists in the directory
    @rtype: C{dict}
    """

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
              # Different from remoteFiles()
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
              readme_path = os.path.join(path, 'readme.md')
              if os.path.isfile(readme_path):
                standard.writeLog(self,"[readRepository]: read artefact %s"%readme_path)
                f = open(readme_path, "rb")
                data = f.read()
                f.close()
                try:
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                except:
                    pass
                r[id]['readme'] = data
              initialized = True
            elif not initialized and name.startswith('__') and name.endswith('__.yaml'):
              # Read YAML-representation of repository-object
              data = parseInit(self, filepath)
              # Analyze YAML-representation of repository-object
              yaml = yamlutil.parse(data)
              id = list(yaml.keys())[0]
              d = yaml[id]
              d['id'] = id
              # Different from remoteFiles()
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
              readme_path = os.path.join(path, 'readme.md')
              if os.path.isfile(readme_path):
                standard.writeLog(self,"[readRepository]: read artefact %s"%readme_path)
                f = open(readme_path, "rb")
                data = f.read()
                f.close()
                try:
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                except:
                    pass
                r[id]['readme'] = data
              initialized = True
        traverse(basepath, basepath)
    return r


security.declarePublic('localFiles')
def localFiles(self, provider, ids=None):
  """
  Read configuration data from ZMS-instance.

  This function retrieves configuration data from a ZMS instance using 
  a provided repository provider. It processes the retrieved data 
  to generate a dictionary of initialization artefacts, which includes
  metadata and file content for each repository object. The function 
  supports both Python and YAML formats for the initialization.

  @param self: The object context.
  @type self: C{object}
  @param provider: An object that provides configuration data, expected to implement the I{provideRepository} method.
  @type provider: C{IZMSRepositoryProvider}
  @param ids: Optional list of identifiers to specify which configuration objects to retrieve. If None, all objects are retrieved.
  @type ids: C{list} or C{None}
  @return: A dictionary mapping filenames to their corresponding data and metadata, generated from the configuration
  objects provided by the configuration provider.
  @rtype: C{dict}
  """
  standard.writeLog(self,"[localFiles]: provider=%s"%str(provider))
  l = {}
  local = provider.provideRepository(ids)
  for id in local:
    o = local[id]
    if self.getConfProperty('ZMS.repository_manager.__init__.format', '') == 'py' or yamlutil is None:
      l.update(init_artefacts(o, {'py':get_init_py(self, o)}))
    else:
      l.update(init_artefacts(o, {'yaml':get_init_yaml(self, o).split('\n')}))
  return l


def init_artefacts(o, init_files):
  """
  Generate a dictionary of initialization artefacts from the given object and initialization files.

  The input object I{o} is expected to have certain keys and structure, and the function processes 
  this object to create a mapping of filenames to their corresponding data and metadata. 
  The initialization files are provided as a dictionary where the key is the format 
  (e.g., 'py' or 'yaml') and the value is a list of strings representing the content 
  of the initialization file. It may contain:
    - I{id}: The identifier of the object.
    - I{acquired}: A flag indicating if the object is acquired (0 or 1).
    - I{__filename__}: A list representing the filename structure.
    - I{__icon__}: An optional icon for the object.
    - I{__description__}: An optional description for the object.
    - I{revision}: A version string in the format "0.0.0".
    - Other keys representing attributes, where capitalized keys with list values are processed.
  The I{initFiles} (dict) is a dictionary where keys are formats (e.g., 'py') and values are lists of strings
  representing the initialization data for each format.
  The return value is a dictionary where keys are filenames and values are dictionaries containing:
    - I{id}: The identifier of the object.
    - I{filename}: The full path of the file.
    - I{data}: The content of the file.
    - I{version}: The version of the file as a list of integers.
    - I{meta_type}: The meta type of the object (e.g., 'Script (Python)').
    - I{__icon__}: The icon of the object (if provided).
    - I{__description__}: The description of the object (if provided).
  
  @param o: Dictionary representing the repository object.
  @type o: C{dict}
  @param init_files: Initialization content grouped by format, for example
      C{{'py': [...]}} or C{{'yaml': [...]}}.
  @type init_files: C{dict}
  @return: Mapping from generated filenames to artefact dictionaries with
      metadata and file content.
  @rtype: C{dict}
  """
  l = {}
  id = o.get('id','?')
  acquired = int(o.get('acquired',0))
  filename = o.get('__filename__', [id, ['__init__.py','__acquired__.py'][acquired]])
  folder = filename[:-1]
  e = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
  for k in e:
    v = o.get(k)
    if v and isinstance(v, list):
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
  # Persist readme as conventional sibling artefact instead of embedding it in __init__.*.
  readme = o.get('readme')
  if readme:
    readme_filename = os.path.sep.join(folder + ['readme.md'])
    l[readme_filename] = {
      'id': id,
      'filename': readme_filename,
      'data': readme,
      'version': o.get('revision', '0.0.0'),
      'meta_type': 'File',
      '__icon__': o.get('__icon__'),
      '__description__': o.get('__description__'),
    }
  for format in init_files:
    data = init_files[format]
    d = {}
    d['__icon__'] = o.get('__icon__')
    d['__description__'] = o.get('__description__')
    d['id'] = id
    d['filename_'] = os.path.sep.join(filename)
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


def get_init_py(self, o):
  """
  Generate a Python class representation of a given object.

  This function takes an object `o` (typically a dictionary) and generates a Python
  class definition as a list of strings. The generated class includes attributes
  and nested classes based on the structure and content of the input object.
  @param self: The object context.
  @type self: C{object}
  @param o: Input object containing keys and values to be represented as a
      Python class.
  @type o: C{dict}
  @return: Python class definition lines.
  @rtype: C{list}
  """
  id = o.get('id','?')
  py = []
  py.append('class %s:'%id.replace('.','_').replace('-','_'))
  py.append('\t"""')
  py.append('\tpython-representation of %s'%o['id'])
  py.append('\t"""')
  py.append('')
  e = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
  keys = sorted([x for x in o if not x.startswith('__') and x not in e and x != 'readme'])
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


def get_init_yaml(self, o):
  """
  Serialize a Python object into a YAML-formatted string.

  This method processes a given object `o` and converts it into a YAML
  representation. It handles attributes and keys in the object, ensuring
  that non-serializable elements (e.g., Acquisition-Wrappers) are excluded.

  @param self: The object context.
  @type self: C{object}
  @param o: Input dictionary-like object to be serialized.
  @type o: C{dict}
  @return: YAML-formatted string representing the serialized object.
  @rtype: C{str}
  """
  if yamlutil is None:
    raise ImportError("Products.zms.yamlutil is required for YAML serialization")

  id = o.get('id','?')
  attrs = sorted([x for x in o if not x.startswith('__') and x==x.capitalize() and isinstance(o[x], list)])
  keys = sorted([x for x in o if not x.startswith('__') and x not in ['id', 'readme'] and x not in attrs and not isinstance(o.get(x), Acquisition.ExplicitAcquisitionWrapper)])
  d = {}
  for k in keys:
    v = o.get(k)
    nv = yamlutil.__cleanup(v)
    if nv:
      d[k] = nv
    elif nv in ['0', 0, False]:
      d[k] = 0
  # Append attribute lists
  for k in attrs:
    nl = []
    l = o.get(k)
    for i in l:
      ni = yamlutil.__cleanup(i)
      if ni:
        if type(ni) is dict:
          # Remove 'ob' from attribute dict (Acquisition-Wrappers are not serializable).
          ni = {x: ni[x] for x in ni if not x=='ob'}
        nl.append(ni)
    if nl:
      d[k] = nl
    elif nl in ['0', 0, False]:
      d[k] = 0
  return yamlutil.dump({id: d})


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