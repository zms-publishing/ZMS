import zExceptions
import ftfy

def printData(self):
  current_roles = self.getUserRoles(self.REQUEST['AUTHENTICATED_USER'])
  allowed_roles = ['Manager','ZMSAdministrator','ZMSEditor']
  authorized = len(self.intersection_list(current_roles,allowed_roles))>0 and True or False
  if not authorized:
    raise zExceptions.Unauthorized
  else:
    frmu = self.ZMSFormulator(self)
    self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
    self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
    self.REQUEST.RESPONSE.setHeader('Content-Type','text/html; charset=utf-8')
    data = frmu.printDataRaw()
    return ftfy.fix_text(data.replace('#/#',' | '))