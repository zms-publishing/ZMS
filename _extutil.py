# -*- coding: utf-8 -*-
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
  'zms3.formulator': ['3.2.0dev5',
                      'JSON-based HTML-Forms',
                      'https://bitbucket.org/zms3/formulator',
                      'sponsored by University of Bern, Switzerland'],
  'zms3.photodb': ['0.1.0',
                   'Read EXIF/XMP/IPTC metadata from Photos and manage Image Galleries',
                   'https://bitbucket.org/zms3/photodb',
                   'developed by Christian Meier, Dresden, Germany'],
  'zms3.deployment': ['0.2.2',
                      'Deployment Library',
                      'https://bitbucket.org/zms3/deployment',
                      'developed by SNTL Publishing, Berlin, Germany'],
  'zms3.themes.ultima': ['0.9.0',
                         'Ultima HTML5 Landing Page',
                         'https://bitbucket.org/zms3/themes.ultima',
                         'based on ULTIMA Awesome Landing Page by 8Guild, Odessa, Ukraine'],
  'Pillow': ['2.8.1',
             'The friendly PIL (Python Imaging Library) fork',
             'https://pypi.python.org/pypi/Pillow',
             'developed by Alex Clark'],
  'MySQL-python': ['1.2.5',
                   'Python Interface to MySQL',
                   'https://pypi.python.org/pypi/MySQL-python',
                   'developed by Andy Dustman'],
  'Products.ZMySQLDA': ['3.1.1',
                        'MySQL Database Adapter',
                        'https://pypi.python.org/pypi/Products.ZMySQLDA',
                        'developed by John Eikenberry'],
  'Products.ZSQLiteDA': ['0.6.1',
                         'SQLite Database Adapter',
                         'https://pypi.python.org/pypi/Products.ZSQLiteDA',
                         'developed by Hajime Nakagami'],
  'Products.ZSQLMethods': ['2.13.4',
                           'SQL Method Support',
                           'https://pypi.python.org/pypi/Products.ZSQLMethods',
                           'developed by Zope Foundation and Contributors'],
  'Products.CMFCore': ['2.3.0dev0',
                       'Filesystem Directory Views',
                       'https://pypi.python.org/pypi/Products.CMFCore',
                       'developed by Zope Foundation and Contributors / patched by SNTL Publishing, Berlin, Germany'],
  'lesscpy': ['0.10.2',
              'Python LESS Compiler',
              'https://pypi.python.org/pypi/lesscpy',
              'developed by Jóhann T Maríusson'],
  'Zope2': ['2.13.23dev0',
            'Open-source web application server',
            'https://github.com/zopefoundation/Zope',
            'developed by Zope Foundation and Contributors / patched by SNTL Publishing, Berlin, Germany'],
  'ZODB': ['4.1.0',
           'Set of tools for using the Zope Object Database',
           'https://github.com/zopefoundation/ZODB',
           'developed by Zope Foundation and Contributors'],
  'zope.publisher': ['3.13.4',
                     'Map requests from HTTP/WebDAV/FTP clients, web browsers and XML-RPC onto Python objects',
                     'https://github.com/zopefoundation/zope.publisher',
                     'developed by Zope Foundation and Contributors'],
  'zope.pagetemplate': ['4.1.0',
                     'Templating mechanism that achieves a clean separation of presentation and application logic',
                     'https://github.com/zopefoundation/zope.pagetemplate',
                     'developed by Zope Foundation and Contributors'],
  'zope.sendmail': ['3.7.5',
                     'Send mails using transaction mechanism and queuing',
                     'https://github.com/zopefoundation/zope.sendmail',
                     'developed by Zope Foundation and Contributors']
}

class ZMSExtensions():
  """
    Utility to handle zms3.extensions
  
    Management interface is at ZMS > Configuration > System > Installed Libraries
    @see zpt/ZMS/manage_customize.zpt line 452
    @see _confmanager.py line 665
    @see ZMSGlobals.py line 1118
  """
  getAll__roles__ = None
  getAllExtensions__roles__ = None
  getAllThemes__roles__ = None
  getAllProducts__roles__ = None
  getAllOthers__roles__ = None
  getAllProjspecs__roles__ = None
  getAllFramework__roles__ = None
  isEnabled__roles__ = None  
  getHint__roles__ = None  
  getInfo__roles__ = None  
  getVersionAvailable__roles__ = None  
  getVersionInstalled__roles__ = None  
  getFiles__roles__ = None  
  getFilesToImport__roles__ = None
  getExample__roles__ = None  
  getExampleToImport__roles__ = None
  importExample__roles__ = None
  getTemplates__roles__ = None  
  getTemplatesToImport__roles__ = None
  importTemplates__roles__ = None
  getUrl__roles__ = None
      
  def __init__(self):
    self.pkg = {}
    self.pkg_names = []
    self.pkg_available = []
    self.pkg_hints = []
    self.pkg_infos = []
    self.pkg_ready = []
    self.pkg_confs = []
    self.pkg_installed = []
    self.pkg_urls = []
        
    for name, info in sorted(EXTENSIONS.iteritems()):
      self.pkg_names.append(name)
      self.pkg_available.append(info[0])
      self.pkg_hints.append(info[1])
      self.pkg_infos.append(info[3])
      self.pkg_urls.append(info[2])
      package = str(WorkingSet().find(Requirement.parse(name))).split()
      if ((name in package) and (len(package) == 2)):
        # TODO: **Normalize Versions** acc. to `PEP 440`: http://legacy.python.org/dev/peps/pep-0440/
        # The version specified requires normalization, consider using '3.2.0.dev3' instead of '3.2.0dev3' etc. + 
        # pip v6.0.6 does not append svn revision specified in `setup.cfg` as v1.5.6 before
        # => `zms.zms_version()` have to be adjusted too...
        self.pkg_installed.append(package[1].replace('.dev', 'dev'))
        self.pkg_ready.append(True)
        try:
          confres = ResourceManager().resource_listdir(name, 'conf')
        except:
          confres = None
        if confres:
          confxml = filter(lambda ob: ob.endswith('.xml') or ob.endswith('.zip'), confres)
          if len(confxml) > 0:
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

  def getAllExtensions(self, prj=None):
    """
      Return all zms3.* extensions
    """
    pkg = filter(lambda x: x.startswith('zms3.') and not x.startswith('zms3.themes.') and x.find('theme') < 0, self.pkg_names)
    if prj is not None:
      pkg = filter(lambda x: x not in self.getAllProjspecs(prj), pkg)
    return pkg

  def getAllThemes(self, prj=None):
    """
      Return all zms3.themes.* extensions
    """
    pkg = filter(lambda x: x.startswith('zms3.themes.') or x.find('theme') >= 0, self.pkg_names)
    if prj is not None:
      pkg = filter(lambda x: x not in self.getAllProjspecs(prj), pkg)
    return pkg

  def getAllProducts(self):
    """
      Return all Products.* extensions
    """
    pkg = filter(lambda x: x.startswith('Products.'), self.pkg_names)
    return pkg
  
  def getAllOthers(self):
    """
      Return all other extensions
    """
    pkg = filter(lambda x: not x.startswith('zms3.') and not x.startswith('Products.') and x not in self.getAllFramework(), self.pkg_names)
    return pkg

  def getAllProjspecs(self, prj=None):
    """
      Return all project specific extensions (define parameter ZMS.Project at ZMS > System > Miscelleanous)
    """
    if prj is not None:
      pkg = filter(lambda x: x.startswith('zms3.%s' % prj.lower()), self.pkg_names)
      return pkg
    return []

  def getAllFramework(self):
    """
      Return all framework specific packages
    """
    pkg = filter(lambda x: x.startswith('Zope2') or x.startswith('ZODB') or x.find('zope') >= 0, self.pkg_names)
    return pkg

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

  def getInfo(self, ext=None):
    """
      Return info about given extension to display as hover-link-title
    """
    if ext in self.pkg_names:
      return self.pkg_infos[self.pkg_names.index(ext)]
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
          filename = ResourceManager().resource_filename(ext, 'conf/' + f)
          filenames.append(filename)
        return filenames
    return []
  
  def getExample(self, ext=None):
    """
      Return an available *.example.xml or *.example.zip file of given extension
    """
    if ext in self.pkg_names:
      files = self.pkg_confs[self.pkg_names.index(ext)]
      if files:
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
      contents = open(_fileutil.getOSPath(filename), 'rb')
      _importable.importFile(context, contents, request, _importable.importContent)
      contents.close()
      
  def getTemplates(self, ext=None):

    # TODO: _extutil.getTemplates()
    
    return None
  
  def getTemplatesToImport(self, ext=None):

    # TODO: _extutil.getTemplatesToImport()
    
    return None
  
  def importTemplates(self, ext=None, context=None, request=None):

    # TODO: _extutil.importTemplates()

    return None
      
  def getUrl(self, ext=None):
    """
      Return url to package website of given extension if available
    """    
    if ext in self.pkg_names:
      return self.pkg_urls[self.pkg_names.index(ext)]
    else:
      return None 
  
