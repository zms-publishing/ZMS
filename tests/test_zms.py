# encoding: utf-8

from OFS.Folder import Folder

# Product imports.
from tests.zms_test_util import *

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest test_zms.ZMSTest
class ZMSTest(ZMSPortalTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    super(ZMSTest, self).setUp()
    print('[setUp] create %s'%self.temp_title)
    zmscontext = self.context
    clients = zmscontext.getPortalClients()
    clients[0].manage_delObjects([clients[0].getCatalogAdapter().id])


  def test_portal(self):
    zmscontext = self.context
    clients = zmscontext.getPortalClients()
    self.assertEqual(3, len(clients))
    for client in clients:
      self.assertIsNotNone(client.getPortalMaster())
  
  def test_zcatalog_adapter(self):
    zmscontext = self.context
    catalog_adapter = zmscontext.getCatalogAdapter()
    self.assertIsNotNone(catalog_adapter)
    # Clients have parent catalog-adapter.
    clients = zmscontext.getPortalClients()
    for i in range(len(clients)):
      client = clients[i]
      if i == 0:
        self.assertEqual(catalog_adapter, client.getCatalogAdapter())
      else:
        self.assertNotEqual(catalog_adapter, client.getCatalogAdapter())

  def test_metaobj_manager(self):
    zmscontext = self.context
    metaobj_manager = zmscontext.getMetaobjManager()
    self.assertIsNotNone(metaobj_manager)
    clients = zmscontext.getPortalClients()
    for i in range(len(clients)):
      client = clients[i]
      self.assertEqual(metaobj_manager.getMetaobjIds(), client.getMetaobjManager().getMetaobjIds())

  def test_conf_properties(self):
    zmscontext = self.context
    clients = zmscontext.getPortalClients()
    for i in range(len(clients)):
      client = clients[i]
      self.assertIsNone(client.getConfProperty('foo'))
      zmscontext.setConfProperty('foo','bar')
      self.assertEqual('bar', client.getConfProperty('foo'))
      zmscontext.delConfProperty('foo')
      self.assertIsNone(client.getConfProperty('foo'))
    

  def tearDown(self):
    print('[tearDown] remove %s'%self.temp_title)
