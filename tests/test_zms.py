# encoding: utf-8

from OFS.Folder import Folder

# Product imports.
from tests.zms_test_util import *
from Products.zms import mock_http
from Products.zms import zms

# /Products/zms> python -m unittest discover -s unit_tests
# /Products/zms> python -m unittest test_zms.ZMSTest
class ZMSTest(ZMSTestCase):

  temp_title = 'temp-test'

  def setUp(self):
    folder = Folder('myzmsx')
    folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview'})
    zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
    self.context = zmscontext
    print('[setUp] create %s'%self.temp_title)
    self.folder = zmscontext.manage_addZMSCustom('ZMSFolder',{'title':self.temp_title,'titlealt':self.temp_title},zmscontext.REQUEST)

  def test_portal(self):
    context = self.context
    request = context.REQUEST
    
    home = context.aq_parent
    ids = []
    clients = []
    n = 3
    for i in range(n):
      id = 'client%i'%i
      client = Folder(id)
      setattr(client, home.id, home)
      home._setObject(client.id, client)
      client = getattr(home, client.id)
      zmscontext = zms.initZMS(client, 'content', id, id, 'eng', 'eng', request)
      zmscontext.setConfProperty('Portal.Master',home.id)
      ids.append(id)
      clients.append(zmscontext)
    context.setConfProperty('Portal.Clients',ids)
    self.assertEqual(n,len(context.getPortalClients()))
    for client in clients:
      self.assertIsNotNone(client.getPortalMaster())
    
  def tearDown(self):
    zmscontext = self.context
    print('[tearDown] remove %s'%self.temp_title)
    zmscontext.manage_delObjects([self.folder.id])
