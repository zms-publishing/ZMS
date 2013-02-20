################################################################################
# _accessmanager.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

# Imports.
from App.special_dtml import HTMLFile
try: # Zope >= 2.13.0
  from OFS.userfolder import UserFolder
except:
  from AccessControl.User import UserFolder 
from types import StringTypes
import copy
import sys
import time
import urllib
import zExceptions
# Product Imports.
import _confmanager
import _globals


# ------------------------------------------------------------------------------
#  _accessmanager.user_folder_meta_types:
#
#  User Folder Meta-Types.
# ------------------------------------------------------------------------------
user_folder_meta_types = ['LDAPUserFolder','User Folder','Simple User Folder','Group User Folder']

# ------------------------------------------------------------------------------
#  _accessmanager.role_defs:
#
#  Role Definitions.
# ------------------------------------------------------------------------------
role_defs = {
   'ZMSAdministrator':{}
  ,'ZMSEditor':{'revoke':['Change DTML Methods','ZMS Administrator','ZMS UserAdministrator']}
  ,'ZMSAuthor':{'revoke':['Change DTML Methods','Import/Export objects','ZMS Administrator','ZMS UserAdministrator']}
  ,'ZMSSubscriber':{'grant':['Access contents information','View']}
  ,'ZMSUserAdministrator':{'revoke':['Change DTML Methods','Import/Export objects','ZMS Administrator','ZMS Author']}
}

# ------------------------------------------------------------------------------
#  _accessmanager.getUserId:
# ------------------------------------------------------------------------------
def getUserId(user):
  if type(user) is dict:
    user = user['__id__']
  elif user is not None and type(user) not in StringTypes:
    user = user.getId()
  return user

# ------------------------------------------------------------------------------
#  _accessmanager.role_permissions:
#
#  Role Permissions.
# ------------------------------------------------------------------------------
def role_permissions(self, role):
  permissions = map(lambda x: x['name'],self.permissionsOfRole('Manager'))
  if role_defs.has_key(role):
    role_def = role_defs[role]
    if role_def.has_key('revoke'):
      for revoke in role_def['revoke']:
        if revoke in permissions:
          permissions.remove(revoke)
    elif role_def.has_key('grant'):
      permissions = role_def['grant']
  return permissions

# ------------------------------------------------------------------------------
#  _accessmanager.insertUser:
# ------------------------------------------------------------------------------
def insertUser(self, newId, newPassword, newEmail, REQUEST):
  id = ''
  lang = REQUEST['lang']
  userFldr = self.getUserFolder()
  
  # Init user.
  # ----------
  newRoles =  []
  newDomains =  []
  userFldr.userFolderAddUser(newId,newPassword,newRoles,newDomains)
  userObj = userFldr.getUser(newId)
  if userObj is not None:
    
    # Set user.
    # ---------
    self.setUserAttr(userObj,'email',newEmail)
    id = getUserId(userObj)

  return id


# ------------------------------------------------------------------------------
#  _accessmanager.deleteUser:
# ------------------------------------------------------------------------------
def deleteUser(self, id):
  
  # Delete local roles in node.
  nodes = self.getUserAttr(id,'nodes',{})
  for node in nodes.keys():
    ob = self.getLinkObj(node)
    if ob is not None:
      ob.manage_delLocalRoles(userids=[id])
  
  # Delete user from ZMS dictionary.
  self.delUserAttr(id)
  
  # Delete user from User-Folder.
  userFldr = self.getUserFolder()
  if userFldr.meta_type != 'LDAPUserFolder':
    userObj = userFldr.getUser(id)
    if userObj is not None:
      userFldr.userFolderDelUsers([id])


################################################################################
################################################################################
###
###   Class AccessableObject
###
################################################################################
################################################################################
class AccessableObject: 

    # --------------------------------------------------------------------------
    #  AccessableObject.getUsers:
    # --------------------------------------------------------------------------
    def getUsers(self, REQUEST):
      users = {}
      d = self.getConfProperty('ZMS.security.users',{})
      for user in d.keys():
        roles = self.getUserRoles( user, aq_parent=0)
        langs = self.getUserLangs( user, aq_parent=0)
        if len(roles) > 0 and len( langs) > 0:
          users[ user] = {'roles':roles,'langs':langs}
      return users

    # --------------------------------------------------------------------------
    #  AccessableObject.hasAccess:
    # --------------------------------------------------------------------------
    def hasAccess(self, REQUEST):
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      access = auth_user.has_permission( 'View', self) in [ 1, True]
      if not access:
        access = access or self.hasPublicAccess() 
      return access

    # --------------------------------------------------------------------------
    #  AccessableObject.getUserRoles:
    # --------------------------------------------------------------------------
    def getUserRoles(self, userObj, aq_parent=1):
      roles = []
      try:
        roles.extend(list(userObj.getRolesInContext(self)))
        if 'Manager' in roles:
          roles = self.concat_list(roles,['ZMSAdministrator','ZMSEditor','ZMSAuthor','ZMSSubscriber','ZMSUserAdministrator'])
      except:
        pass
      nodes = self.getUserAttr(userObj,'nodes',{})
      ob = self
      depth = 0
      while ob is not None:
        if depth > sys.getrecursionlimit():
          raise zExceptions.InternalError("Maximum recursion depth exceeded")
        depth = depth + 1
        nodekey = self.getRefObjPath(ob)
        if nodekey in nodes.keys():
          roles = self.concat_list(roles,nodes[nodekey]['roles'])
          break
        if aq_parent:
          ob = ob.getParentNode()
        else:
          ob = None
      # Resolve security_roles.
      security_roles = self.getConfProperty('ZMS.security.roles',{})
      for id in filter(lambda x: x in security_roles.keys(),roles):
        dict = security_roles.get(id,{})
        for v in dict.values():
          for role in map(lambda x: x.replace( ' ', ''),v.get('roles',[])):
            if role not in roles:
              roles.append( role)
      return roles

    # --------------------------------------------------------------------------
    #  AccessableObject.getUserLangs:
    # --------------------------------------------------------------------------
    def getUserLangs(self, userObj, aq_parent=1):
      langs = []
      try:
        langs.extend(list(getattr(userObj,'langs',['*'])))
      except:
        pass
      nodes = self.getUserAttr(userObj, 'nodes', {})
      ob = self
      depth = 0
      while ob is not None:
        if depth > sys.getrecursionlimit():
          raise zExceptions.InternalError("Maximum recursion depth exceeded")
        depth = depth + 1
        nodekey = self.getRefObjPath(ob)
        if nodekey in nodes.keys():
          langs = nodes[nodekey]['langs']
          break
        if aq_parent:
          ob = ob.getParentNode()
        else:
          ob = None
      return langs


    ############################################################################
    ###
    ###  Public Access (Subscribers)
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  AccessableObject.hasRestrictedAccess:
    # --------------------------------------------------------------------------
    def hasRestrictedAccess(self):
      restricted = False
      if 'attr_dc_accessrights_restricted' in self.getObjAttrs().keys():
        req = {'lang':self.getPrimaryLanguage()}
        restricted = restricted or self.getObjProperty( 'attr_dc_accessrights_restricted', req) in [ 1, True]
      return restricted

    # --------------------------------------------------------------------------
    #  AccessableObject.hasPublicAccess:
    # --------------------------------------------------------------------------
    def hasPublicAccess(self):
      if 'attr_dc_accessrights_public' in self.getObjAttrs().keys():
        req = {'lang':self.getPrimaryLanguage()}
        if self.getObjProperty( 'attr_dc_accessrights_public', req) in [ 1, True]:
          return True
      public = not self.hasRestrictedAccess()
      parent = self.getParentNode()
      if parent is not None and isinstance( parent, AccessableObject):
        public = public and parent.hasPublicAccess()
      return public


    # --------------------------------------------------------------------------
    #  AccessableObject.synchronizePublicAccess:
    # --------------------------------------------------------------------------
    def synchronizePublicAccess(self):
      # This is ugly, but necessary since ZMSObject is inherited from 
      # AccessableObject and ZMSContainerObject is inherited from 
      # AccessableContainer!
      restricted = self.hasRestrictedAccess()
      if self.meta_id == 'ZMSLinkElement' and self.isEmbedded( self.REQUEST):
        ob = self.getRefObj()
        if ob is not None:
          for item in ob.breadcrumbs_obj_path():
            restricted = restricted or item.hasRestrictedAccess()
            if restricted: 
              break
      else:
        ob = self
      if isinstance( ob, AccessableContainer):
        if restricted:
          self.revokePublicAccess()
        else:
          self.grantPublicAccess()
      

    ############################################################################
    ###
    ###  Properties
    ###
    ############################################################################

    ############################################################################
    #  AccessableObject.manage_user:
    #
    #  Change user.
    ############################################################################
    manage_userForm = HTMLFile('dtml/ZMS/manage_user', globals())
    def manage_user(self, btn, lang, REQUEST, RESPONSE):
      """ AccessManager.manage_user """
      message = ''
      
      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_SAVE'):
        id = getUserId(REQUEST['AUTHENTICATED_USER'])
        userObj = self.findUser(id)
        password = REQUEST.get('password','******')
        confirm = REQUEST.get('confirm','')
        if password!='******' and password==confirm:
          for userFldr in self.getUserFolders():
            if id in userFldr.getUserNames():
              try:
                roles = userObj.getRoles()
                domains = userObj.getDomains()
                userFldr.userFolderEditUser(id, password, roles, domains)
                message += self.getZMILangStr('ATTR_PASSWORD') + ': '
              except: 
                message += _globals.writeError(self,'[manage_user]: can\'t change password')
              break
        self.setUserAttr(userObj,'email',REQUEST.get('email','').strip())
        #-- Assemble message.
        message += self.getZMILangStr('MSG_CHANGED')
      
      #-- Build json.
      RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      return self.str_json(message)


################################################################################
################################################################################
###
###   Class AccessableContainer
###
################################################################################
################################################################################
class AccessableContainer(AccessableObject): 

    # --------------------------------------------------------------------------
    #  AccessableContainer.synchronizeRolesAccess:
    # --------------------------------------------------------------------------
    def synchronizeRolesAccess(self):
      message = []
      security_roles = self.getConfProperty('ZMS.security.roles',{})
      for id in security_roles.keys():
        self.manage_role(role_to_manage=id,permissions=[])
        message.append("id="+id)
        d = security_roles.get(id,{})
        for node in d.keys():
          message.append("node="+node)
          ob = self.getLinkObj(node)
          if ob is not None:
            message.append("ob="+ob.absolute_url())
            roles = d[node]['roles']
            message.append("roles="+str(roles))
            permissions = []
            for role in roles:
              permissions = ob.concat_list(permissions,role_permissions(self,role.replace(' ','')))
            message.append("permissions="+str(permissions))
            ob.manage_role(role_to_manage=id,permissions=permissions)
      return '\n'.join(message)


    # --------------------------------------------------------------------------
    #  AccessableContainer.restrictAccess:
    # --------------------------------------------------------------------------
    def restrictAccess(self):
      for lang in self.getLangIds():
        for key in ['index_%s.html','index_print_%s.html','search_%s.html','sitemap_%s.html']:
          id = key%lang
          if hasattr(self,id):
            ob = getattr(self,id)
            ob.manage_acquiredPermissions(permissions=['Access contents information','View'])
            for role in ['Manager']: 
              ob.manage_role(role_to_manage=role,permissions=role_permissions(ob,role))

    # --------------------------------------------------------------------------
    #  AccessableContainer.grantPublicAccess:
    # --------------------------------------------------------------------------
    def grantPublicAccess(self):
      self.restrictAccess()
      self.manage_acquiredPermissions(role_permissions(self,'Manager'))
      security_roles = self.getConfProperty('ZMS.security.roles',{})
      for role in filter(lambda x: x not in ['Anonymous','Authenticated','Owner','Manager',],self.valid_roles()):
        permissions = []
        if self.getLevel() == 0:
          permissions = role_permissions(self,role)
        self.manage_role(role_to_manage=role,permissions=permissions)
      # Anonymous / Authenticated.
      permissions = []
      if self.getLevel() == 0:
        permissions = ['Access contents information','View']
      self.manage_role(role_to_manage='Anonymous',permissions=permissions)
      self.manage_role(role_to_manage='Authenticated',permissions=permissions)

    # --------------------------------------------------------------------------
    #  AccessableContainer.revokePublicAccess:
    # --------------------------------------------------------------------------
    def revokePublicAccess(self):
      self.restrictAccess()
      self.manage_acquiredPermissions([])
      security_roles = self.getConfProperty('ZMS.security.roles',{})
      for role in filter(lambda x: x not in ['Anonymous','Authenticated','Owner','Manager',],self.valid_roles()):
        permissions=role_permissions(self,role)
        if role in security_roles.keys():
          permissions = []
          # Authors & Editors
          if len(permissions) == 0:
            ob = self.getParentNode()
            while ob is not None and len(permissions)==0:
              permissions = map(lambda x: x['name'], filter(lambda x: x['selected']=='SELECTED',ob.permissionsOfRole(role)))
              ob = ob.getParentNode()
          # Subscribers
          if len(permissions) == 0:
            security_role = security_roles[role]
            for node in security_role.keys():
              ob = self.getLinkObj(node)
              if ob == self:
                for node_role in security_role[node]['roles']:
                  node_role_id = node_role.replace(' ','')
                  node_role_permissions = role_permissions(self,node_role_id)
                  permissions = self.concat_list(permissions,node_role_permissions)
        self.manage_role(role_to_manage=role,permissions=permissions)
      # Anonymous / Authenticated.
      permissions=['Access contents information']
      self.manage_role(role_to_manage='Anonymous',permissions=permissions)
      self.manage_role(role_to_manage='Authenticated',permissions=permissions)


################################################################################
################################################################################
###
###   Class AccessManager
###
################################################################################
################################################################################
class AccessManager(AccessableContainer): 

    # --------------------------------------------------------------------------
    #  AccessManager.getValidUserids:
    # --------------------------------------------------------------------------
    def getValidUserids(self, search_term='', without_node_check=True):
      local_userFldr = self.getUserFolder()
      valid_userids = []
      c = 0
      for userFldr in self.getUserFolders():
        doc_elmnts = userFldr.aq_parent.objectValues(['ZMS'])
        if doc_elmnts:
          doc_elmnt = doc_elmnts[0]
          if userFldr.meta_type == 'LDAPUserFolder':
            if c == 0:
              search_param = self.getConfProperty('LDAPUserFolder.login_attr',userFldr.getProperty('_login_attr'))
              users = userFldr.findUser(search_param=search_param,search_term=search_term)
              for user in users:
                d = {}
                d['localUserFldr'] = userFldr
                d['name'] = user[search_param]
                for extra in ['givenName','sn']:
                  try: d[extra] = user[extra]
                  except: pass
                valid_userids.append(d)
            else:
              node_prefix = '{$%s@'%self.getHome().id
              sec_users = doc_elmnt.getConfProperty('ZMS.security.users')
              for sec_user in sec_users:
                nodes = doc_elmnt.getUserAttr(sec_user,'nodes')
                if str(nodes).find(node_prefix) >= 0:
                  d = {}
                  d['localUserFldr'] = userFldr
                  d['name'] = sec_user
                  valid_userids.append(d)
          elif userFldr.meta_type != 'LDAPUserFolder':
            for userName in userFldr.getUserNames():
              if without_node_check or (local_userFldr == userFldr) or self.get_local_roles_for_userid(userName):
                if search_term == '' or search_term == userName:
                  d = {}
                  d['localUserFldr'] = userFldr
                  d['name'] = userName
                  valid_userids.append(d)
          c += 1
      return valid_userids
  
  
    # --------------------------------------------------------------------------
    #  AccessManager.setUserAttr:
    # --------------------------------------------------------------------------
    def setUserAttr(self, user, name, value):
      user = getUserId(user)
      d = self.getConfProperty('ZMS.security.users',{})
      i = d.get(user,{})
      i[name] = value
      d[user] = i.copy()
      self.setConfProperty('ZMS.security.users',d.copy())

    # --------------------------------------------------------------------------
    #  AccessManager.getLDAPUserAttr:
    # --------------------------------------------------------------------------
    def getLDAPUserAttr(self, user, name):
      user = getUserId(user)
      userFldr = self.getUserFolder()
      if userFldr.meta_type == 'LDAPUserFolder':
        userObj = userFldr.getUserByAttr( userFldr.getProperty( '_login_attr' ), user, pwd=None, cache=1)
        if userObj is not None:
          if name in userObj._properties:
            value = userObj.getProperty( name)
            return value
          elif name == 'email':
            for key in userObj._properties:
              value = userObj.getProperty( key)
              if value.find( '@') > 0 and value.rfind( '.') > 0 and value.find( '@') < value.rfind( '.'):
                return value
      return None

    # --------------------------------------------------------------------------
    #  AccessManager.getUserAttr:
    # --------------------------------------------------------------------------
    def getUserAttr(self, user, name=None, default=None, flag=0):
      user = getUserId(user)
      if name not in [ 'nodes']:
        v = self.getLDAPUserAttr( user, name)
        if v is not None:
          return v
      d = self.getConfProperty('ZMS.security.users',{})
      if name is None:
        v = d.get(user,None)
      else:
        i = d.get(user,{})
        v = i.get(name,default)
        # Process master.
        if flag == 0:
          portalMaster = self.getPortalMaster()
          if portalMaster is not None:
            w = portalMaster.getUserAttr(user, name, default, 1)
            if type(w) in StringTypes:
              if type(v) in StringTypes:
                if len(v) == 0:
                  v = w
        # Process clients.
        if flag == 0:
          for portalClient in self.getPortalClients():
            w = portalClient.getUserAttr(user, name, default)
            if type(w) is dict:
              if v is None:
                v = w
              elif type(v) is dict:
                v = v.copy()
                for node in w.keys():
                  ob = portalClient.getLinkObj(node)
                  newNode = self.getRefObjPath(ob)
                  v[newNode] = w[node]
      return v

    # --------------------------------------------------------------------------
    #  AccessManager.delUserAttr:
    # --------------------------------------------------------------------------
    def delUserAttr(self, user):
      user = getUserId(user)
      d = self.getConfProperty('ZMS.security.users',{})
      try:
        del d[user]
        self.setConfProperty('ZMS.security.users',d)
      except:
        _globals.writeError(self,'[delUserAttr]: user=%s not deleted!'%user)

    # --------------------------------------------------------------------------
    #  AccessManager.initRoleDefs:
    #
    #  Init Role-Definitions and Permission Settings
    # --------------------------------------------------------------------------
    def initRoleDefs(self):
    
      # Init Roles.
      for role in role_defs.keys():
        role_def = role_defs[role]
        # Add Local Role.
        if not role in self.valid_roles(): self._addRole(role)
        # Set permissions for Local Role.
        self.manage_role(role_to_manage=role,permissions=role_permissions(self,role))
      
      # Clear acquired permissions.
      self.manage_acquiredPermissions([])
      
      # Grant public access.
      self.synchronizePublicAccess()


    # --------------------------------------------------------------------------
    #  AccessManager.findUser:
    # --------------------------------------------------------------------------
    def findUser(self, name):
      for userFldr in self.getUserFolders():
        userObj = None
        if userFldr.meta_type=='LDAPUserFolder':
          if self.getConfProperty('LDAPUserFolder.login_attr','') == 'dn':
            userObj = userFldr.getUserByDN(name)
          else:
            ldapUsersObjs = userFldr.findUser(search_param=userFldr.getProperty('_login_attr'),search_term=name)
            if len(ldapUsersObjs) == 1:
              userObj = ldapUsersObjs[0]
              userObj['__id__'] = userObj[userFldr.getProperty( '_login_attr' )]
        else:
          userObj = userFldr.getUser(name)
        if userObj is not None:
          return userObj
      return None

    # --------------------------------------------------------------------------
    #  AccessManager.getUserFolder:
    # --------------------------------------------------------------------------
    def getUserFolder(self):
      homeElmnt = self.getHome()
      userFldrs = homeElmnt.objectValues(user_folder_meta_types)
      if len(userFldrs)==0:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          userFldr = portalMaster.getUserFolder()
        else:
          userFldr = UserFolder()
          homeElmnt._setObject(userFldr.id, userFldr)
      else:
        userFldr = userFldrs[0]
      return userFldr


    # --------------------------------------------------------------------------
    #  AccessManager.getUserFolders:
    # --------------------------------------------------------------------------
    def getUserFolders(self):
      userFolders = []
      ob = self
      depth = 0
      while True:
        if depth > sys.getrecursionlimit():
          raise zExceptions.InternalError("Maximum recursion depth exceeded")
        depth = depth + 1
        if ob is None: 
          break
        try:
          localUserFolders = ob.objectValues(user_folder_meta_types)
          if len(localUserFolders)==1:
            localUserFolder = localUserFolders[0]
            if localUserFolder not in userFolders:
              userFolders.append(localUserFolder)
          ob = ob.aq_parent
        except:
          ob = None
      return userFolders


    ############################################################################
    ###
    ###  Local Users
    ###
    ############################################################################

    # ------------------------------------------------------------------------------
    #  AccessManager.purgeLocalUsers
    # ------------------------------------------------------------------------------
    def purgeLocalUsers(self, ob=None, valid_userids=[], invalid_userids=[]):
      rtn = ""
      if ob is None: ob = self
      
      for local_role in ob.get_local_roles():
        delLocalRoles = False
        userid = local_role[0]
        userroles = local_role[1]
        if 'Owner' not in userroles:
          if userid not in valid_userids and userid not in invalid_userids:
            userob = ob.findUser(userid)
            if userob is None:
              invalid_userids.append(userid)
            else:
              valid_userids.append(userid)
          if userid in valid_userids:
            nodes = self.getUserAttr(userid,'nodes',{})
            if len(filter(lambda x: (x=="{$}" and ob.id=="content") or x=="{$%s}"%ob.id or x.endswith("/%s}"%ob.id),nodes.keys()))==0:
              delLocalRoles = True
          elif userid in invalid_userids:
            delLocalRoles = True
        if delLocalRoles:
          rtn += ob.absolute_url()+ " " + userid + " " + str(userroles) + "<br/>"
          ob.manage_delLocalRoles(userids=[userid])
      
      # Process subtree.
      for subob in ob.objectValues(ob.dGlobalAttrs.keys()):
        rtn += self.purgeLocalUsers(subob, valid_userids, invalid_userids)
      
      return rtn


    # --------------------------------------------------------------------------
    #  AccessManager.setLocalUser:
    # --------------------------------------------------------------------------
    def setLocalUser(self, id, node, roles, langs):
      
      # Insert node to user-properties.
      nodes = self.getUserAttr(id,'nodes',{})
      nodes[node] = {'langs':langs,'roles':roles}
      nodes = nodes.copy()
      self.setUserAttr(id,'nodes',nodes)
      roles = list(roles)
      if 'ZMSAdministrator' in roles:
        roles.append('Manager')
      
      # Set local roles in node.
      ob = self.getLinkObj(node,self.REQUEST)
      if ob is not None:
        ob.manage_setLocalRoles(id,roles)


    # --------------------------------------------------------------------------
    #  AccessManager.delLocalUser:
    # --------------------------------------------------------------------------
    def delLocalUser(self, id, node):
      
      # Delete node from user-properties.
      nodes = self.getUserAttr(id,'nodes',{})
      if nodes.has_key(node): del nodes[node]
      nodes = nodes.copy()
      self.setUserAttr(id,'nodes',nodes)
      
      # Delete local roles in node.
      ob = self.getLinkObj(node,self.REQUEST)
      if ob is not None:
        ob.manage_delLocalRoles(userids=[id])


    ############################################################################
    ###
    ###  Properties
    ###
    ############################################################################

    # Management Interface.
    # ---------------------
    manage_users = _confmanager.ConfDict.template('ZMS/manage_users')
    manage_users_sitemap = HTMLFile('dtml/ZMS/manage_users_sitemap', globals())

    ############################################################################
    #  AccessManager.manage_roleProperties:
    #
    #  Change or delete roles.
    ############################################################################
    def manage_roleProperties(self, btn, key, lang, REQUEST, RESPONSE=None):
      """ AccessManager.manage_roleProperties """
      message = ''
      id = REQUEST.get('id','')
      
      # Cancel.
      # -------
      if btn in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        id = ''
      
      # Insert.
      # -------
      if btn == self.getZMILangStr('BTN_INSERT'):
        if key=='obj':
          #-- Add local role.
          id = REQUEST.get('newId').strip()
          if id not in self.valid_roles(): self._addRole(role=id,REQUEST=REQUEST)
          #-- Prepare nodes from config-properties.
          security_roles = self.getConfProperty('ZMS.security.roles',{})
          security_roles[id] = {}
          security_roles = security_roles.copy()
          self.setConfProperty('ZMS.security.roles',security_roles)
          #-- Assemble message.
          message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_ROLE')
        elif key=='attr':
          #-- Insert node to config-properties.
          node = REQUEST.get('node')
          roles = REQUEST.get('roles',[])
          if not type(roles) is list: roles = [roles]
          security_roles = self.getConfProperty('ZMS.security.roles',{})
          dict = security_roles.get(id,{})
          dict[node] = {'roles':roles}
          security_roles[id] = dict
          security_roles = security_roles.copy()
          self.setConfProperty('ZMS.security.roles',security_roles)
          #-- Set permissions in node.
          ob = self.getLinkObj(node,REQUEST)
          permissions = []
          for role in roles:
            permissions = ob.concat_list(permissions,role_permissions(self,role.replace(' ','')))
          ob.manage_role(role_to_manage=id,permissions=permissions)
          #-- Assemble message.
          message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_NODE')
      
      # Delete.
      # -------
      elif btn in ['delete', self.getZMILangStr('BTN_DELETE')]:
        if key=='obj':
          #-- Delete local role.
          self._delRoles(roles=[id],REQUEST=REQUEST)
          #-- Delete nodes from config-properties.
          security_roles = self.getConfProperty('ZMS.security.roles',{})
          if security_roles.has_key(id): del security_roles[id]
          security_roles = security_roles.copy()
          self.setConfProperty('ZMS.security.roles',security_roles)
          id = ''
        elif key=='attr':
          #-- Delete node from config-properties.
          node = REQUEST.get('nodekey')
          security_roles = self.getConfProperty('ZMS.security.roles',{})
          dict = security_roles.get(id,{})
          if dict.has_key(node): del dict[node]
          security_roles[id] = dict
          security_roles = security_roles.copy()
          self.setConfProperty('ZMS.security.roles',security_roles)
          #-- Delete permissions in node.
          permissions = []
          ob = self.getLinkObj(node,REQUEST)
          if ob is not None:
            ob.manage_role(role_to_manage=id,permissions=permissions)
        #-- Assemble message.
        message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      # Return with message.
      if RESPONSE:
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_users?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))


    ############################################################################
    #  AccessManager.manage_userProperties:
    #
    #  Change or delete users.
    ############################################################################
    def manage_userProperties(self, btn, key, lang, REQUEST, RESPONSE=None):
      """ AccessManager.manage_userProperties """
      message = ''
      id = REQUEST.get('id','')
      
      # Cancel.
      # -------
      if btn in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        id = ''
      
      # Insert.
      # -------
      if btn == self.getZMILangStr('BTN_INSERT'):
        if key=='obj':
          #-- Insert user.
          newId = REQUEST.get('newId','').strip()
          newPassword = REQUEST.get('newPassword','').strip()
          newConfirm = REQUEST.get('newConfirm','').strip()
          newEmail = REQUEST.get('newEmail','').strip()
          id = insertUser(self,newId,newPassword,newEmail,REQUEST)
          #-- Assemble message.
          message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_USER')
        elif key=='attr':
          #-- Insert local user.
          langs = REQUEST.get('langs',[])
          if not type(langs) is list: langs = [langs]
          roles = REQUEST.get('roles',[])
          if not type(roles) is list: roles = [roles]
          node = REQUEST.get('node')
          ob = self.getLinkObj(node,REQUEST)
          docElmnt = ob.getDocumentElement()
          node = docElmnt.getRefObjPath(ob)
          docElmnt.setLocalUser(id, node, roles, langs)
          #-- Assemble message.
          message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_NODE')
      
      # Change.
      # -------
      elif btn == self.getZMILangStr('BTN_SAVE'):
        userObj = self.findUser(id)
        if key=='obj':
          password = REQUEST.get('password','******')
          confirm = REQUEST.get('confirm','')
          if password!='******' and password==confirm:
            try:
              userFldr = self.getUserFolder()
              roles = userObj.getRoles()
              domains = userObj.getDomains()
              userFldr.userFolderEditUser(id, password, roles, domains)
            except: 
              _globals.writeError(self,'[manage_user]: can\'t change password')
          self.setUserAttr(id,'email',REQUEST.get('email','').strip())
          self.setUserAttr(id,'profile',REQUEST.get('profile','').strip())
        elif key=='attr':
          pass
        #-- Assemble message.
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn in ['delete', self.getZMILangStr('BTN_DELETE')]:
        if key=='obj':
          #-- Delete user.
          deleteUser(self,id)
          id = ''
          #-- Assemble message.
          message = self.getZMILangStr('MSG_DELETED')%int(1)
        elif key=='attr':
          #-- Delete local user.
          node = REQUEST.get('nodekey')
          try:
            self.delLocalUser(id, node)
          except:
            pass
          try:
            docElmnt = self.getDocumentElement()
            ob = self.getLinkObj(node,REQUEST)
            if ob is not None:
              docElmnt = ob.getDocumentElement()
              node = docElmnt.getRefObjPath(ob)
            docElmnt.delLocalUser(id, node)
          except:
            pass
          #-- Assemble message.
          message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      # Invite.
      # -------
      elif btn == self.getZMILangStr('BTN_INVITE'):
        if key=='obj':
          email = self.getUserAttr(id,'email','')
          nodekeys = REQUEST.get('nodekeys',[])
          if len(email) > 0 and len(nodekeys) > 0:
            # Send notification.
            # ------------------
            #-- Recipient
            mto = email
            #-- Body
            userObj = self.findUser(id)
            mbody = []
            mbody.append(self.getTitle(REQUEST)+' '+self.getHref2IndexHtml(REQUEST))
            mbody.append('\n')
            mbody.append('\n%s: %s'%(self.getZMILangStr('ATTR_ID'),id))
            mbody.append('\n')
            for nodekey in nodekeys:
              ob = self.getLinkObj(nodekey,REQUEST)
              mbody.append('\n * '+ob.getTitlealt(REQUEST)+' ['+ob.display_type(REQUEST)+']: '+ob.absolute_url()+'/manage')
            mbody.append('\n')
            mbody.append('\n' + self.getZMILangStr('WITH_BEST_REGARDS'))
            mbody.append('\n' + str(REQUEST['AUTHENTICATED_USER']))
            mbody.append('\n-------------------------------')
            mbody = ''.join(mbody)
            #-- Subject
            msubject = '%s (invitation)'%self.getTitlealt(REQUEST)
            #-- Send
            self.sendMail(mto,msubject,mbody,REQUEST)
            #-- Assemble message.
            message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      if RESPONSE:
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_users?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################