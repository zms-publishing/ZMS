import test_util

class PerformanceTest(test_util.BaseTest):

  lp = 5
  lc = 10

  def setUp(self):
    pass

  def test_c(self):
    zmscontext = self.context
    r = 100000
    """
    self.startMeasurement('getReqBuffId')
    for i in range(r):
      reqBuffId = zmscontext.getReqBuffId('xxx')
    self.stopMeasurement('getReqBuffId')
    self.startMeasurement('getReqBuffId2')
    for i in range(r):
      reqBuffId = zmscontext.getReqBuffId2('xxx')
    self.stopMeasurement('getReqBuffId2')
    """
    pass

  def test_metaobj_manager(self):
    zmscontext = self.context
    request = zmscontext.REQUEST
    metaobj_manager = zmscontext.metaobj_manager
    
    # disable request-buffer
    request.set('URL','%s/manage'%zmscontext.absolute_url())
    request.set('__get_metaobjs__',True)
    
    # no test-content-objects
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmscontext.getMetaobjIds())
    self.assertEquals("#%s.metaobj_ids"%zmscontext.getHome().id,0,len(ids))
    # create test-content-objects
    self.writeInfo('[test_metaobj_manager] create %i content-object packages and %i content-object-defs'%(self.lp,self.lc))
    for ip in range(self.lp):
      id = 'com.zms.test.package%i'%ip
      package = {}
      package['id'] = id
      package['name'] = id
      package['type'] = 'ZMSPackage'
      metaobj_manager.setMetaobj( package)
      for ic in range(self.lc):
        id = 'LgTest_%i_%i'%(ip,ic)
        clazz = {}
        clazz['id'] = id 
        clazz['name'] = 'Test-%i-%i'%(ip,ic)
        clazz['type'] = 'ZMSObject'
        clazz['package'] = package['id']
        metaobj_manager.setMetaobj( clazz)
    # create portal-client
    self.writeInfo('[test_metaobj_manager] create portal-client')
    zmsclient0 = self.addClient(zmscontext,'client0')
    # create portal-client
    self.writeInfo('[test_metaobj_manager] create client-client')
    zmsclient00 = self.addClient(zmsclient0,'client00')
    
    def testMetaobjAttrIds(zmscontext):
      self.startMeasurement('%s.getMetaobjAttr'%zmscontext.getHome().id)
      metaObjIds = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmscontext.metaobj_manager.model.keys())
      for metaObjId in metaObjIds:
        metaObj = zmscontext.getMetaobj(metaObjId)
        for metaObjAttrId in zmscontext.getMetaobjAttrIds(metaObjId):
          metaObjAttr = zmscontext.getMetaobjAttr(metaObjId,metaObjAttrId)
      self.stopMeasurement('%s.getMetaobjAttr'%zmscontext.getHome().id)
    
    # count test-content-objects
    self.startMeasurement('zmscontext.getMetaobjIds')
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmscontext.getMetaobjIds())
    self.assertEquals("#%s.metaobj_ids"%zmscontext.getHome().id,self.lp*(1+self.lc),len(ids))
    self.stopMeasurement('zmscontext.getMetaobjIds')
    testMetaobjAttrIds(zmscontext)
    # count test-content-objects in portal-client
    self.startMeasurement('zmsclient0.getMetaobjIds')
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmsclient0.getMetaobjIds())
    self.assertEquals("#%s.metaobj_ids"%zmsclient0.getHome().id,self.lp*(1+self.lc),len(ids))
    self.stopMeasurement('zmsclient0.getMetaobjIds')
    testMetaobjAttrIds(zmsclient0)
    # count test-content-objects in client-client
    self.startMeasurement('zmsclient00.getMetaobjIds')
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmsclient00.getMetaobjIds())
    self.assertEquals("#%s.metaobj_ids"%zmsclient00.getHome().id,self.lp*(1+self.lc),len(ids))
    self.stopMeasurement('zmsclient00.getMetaobjIds')
    testMetaobjAttrIds(zmsclient00)
    
    # remove portal-client (and client-client)
    self.writeInfo('[test_metaobj_manager] remove portal-client %s'%zmsclient0.id)
    self.removeClient(zmscontext,zmsclient0.getHome().id)
    # remove test-content-objects
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmscontext.getMetaobjIds())
    self.writeInfo('[test_metaobj_manager] remove %i content-objects'%len(ids))
    for id in ids:
      metaobj_manager.delMetaobj( id)
    # no test-content-objects
    ids = filter(lambda x: x.startswith('com.zms.test.package') or x.startswith('LgTest_'),zmscontext.getMetaobjIds())
    self.assertEquals("#%s.metaobj_ids"%zmscontext.getHome().id,0,len(ids))

  def test_content(self):
    zmscontext = self.context
    request = self.REQUEST
    #request.set('zmi-measurement',True)
    
    # create test-folder
    self.writeInfo('[test_content] create test-folder')
    folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':'Temp-Folder','titlealt':'Temp-Folder'},request)
    lta = []
    for i in range(10):
      lta.append(folder.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request))
    for i in range(40):
      doc = folder.manage_addZMSCustom('ZMSDocument',{'title':'Temp-Document-%i'%i,'titlealt':'Temp-Document-%i'%i},request)
      for j in range(5):
        lta.append(doc.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request))
    folder2 = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':'Temp-Folder','titlealt':'Temp-Folder'},request)
    text = 'Lorem ipsum dolor '
    for ta in lta:
      text += '<a data-id="%s" href="index_html">Textarea %i</a> '%(folder2.getRefObjPath(ta),lta.index(ta))
    ta2 = folder2.manage_addZMSCustom('ZMSTextarea',{'text':text},request)
    #self.writeInfo('[test_content] %s'%text)
    
    # render manage_container
    zmscontext.clearMeasurement()
    self.startMeasurement('manage_container')
    html = folder.manage_container(folder,request)
    self.writeInfo('[test_content] folder.manage_container [%i]'%len(html))
    #self.writeInfo('[test_content] folder.manage_container [%s]'%html.encode('ascii', 'xmlcharrefreplace'))
    self.stopMeasurement('manage_container')
    self.writeInfo('[test_content] %s'%str(zmscontext.getMeasurement()))
    
    # render manage_container
    zmscontext.clearMeasurement()
    self.startMeasurement('manage_container')
    html = folder2.manage_container(folder2,request)
    self.writeInfo('[test_content] folder2.manage_container [%i]'%len(html))
    #self.writeInfo('[test_content] folder2.manage_container [%s]'%html.encode('ascii', 'xmlcharrefreplace'))
    self.stopMeasurement('manage_container')
    self.writeInfo('[test_content] %s'%str(zmscontext.getMeasurement()))
    
    # remove test-folder
    self.writeInfo('[test_content] remove test-folder')
    zmscontext.manage_delObjects([folder.id,folder2.id])


  def tearDown(self):
    pass
