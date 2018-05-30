"""
The ZMS environment consists of an application server based on pegged versions 
of depending packages (see requirements.txt).

  Use
    $ cd path/to/zms/checkout
    $ pip install -r https://raw.githubusercontent.com/zopefoundation/Zope/zmi-bootstrap/requirements-full.txt
    $ pip install -r requirements-zope4-bootstrap-zmi.txt
    $ pip install -r requirements.txt
    $ pip install -e .
  to install the environment fetching the latest development snapshots from SVN/GIT-Repositories
  (currently unstable)

@see http://gpiot.com/blog/creating-a-python-package-and-publish-it-to-pypi/
@see https://caremad.io/2013/07/setup-vs-requirement/
"""
import os
import sys
from setuptools import setup

setup_path = os.path.dirname(__file__)
for path in sys.path:
  if path.endswith('site-packages'):
    site_packages = path

INSTALL_REQUIRES = [
  'Zope>=4.0b4',
  'docutils',
  'initgroups',
  'nt-svcutils',
  'mechanize',
  'Products.CMFCore',
  'Products.ExternalMethod',
  'Products.GenericSetup',
  'Products.MailHost',
#  'Products.MIMETools', # completely outdated, needs to be ported to python3
  'Products.OFSP',
  'Products.StandardCacheManagers',
  'tempstorage',
  'zLOG',
  'zope.app.publication',
  'zope.authentication',
  'zope.untrustedpython',
  'zope.error',
  'ZopeUndo',
  
  # Pinned versions because of bugs:
  # due to zdaemon>=4.0.1 causes AttributeError: ZopeCtlOptions instance has no attribute 'transcript'
  # 'zdaemon<4.0.1',
  # zope.browserresource>4.1.0 requires zope.publisher>=4.2.1
  # 'zope.browsermenu<4.1.0',
  # due to zope.publisher>=4.0.0 causes errors on rendering legacy DTML-Methods
  # 'zope.publisher<4.0.0',
  # due to ZopeUndo==4.0 causes ZEO DisconnectedError on manageUndo
  # 'ZopeUndo<4.0.0',
]

README = open(os.path.join(setup_path, 'README')).read()

# Remove text from version for PyPI
VERSION = open(os.path.join(setup_path, 'Products', 'zms', 'version.txt')).read().replace('ZMS3-', '').replace('.REV', '')
VERSION = VERSION.strip().split('.')
# Remove revision too
if len(VERSION)==4: VERSION.pop()
VERSION = '.'.join(VERSION)

PACKAGE_DATA = []
# Exclude special folders and files
for dirpath, dirnames, filenames in os.walk('.'):
  if (
    '.'                           != dirpath and
    '.settings'                   not in dirpath and
    '.svn'                        not in dirpath and
    'ZMS3.egg-info'               not in dirpath and
    'dist'                        not in dirpath and
    'dll'                         not in dirpath and
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

DATA_FILES = []
if sys.platform[:3].lower() == "win":
  DATA_FILES += [
    (site_packages, ['dll/pywintypes27.dll', 'dll/win32file.pyd'])
  ]

CLASSIFIERS = [
  'Development Status :: 4 - Beta',
  'Framework :: Zope :: 4',
  'Programming Language :: Python :: 3',
  'Operating System :: OS Independent',
  'Environment :: Web Environment',
  'Topic :: Internet :: WWW/HTTP :: Site Management',
  'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
  'Intended Audience :: Education',
  'Intended Audience :: Science/Research',
  'Intended Audience :: Customer Service',
  'Intended Audience :: End Users/Desktop',
  'Intended Audience :: Healthcare Industry',
  'Intended Audience :: Information Technology',
  'Intended Audience :: Telecommunications Industry',
  'Intended Audience :: Financial and Insurance Industry',
  'License :: OSI Approved :: GNU General Public License (GPL)',
]

setup(
  name                  = 'ZMS',
  description           = 'ZMS: Simplified Content Modelling',
  long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'http://www.zms-publishing.com',
  download_url          = 'https://zmslabs.org',
  install_requires      = INSTALL_REQUIRES,
  namespace_packages    = ['Products'],
  packages              = ['Products.zms'],
  package_data          = {'Products.zms': PACKAGE_DATA},
  data_files            = DATA_FILES,
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)
