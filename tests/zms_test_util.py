# encoding: utf-8

from OFS.Folder import Folder
import unittest
# Product imports.
from Products.zms import standard
from Products.zms import zms


class ZMSTestCase(unittest.TestCase):

    measurements = {}

    def setUp(self):
        print(self,"ZMSTestCase.setUp")
        folder = Folder('myzmsx')
        folder.REQUEST = MockHTTPRequest({'lang':'eng','preview':'preview'})
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

class MockUser:

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id
    
class MockDict:

    def __init__(self, d={}):
        self.d = d

    __getitem____roles = None
    def __getitem__(self, k, v=None):
        return self.get(k)

    __setitem____roles = None
    def __setitem__(self, k, v):
        self.set(k,v)

    def __contains__(self, item):
        """ override in-operator """
        return item in self.d
    
    get__roles__ = None
    def get(self, k, v=None):
        return self.d.get(k,v)

    set__roles__ = None
    def set(self, k, v):
        self.d[k] = v

    has_key__roles__ = None
    def has_key(self, k):
        return self.d.has_key(k)

    keys__roles__ = None
    def keys(self):
        return self.d.keys()

class MockHTTPResponse:

    def __init__(self):
        self.headers = {}
    
    def setHeader(self, k, v):
        self.headers[k] = v

class MockHTTPSession(MockDict):

    pass

class MockHTTPRequest(MockDict):

    def __init__(self, d={}, form={}, environ={}, other={}):
        self.d = d
        self.form = form
        self.environ = environ
        self.other = other
        self.AUTHENTICATED_USER = MockUser("test")
        self.RESPONSE = MockHTTPResponse()
        self.SESSION = MockHTTPSession()
        self.set('AUTHENTICATED_USER', self.AUTHENTICATED_USER)
        self.set('RESPONSE', self.RESPONSE)
        self.set('SESSION', self.SESSION)

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
