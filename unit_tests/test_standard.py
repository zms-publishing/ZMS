# encoding: utf-8

import sys
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import standard

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_standard.StandardTest
class StandardTest(ZMSTestCase):

  def test_url_append_params(self):
    expected = 'index.html?a=b&amp;c=d&amp;e=1&amp;f:list=1&amp;f:list=2&amp;f:list=3'
    v = standard.url_append_params('index.html?a=b',{'c':'d','e':1,'f':[1,2,3]})
    self.assertEqual(expected,v)
