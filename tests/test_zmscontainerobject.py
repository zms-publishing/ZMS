import test_util

class ZMSContainerObjectTest(test_util.BaseTest):

  temp_title = 'temp-test'

  def setUp(self):
    context = self.context
    request = self.REQUEST
    self.writeInfo('[setUp] create %s'%self.temp_title)
    self.folder = context.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},request)

  def test_tree(self):
    context = self.context
    request = self.REQUEST
    
    folder = self.folder
    self.writeInfo('>>>>>>>>>> test tree')
    ta1 = folder.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc1 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-1','titlealt':'doc-1'},request)
    ta11 = doc1.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc2 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-2','titlealt':'doc-2'},request)
    ta21 = doc2.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    doc3 = folder.manage_addZMSCustom('ZMSDocument',{'title':'document-3','titlealt':'doc-3'},request)
    ta31 = doc3.manage_addZMSCustom('ZMSTextarea',{'text':'Lorem ipsum dolor'},request)
    self.assertEquals("%s.#child_nodes"%folder.id,4,len(folder.getChildNodes(request)))
    self.assertEquals("%s.#child_nodes:pageelements"%folder.id,1,len(folder.getChildNodes(request,context.PAGEELEMENTS)))
    self.assertEquals("%s.#child_nodes:pages"%folder.id,3,len(folder.getChildNodes(request,context.PAGES)))
    self.assertEquals("%s.#tree_nodes"%folder.id,7,len(folder.getTreeNodes(request)))
    
    self.writeInfo('>>>>>>>>>> test zmsindex')
    catalog = getattr(context,'zcatalog_index',None)
    if catalog is None:
      self.writeInfo('skip')
    else:
      self.writeDebug('inline-link from ta11 (%s) to doc2 (%s)'%(ta11.absolute_url(),doc2.absolute_url()))
      ta11.setObjProperty('text','Lorem <a data-id="{$%s}" href="test.html">ipsum</a> dolor'%doc2.get_uid(),request['lang'])
      href = context.getRelativeUrl(ta11.getHref2IndexHtml(request),doc2.getHref2IndexHtml(request))
      self.writeDebug('inline-link from ta11 to doc2: '+href)
      self.assertTrue('%s.text:contains(href="%s")'%(ta11.id,href),ta11.attr('text').find('href="%s"'%href)>0)

  def tearDown(self):
    context = self.context
    request = self.REQUEST
    self.writeInfo('[tearDown] remove %s'%self.temp_title)
    context.manage_delObjects([self.folder.id])
