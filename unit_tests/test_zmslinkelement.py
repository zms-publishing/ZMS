# encoding: utf-8

from OFS.Folder import Folder
import sys
import time
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_zmslinkelement.ZMSLinkElementTest
class ZMSLinkElementTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    print(self,"[ZMSLinkElementTest.setUp]")
    # super
    ZMSTestCase.setUp(self)
    zmscontext = self.context
    # create folder
    print('[ZMSLinkElementTest.setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},zmscontext.REQUEST)


  def test_link(self):
    context = self.context
    request = self.context.REQUEST
    lang = request['lang']
    
    folder = self.folder
    print('>>>>>>>>>> test link')
    doc1 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-1','titlealt':'doc-1'},request)
    ta11 = doc1.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    ref1 = folder.getRefObjPath(doc1)
    link1 = folder.manage_addZMSCustom('ZMSLinkElement',{'title':'Link-1','titlealt':'Link-1','attr_ref':ref1},request)
    self.assertEqual('Link-1', link1.attr('title'))
    self.assertEqual('Link-1', link1.attr('titlealt'))
    self.assertEqual(ref1, link1.getRef())
    
    for attr_type in ['replace','embed','recursive']:
      print('>>>>>>>>>> test attr_type=%s'%attr_type)
      link1.setObjProperty('attr_type',attr_type,lang)
      link2 = filter(lambda x:x.id==link1.id,folder.getChildNodes(request))[0]
      for link in [link1,link2]:
        print('>>>>>>>>>> test link=%s'%str(link))
        
        link1.setObjProperty('active',True,lang)
        # if link is active require activity from target
        doc1.setObjProperty('active',True,lang)
        self.assertTrue(link.isActive(request))
        doc1.setObjProperty('active',False,lang)
        self.assertFalse(link.isActive(request))
        
        link1.setObjProperty('active',False,lang)
        # if link is inactive do not require activity from target
        doc1.setObjProperty('active',True,lang)
        self.assertFalse(link.isActive(request))
        doc1.setObjProperty('active',False,lang)
        self.assertFalse(link.isActive(request))


  def tearDown(self):
    zmscontext = self.context
    request = self.context.REQUEST
    print('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
    # super
    ZMSTestCase.tearDown(self)
