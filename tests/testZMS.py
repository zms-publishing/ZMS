################################################################################
# ZMS
# Zope-based content management system for science, technology and medicine
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
################################################################################

"""
ZMS unit tests
"""

import sys, os, unittest
from AccessControl import SecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import Implicit
from Testing import ZopeTestCase

ZopeTestCase.installProduct('zms', 1)
ZopeTestCase.installProduct('ZCatalog', 1)
ZopeTestCase.installProduct('ZCTextIndex', 1)

from zope.interface.verify import verifyClass
from OFS.DTMLDocument import addDTMLDocument


class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1

    def checkPermission( self, permission, object, context) :
        return 1

class UnitTestUser( Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'

    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

    def has_permission( self, object, object_roles=None ):
        return 1


class UnitTestRequest:
    """
    """
    def __init__(self, d={}):
        self.d = d

    def __getitem__(self, key):
        return self.d.get(key)

    def get(self, key, defaultValue=None):
        return self.d.get(key,defaultValue)

    def set(self, key, value):
        self.d[key] = value


class ZMSTests(ZopeTestCase.ZopeTestCase):

    def tearDown(self):
        print "DEBUG tearDown"
        noSecurityManager()
        SecurityManager.setSecurityPolicy( self.oldPolicy )
        del self.oldPolicy
        del self.policy

    def afterSetUp(self):
        print "DEBUG afterSetUp"
        self.policy = UnitTestSecurityPolicy()
        self.oldPolicy = SecurityManager.setSecurityPolicy( self.policy )
        newSecurityManager( None, UnitTestUser().__of__(self.folder) )
        REQUEST = UnitTestRequest({
            'btn':'Add',
            'lang':'eng',
            'lang_label':'English',
            'manage_lang':'eng',
            'theme':'myZMStheme5.zexp',
            'folder_id':'myzmsx',
            'initialization':1,
          })
        factory = self.folder.manage_addProduct['zms']
        factory.manage_addZMS('eng', 'eng', REQUEST)
        zms = self.folder['myzmsx']
        print zms

    def testVoid1(self):
        print "DEBUG testVoid1"
        REQUEST = {}
        print self.folder.myzmsx
        print len(self.folder.myzmsx.getChildNode(REQUEST))

    def testVoid2(self):
        print "DEBUG testVoid2"


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ZMSTests))
    return s

def main():
    unittest.TextTestRunner().run(test_suite())

def debug():
    test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')

if __name__=='__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        main()
