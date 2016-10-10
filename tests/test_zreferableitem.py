import test_util

class ZReferableItemTest(test_util.BaseTest):


  temp_title = 'temp-test'

  def setUp(self):
    zmscontext = self.context
    request = self.REQUEST
    self.writeInfo('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},request)

  def test_getRelativeUrl(self):
    context = self.context
    def assertEquals(path,url,expected):
      self.assertEquals("getRelativeUrl: %s->%s"%(path,url),expected,context.getRelativeUrl(path,url))
    assertEquals('/e1/e2/e3','/e1/e4/e5/e6','./../e4/e5/e6')
    assertEquals('http://host:port/e1/e2/e3#e4','http://host:port/e5?preview=preview#e6','./../../e5?preview=preview#e6')

  def test_getRefObjPath(self):
    zmscontext = self.context
    request = self.REQUEST
    folder = self.folder
    ref = '{$%s@%s}'%(zmscontext.getHome().id,'/'.join(folder.getPhysicalPath()[-folder.getLevel():]))
    self.assertEquals("getRefObjPath",'{$%s@%s}'%(zmscontext.getHome().id,'/'.join(folder.getPhysicalPath()[-folder.getLevel():])),zmscontext.getRefObjPath(folder))
    self.assertEquals("getLinkObj(@)",folder,zmscontext.getLinkObj(ref))
    ref = '{$%s}'%('/'.join(folder.getPhysicalPath()[-folder.getLevel():]))
    self.assertEquals("getLinkObj(!@)",folder,zmscontext.getLinkObj(ref))

  def tearDown(self):
    zmscontext = self.context
    request = self.REQUEST
    self.writeInfo('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
