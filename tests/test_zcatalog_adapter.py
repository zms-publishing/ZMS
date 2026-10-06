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

  def _count_reindex_calls(self, adapter, node, **kwargs):
    calls = []
    adapter.reindex = lambda connector, base, **kw: calls.append(base.getPhysicalPath())
    adapter.get_connectors = lambda: [object()]
    adapter.setCustomFilterFunction('##\nreturn True')
    adapter.reindex_node(node, **kwargs)
    return calls

  def test_reindex_node_dedup_per_request(self):
    adapter = self.context.getCatalogAdapter()
    first = self._count_reindex_calls(adapter, self.context)
    second = self._count_reindex_calls(adapter, self.context)
    self.assertTrue(len(first) > 0)
    self.assertEqual([], second)

  def test_reindex_node_dedup_explicit_seen(self):
    adapter = self.context.getCatalogAdapter()
    request_log = set(self.context.REQUEST.get('reindex_node_log') or [])
    seen = set()
    first = self._count_reindex_calls(adapter, self.context, seen=seen)
    self.assertTrue(len(first) > 0)
    self.assertEqual(len(first), len(seen))
    # An explicit set does not touch the request-wide state.
    self.assertEqual(request_log, set(self.context.REQUEST.get('reindex_node_log') or []))
    self.assertEqual([], self._count_reindex_calls(adapter, self.context, seen=seen))
    self.assertTrue(len(self._count_reindex_calls(adapter, self.context, seen=set())) > 0)

  def test_reindex_nodes_returns_plain_dict(self):
    from Products.zms.ZMSZCatalogConnector import ZMSZCatalogConnector
    adapter = self.context.getCatalogAdapter()
    adapter.setCustomFilterFunction('##\nreturn True')
    added = []

    class Stub:
      getCatalogAdapter = lambda self: adapter
      manage_objects_clear = lambda self, home_id: (0, 0)
      manage_objects_add = lambda self, objects: (added.extend(objects) or (len(objects), 0))
    result = ZMSZCatalogConnector.reindex_nodes(Stub(), [self.context], fileparsing=False, langs=['eng'])
    self.assertEqual(['success', 'failed', 'log'], [k for k in result if k in ('success', 'failed', 'log')])
    self.assertEqual(len(added), result['success'])
    self.assertEqual(0, result['failed'])
    self.assertEqual(0, result['log'][0]['index'])
    self.assertEqual(self.context.getHome().id, result['home_id'])
    self.assertEqual(['eng'], list(result['log'][0]['objects']))
    self.assertTrue(all(d['lang'] == 'eng' for _, d in added))
