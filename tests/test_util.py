from traceback import format_exception
import inspect
import logging
import sys
import time
import transaction

class BaseTest(object):

  measurements = {}

  def __init__(self, test_suite):
    self.test_suite = test_suite
    self.context = test_suite.context
    self.REQUEST = self.context.REQUEST

  def writeDebug(self, s):
    self.test_suite.write(logging.DEBUG,s)

  def writeInfo(self, s):
    self.test_suite.write(logging.INFO,s)

  def writeError(self, s):
    self.test_suite.write(logging.ERROR,s)

  def startMeasurement(self, category):
    self.measurements[category] = time.time()

  def stopMeasurement(self, category):
    if self.measurements.has_key(category):
      self.writeInfo('[stopMeasurement] | PERFORMANCE | %s | %.2fsecs.'%(category,time.time()-self.measurements[category]))
      del self.measurements[category]

  def assertTrue(self, message, actual):
    self.assertEquals(message,True,actual)

  def assertFalse(self, message, actual):
    self.assertEquals(message,False,actual)

  def assertEquals(self, message, expected, actual):
    clazz = ''
    details = ''
    if expected == actual:
      clazz = 'success'
      details = str(actual)
    else:
      clazz = 'failed'
      details = 'expected %s but was %s'%(str(expected),str(actual))
    self.writeInfo('[assertEquals] | %s | %s | %s'%(clazz.upper(),message,details))

  def addClient(self, zmscontext, id):
    request = zmscontext.REQUEST
    home = zmscontext.getHome()
    home.manage_addFolder(id=id,title=id.capitalize())
    folder_inst = getattr(home,id)
    request.set('lang_label',zmscontext.getLanguageLabel(request['lang']))
    zms_inst = zmscontext.initZMS(folder_inst, 'content', 'Title of %s'%id, 'Titlealt of %s'%id, request['lang'], request['lang'], request)
    zms_inst.setConfProperty('Portal.Master',home.id)
    for metaObjId in zmscontext.getMetaobjIds():
      zms_inst.metaobj_manager.acquireMetaobj(metaObjId)
    zmscontext.setConfProperty('Portal.Clients',zmscontext.getConfProperty('Portal.Clients',[])+[id])
    return zms_inst

  def removeClient(self, zmscontext, id):
    request = zmscontext.REQUEST
    home = zmscontext.getHome()
    home.manage_delObjects(ids=[id])
    zmscontext.setConfProperty('Portal.Clients',filter(lambda x:x!=id,zmscontext.getConfProperty('Portal.Clients',[])))


class TestSuite(object):

  def __init__(self, context):
    self.context = context
    self.printed = []
    request = context.REQUEST
    request.set('lang',request.get('lang',context.getPrimaryLanguage()))
    self.logger = logging.getLogger('tests.ZMS')
    loglevel = request.get('loglevel','DEBUG')
    loglevels = [logging.DEBUG,logging.INFO,logging.ERROR]
    self.loglevel = loglevels[loglevels.index({'DEBUG':logging.DEBUG,'INFO':logging.INFO,'ERROR':logging.ERROR}[loglevel]):]

  def write(self, l, s):
    from DateTime import DateTime
    dt = DateTime()
    line = '%s %s'%(dt.strftime("%Y-%m-%d %H:%M:%S,%f"),str(s))
    self.logger.log(l,line)
    if l in self.loglevel:
      self.printed.append(line)

  def find_tests(self):
    l = []
    mod_tests = 'Products.zms.tests'
    for mod_name, mod_obj in inspect.getmembers(sys.modules[mod_tests],inspect.ismodule):
      for cls_name, cls_obj in inspect.getmembers(sys.modules['%s.%s'%(mod_tests,mod_name)],inspect.isclass):
        if cls_name.endswith('Test'):
          inst = cls_obj(self)
          keys = map(lambda x:x[0],inspect.getmembers(cls_obj,inspect.ismethod))
          filtered = []
          filtered.extend(filter(lambda x:x=='setUp',keys))
          filtered.extend(filter(lambda x:x.startswith('test_'),keys))
          filtered.extend(filter(lambda x:x=='tearDown',keys))
          if filtered:
            l.append((cls_name, cls_obj))
    return l

  def run_all(self):
    mod_tests = 'Products.zms.tests'
    for mod_name, mod_obj in inspect.getmembers(sys.modules[mod_tests],inspect.ismodule):
      for cls_name, cls_obj in inspect.getmembers(sys.modules['%s.%s'%(mod_tests,mod_name)],inspect.isclass):
        if cls_name.endswith('Test'):
          inst = cls_obj(self)
          keys = map(lambda x:x[0],inspect.getmembers(cls_obj,inspect.ismethod))
          filtered = []
          filtered.extend(filter(lambda x:x=='setUp',keys))
          filtered.extend(filter(lambda x:x.startswith('test_'),keys))
          filtered.extend(filter(lambda x:x=='tearDown',keys))
          if filtered:
            self.write(logging.INFO,cls_name)
            for key in filtered:
              self.write(logging.INFO,'%s.%s'%(cls_name,key))
              try:
                getattr(inst,key)()
              except:
                t,v,tb = sys.exc_info()
                msg = 'can\'t %s.%s - exception: '%(cls_name,key)+''.join(format_exception(t, v, tb))
                self.write(logging.ERROR,msg)
            transaction.abort()
    return self.printed

  def run_single(self, name=None):
    rtn = {}
    mod_tests = 'Products.zms.tests'
    for mod_name, mod_obj in inspect.getmembers(sys.modules[mod_tests],inspect.ismodule):
      for cls_name, cls_obj in inspect.getmembers(sys.modules['%s.%s'%(mod_tests,mod_name)],inspect.isclass):
        if cls_name.endswith('Test'):
          inst = cls_obj(self)
          keys = map(lambda x:x[0],inspect.getmembers(cls_obj,inspect.ismethod))
          filtered = []
          filtered.extend(filter(lambda x:x=='setUp',keys))
          filtered.extend(filter(lambda x:x.startswith('test_'),keys))
          filtered.extend(filter(lambda x:x=='tearDown',keys))
          if filtered:
            if rtn.has_key('printed'):
              rtn['next'] = cls_name
              return rtn
            elif not name or name == cls_name:
              self.write(logging.INFO,cls_name)
              for key in filtered:
                self.write(logging.INFO,'%s.%s'%(cls_name,key))
                try:
                  getattr(inst,key)()
                except:
                  t,v,tb = sys.exc_info()
                  msg = 'can\'t %s.%s - exception: '%(cls_name,key)+''.join(format_exception(t, v, tb))
                  self.write(logging.ERROR,msg)
              transaction.abort()
              rtn['printed'] = self.printed
    return rtn