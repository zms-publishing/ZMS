# encoding: utf-8

import sys
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import pilutil

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_pilutil.PilUtilTest
class PilUtilTest(ZMSTestCase):
  def test_resize(self):
    img = self.read_image('zope_logo.png')
    size = (img.getWidth()/2,img.getHeight()/2)
    # @skip
    #img2 = pilutil.resize(img,size)

  def test_optimize(self):
    img = self.read_image('zope_logo.png')
    # @skip
    #img2 = pilutil.optimize(img)
  
if __name__ == '__main__':
    unittest.main()