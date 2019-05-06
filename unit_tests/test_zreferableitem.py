# encoding: utf-8

import sys
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_zreferableitem.ZReferableItemTest
class ZReferableItemTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    print(self,"[ZReferableItemTest.setUp]")
    # super
    ZMSTestCase.setUp(self)
    zmscontext = self.context
    # create folder
    print('[ZReferableItemTest.setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},zmscontext.REQUEST)


  def test_getRelativeUrl(self):
    print('[ZReferableItemTest.test_getRelativeUrl]')
    context = self.context
    def assertEqual(path,url,expected):
      self.assertEqual(expected,context.getRelativeUrl(path,url))
    assertEqual('/e1/e2/e3','/e1/e4/e5/e6','./../e4/e5/e6')
    assertEqual('http://host:port/e1/e2/e3#e4','http://host:port/e5?preview=preview#e6','./../../e5?preview=preview#e6')
    assertEqual('/e1/e2/e3/index_ger.html','/e1/e4/e5/e6/index_eng.html','./../../e4/e5/e6/index_eng.html')
    assertEqual('http://host/e1/e2/e3/index_ger.html','http://host/e1/e4/e5/e6/index_eng.html','./../../e4/e5/e6/index_eng.html')
    assertEqual('https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e5','https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e25/e28','./e25/e28')
    assertEqual('https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e5/index_html','https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e25/e28','./../e25/e28')
    assertEqual('https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e5/index_ger.html','https://demo.zms-demo.zms.hosting/sites/zmsdemo/content/e25/e28','./../e25/e28')


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
    print('[ZReferableItemTest.test_getRefObjPath] create portal-client')
    zmsclient0 = addClient(zmscontext,'client0')
    # create portal-client
    print('[ZReferableItemTest.test_getRefObjPath] create client-client')
    zmsclient00 = addClient(zmsclient0,'client00')
    # Test refs.
    for docelmnt in [zmscontext.getDocumentElement(),zmsclient0,zmsclient00]:
      self.assertEqual(zmscontext,docelmnt.getLinkObj(docelmnt.getRefObjPath(zmscontext)))
      self.assertEqual(docelmnt,zmscontext.getLinkObj(zmscontext.getRefObjPath(docelmnt)))
    # remove portal-client (and client-client)
    print('[ZReferableItemTest.test_getRefObjPath] remove portal-client %s'%zmsclient0.id)
    removeClient(zmscontext,zmsclient0.getHome().id)


  def tearDown(self):
    zmscontext = self.context
    request = self.context.REQUEST
    print('[ZReferableItemTest.tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
    # super
    ZMSTestCase.tearDown(self)
