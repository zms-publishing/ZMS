"""
The ZMS3 environment consists of an application server based on pegged versions 
of depending packages (see INSTALL_REQUIRES_CONCRETE below or requirements.txt).

  Use '$ pip install ZMS3'
  to install the environment fetching packages from PyPI at https://pypi.python.org/pypi/
  (official releases)

  Use '$ pip install https://zmslabs.org/download/ZMS3-latest.tar.gz'
  to install the environment fetching the latest nightly build from ZMSLabs
  (maybe unstable)

  Use '$ pip install -r https://zmslabs.org/svn/zmslabs/ZMS/trunk/requirements.txt'
  to install the environment fetching the latest development snapshots from SVN/GIT-Repositories
  (maybe unstable)

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

# Abstract requirements to build the environment
# catch latest versions from PyPI
INSTALL_REQUIRES_ABSTRACT = [

]

# Concrete requirements to build the environment
# catch pegged versions from PyPI
INSTALL_REQUIRES_CONCRETE = [
  'AccessControl==3.0.12',
  'Acquisition==4.2.2',
  'BTrees==4.2.0',
  'DateTime==4.1.1',
  'DocumentTemplate==2.13.2',
  'docutils==0.12',
  'ExtensionClass==4.1.2',  # ExtensionClass>=4.1a1 required by Record-3.0
  'five.globalrequest==1.0',
  'five.localsitemanager==2.0.5',
  'initgroups==2.13.0',
  'mechanize==0.2.5',
  'Missing==3.1',
  'MultiMapping==3.0',
  'nt-svcutils==2.13.0',
  'Persistence==2.13.2',
  'persistent==4.2.0',
  'Products.BTreeFolder2==2.14.0',
  'Products.CMFCore==2.2.10',
  'Products.ExternalMethod==2.13.1',
  'Products.GenericSetup==1.8.3',
  'Products.MailHost==2.13.2',
  'Products.MIMETools==2.13.0',
  'Products.OFSP==2.13.2',
  'Products.PythonScripts==2.13.2',
  'Products.StandardCacheManagers==2.13.1',
  'Products.ZCatalog==3.1',
  'Products.ZCTextIndex==2.13.5',
  'pytz==2016.4',
  'Record==3.1',
  'RestrictedPython==3.6.0',
  'six==1.10.0',
  'tempstorage==3.0',
  'ThreadLock==2.13.0',
  'transaction==1.5.0',
  'zc.lockfile==1.1.0',
  'ZConfig==3.1.0',
  'zdaemon==4.0.0', # due to zdaemon>=4.0.1 causes AttributeError: ZopeCtlOptions instance has no attribute 'transcript'
  'ZEO==4.2.0b1',
  'zExceptions==3.0',
  'zLOG==3.0',
  'zodbpickle==0.6.0',
  'ZODB==4.2.0',
  'ZODB3==3.11.0',
  'zope.annotation==4.4.1',
  'zope.app.publication==3.14.0',
  'zope.authentication==4.1.0',
  'zope.browser==2.1.0',
  'zope.browsermenu==4.1.0', # zope.browserresource>4.1.0 requires zope.publisher>=4.2.1
  'zope.browserpage==4.1.0',
  'zope.browserresource==4.1.0', # zope.browserresource>4.0.1 due to https://github.com/zopefoundation/zope.browserresource/pull/1/files
  'zope.component==4.2.2',
  'zope.configuration==4.0.3',
  'zope.container==4.1.0',
  'zope.contentprovider==4.0.0',
  'zope.contenttype==4.1.0',
  'zope.datetime==4.1.0',
  'zope.deferredimport==4.1.0',
  'zope.dottedname==4.1.0',
  'zope.error==4.1.1',
  'zope.event==4.2.0',
  'zope.exceptions==4.0.8',
  'zope.filerepresentation==4.1.0',
  'zope.formlib==4.3.0',
  'zope.globalrequest==1.0',
  'zope.i18n==4.1.0',
  'zope.i18nmessageid==4.0.3',
  'zope.interface==4.1.3',
  'zope.lifecycleevent==4.1.0',
  'zope.location==4.0.3',
  'zope.pagetemplate==4.2.1',
  'zope.processlifetime==2.1.0',
  'zope.proxy==4.2.0',
  'zope.ptresource==4.0.0',
  'zope.publisher==3.13.4', # due to zope.publisher>=4.0.0 causes errors on rendering legacy DTML-Methods
  'zope.schema==4.4.2',
  'zope.security==4.0.3',
  'zope.sendmail==3.7.5', # due to https://github.com/zopefoundation/zope.sendmail/issues/1
  'zope.sequencesort==4.0.1',
  'zope.site==4.0.0',
  'zope.size==4.1.0',
  'zope.structuredtext==4.1.0',
  'zope.tal==4.2.0',
  'zope.tales==4.1.1',
  'zope.testbrowser==4.0.4',
  'zope.testing==4.5.0',
  'zope.traversing==4.0.0',
  'zope.untrustedpython==4.0.0',
  'zope.viewlet==4.0.0',
  'Zope2==2.13.24',
  'ZopeUndo==2.12.0', # due to ZopeUndo==4.0 causes ZEO DisconnectedError on manageUndo
]

README = open(os.path.join(setup_path, 'README')).read()

# Remove text from version for PyPI
VERSION = open(os.path.join(setup_path, 'version.txt')).read().replace('ZMS3-', '').replace('.REV', '')
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
    (site_packages, ['dll/pywintypes27.dll','dll/win32file.pyd'])
  ]

CLASSIFIERS = [
  'Development Status :: 4 - Beta',
  'Framework :: Zope2',
  'Programming Language :: Python :: 2.7',
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
  name                  = 'ZMS3',
  description           = 'ZMS: Simplified Content Modelling',
  long_description      = README,
  version               = VERSION,
  author                = 'HOFFMANN+LIEBENBERG in association with SNTL Publishing, Berlin',
  author_email          = 'zms@sntl-publishing.com',
  url                   = 'http://www.zms-publishing.com',
  download_url          = 'https://zmslabs.org',
  install_requires      = INSTALL_REQUIRES_ABSTRACT + INSTALL_REQUIRES_CONCRETE,
  namespace_packages    = ['Products'],
  packages              = ['Products.zms'],
  package_dir           = {'Products.zms': '.'},
  package_data          = {'Products.zms': PACKAGE_DATA},
  data_files            = DATA_FILES,
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)
