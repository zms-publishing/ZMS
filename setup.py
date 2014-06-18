# @see http://gpiot.com/blog/creating-a-python-package-and-publish-it-to-pypi/

import os
import sys
import site
from distutils.core import setup
from setuptools import find_packages

# @see https://docs.python.org/2/library/site.html
# says site.getusersitepackages() "New in version 2.7" but it is still missing at
# 2.7.5 (default, Mar  9 2014, 22:15:05) 
# [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)]
#
# site_packages = site.getusersitepackages()
#
# therefore get it from sys.path
for path in sys.path:
  if path.endswith('site-packages'):
    site_packages = path

setup_path = os.path.dirname(__file__)

README = open(os.path.join(setup_path, 'README')).read()

#VERSION = __import__("zms").__version__
VERSION = open(os.path.join(setup_path, 'version.txt')).read()
if VERSION.find('.REV')>0:
  print 'Add the revision number to version.txt'
  sys.exit()
else:
  # remove revision and text from version info for PyPI
  VERSION = VERSION.replace('ZMS3','').replace('-','').strip().split('.')
  if len(VERSION)==4: VERSION.pop()
  VERSION = '.'.join(VERSION)

# Determined packages are required for a OS Independent installation
# Binaries for Windows are available at this order(!) and these versions(!) only
# For Windows Package-Manager "easy_install" MUST BE used, for *nix "pip"
# @see http://www.zms-publishing.com/download/probleme/index_ger.html#e5969
INSTALL_REQUIRES = [
 'ExtensionClass==2.13.2', # or 'ExtensionClass==4.1a1' for OS != 'win'
 'Record==2.13.0',
 'Missing==2.13.1',
 'Acquisition==2.13.8',
 'AccessControl==3.0.6',
 'zope.site==3.9.2',
 'zope.publisher==3.13.4',
 'zope.untrustedpython',
 'zope.browserresource==3.10.3', # @see configure.zcml <browser:resourceDirectory> just works with v3.10.3
 'Zope2==2.13.22',  # @see https://pypi.python.org/pypi/Zope2/2.13.22
 'Products.CMFCore==2.2.8', # @see configure.zcml <cmf:registerDirectory>

# 'PIL==1.1.7', # @see https://pypi.python.org/pypi/PIL/
# pip (>1.4.1) announces PIL as a insecure and unverifiable file, because PIL is not hosted at PyPI 
# => $ pip install PIL --allow-external PIL --allow-unverified PIL
# 'MySQL-python', # errors while installing
# 'Products.ZMySQLDA', # see MySQL-python above

 'Products.ZSQLiteDA',
 'Products.ZSQLMethods',

 'Products.StandardCacheManagers',
 'Products.BTreeFolder2',
 'nt-svcutils',
 'persistent',
 'mechanize==0.2.5',
 'six',
 'zeo',
 'zodb',
 'zc.lockfile',
 'zope.filerepresentation',
 'zope.datetime',
 'zope.dottedname',
 'zope.formlib',
 'zope.globalrequest',
 'zope.traversing',
 'zope.security',
 'zope.schema',
 'zope.lifecycleevent',
 'zope.interface',
 'zope.i18nmessageid',
 'zope.i18n',
 'nt_svcutils',
 'products.standardcachemanagers',
 'zope.component',
 'transaction',
 'zope.event',
 'products.pythonscripts',
 'products.mimetools',
 'products.mailhost',
 'products.externalmethod',
 'products.btreefolder2',
 'zope.viewlet',
 'zope.testing',
 'zope.testbrowser',
 'zope.tales',
 'zope.tal',
 'zope.structuredtext',
 'zope.size',
 'zope.sequencesort',
 'zope.sendmail',
 'zope.ptresource',
 'zope.proxy',
 'zope.processlifetime',
 'zope.pagetemplate',
 'zope.location',
 'zope.exceptions',
 'zope.deferredimport',
 'zope.contenttype',
 'zope.contentprovider',
 'zope.container',
 'zope.configuration',
 'zope.browserpage',
 'zope.browsermenu',
 'zope.browser',
 'zlog',
 'zexceptions',
 'zdaemon',
 'tempstorage',
 'pytz',
 'initgroups',
 'docutils',
 'zopeundo',
 'zodb3',
 'zconfig',
 'restrictedpython',
 'products.zctextindex',
 'products.zcatalog',
 'products.ofsp',
 'persistence',
 'multimapping',
 'documenttemplate',
 'datetime',
 'zope.annotation',
 'btrees',
]
  
PACKAGE_DATA = []
# Exclude special folders and files
for dirpath, dirnames, filenames in os.walk('.'):
  if (
    '.'                           != dirpath and
    '.settings'                   not in dirpath and
    '.svn'                        not in dirpath and
    'ZMS3.egg-info'               not in dirpath and
    'dist'                        not in dirpath and
    'hotfixes'                    not in dirpath
    ): 
    if filenames: 
      for filename in filenames:
        if filename != '.DS_Store':
          PACKAGE_DATA.append(dirpath[2:]+'/%s' % filename)
# Include files from root path (because '.' is exclude above)
PACKAGE_DATA.append('configure.zcml')
PACKAGE_DATA.append('*.zpt')
PACKAGE_DATA.append('*.txt')

# Hotfixes to get Zope running
# @see http://www.zms-publishing.com/download/probleme/index_ger.html#e6073
DATA_FILES = [
  (os.path.join(site_packages, 'Products/Five'), ['hotfixes/Products/Five/configure.zcml']),
  (os.path.join(site_packages, 'Products/PageTemplates'), ['hotfixes/Products/PageTemplates/PageTemplate.py']),
  (os.path.join(site_packages, 'zdaemon'), ['hotfixes/zdaemon/zdctl.py'])
]

CLASSIFIERS = [
  'Framework :: Zope2',
  'Programming Language :: Python :: 2.7',
  'License :: OSI Approved :: GNU General Public License (GPL)',
  'Operating System :: OS Independent',
  'Topic :: Internet :: WWW/HTTP :: Site Management',
  'Intended Audience :: Education',
]

setup(
  name                  = 'ZMS3',
  description           = 'ZMS: Simplified Content Modelling',
  long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'http://www.zms-publishing.com',
  #download_url          = 'https://pypi.python.org/packages/source/Z/ZMS3/ZMS3-%s.tar.gz' % VERSION,
  install_requires      = INSTALL_REQUIRES,
  namespace_packages    = ['Products'],
  packages              = ['Products.zms'],
  package_dir           = {'Products.zms': '.'},
  package_data          = {'Products.zms': PACKAGE_DATA},
  data_files            = DATA_FILES,
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)