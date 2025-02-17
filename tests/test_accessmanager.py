# encoding: utf-8

from OFS.Folder import Folder
import sys
import time
import unittest

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import zms

# /ZMS> python3 -m unittest discover -s tests
# /ZMS> python3 -m unittest tests.test_accessmanager.AccessManagerTest
class AccessManagerTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview','theme':'conf:aquire','minimal_init':1,'content_init':1 })
    zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    self.context = zmscontext

  def test_user_attr(self):
    context = self.context
    request = context.REQUEST
    expected = 'bar'
    context.setUserAttr('johndoe','foo',expected)
    v = context.getUserAttr('johndoe','foo')
    self.assertEqual(expected,v)
