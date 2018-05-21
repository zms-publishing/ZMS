# encoding: utf-8

import sys
import unittest
# Product imports.
from zms_test_util import *
import zms
sys.path.append("..")

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_zreferableitem.ZReferableItemTest
class ZReferableItemTest(unittest.TestCase):

  temp_title = 'temp-test'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = HTTPRequest({'lang':'eng','preview':'preview'})
    zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    self.context = zmscontext
    print('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},zmscontext.REQUEST)


  def test_getRelativeUrl(self):
    context = self.context
    def assertEqual(path,url,expected):
      self.assertEqual(expected,context.getRelativeUrl(path,url))
    assertEqual('/e1/e2/e3','/e1/e4/e5/e6','./../e4/e5/e6')
    assertEqual('http://host:port/e1/e2/e3#e4','http://host:port/e5?preview=preview#e6','./../../e5?preview=preview#e6')


  def test_getRefObjPath(self):
    zmscontext = self.context
    request = self.context.REQUEST
    folder = self.folder
    ref = '{$%s@%s}'%(zmscontext.getHome().id,'/'.join(folder.getPhysicalPath()[-folder.getLevel():]))
    self.assertEqual('{$%s@%s}'%(zmscontext.getHome().id,'/'.join(folder.getPhysicalPath()[-folder.getLevel():])),zmscontext.getRefObjPath(folder))
    self.assertEqual(folder,zmscontext.getLinkObj(ref))
    ref = '{$%s}'%('/'.join(folder.getPhysicalPath()[-folder.getLevel():]))
    self.assertEqual(folder,zmscontext.getLinkObj(ref))
    
    # create portal-client
    print('[test_metaobj_manager] create portal-client')
    zmsclient0 = addClient(zmscontext,'client0')
    # create portal-client
    print('[test_metaobj_manager] create client-client')
    zmsclient00 = addClient(zmsclient0,'client00')
    # Test refs.
    for docelmnt in [zmscontext.getDocumentElement(),zmsclient0,zmsclient00]:
      self.assertEqual(zmscontext,docelmnt.getLinkObj(docelmnt.getRefObjPath(zmscontext)))
      self.assertEqual(docelmnt,zmscontext.getLinkObj(zmscontext.getRefObjPath(docelmnt)))
    # remove portal-client (and client-client)
    print('[test_metaobj_manager] remove portal-client %s'%zmsclient0.id)
    removeClient(zmscontext,zmsclient0.getHome().id)


  def tearDown(self):
    zmscontext = self.context
    request = self.context.REQUEST
    print('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
