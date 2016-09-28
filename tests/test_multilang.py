import test_util

class MultiLanguageTest(test_util.BaseTest):

  temp_lang = 'xxx'
  temp_title = 'temp-test'

  def setUp(self):
    zmscontext = self.context
    # create language
    prim_lang = zmscontext.getPrimaryLanguage()
    request = self.REQUEST
    request.set('lang',prim_lang)
    self.writeInfo('[setUp] create language %s'%self.temp_lang)
    newLabel = 'Test Language'
    newParent = prim_lang
    newManage = 'eng'
    zmscontext.setLanguage(self.temp_lang, newLabel, newParent, newManage)
    self.writeInfo('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},request)
    # create lang-string
    lang_dict = zmscontext.get_lang_dict()
    key = 'ATTR_XXX'
    lang_dict[key] = {'ger':'Xxx','eng':'Yyy',self.temp_lang:'Zzz'}
    zmscontext.set_lang_dict(lang_dict)

  def test_getLangStr(self):
    zmscontext = self.context
    # create portal-client
    self.writeInfo('[test_metaobj_manager] create portal-client')
    zmsclient0 = self.addClient(zmscontext,'client0')
    # create portal-client
    self.writeInfo('[test_metaobj_manager] create client-client')
    zmsclient00 = self.addClient(zmsclient0,'client00')
    # Test lang-strings
    for context in [zmscontext,zmsclient0,zmsclient00]:
      key = 'ATTR_DC_COVERAGE'
      self.assertEquals('%s.getLangStr(%s,ger)'%(context.getHome().id,key),'Reichweite',context.getLangStr(key,'ger'))
      self.assertEquals('%s.getLangStr(%s,eng)'%(context.getHome().id,key),'Coverage',context.getLangStr(key,'eng'))
      self.assertEquals('%s.getLangStr(%s,ned)'%(context.getHome().id,key),'Draagwijte',context.getLangStr(key,'ned'))
      self.assertEquals('%s.getLangStr(%s,fra)'%(context.getHome().id,key),'Envergure',context.getLangStr(key,'fra'))
      self.assertEquals('%s.getLangStr(%s,ita)'%(context.getHome().id,key),'Copertura',context.getLangStr(key,'ita'))
      self.assertEquals('%s.getLangStr(%s,esp)'%(context.getHome().id,key),'Cobertura',context.getLangStr(key,'esp'))
      self.assertEquals('%s.getLangStr(%s,%s)'%(context.getHome().id,key,self.temp_lang),context.getLangStr(key,'eng'),context.getLangStr(key,self.temp_lang))
      key = 'ATTR_XXX'
      self.assertEquals('%s.getLangStr(%s,ger)'%(context.getHome().id,key),'Xxx',context.getLangStr(key,'ger'))
      self.assertEquals('%s.getLangStr(%s,eng)'%(context.getHome().id,key),'Yyy',context.getLangStr(key,'eng'))
      self.assertEquals('%s.getLangStr(%s,ned)'%(context.getHome().id,key),key,context.getLangStr(key,'ned'))
      self.assertEquals('%s.getLangStr(%s,fra)'%(context.getHome().id,key),key,context.getLangStr(key,'fra'))
      self.assertEquals('%s.getLangStr(%s,ita)'%(context.getHome().id,key),key,context.getLangStr(key,'ita'))
      self.assertEquals('%s.getLangStr(%s,esp)'%(context.getHome().id,key),key,context.getLangStr(key,'esp'))
      self.assertEquals('%s.getLangStr(%s,%s)'%(context.getHome().id,key,self.temp_lang),'Zzz',context.getLangStr(key,self.temp_lang))
    # remove portal-client (and client-client)
    self.writeInfo('[test_metaobj_manager] remove portal-client %s'%zmsclient0.id)
    self.removeClient(zmscontext,zmsclient0.getHome().id)

  def test_multiLanguageManager(self):
    zmscontext = self.context
    prim_lang = zmscontext.getPrimaryLanguage()
    request = self.REQUEST
    request.set('lang',prim_lang)
    folder = self.folder
    # test language exists
    self.writeInfo('>>>>>>>>>> test language exists')
    self.assertTrue('%s in getLangIds'%self.temp_lang,self.temp_lang in zmscontext.getLangIds())
    # test default activity of zmsobject in primary and secondary language
    self.writeInfo('>>>>>>>>>> test default activity of zmsobject in primary and secondary language')
    request.set('lang',prim_lang)
    prim_desc = 'primary'
    folder.setObjStateModified(request)
    folder.setObjProperty('attr_dc_description',prim_desc,request['lang'])
    folder.onChangeObj(request)
    self.assertTrue('folder.isActive(lang=%s)'%prim_lang,folder.isActive(request))
    request.set('lang',self.temp_lang)
    self.assertFalse('!folder.isActive(lang=%s)'%self.temp_lang,folder.isActive(request))
    secnd_desc = 'secondary'
    folder.setObjStateModified(request)
    folder.setObjProperty('active',1,request['lang'])
    folder.setObjProperty('attr_dc_description',secnd_desc,request['lang'])
    folder.onChangeObj(request)
    self.assertTrue('folder.isActive(lang=%s)'%prim_lang,folder.isActive(request))
    # [https://zmslabs.org/trac/ticket/303] test activity of zmslinkelement in primary and secondary language
    self.writeInfo('>>>>>>>>>> [https://zmslabs.org/trac/ticket/303] test activity of zmslinkelement in primary and secondary language')
    request.set('lang',prim_lang)
    zmscontainer = folder.getParentNode()
    test_link_attrs = {'title':'test-link','titlealt':'test-link','attr_ref':zmscontainer.getRefObjPath(folder)}
    self.writeInfo('[test_multiLanguageManager] create test-link %s'%str(test_link_attrs))
    zmslinkelement = zmscontainer.manage_addZMSCustom('ZMSLinkElement',test_link_attrs,request)
    request.set('lang',prim_lang)
    self.assertEquals('zmslinkelement.description(lang=%s)'%request['lang'],prim_desc,zmslinkelement.attr('attr_dc_description'))
    self.assertTrue('zmslinkelement.active(lang=%s)'%request['lang'],zmslinkelement.attr('active'))
    self.assertTrue('zmslinkelement.isActive(lang=%s)'%request['lang'],zmslinkelement.isActive(request))
    request.set('lang',self.temp_lang)
    self.assertEquals('zmslinkelement.description(lang=%s)'%request['lang'],secnd_desc,zmslinkelement.attr('attr_dc_description'))
    self.assertFalse('!zmslinkelement.active(lang=%s)'%request['lang'],zmslinkelement.attr('active'))
    self.assertFalse('!zmslinkelement.isActive(lang=%s)'%request['lang'],zmslinkelement.isActive(request))
    self.writeInfo('[test_multiLanguageManager] remove test-link')
    zmscontainer.manage_delObjects([zmslinkelement.id])

  def tearDown(self):
    zmscontext = self.context
    # create lang-string
    lang_dict = zmscontext.get_lang_dict()
    key = 'ATTR_XXX'
    del lang_dict[key]
    zmscontext.set_lang_dict(lang_dict)
    # remove language
    prim_lang = zmscontext.getPrimaryLanguage()
    request = self.REQUEST
    request.set('lang',prim_lang)
    self.writeInfo('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
    self.writeInfo('[tearDown] delete language %s'%self.temp_lang)
    zmscontext.delLanguage(self.temp_lang)
