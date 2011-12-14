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
from Testing import ZopeTestCase
ZopeTestCase.installProduct('ZCatalog', 1)
ZopeTestCase.installProduct('ZMS', 1)

from zope.interface.verify import verifyClass
from OFS.DTMLDocument import addDTMLDocument


class ZMSTests(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        print "afterSetUp"
        factory = self.folder.manage_addProduct['ZCatalog']
        factory.manage_addZCatalog('catalog', 'catalog')
        catalog = self.folder['catalog']

    def testVoid1(self):
        print "testVoid1"

    def testVoid2(self):
        print "testVoid2"


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
