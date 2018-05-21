from OFS.Folder import Folder


class HTTPRequest:

    def __init__(self, d={}, other={}):
        self.d = d
        self.other = other

    def __getitem__(self, k, v=None):
        return self.get(k)

    def __setitem__(self, k, v):
        self.set(k,v)
    
    def get(self, k, v=None):
        return self.d.get(k,v)

    def set(self, k, v):
        self.d[k] = v

    has_key__roles__ = None
    def has_key(self, k):
        return self.d.has_key(k)

    keys__roles__ = None
    def keys(self):
        return self.d.keys()


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

