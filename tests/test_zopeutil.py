# encoding: utf-8

import unittest
from Products.zms import zopeutil

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest tests.test_zopeutil.ZopeUtilTest
class ZopeUtilTest(unittest.TestCase):

    def test_is_manage(self):
        self.assertFalse(zopeutil.is_manage('foo'))
        self.assertFalse(zopeutil.is_manage('bar'))
        self.assertFalse(zopeutil.is_manage('manager'))
        self.assertFalse(zopeutil.is_manage('topmanagement'))
        self.assertTrue(zopeutil.is_manage('manage'))
        self.assertTrue(zopeutil.is_manage('manage_main'))
        self.assertTrue(zopeutil.is_manage('manage_opensearch_test'))
