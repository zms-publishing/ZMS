import zExceptions

def resetData(self):
  current_roles = self.getUserRoles(self.REQUEST['AUTHENTICATED_USER'])
  allowed_roles = ['Manager','ZMSAdministrator','ZMSEditor']
  authorized = len(self.intersection_list(current_roles,allowed_roles))>0 and True or False
  if not authorized:
    raise zExceptions.Unauthorized
  else:
    frmu = self.ZMSFormulator(self)
    frmu.clearData()