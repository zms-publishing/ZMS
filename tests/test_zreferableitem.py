import test_util

class ZReferableItemTest(test_util.BaseTest):

  def test_getRelativeUrl(self):
    context = self.context
    def assertEquals(path,url,expected):
      self.assertEquals("getRelativeUrl: %s->%s"%(path,url),expected,context.getRelativeUrl(path,url))
    assertEquals('/e1/e2/e3','/e1/e4/e5/e6','./../e4/e5/e6')
    assertEquals('http://host:port/e1/e2/e3#e4','http://host:port/e5?preview=preview#e6','./../../e5?preview=preview#e6')
