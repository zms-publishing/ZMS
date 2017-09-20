import test_util

class ZMSLinkElementTest(test_util.BaseTest):

  temp_title = 'temp-test'

  def setUp(self):
    zmscontext = self.context
    request = self.REQUEST
    self.writeInfo('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},request)

  def test_link(self):
    context = self.context
    request = self.REQUEST
    lang = request['lang']
    
    folder = self.folder
    self.writeInfo('>>>>>>>>>> test link')
    doc1 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-1','titlealt':'doc-1'},request)
    ta11 = doc1.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    link1 = folder.manage_addZMSCustom('ZMSLinkElement',{'title':'link-1','titlealt':'link-1','attr_ref':folder.getRefObjPath(doc1)},request)
    
    for attr_type in ['replace','embed','recursive']:
      self.writeInfo('>>>>>>>>>> test attr_type=%s'%attr_type)
      link1.setObjProperty('attr_type',attr_type,lang)
      link2 = filter(lambda x:x.id==link1.id,folder.getChildNodes(request))[0]
      for link in [link1,link2]:
        self.writeInfo('>>>>>>>>>> test link=%s'%str(link))
        
        link1.setObjProperty('active',True,lang)
        doc1.setObjProperty('active',True,lang)
        self.assertTrue('isActive(True->True)',link.isActive(request))
        doc1.setObjProperty('active',False,lang)
        self.assertFalse('isActive(True->False)',link.isActive(request))
        
        link1.setObjProperty('active',False,lang)
        doc1.setObjProperty('active',True,lang)
        self.assertFalse('isActive(False->True)',link.isActive(request))
        doc1.setObjProperty('active',False,lang)
        self.assertFalse('isActive(False->False)',link.isActive(request))

  def tearDown(self):
    zmscontext = self.context
    request = self.REQUEST
    self.writeInfo('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
