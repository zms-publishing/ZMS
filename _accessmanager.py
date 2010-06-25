################################################################################
# _accessmanager.py
#
# $Id: _accessmanager.py,v 1.11 2004/10/04 19:57:06 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.11 $
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
from __future__ import nested_scopes
from App.special_dtml import HTMLFile
from AccessControl.User import UserFolder
from types import StringTypes
import copy
import sys
import time
import urllib
# Product Imports.
import _globals


# ------------------------------------------------------------------------------
#  _accessmanager.user_folder_meta_types:
#
#  User Folder Meta-Types.
# ------------------------------------------------------------------------------
user_folder_meta_types = ['LDAPUserFolder','User Folder','Simple User Folder']

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
def deleteUser(self, id, REQUEST):
  userFldr = self.getUserFolder()
  
  # Delete local roles in node.
  # ---------------------------
  nodes = self.getUserAttr(id,'nodes',{})
  for node in nodes.keys():
    ob = self.getLinkObj(node,REQUEST)
    if ob is not None:
      ob.manage_delLocalRoles(userids=[id])
  
  # Delete user from ZMS dictionary.
  # --------------------------------
  self.delUserAttr(id)
  
  # Delete user from User-Folder.
  # -----------------------------
  if userFldr.meta_type != 'LDAPUserFolder':
    userObj = userFldr.getUser(id)
    if userObj is not None:
      userFldr.userFolderDelUsers([id])
  
  id = ''
  return id


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
      access = True
      auth_user = REQUEST.get('AUTHENTICATED_USER')
      url = REQUEST.get('URL','/manage')
      url = url[url.rfind('/'):]
      if url.find('/manage') >= 0:
        if access:
          rights = self.getObjProperty( 'attr_dc_accessrights_restrictededitors', REQUEST)
          if type( rights) is list and len( rights) > 0:
            roles = auth_user.getRolesInContext(self)
            access = len( filter( lambda x: x in roles, rights)) > 0
            for right in rights:
              access = access or auth_user.has_role( right)
              access = access or auth_user.has_permission( right, self)
        if access:
          ob_access = self.getObjProperty('manage_access',REQUEST)
          access = access and ((not type(ob_access) is dict) or (ob_access.get( 'edit') is None) or (len( self.intersection_list( self.concat_list( ob_access.get( 'edit'), [ 'Manager']), self.getUserRoles(auth_user))) > 0))
        access = access and auth_user.has_permission( 'ZMS Author', self) in [ 1, True]
      else:
        access = access and auth_user.has_permission( 'View', self) in [ 1, True]
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
          raise "Maximum recursion depth exceeded"
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
      for id in roles:
        if id in security_roles.keys():
          dict = security_roles.get(id,{})
          for v in dict.values():
            for perm in v.get('roles',[]):
              role = perm.replace( ' ', '')
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
          raise "Maximum recursion depth exceeded"
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
          try:
            userFldr = self.getUserFolder()
            roles = userObj.getRoles()
            domains = userObj.getDomains()
            userFldr.userFolderEditUser(id, password, roles, domains)
          except: 
            _globals.writeError(self,'[manage_user]: can\'t change password')
        self.setUserAttr(userObj,'email',REQUEST.get('email','').strip())
        #-- Assemble message.
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_userForm?lang=%s&manage_tabs_message=%s'%(lang,message))


################################################################################
################################################################################
###
###   Class AccessableContainer
###
################################################################################
################################################################################
class AccessableContainer(AccessableObject): 

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
      for role in role_defs.keys():
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
      for role in role_defs.keys():
        self.manage_role(role_to_manage=role,permissions=role_permissions(self,role))
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
    def getValidUserids(self, search_term=''):
      valid_userids = []
      for userFldr in self.getUserFolders():
        if userFldr.aq_parent.objectValues(['ZMS']):
          if userFldr.meta_type == 'LDAPUserFolder':
            search_param = userFldr.getProperty('_login_attr')
            for user in userFldr.findUser(search_param=search_param,search_term=search_term):
              d = {}
              d['localUserFldr'] = userFldr
              d['name'] = user[search_param]
              for extra in ['givenName','sn']:
                try: d[extra] = user[extra]
                except: pass
              valid_userids.append(d)
          else:
            for userName in userFldr.getUserNames():
              if search_term == '' or search_term == userName:
                d = {}
                d['localUserFldr'] = userFldr
                d['name'] = userName
                valid_userids.append(d)
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
    def getUserAttr(self, user, name, default, flag=0):
      user = getUserId(user)
      if name not in [ 'nodes']:
        v = self.getLDAPUserAttr( user, name)
        if v is not None:
          return v
      d = self.getConfProperty('ZMS.security.users',{})
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
          raise "Maximum recursion depth exceeded"
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

    # --------------------------------------------------------------------------
    #  AccessManager.setLocalUser:
    # --------------------------------------------------------------------------
    def setLocalUser(self, id, node, roles, langs):
      #-- Insert node to user-properties.
      nodes = self.getUserAttr(id,'nodes',{})
      nodes[node] = {'langs':langs,'roles':roles}
      nodes = nodes.copy()
      self.setUserAttr(id,'nodes',nodes)
      roles = list(roles)
      if 'ZMSAdministrator' in roles: roles.append('Manager')
      #-- Set local roles in node.
      ob = self.getLinkObj(node,self.REQUEST)
      try:
        ob.manage_setLocalRoles(id,roles)
      except:
        _globals.writeError(self,'[setLocalUser]: node=%s does not exist!'%node)


    # --------------------------------------------------------------------------
    #  AccessManager.delLocalUser:
    # --------------------------------------------------------------------------
    def delLocalUser(self, id, node):
      #-- Delete node from user-properties.
      nodes = self.getUserAttr(id,'nodes',{})
      if nodes.has_key(node): del nodes[node]
      nodes = nodes.copy()
      self.setUserAttr(id,'nodes',nodes)
      #-- Delete local roles in node.
      ob = self.getLinkObj(node,self.REQUEST)
      try:
        ob.manage_delLocalRoles(userids=[id])
      except:
        _globals.writeError(self,'[delLocalUser]: node=%s does not exist!'%node)


    ############################################################################
    ###
    ###  Properties
    ###
    ############################################################################

    # Management Interface.
    # ---------------------
    manage_users = HTMLFile('dtml/ZMS/manage_users', globals())
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
          self.setUserAttr(userObj,'email',REQUEST.get('email','').strip())
          self.setUserAttr(userObj,'profile',REQUEST.get('profile','').strip())
        elif key=='attr':
          pass
        #-- Assemble message.
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn in ['delete', self.getZMILangStr('BTN_DELETE')]:
        if key=='obj':
          #-- Delete user.
          id = deleteUser(self,id,REQUEST)
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
