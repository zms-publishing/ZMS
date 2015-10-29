from traceback import format_exception
import inspect
import logging
import sys

class BaseTest(object):

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

  def assertTrue(self, message, actual):
    self.assertEquals(message,True,actual)

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

  def run(self):
    mod_tests = 'Products.zms.tests'
    for mod_name, mod_obj in inspect.getmembers(sys.modules[mod_tests],inspect.ismodule):
      for cls_name, cls_obj in inspect.getmembers(sys.modules['%s.%s'%(mod_tests,mod_name)],inspect.isclass):
        if cls_name.endswith('Test'):
          self.write(logging.INFO,cls_name)
          inst = cls_obj(self)
          keys = map(lambda x:x[0],inspect.getmembers(cls_obj,inspect.ismethod))
          filtered = []
          filtered.extend(filter(lambda x:x=='setUp',keys))
          filtered.extend(filter(lambda x:x.startswith('test_'),keys))
          filtered.extend(filter(lambda x:x=='tearDown',keys))
          for key in filtered:
            self.write(logging.INFO,'%s.%s'%(cls_name,key))
            try:
              getattr(inst,key)()
            except:
              t,v,tb = sys.exc_info()
              msg = 'can\'t %s.%s - exception: '%(cls_name,key)+''.join(format_exception(t, v, tb))
              self.write(logging.ERROR,msg)
    return self.printed