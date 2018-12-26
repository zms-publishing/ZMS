# encoding: utf-8

from OFS.Folder import Folder
from xml.dom import minidom
import sys
import time
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_ZMSMetaobjManager.ZMSMetaobjManagerTest
class ZMSMetaobjManagerTest(ZMSTestCase):

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = HTTPRequest({'lang':'eng','preview':'preview'})
    zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    self.context = zmscontext

  def test_export(self):
    zmscontext = self.context
    request = zmscontext.REQUEST
    
    metaobj_manager = zmscontext.metaobj_manager
    xml = metaobj_manager.exportMetaobjXml(ids=['ZMSDocument'])
    dom = minidom.parseString(xml)
    v = zmscontext.parseXmlString(xml)
    self.assertTrue(type(v) is dict)
    self.assertEqual('ZMSDocument',v['key'])
    
    value = v['value']
    self.assertEqual('ZMSDocument',value['name'])
    self.assertEqual('com.zms.foundation',value['package'])
    self.assertTrue(value['enabled'])
    
    attrs = value['__obj_attrs__']
    self.assertEqual('title',[x['meta_type'] for x in attrs if x['id']=='title'][0])
    self.assertEqual('string',[x['type'] for x in attrs if x['id']=='title'][0])
    self.assertEqual('titlealt',[x['meta_type'] for x in attrs if x['id']=='titlealt'][0])
    self.assertEqual('string',[x['type'] for x in attrs if x['id']=='titlealt'][0])
