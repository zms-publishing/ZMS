import unittest
# encoding: utf-8

import os
import tempfile
import threading
import time
from OFS.Folder import Folder

from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import standard
from Products.zms import ZMSZCatalogAdapterQueue


class StubConnector:
  """Records the pages handed to reindex_nodes."""
  def __init__(self, fail_on=None):
    self.pages = []
    self.fail_on = fail_on

  def reindex_nodes(self, nodes, fileparsing=True, langs=None):
    if self.fail_on and self.fail_on in [n.id for n in nodes]:
      raise ValueError('boom')
    self.pages.append([n.id for n in nodes])
    return {'success': len(nodes), 'failed': 0,
            'log': [{'objects': {'eng': 1}} for n in nodes]}


# pytest tests/test_zcatalog_adapter_queue.py
class JobControlTest(ZMSTestCase):

  def setUp(self):
    self.dir = tempfile.TemporaryDirectory()
    self.control = ZMSZCatalogAdapterQueue.JobControl('http://host/site', self.dir.name)

  def tearDown(self):
    self.dir.cleanup()

  def test_single_flight_lock(self):
    self.assertFalse(self.control.is_locked())
    fd = self.control.try_acquire()
    self.assertIsNotNone(fd)
    self.assertTrue(self.control.is_locked())
    self.assertIsNone(self.control.try_acquire())
    self.control.release(fd)
    self.assertFalse(self.control.is_locked())
    self.assertIsNotNone(self.control.try_acquire())

  def test_status_and_markers(self):
    self.assertIsNone(self.control.read_status())
    self.control.update_status({'job_id': 'a', 'state': 'running'}, replace=True)
    self.control.update_status({'state': 'failed'}, expected_job_id='other')
    self.assertEqual('running', self.control.read_status()['state'])
    self.control.update_status({'state': 'completed'}, expected_job_id='a')
    self.assertEqual('completed', self.control.read_status()['state'])
    self.assertFalse(self.control.pause_requested())
    self.control.request_pause()
    self.assertTrue(self.control.pause_requested())
    self.control.request_stop()
    self.assertTrue(self.control.stop_requested())
    self.control.clear_markers()
    self.assertFalse(self.control.pause_requested() or os.path.exists(self.control.stop_path))


class RunReindexTest(ZMSTestCase):

  lang = 'eng'

  def setUp(self):
    folder = Folder('site')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview','url':'{$}','theme':'conf:aquire','minimal_init':1,'content_init':1})
    self.context = standard.initZMS(folder, 'myzmsx', 'titlealt', 'title', self.lang, self.lang, folder.REQUEST)
    self.dir = tempfile.TemporaryDirectory()
    self.control = ZMSZCatalogAdapterQueue.JobControl('k', self.dir.name)
    self.client = [{'home_id': '{$}', 'expected': None, 'node': self.context}]

  def tearDown(self):
    self.dir.cleanup()

  def test_iter_nodes_filters_meta_ids(self):
    all_nodes = list(ZMSZCatalogAdapterQueue.iter_nodes(self.context))
    self.assertEqual(self.context, all_nodes[0])
    folders = list(ZMSZCatalogAdapterQueue.iter_nodes(self.context, {'ZMSFolder'}))
    self.assertTrue(all(n.meta_id == 'ZMSFolder' for n in folders))
    self.assertTrue(len(folders) <= len(all_nodes))

  def test_run_pages_and_progress(self):
    connector = StubConnector()
    events = []
    commits = []
    stats = ZMSZCatalogAdapterQueue.run_reindex(
      connector, self.client, self.control,
      progress=lambda s, state, uid, path: events.append(state),
      page_size=2, commit=lambda: commits.append(1))
    total = len(list(ZMSZCatalogAdapterQueue.iter_nodes(self.context)))
    self.assertEqual(total, stats['candidates'])
    self.assertEqual(total, stats['success'])
    self.assertEqual(total, stats['objects'])
    self.assertEqual(['{$}'], stats['completed_clients'])
    self.assertEqual(len(connector.pages), len(commits))
    self.assertTrue(all(len(p) <= 2 for p in connector.pages))
    self.assertEqual('completed', events[-1])

  def test_failed_page_is_counted_and_aborted(self):
    first = list(ZMSZCatalogAdapterQueue.iter_nodes(self.context))[0].id
    aborts = []
    stats = ZMSZCatalogAdapterQueue.run_reindex(
      StubConnector(fail_on=first), self.client, self.control,
      page_size=1, abort=lambda: aborts.append(1))
    self.assertEqual(1, stats['failed'])
    self.assertEqual(['{$}'], stats['failed_clients'])
    self.assertEqual(1, len(aborts))

  def test_stop_ends_run(self):
    connector = StubConnector()
    self.control.request_stop()
    events = []
    ZMSZCatalogAdapterQueue.run_reindex(connector, self.client, self.control,
      progress=lambda s, state, uid, path: events.append(state))
    self.assertEqual([], connector.pages)
    self.assertEqual('stopped', events[-1])

  def test_pause_and_proceed(self):
    connector = StubConnector()
    self.control.request_pause()
    t = threading.Thread(target=ZMSZCatalogAdapterQueue.run_reindex, args=(connector, self.client, self.control))
    t.start()
    time.sleep(0.8)
    self.assertEqual([], connector.pages)
    self.control.clear_pause()
    t.join(10)
    self.assertFalse(t.is_alive())
    self.assertTrue(len(connector.pages) > 0)


class StartJobTest(unittest.TestCase):
  """Runs a real job: own thread, own ZODB connection, one commit per page."""

  def setUp(self):
    import transaction
    from AccessControl.SpecialUsers import system
    from App.config import getConfiguration
    from OFS.Application import Application
    from Testing.makerequest import makerequest
    from ZODB.DB import DB
    from ZODB.MappingStorage import MappingStorage
    # The connector writes its external methods to INSTANCE_HOME/Extensions.
    self.instance_dir = tempfile.TemporaryDirectory()
    self.config = getConfiguration()
    self.instancehome = self.config.instancehome
    self.config.instancehome = self.instance_dir.name
    os.makedirs(os.path.join(self.instance_dir.name, 'Extensions'))
    self.control_dir = tempfile.TemporaryDirectory()
    self.db = DB(MappingStorage())
    self.conn = self.db.open()
    app = Application()
    self.conn.root()['Application'] = app
    app._setObject('site', Folder('site'))
    wapp = makerequest(app)
    request = wapp.REQUEST
    request.other['AUTHENTICATED_USER'] = system
    for k, v in {'lang':'eng','lang_label':'English','manage_lang':'eng','preview':'preview',
        'theme':'conf:aquire','minimal_init':1,'content_init':1}.items():
      request.set(k, v)
    self.root = standard.initZMS(wapp.site, 'myzmsx', 'titlealt', 'title', 'eng', 'eng', request)
    adapter = self.root.getCatalogAdapter()
    adapter.ensure_zcatalog_connector_is_initialized()
    self.connector = adapter.add_connector('zcatalog_connector')
    self.connector.manage_init()
    transaction.commit()
    self.key = 'test-%s' % id(self)
    self.control = ZMSZCatalogAdapterQueue.JobControl(self.key, self.control_dir.name)
    self.control_dir_saved = ZMSZCatalogAdapterQueue.CONTROL_DIR
    ZMSZCatalogAdapterQueue.CONTROL_DIR = self.control_dir.name

  def tearDown(self):
    import transaction
    ZMSZCatalogAdapterQueue.CONTROL_DIR = self.control_dir_saved
    transaction.abort()
    self.conn.close()
    self.db.close()
    self.config.instancehome = self.instancehome
    self.instance_dir.cleanup()
    self.control_dir.cleanup()

  def _wait(self):
    for _ in range(150):
      status = ZMSZCatalogAdapterQueue.get_status(self.key)
      if status['state'] in ('completed', 'failed', 'stopped'):
        return status
      time.sleep(0.2)
    self.fail('job did not finish')

  def _indexed(self):
    import transaction
    transaction.abort()
    return sum(len(c._catalog) for c in self.root.objectValues() if c.meta_type == 'ZCatalog')

  def test_start_indexes_in_worker_thread(self):
    self.assertIsNone(ZMSZCatalogAdapterQueue.start(self.root, ['{$}'], key=self.key))
    status = self._wait()
    self.assertEqual('completed', status['state'])
    self.assertEqual(0, status['failed'])
    self.assertTrue(status['success'] > 0)
    self.assertEqual(status['success'], self._indexed())
    self.assertFalse(self.control.is_locked())

  def test_start_while_locked(self):
    fd = self.control.try_acquire()
    try:
      self.assertEqual('Background Job is already running',
        ZMSZCatalogAdapterQueue.start(self.root, ['{$}'], key=self.key))
    finally:
      self.control.release(fd)

  def test_start_without_client(self):
    self.assertEqual('No ZMS-node selected', ZMSZCatalogAdapterQueue.start(self.root, [], key=self.key))


class AdapterEndpointsTest(StartJobTest):
  """Adapter API and the manage_reindex_* endpoints on top of the job."""

  def _request(self, method='POST', **form):
    request = self.root.REQUEST
    request.other['REQUEST_METHOD'] = method
    for k, v in form.items():
      request.set(k, v)
    return request

  def test_start_and_status_endpoints(self):
    import json
    adapter = self.root.getCatalogAdapter()
    adapter.get_reindex_job_key = lambda: self.key
    self.assertEqual('idle', json.loads(adapter.manage_reindex_status(self._request('GET')))['state'])
    result = json.loads(adapter.manage_reindex_start(self._request(home_ids=['{$}'], page_size='5')))
    self.assertEqual({'message': None}, result)
    status = self._wait()
    self.assertEqual('completed', status['state'])
    self.assertTrue(status['success'] > 0)
    self.assertEqual(status['success'], json.loads(adapter.manage_reindex_status(self._request('GET')))['success'])

  def test_state_changes_require_post(self):
    import json
    adapter = self.root.getCatalogAdapter()
    adapter.get_reindex_job_key = lambda: self.key
    for endpoint in (adapter.manage_reindex_start, adapter.manage_reindex_pause,
                     adapter.manage_reindex_proceed, adapter.manage_reindex_stop):
      result = json.loads(endpoint(self._request('GET', home_ids=['{$}'])))
      self.assertEqual('POST required', result['message'])
    self.assertEqual('idle', adapter.get_reindex_job_status()['state'])

  def test_control_without_job(self):
    import json
    adapter = self.root.getCatalogAdapter()
    adapter.get_reindex_job_key = lambda: self.key
    for endpoint in (adapter.manage_reindex_pause, adapter.manage_reindex_proceed, adapter.manage_reindex_stop):
      self.assertEqual('No background job is running', json.loads(endpoint(self._request()))['message'])


class PageFallbackTest(unittest.TestCase):

  def test_failed_page_is_retried_per_node(self):
    class N:
      meta_id = 'ZMSDocument'
      def __init__(self, n): self.n = n
      def get_uid(self): return str(self.n)
      def getPhysicalPath(self): return ('', 'x', str(self.n))
    class Connector:
      def reindex_nodes(self, nodes, fileparsing=False):
        if len(nodes) > 1 or nodes[0].n == 2:
          raise ValueError('boom')
        return {'success': 1, 'failed': 0, 'log': [{'objects': {'ger': 1}}]}
    class Control:
      def stop_requested(self): return False
      def pause_requested(self): return False
    nodes = [N(i) for i in range(4)]
    original = ZMSZCatalogAdapterQueue.iter_nodes
    ZMSZCatalogAdapterQueue.iter_nodes = lambda node, meta_ids=None: iter(nodes)
    try:
      stats = ZMSZCatalogAdapterQueue.run_reindex(
        Connector(), [{'home_id': 'h', 'node': None}], Control(), page_size=4)
    finally:
      ZMSZCatalogAdapterQueue.iter_nodes = original
    self.assertEqual(3, stats['success'])
    self.assertEqual(1, stats['failed'])
    self.assertEqual(4, stats['nodes_completed'])


class PassiveQueueTest(StartJobTest):
  """Mode 'async': reindex_node queues, a worker thread indexes after commit."""

  def _wait_empty(self):
    import transaction
    adapter = self.root.getCatalogAdapter()
    for _ in range(100):
      transaction.abort()
      if not ZMSZCatalogAdapterQueue.pending(adapter):
        time.sleep(0.3)  # the drainer may still hold the lock
        return
      time.sleep(0.1)
    self.fail('queue not drained')

  def test_sync_mode_does_not_queue(self):
    import transaction
    adapter = self.root.getCatalogAdapter()
    adapter.setCustomFilterFunction('##\nreturn True')
    self.assertTrue(adapter.reindex_node(self.root))
    self.assertEqual(0, ZMSZCatalogAdapterQueue.pending(adapter))

  def test_async_mode_queues_and_drains_after_commit(self):
    import transaction
    adapter = self.root.getCatalogAdapter()
    adapter.setCustomFilterFunction('##\nreturn True')
    self.root.setConfProperty('ZMS.CatalogAwareness.mode', 'async')
    transaction.commit()
    before = self._indexed()
    self.assertTrue(adapter.reindex_node(self.root))
    self.assertEqual(1, ZMSZCatalogAdapterQueue.pending(adapter))
    self.assertEqual(before, self._indexed())
    transaction.commit()
    self._wait_empty()
    self.assertEqual({}, adapter.get_reindex_queue_status()['failed'])

  def test_rolled_back_edit_is_not_queued(self):
    import transaction
    adapter = self.root.getCatalogAdapter()
    self.root.setConfProperty('ZMS.CatalogAwareness.mode', 'async')
    transaction.commit()
    adapter.reindex_node(self.root)
    transaction.abort()
    self.assertEqual(0, ZMSZCatalogAdapterQueue.pending(adapter))

  def test_failing_entry_becomes_dead_letter(self):
    import transaction
    adapter = self.root.getCatalogAdapter()
    adapter.setCustomFilterFunction('##\nreturn True')
    self.root.setConfProperty('ZMS.CatalogAwareness.mode', 'async')
    transaction.commit()
    adapter.__class__.reindex_node_now, saved = (lambda self, node, seen=None: False), adapter.__class__.reindex_node_now
    try:
      adapter.reindex_node(self.root)
      transaction.commit()
      # retry delay of the hook-started drainer is 1s; wait for 3 attempts
      for _ in range(100):
        transaction.abort()
        if adapter.get_reindex_queue_status()['failed']:
          break
        time.sleep(0.2)
    finally:
      adapter.__class__.reindex_node_now = saved
    self.assertEqual(1, len(adapter.get_reindex_queue_status()['failed']))
    self.assertEqual(0, ZMSZCatalogAdapterQueue.pending(adapter))

  def test_queue_mode_endpoint_and_status(self):
    import json
    adapter = self.root.getCatalogAdapter()
    request = self.root.REQUEST
    request.other['REQUEST_METHOD'] = 'GET'
    response = json.loads(adapter.manage_reindex_queue_mode(request))
    self.assertEqual('POST required', response['message'])
    self.assertEqual(405, request.RESPONSE.status)
    request.other['REQUEST_METHOD'] = 'POST'
    request.set('queue_mode', 'invalid')
    self.assertEqual('Invalid reindex mode',
      json.loads(adapter.manage_reindex_queue_mode(request))['message'])
    request.set('queue_mode', 'sync')
    result = json.loads(adapter.manage_reindex_queue_mode(request))
    self.assertEqual('sync', result['mode'])
    status = json.loads(adapter.manage_reindex_queue_status(request))
    self.assertEqual('sync', status['mode'])
    self.assertEqual(0, status['pending'])
