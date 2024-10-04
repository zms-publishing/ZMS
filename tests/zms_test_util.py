# encoding: utf-8

from OFS.Folder import Folder
import unittest
# Product imports.
from Products.zms import mock_http
from Products.zms import zms


class ZMSTestCase(unittest.TestCase):

    measurements = {}

    def setUp(self):
        print(self,"ZMSTestCase.setUp")
        folder = Folder('myzmsx')
        folder.REQUEST = mock_http.MockHTTPRequest({'lang':'eng','preview':'preview'})
        zmscontext = zms.initZMS(folder, 'content', 'titlealt', 'title', 'eng', 'eng', folder.REQUEST)
        self.context = zmscontext

    def tearDown(self):
        print(self,"ZMSTestCase.tearDown")

    def writeDebug(self, s):
        self.context.write(logging.DEBUG,s)

    def writeInfo(self, s):
        self.context.write(logging.INFO,s)

    def writeError(self, s):
        self.context.write(logging.ERROR,s)


class ZMSPortalTestCase(ZMSTestCase):

    def setUp(self):
        super(ZMSPortalTestCase, self).setUp()
        zmscontext = self.context
        request = zmscontext.REQUEST
        home = zmscontext.aq_parent
        ids = []
        n = 3
        for i in range(n):
            id = 'client%i'%i
            client = Folder(id)
            setattr(client, home.id, home)
            home._setObject(client.id, client)
            client = getattr(home, client.id)
            zmsclient = zms.initZMS(client, 'content', id, id, 'eng', 'eng', request)
            zmsclient.setConfProperty('Portal.Master',home.id)
            ids.append(id)
        zmscontext.setConfProperty('Portal.Clients',ids)

def addClient(zmscontext, id):
    """
    Add ZMS client.
    """
    request = zmscontext.REQUEST
    home = zmscontext.getHome()
    folder = Folder(id)
    home._setObject(folder.id,folder)
    folder_inst = getattr(home,id)
    request.set('lang_label',zmscontext.getLanguageLabel(request['lang']))
    zms_inst = zmscontext.initZMS(folder_inst, 'content', 'Title of %s'%id, 'Titlealt of %s'%id, request['lang'], request['lang'], request)
    print("home.id",home.id)
    zms_inst.setConfProperty('Portal.Master',home.id)
    for metaObjId in zmscontext.getMetaobjIds():
        zms_inst.metaobj_manager.acquireMetaobj(metaObjId)
    zmscontext.setConfProperty('Portal.Clients',zmscontext.getConfProperty('Portal.Clients',[])+[id])
    return zms_inst


def removeClient(zmscontext, id):
    """
    Remove ZMS client.
    """
    request = zmscontext.REQUEST
    home = zmscontext.getHome()
    home.manage_delObjects(ids=[id])
    zmscontext.setConfProperty('Portal.Clients',filter(lambda x:x!=id,zmscontext.getConfProperty('Portal.Clients',[])))
