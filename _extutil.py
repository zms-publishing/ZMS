################################################################################
# _extutil.py
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
from pkg_resources import WorkingSet, Requirement, ResourceManager

EXTENSIONS = {
  'zms3.formulator': ['3.2.0dev3', 'JSON-based HTML-Forms', 'http://code.zms3.com/formulator'],
  'zms3.deployment': ['0.2.1', 'Deployment Library', 'http://code.zms3.com/deployment'],
# 'zms3.app.foo': ['{VERSION}', 'Test Description', ''],  # Test unavailable Extension
# 'zms3.foo': ['1.2.3', 'Test Description', ''],          # Test unavailable Extension 
# 'Foo': ['0.0.1', 'Test Description', '#'],              # Test unavailable Python Package
  'Pillow': ['2.7.0', 'Fork of Python Imaging Library', 'https://pypi.python.org/pypi/Pillow'],
  'MySQL-python': ['1.2.5', 'Python interface to MySQL', 'https://pypi.python.org/pypi/MySQL-python'],
  'Products.ZMySQLDA': ['3.1.1', 'MySQL Database Adapter', 'https://pypi.python.org/pypi/Products.ZMySQLDA'],
  'Products.ZSQLiteDA': ['0.6.1', 'SQLite database adapter', 'https://pypi.python.org/pypi/Products.ZSQLiteDA'],
  'Products.ZSQLMethods': ['2.13.4', 'SQL method support', 'https://pypi.python.org/pypi/Products.ZSQLMethods'],
  'Products.CMFCore': ['2.2.8', 'Provides Filesystem Directory Views', 'https://pypi.python.org/pypi/Products.CMFCore'],
  'lesscpy': ['0.10.2', 'Python LESS compiler', 'https://pypi.python.org/pypi/lesscpy'],
}

class Extensions():
  """
    Utility to handle zms3.extensions
  
    Management interface is at ZMS > Configuration > System > Installed Libraries
    @see zpt/ZMS/manage_customize.zpt line 452
    @see _confmanager.py line 665
    @see ZMSGlobals.py line 1118
  """
  getAll__roles__               = None
  isEnabled__roles__            = None  
  getHint__roles__              = None  
  getVersionAvailable__roles__  = None  
  getVersionInstalled__roles__  = None  
  getFiles__roles__             = None  
  getFilesToImport__roles__     = None
  getExample__roles__           = None  
  getExampleToImport__roles__   = None
  importExample__roles__        = None
  getUrl__roles__               = None
      
  def __init__(self):
    self.pkg                    = {}
    self.pkg_names              = []
    self.pkg_available          = []
    self.pkg_hints              = []
    self.pkg_ready              = []
    self.pkg_confs              = []
    self.pkg_installed          = []
    self.pkg_urls               = []
        
    for name, info in sorted(EXTENSIONS.iteritems()):
      self.pkg_names.append(name)
      self.pkg_available.append(info[0])
      self.pkg_hints.append(info[1])
      self.pkg_urls.append(info[2])
      package = str(WorkingSet().find(Requirement.parse(name))).split()
      if ((name in package) and (len(package)==2)):
        # TODO: **Normalize Versions** acc. to `PEP 440`: http://legacy.python.org/dev/peps/pep-0440/
        # The version specified requires normalization, consider using '3.2.0.dev3' instead of '3.2.0dev3' etc. + 
        # pip v6.0.6 does not append svn revision specified in `setup.cfg` as v1.5.6 before
        # => `zms.zms_version()` have to be adjusted too...
        self.pkg_installed.append(package[1].replace('.dev','dev'))
        self.pkg_ready.append(True)
        try:
          confres = ResourceManager().resource_listdir(name, 'conf')
        except:
          confres = None
        if confres:
          confxml = filter(lambda ob: ob.endswith('.xml') or ob.endswith('.zip'), confres)
          if len(confxml)>0:
            self.pkg_confs.append(confxml)
          else:
            self.pkg_confs.append(None)
        else:
          self.pkg_confs.append(None)
      else:
        self.pkg_installed.append(None)
        self.pkg_confs.append(None)
        self.pkg_ready.append(False)

    
  def getAll(self):
    """
      Return all defined extensions
    """
    return self.pkg_names
  
  def isEnabled(self, ext=None):
    """
      Return TRUE if given extension is available as python package in environment
      otherwise FALSE
    """
    if ext in self.pkg_names:
      return self.pkg_ready[self.pkg_names.index(ext)]
    else:
      return False
  
  def getHint(self, ext=None):
    """
      Return short description of given extension
    """
    if ext in self.pkg_names:
      return self.pkg_hints[self.pkg_names.index(ext)]
    else:
      return None

  def getVersionAvailable(self, ext=None):
    """
      Return python package version of given extension configured above
    """
    if ext in self.pkg_names:
      return self.pkg_available[self.pkg_names.index(ext)]
    else:
      return None
  
  def getVersionInstalled(self, ext=None):
    """
      Return python package version of given extension installed in environment
    """
    if ext in self.pkg_names:
      return self.pkg_installed[self.pkg_names.index(ext)]
    else:
      return None

  def getFiles(self, ext=None):
    """
      Return configuration files found at $LIBS/zms3/{ext}/conf/*.xml
    """
    if ext in self.pkg_names:
      files = self.pkg_confs[self.pkg_names.index(ext)]
      files = filter(lambda filename: not filename.endswith('.example.xml') and not filename.endswith('.example.zip'), files)
      return files
    else:
      return None
      
  def getFilesToImport(self, ext=None):
    """
      Return list of configuration files of given extension with full pathnames
    """
    if ext in self.pkg_names:
      files = self.pkg_confs[self.pkg_names.index(ext)]
      if files:
        filenames = []
        for f in files:
          filename = ResourceManager().resource_filename(ext, 'conf/'+f)
          filenames.append(filename)
        return filenames
    return []
  
  def getExample(self, ext=None):
    """
      Return an available *.example.xml or *.example.zip file of given extension
    """
    if ext in self.pkg_names:
      files = self.pkg_confs[self.pkg_names.index(ext)]
      for filename in files:
        if filename.endswith('.example.xml') or filename.endswith('.example.zip'):
          return filename
    return None
  
  def getExampleToImport(self, ext=None):
    """
      Return an available example file of given extension with full pathname
    """
    example = self.getExample(ext)
    if example is not None:
      files = self.getFilesToImport(ext)
      for filename in files:
        if filename.endswith(example):
          return filename
    return None
  
  def importExample(self, ext=None, context=None, request=None):
    """
      Import example file of given extension at given context
    """
    import _fileutil
    import _importable
    example = self.getExample(ext)
    if example is not None:
      filename = self.getExampleToImport(ext)
      contents = open(_fileutil.getOSPath(filename),'rb')
      _importable.importFile(context, contents, request, _importable.importContent)
      contents.close()
      
  def getUrl(self, ext=None):
    """
      Return url to package website of given extension if available
    """    
    if ext in self.pkg_names:
      return self.pkg_urls[self.pkg_names.index(ext)]
    else:
      return None 
  