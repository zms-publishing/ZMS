from Products.zms import standard
import test_util

class StandardTest(test_util.BaseTest):

  def test_url_append_params(self):
    expected = 'index.html?a=b&amp;c=d&amp;e=1&amp;f:list=1&amp;f:list=2&amp;f:list=3'
    v = standard.url_append_params('index.html?a=b',{'c':'d','e':1,'f':[1,2,3]})
    self.assertEquals('standard.url_append_params()',expected,v)
