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