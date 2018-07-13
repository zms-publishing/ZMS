# encoding: utf-8

from OFS.Folder import Folder
import sys
import time
import unittest
sys.path.append("..")
# Product imports.
from zms_test_util import *
import zms
import _confmanager
import _multilangmanager

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest unit_tests.test_multilang.MultiLanguageTest
class MultiLanguageTest(ZMSTestCase):

  temp_lang = 'xxx'
  temp_title = 'temp-test'

  def setUp(self):
    print(self,"MultiLanguageTest.setUp")
    # super
    ZMSTestCase.setUp(self)
    zmscontext = self.context
    # create language
    prim_lang = zmscontext.getPrimaryLanguage()
    request = zmscontext.REQUEST
    request.set('lang',prim_lang)
    print('[setUp] create language %s'%self.temp_lang)
    newLabel = 'Test Language'
    newParent = prim_lang
    newManage = 'eng'
    zmscontext.setLanguage(self.temp_lang, newLabel, newParent, newManage)
    print('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'active':1,'title':self.temp_title,'titlealt':self.temp_title},request)
    # create lang-string
    lang_dict = zmscontext.get_lang_dict()
    key = 'ATTR_XXX'
    lang_dict[key] = {'ger':'Xxx','eng':'Yyy',self.temp_lang:'Zzz'}
    zmscontext.set_lang_dict(lang_dict)

  def test_getLangStr(self):
    zmscontext = self.context
    # create portal-client
    print('[test_multilang] create portal-client')
    zmsclient0 = addClient(zmscontext,'client0')
    # create portal-client
    print('[test_multilang] create client-client')
    zmsclient00 = addClient(zmsclient0,'client00')
    # Test lang-strings
    for context in [zmscontext,zmsclient0,zmsclient00]:
      print("zmscontext.1",context.getHome().id)
      key = 'ATTR_DC_COVERAGE'
      self.assertEqual('Reichweite',context.getLangStr(key,'ger'))
      self.assertEqual('Coverage',context.getLangStr(key,'eng'))
      self.assertEqual('Draagwijte',context.getLangStr(key,'ned'))
      self.assertEqual('Envergure',context.getLangStr(key,'fra'))
      self.assertEqual('Copertura',context.getLangStr(key,'ita'))
      self.assertEqual('Cobertura',context.getLangStr(key,'esp'))
      self.assertEqual(context.getLangStr(key,'eng'),context.getLangStr(key,self.temp_lang))
      key = 'ATTR_XXX'
      self.assertEqual('Xxx',context.getLangStr(key,'ger'))
      self.assertEqual('Yyy',context.getLangStr(key,'eng'))
      self.assertEqual(key,context.getLangStr(key,'ned'))
      self.assertEqual(key,context.getLangStr(key,'fra'))
      self.assertEqual(key,context.getLangStr(key,'ita'))
      self.assertEqual(key,context.getLangStr(key,'esp'))
      self.assertEqual('Zzz',context.getLangStr(key,self.temp_lang))
      print("zmscontext.2",context.getHome().id)
    # remove portal-client (and client-client)
    print('[test_multilang] remove portal-client %s'%zmsclient0.id)
    removeClient(zmscontext,zmsclient0.getHome().id)

  """
  @skip
  def test_multiLanguageManager(self):
    zmscontext = self.context
    prim_lang = zmscontext.getPrimaryLanguage()
    request = zmscontext.REQUEST
    request.set('lang',prim_lang)
    folder = self.folder
    # test language exists
    print('>>>>>>>>>> test language exists')
    self.assertTrue(self.temp_lang in zmscontext.getLangIds(),'%s in getLangIds'%self.temp_lang)
    # test default activity of zmsobject in primary and secondary language
    print('>>>>>>>>>> test default activity of zmsobject in primary and secondary language')
    request.set('lang',prim_lang)
    prim_desc = 'primary'
    folder.setObjStateModified(request)
    folder.setObjProperty('attr_dc_description',prim_desc,request['lang'])
    folder.onChangeObj(request)
    self.assertTrue(folder.isActive(request),'folder.isActive(lang=%s)'%prim_lang)
    request.set('lang',self.temp_lang)
    self.assertFalse(folder.isActive(request),'!folder.isActive(lang=%s)'%self.temp_lang)
    secnd_desc = 'secondary'
    folder.setObjStateModified(request)
    folder.setObjProperty('active',1,request['lang'])
    folder.setObjProperty('attr_dc_description',secnd_desc,request['lang'])
    folder.onChangeObj(request)
    self.assertTrue(folder.isActive(request),'folder.isActive(lang=%s)'%prim_lang)
    # [https://zmslabs.org/trac/ticket/303] test activity of zmslinkelement in primary and secondary language
    print('>>>>>>>>>> [https://zmslabs.org/trac/ticket/303] test activity of zmslinkelement in primary and secondary language')
    request.set('lang',prim_lang)
    zmscontainer = folder.getParentNode()
    test_link_attrs = {'title':'test-link','titlealt':'test-link','attr_ref':zmscontainer.getRefObjPath(folder)}
    print('[test_multiLanguageManager] create test-link %s'%str(test_link_attrs))
    zmslinkelement = zmscontainer.manage_addZMSCustom('ZMSLinkElement',test_link_attrs,request)
    request.set('lang',prim_lang)
    self.assertEqual(prim_desc,zmslinkelement.attr('attr_dc_description'),'zmslinkelement.description(lang=%s)'%request['lang'])
    self.assertTrue(zmslinkelement.attr('active'),'zmslinkelement.active(lang=%s)'%request['lang'])
    self.assertTrue(zmslinkelement.isActive(request),'zmslinkelement.isActive(lang=%s)'%request['lang'])
    request.set('lang',self.temp_lang)
    self.assertEqual(secnd_desc,zmslinkelement.attr('attr_dc_description'),'zmslinkelement.description(lang=%s)'%request['lang'])
    self.assertFalse(zmslinkelement.attr('active'),'!zmslinkelement.active(lang=%s)'%request['lang'])
    self.assertFalse(zmslinkelement.isActive(request),'!zmslinkelement.isActive(lang=%s)'%request['lang'])
    print('[test_multiLanguageManager] remove test-link')
    zmscontainer.manage_delObjects([zmslinkelement.id])
  """

  def test_getLinkUrl(self):
    zmscontext = self.context
    request = zmscontext.REQUEST
    request.set('preview','')
    folder = self.folder
    request = {'lang':zmscontext.getPrimaryLanguage()}
    ref = zmscontext.getRefObjPath(folder)
    self.assertEqual(zmscontext.getLinkUrl(ref,request),folder.getHref2IndexHtml(request))
    request = {'lang':zmscontext.getPrimaryLanguage()}
    newref = '{$%s;lang=%s}'%(ref[2:-1],request['lang'])
    self.assertEqual(zmscontext.getLinkUrl(newref,request),folder.getHref2IndexHtml(request))
    request = {'lang':self.temp_lang}
    newref = '{$%s;lang=%s}'%(ref[2:-1],request['lang'])
    self.assertEqual(zmscontext.getLinkUrl(newref,request),folder.getHref2IndexHtml(request))

  def tearDown(self):
    zmscontext = self.context
    # create lang-string
    lang_dict = zmscontext.get_lang_dict()
    key = 'ATTR_XXX'
    del lang_dict[key]
    zmscontext.set_lang_dict(lang_dict)
    # remove language
    prim_lang = zmscontext.getPrimaryLanguage()
    request = zmscontext.REQUEST
    request.set('lang',prim_lang)
    print('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
    print('[tearDown] delete language %s'%self.temp_lang)
    zmscontext.delLanguage(self.temp_lang)
    # super
    ZMSTestCase.tearDown(self)
