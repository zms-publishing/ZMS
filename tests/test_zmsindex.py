# encoding: utf-8

from OFS.Folder import Folder
import json

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import standard

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest tests.test_zmsindex.ZMSIndexTest
class ZMSIndexTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    folder = Folder('site')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview','url':'{$}'})
    self.context = standard.initZMS(folder, 'myzmsx', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    print('[setUp] create %s'%self.temp_title)

  def test_zmsindex(self):
    count = 0
    count_none = 0
    zmsindex = self.context.getZMSIndex()
    self.assertIsNotNone(zmsindex)
    zmsindex.manage_reindex()
    for document in self.context.getTreeNodes(mock_http.MockHTTPRequest(), 'ZMSDocument'):
        print('{$%s}'%document.get_uid())
        actual = self.context.getLinkObj('{$%s}'%document.get_uid())
        if actual is not None:
          self.assertEqual(actual.id, document.id)
        else:
          print('[test_zmsindex] {$%s} not found'%document.get_uid())
          count_none += 1
        count += 1
    print('[test_zmsindex] %s artifact items in index'%count_none)
    self.assertEqual( 64, count)
