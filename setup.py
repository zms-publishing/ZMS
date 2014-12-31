"""
The ZMS3 environment consists of an application server based on pegged versions 
of depending packages (see INSTALL_REQUIRES_CONCRETE below or requirements.txt).

  Use 'pip install ZMS3 [--process-dependency-links]'
  to install the environment based on releases at https://pypi.python.org/pypi/
  (include dependency links for unreleased packages at PyPI)

  Use 'pip install https://zmslabs.org/download/ZMS3-latest.tar.gz [--process-dependency-links]'
  to install the environment fetching the latest nightly build at ZMSLabs
  (maybe unstable)

  Use 'pip install -r https://zmslabs.org/svn/zmslabs/ZMS/trunk/requirements.txt'
  to install the environment fetching the latest development snapshots from svn/git-repos
  (maybe unstable)

@see http://gpiot.com/blog/creating-a-python-package-and-publish-it-to-pypi/
@see https://caremad.io/2013/07/setup-vs-requirement/
"""
import os
from setuptools import setup

setup_path = os.path.dirname(__file__)

# Abstract requirements to define the environment
INSTALL_REQUIRES_ABSTRACT = [
  'Zope2==2.13.23dev',            # due to https://github.com/zopefoundation/Zope/pull/13/files
  'ExtensionClass>=4.1a1',        # required by Record-3.0
  'Products.CMFCore',
  'Products.ZSQLiteDA',
  'Products.ZSQLMethods',
  'zope.browserresource>4.0.1',   # due to https://github.com/zopefoundation/zope.browserresource/pull/1/files
  'zope.globalrequest',
  'zope.untrustedpython',
]

# Unreleased packages to build the environment
DEPENDENCY_LINKS = [
  'https://zmslabs.org/download/' # https://zmslabs.org/download/Zope2-2.13.23dev.tar.gz
]

# Concrete requirements to build the environment
INSTALL_REQUIRES_CONCRETE = [
  'AccessControl==3.0.11',
  'Acquisition==4.1',
  'BTrees==4.0.8',
  'DateTime==4.0.1',
  'DocumentTemplate==2.13.2',
  'docutils==0.12',
  'ExtensionClass==4.1',
  'five.localsitemanager==2.0.5',
  'initgroups==2.13.0',
  'mechanize==0.2.5',
  'Missing==3.0',
  'MultiMapping==2.13.0',
  'nt-svcutils==2.13.0',
  'Persistence==2.13.2',
  'persistent==4.0.8',
  'Products.BTreeFolder2==2.13.4',
  'Products.CMFCore==2.2.8',
  'Products.ExternalMethod==2.13.1',
  'Products.GenericSetup==1.7.5',
  'Products.MailHost==2.13.2',
  'Products.MIMETools==2.13.0',
  'Products.OFSP==2.13.2',
  'Products.PythonScripts==2.13.2',
  'Products.StandardCacheManagers==2.13.1',
  'Products.ZCatalog==3.1',
  'Products.ZCTextIndex==2.13.5',
  'Products.ZSQLiteDA==0.6.1',
  'Products.ZSQLMethods==2.13.4',
  'pytz==2014.10',
  'Record==3.0',
  'RestrictedPython==3.6.0',
  'six==1.8.0',
  'tempstorage==2.12.2',
  'ThreadLock==2.13.0',
  'transaction==1.4.3',
  'zc.lockfile==1.1.0',
  'ZConfig==3.0.4',
  'zdaemon==4.0.0',
  'ZEO==4.0.0',
  'zExceptions==2.13.0',
  'zLOG==2.12.0',
  'ZODB==4.0.1',
  'ZODB3==3.11.0',
  'zope.annotation==4.2.0',
  'zope.app.publication==3.14.0',
  'zope.authentication==4.1.0',
  'zope.browser==2.0.2',
  'zope.browsermenu==4.1.0',
  'zope.browserpage==4.1.0',
  'zope.browserresource==4.0.2',
  'zope.component==4.2.1',
  'zope.configuration==4.0.3',
  'zope.container==4.0.0',
  'zope.contentprovider==4.0.0',
  'zope.contenttype==4.0.1',
  'zope.datetime==4.0.0',
  'zope.deferredimport==4.0.0',
  'zope.dottedname==4.0.1',
  'zope.error==4.1.1',
  'zope.event==4.0.3',
  'zope.exceptions==4.0.7',
  'zope.filerepresentation==4.0.2',
  'zope.formlib==4.3.0',
  'zope.globalrequest==1.0',
  'zope.i18n==4.0.0',
  'zope.i18nmessageid==4.0.3',
  'zope.interface==4.1.1',
  'zope.lifecycleevent==4.0.3',
  'zope.location==4.0.3',
  'zope.pagetemplate==4.0.4',
  'zope.processlifetime==2.0.0',
  'zope.proxy==4.1.4',
  'zope.ptresource==3.9.0',
  'zope.publisher==4.0.0',
  'zope.schema==4.4.2',
  'zope.security==4.0.1',
  'zope.sendmail==4.0.0',
  'zope.sequencesort==4.0.1',
  'zope.site==3.9.2',
  'zope.size==4.0.1',
  'zope.structuredtext==4.0.0',
  'zope.tal==4.0.0',
  'zope.tales==4.0.2',
  'zope.testbrowser==4.0.4',
  'zope.testing==4.1.3',
  'zope.traversing==4.0.0',
  'zope.untrustedpython==4.0.0',
  'zope.viewlet==3.7.2',
  'ZopeUndo==4.0',
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

CLASSIFIERS = [
  'License :: OSI Approved :: GNU General Public License (GPL)',
  'Environment :: Web Environment',
  'Framework :: Zope2',
  'Programming Language :: Python :: 2.7',
  'Operating System :: OS Independent',
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
  dependency_links      = DEPENDENCY_LINKS,
  namespace_packages    = ['Products'],
  packages              = ['Products.zms'],
  package_dir           = {'Products.zms': '.'},
  package_data          = {'Products.zms': PACKAGE_DATA},
  classifiers           = CLASSIFIERS,
  include_package_data  = True,
  zip_safe              = False,
)
