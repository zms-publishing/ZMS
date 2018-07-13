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
# /Products/zms> python -m unittest unit_tests.test_zmscontainerobject.ZMSContainerObjectTest
class ZMSContainerObjectTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = HTTPRequest({'lang':'eng','preview':'preview'})
    zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    self.context = zmscontext
    print('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},zmscontext.REQUEST)

  def test_tree(self):
    context = self.context
    request = context.REQUEST
    
    folder = self.folder
    print('>>>>>>>>>> test tree')
    ta1 = folder.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc1 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-1','titlealt':'doc-1'},request)
    ta11 = doc1.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc2 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-2','titlealt':'doc-2'},request)
    ta21 = doc2.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc3 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-3','titlealt':'doc-3'},request)
    ta31 = doc3.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    self.assertEqual(4,len(folder.getChildNodes(request)))
    self.assertEqual(1,len(folder.getChildNodes(request,context.PAGEELEMENTS)))
    self.assertEqual(3,len(folder.getChildNodes(request,context.PAGES)))
    self.assertEqual(7,len(folder.getTreeNodes(request)))
    
    print('>>>>>>>>>> test zmsindex')
    catalog = getattr(context,'zcatalog_index',None)
    if catalog is None:
      print('skip')
    else:
      print('inline-link from ta11 (%s) to doc2 (%s)'%(ta11.absolute_url(),doc2.absolute_url()))
      ta11.setObjProperty('text','Lorem <a data-id="{$%s}" href="test.html">ipsum</a> dolor'%doc2.get_uid(),request['lang'])
      href = context.getRelativeUrl(ta11.getHref2IndexHtml(request),doc2.getHref2IndexHtml(request))
      print('inline-link from ta11 to doc2: '+href)
      self.assertTrue(ta11.attr('text').find('href="%s"'%href)>0)

  def tearDown(self):
    zmscontext = self.context
    print('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
