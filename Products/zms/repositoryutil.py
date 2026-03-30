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


security.declarePublic('get_modelfileset_from_disk')
def get_modelfileset_from_disk(self, basepath, deep=True):
    """
    High-level: Collect all model files from a filesystem repository path.

    Recursively traverses the directory tree rooted at C{basepath} looking
    for repository object folders (identified by C{__init__.py} or
    C{__init__.yaml}).  For each folder found, the init file and all sibling
    resource files are read into metadata records.

    Delegates to:
      - L{get_file_from_disk} — to read each individual file and build its
        metadata record C{{id, filename, data, version}}.
      - L{parse_modelfile} — to extract the revision from the init file's
        parsed object definition.

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
        - C{data}: File content as string (for .yaml/.py) or bytes
        - C{version}: Revision from repository definition or file modification time
    @rtype: C{dict}
    @raise IOError: If file read operations fail during traversal.
    @see: L{get_file_from_disk}, L{parse_modelfile}
    """

    standard.writeLog(self,"[get_modelfileset_from_disk]: basepath=%s"%basepath)
    r = {}
    if os.path.exists(basepath):
        def traverse(base, path, level=0):
          initialized = False
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path, name)
            if os.path.isdir(filepath) and (deep or level == 0):
              traverse(base, filepath, level+1)
            elif not initialized \
                and name.startswith('__') \
                and name.split('.')[-2].endswith('__') \
                and name.split('.')[-1] in ['py', 'yaml']:
              # Read repository object definition.
              rd = get_file_from_disk(self, base, path, name)
              r[rd['filename']] = rd
              # Get version from repository definition if available,
              # otherwise use file modification time.
              artefact = parse_modelfile(self, path, name, rd['data'])
              rd['version'] = artefact.get("revision",rd['version'])
              # Read related file-resources. 
              for file in [x for x in names if x != name and not x.startswith('.')]:
                filepath = os.path.join(path,file)
                if os.path.isfile(filepath):
                    rd = get_file_from_disk(self, base, path, file)
                    r[rd['filename']] = rd
              initialized = True
        traverse(basepath,basepath)
    return r

def get_file_from_disk(self, base, path, name):
    """Mid-level: Read a single file from disk and return a metadata record.

    Delegates to L{read_file_from_disk} for the actual I/O, then packages the
    result into a dict with C{id}, C{filename} (relative to C{base}), C{data},
    and C{version} (file modification time).

    Called by L{get_modelfileset_from_disk}.

    @param base: The repository base path used to compute relative filenames.
    @type base: C{str}
    @param path: The directory containing the file.
    @type path: C{str}
    @param name: The filename to read.
    @type name: C{str}
    @return: Metadata record C{{id, filename, data, version}}.
    @rtype: C{dict}
    @see: L{read_file_from_disk}
    """
    filepath = os.path.join(path, name)
    filedata = read_file_from_disk(self, path, name)
    d = {}
    d['id'] = id
    d['filename'] = filepath[len(base)+1:]
    d['data'] = filedata
    d['version'] = self.getLangFmtDate(os.path.getmtime(filepath),'eng')
    return d


security.declarePublic('get_models_from_disk')
def get_models_from_disk(self, basepath, deep=True):
    """
    High-level: Load and parse all model definitions from a filesystem
    repository path.

    Traverses the directory tree rooted at C{basepath}, reads each init
    file (C{__init__.py} / C{__init__.yaml}), parses it into a structured
    model definition, and resolves embedded attribute data from sibling
    resource files.

    Unlike L{get_modelfileset_from_disk} (which returns raw file records),
    this function returns fully parsed model objects keyed by object ID.

    Delegates to:
      - L{read_file_from_disk} — low-level file I/O for init and readme files.
      - L{parse_modelfile} — to parse the init file contents into a model dict.
      - L{value_data} — to resolve embedded attribute data from sibling files.

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
        - Both formats: 'data' field populated for sibling resource files matching
          object IDs, and 'readme' field if readme.md exists in the directory
    @rtype: C{dict}
    @see: L{get_modelfileset_from_disk}, L{read_file_from_disk}, L{parse_modelfile}, L{value_data}
    """

    standard.writeLog(self,"[get_models_from_disk]: basepath=%s"%basepath)
    r = {}
    if os.path.exists(basepath):
        def traverse(base, path, level=0):
          initialized = False
          names = os.listdir(path)
          for name in names:
            filepath = os.path.join(path, name)
            if os.path.isdir(filepath) and (deep or level == 0):
                traverse(base, filepath, level+1)
            elif not initialized \
                and name.startswith('__') \
                and name.split('.')[-2].endswith('__') \
                and name.split('.')[-1] in ['py', 'yaml']:
              filedata = read_file_from_disk(self, path, name)
              d = parse_modelfile(self, path, name, filedata)
              id = d.get('id', path.split(os.sep)[-1])
              # For Python-style repository objects, 
              # convert nested class definitions to sorted lists of attribute dicts.
              if name.endswith('.py'):
                r[id] = {}
                for k in [x for x in d if not x.startswith('__')]:
                  v = d[k]
                  if inspect.isclass(v):
                    dd = v.__dict__
                    v = []
                    for kk in [x for x in dd if not x.startswith('__')]:
                      vv = value_data(self, dd[kk], names, path, name)
                      # Sort by position in file to preserve order of definitions.
                      v.append((filedata.find('\t\t%s ='%kk), vv))
                    # Sort by position in file and remove position from value.
                    v = [x[1] for x in sorted(v, key=lambda x: x[0])]
                  r[id][k] = v
              # For YAML-style repository objects, 
              # use the parsed YAML structure directly.
              elif name.endswith('.yaml'):
                r[id] = d
                for k in [x for x in d if type(d[x]) is list]:
                  v = []
                  for vv in d[k]:
                    v.append(value_data(self, vv, names, path, name))
                  r[id][k] = v
              r[id]['readme'] = read_file_from_disk(self, path, 'readme.md')
              initialized = True
        traverse(basepath, basepath)
    return r

def value_data(self, vv, names, path, file):
    if type(vv) is dict and 'id' in vv:
      fileprefix = vv['id'].split('/')[-1]
      for file in [x for x in names if x==fileprefix or x.startswith('%s.'%fileprefix)]:
        vv['data'] = read_file_from_disk(self, path, file)
        break
    return vv

def parse_modelfile(self, path, filename, data):
    """Low-level: Parse in-memory model file contents into a model definition dict.

    Interprets the C{data} string (previously read by L{read_file_from_disk})
    according to the file extension:
      - C{.yaml}: parsed via L{yamlutil.parse} into a dict keyed by object ID.
      - C{.py}: executed via L{get_class} to extract the class C{__dict__}.

    Does B{not} perform any filesystem I/O — it operates solely on the
    C{data} parameter.

    Called by L{get_modelfileset_from_disk} and L{get_models_from_disk}.

    @param path: Directory path (used only for error messages).
    @type path: C{str}
    @param filename: Filename including extension (determines parse strategy).
    @type filename: C{str}
    @param data: The file contents to parse (text string).
    @type data: C{str}
    @return: Parsed model definition dict; on error contains a C{revision} key
      with the error message.
    @rtype: C{dict}
    @see: L{read_file_from_disk}, L{get_class}, L{yamlutil.parse}
    """
    d = {}
    filepath = os.path.join(path, filename)
    try:
        # For .yaml files, parse the YAML content and extract the object definition.
        if filename.endswith('.yaml'):
            yaml = yamlutil.parse(data)
            if not yaml or len(yaml) == 0 or list(yaml.keys())[0] is None or len(yaml.keys()) > 1:
                # Invalid YAML structure: must contain exactly one top-level key representing the object ID.
                d['id'] = path.split(os.sep)[-1]
                d['name'] = path.split(os.sep)[-1]
                d['revision'] = standard.writeError(self,"[get_modelfileset_from_disk.traverse]: can't analyze filepath=%s"%filepath)
            else:
                id = list(yaml.keys())[0]
                d = yaml[id]
                d['id'] = id
        # For .py files, execute the Python code to obtain the class definition 
        # and extract its attributes.
        elif filename.endswith('.py'):
            py = get_class(data)
            d = py.__dict__
    except:
        d['id'] = path.split(os.sep)[-1]
        d['name'] = path.split(os.sep)[-1]
        d['revision'] = standard.writeError(self,"[get_modelfileset_from_disk.traverse]: can't analyze filepath=%s"%filepath)
    return d

def read_file_from_disk(self, path, filename):
  """Low-level: Read raw file contents from the filesystem.

  Opens the file at C{path/filename} in binary mode and attempts UTF-8
  decoding.  Returns C{str} if decodable, raw C{bytes} otherwise, or
  C{None} if the file does not exist.

  This is the lowest-level I/O helper in the repository utilities.
  Called by L{get_file_from_disk}, L{get_models_from_disk}, L{value_data},
  and any other function needing raw file contents.

  @param path: Directory containing the file.
  @type path: C{str}
  @param filename: Name of the file to read.
  @type filename: C{str}
  @return: File contents as C{str} (UTF-8) or C{bytes}, or C{None} if
    the file does not exist.
  @rtype: C{str} or C{bytes} or C{None}
  """
  data = None
  filepath = os.path.join(path, filename)
  if os.path.isfile(filepath):
    standard.writeLog(self,"[read_file_from_disk]: %s"%filepath)
    with open(filepath,"rb") as f:
      data = f.read()
      try:
        if isinstance(data, bytes):
          data = data.decode('utf-8')
      except:
        pass
    return data


security.declarePublic('get_modelfileset_from_zodb')
def get_modelfileset_from_zodb(self, provider, ids=None):
  """High-level: Export model files from ZODB via a repository provider.

  Queries the C{provider} for repository objects stored in the ZODB, then
  serializes each object into a set of filesystem-ready file records (init
  file + sibling resource files).

  This is the ZODB counterpart to L{get_modelfileset_from_disk}; both
  return the same C{{filename: {{id, filename, data, version, ...}}}} dict
  structure so that results can be compared with L{get_diffs}.

  Delegates to:
    - C{provider.provideRepository(ids)} — to retrieve objects from ZODB.
    - L{get_init_py} / L{get_init_yaml} — to serialize objects into init
      file content (Python class or YAML).
    - L{create_modelfileset} — to build the filename-to-metadata mapping
      from the serialized init content and sibling resource objects.

  @param provider: A repository provider implementing
    C{IZMSRepositoryProvider.provideRepository()}.
  @type provider: C{IZMSRepositoryProvider}
  @param ids: Optional list of object IDs to export. If C{None}, all
    objects from the provider are exported.
  @type ids: C{list} or C{None}
  @return: Dictionary mapping filenames to metadata records.
  @rtype: C{dict}
  @see: L{get_modelfileset_from_disk}, L{create_modelfileset}, L{get_init_py}, L{get_init_yaml}
  """
  standard.writeLog(self,"[get_modelfileset_from_zodb]: provider=%s"%str(provider))
  l = {}
  local = provider.provideRepository(ids)
  for id in local:
    o = local[id]
    if self.getConfProperty('ZMS.repository_manager.__init__.format', '') == 'py' or yamlutil is None:
      l.update(create_modelfileset(o, {'py':get_init_py(self, o)}))
    else:
      l.update(create_modelfileset(o, {'yaml':get_init_yaml(self, o).split('\n')}))
  return l


def create_modelfileset(o, init_files):
  """Mid-level: Build the complete set of file records for one model object.

  Given a ZODB model object dict C{o} and its pre-serialized init file
  content (from L{get_init_py} or L{get_init_yaml}), this function
  produces the full filename-to-metadata mapping that represents the
  object on disk.  The mapping includes:
    - The init file itself (C{__init__.py} or C{__init__.yaml}).
    - Sibling resource files (templates, scripts, images) extracted from
      the object's attribute lists.
    - A C{readme.md} sibling if the object carries a C{readme} field.

  Does B{not} perform filesystem I/O — it operates purely on in-memory
  data.  Called by L{get_modelfileset_from_zodb} for each model object.

  @param o: Repository object dict.  Expected keys include C{id},
    C{acquired}, C{__filename__}, C{__icon__}, C{__description__},
    C{revision}, and capitalized attribute-list keys.
  @type o: C{dict}
  @param init_files: Pre-serialized init content grouped by format,
    e.g. C{{'py': [line, ...]}} or C{{'yaml': [line, ...]}}.
  @type init_files: C{dict}
  @return: Mapping from generated filenames to file-record dicts, each
    containing C{id}, C{filename}, C{data}, C{version}, C{meta_type}.
  @rtype: C{dict}
  @see: L{get_modelfileset_from_zodb}, L{get_init_py}, L{get_init_yaml}
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