# encoding: utf-8

from OFS.Folder import Folder

from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import standard
from Products.zms.ZMSZCatalogAdapter import catalog_request_context


# pytest tests/test_zcatalog_adapter.py
class ZCatalogAdapterTest(ZMSTestCase):

  def setUp(self):
    folder = Folder('site')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview','url':'{$}','theme':'conf:aquire','minimal_init':1,'content_init':1})
    self.context = standard.initZMS(folder, 'myzmsx', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)

  def test_request_context_restores_state(self):
    request = self.context.REQUEST
    request.set('lang', 'ger')
    request.set('ZMS_CONTEXT_URL', None)
    with catalog_request_context(self.context, 'eng') as lang:
      self.assertEqual('eng', lang)
      self.assertEqual('eng', request.get('lang'))
      self.assertTrue(request.get('ZMS_CONTEXT_URL'))
    self.assertEqual('ger', request.get('lang'))
    self.assertIsNone(request.get('ZMS_CONTEXT_URL'))

  def test_get_catalog_objects_explicit_lang(self):
    request = self.context.REQUEST
    adapter = self.context.getCatalogAdapter()
    adapter.setCustomFilterFunction('##\nreturn True')
    objects = adapter.get_catalog_objects(self.context, False, 'eng')
    self.assertTrue(len(objects) > 0)
    for node, d in objects:
      self.assertEqual('eng', d['lang'])
      self.assertTrue(d['id'].endswith('_eng'))
    self.assertEqual('eng', request.get('lang'))
