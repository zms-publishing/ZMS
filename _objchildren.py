################################################################################
# _objchildren.py
#
# $Id: _objchildren.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.7 $
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
import copy
import time
import urllib
# Product Imports.
import _blobfields
import _fileutil
import _globals


################################################################################
################################################################################
###
###   Object Children
###
################################################################################
################################################################################
class ObjChildren:

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage_initObjChild',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)

    """
    ############################################################################
    ###
    ###  Constructor
    ###
    ############################################################################
    """
    # --------------------------------------------------------------------------
    #	ObjChildren.initObjChild
    # --------------------------------------------------------------------------
    def initObjChild(self, id, _sort_id, type, REQUEST):
      
      ##### ID ####
      metaObjAttr = self.getObjChildrenAttr(id)
      repetitive = metaObjAttr.get('repetitive',0)==1
      if repetitive:
        id += str(self.getSequence().nextVal())
      
      ##### Create ####
      oItem = getattr(self,id,None)
      if oItem is None or id not in self.objectIds():
        if self.dGlobalAttrs.has_key(type):
          obj = self.dGlobalAttrs[type]['obj_class'](id,_sort_id+1)
        else:
          obj = self.dGlobalAttrs['ZMSCustom']['obj_class'](id,_sort_id+1,type)
        self._setObject(obj.id, obj)
        oItem = getattr(self,id)
        
      ##### Object State ####
      oItem.setObjStateNew(REQUEST)
      ##### Init Properties ####
      oItem.setObjStateModified(REQUEST)
      for lang in self.getLangIds():
        oItem.setObjProperty('active',1,lang)
      ##### VersionManager ####
      oItem.onChangeObj(REQUEST)
          
      ##### Normalize Sort-IDs ####
      self.normalizeSortIds(_globals.id_prefix(id))
        
      return oItem


    # --------------------------------------------------------------------------
    #  ObjChildren._initObjChildren
    # --------------------------------------------------------------------------
    def _initObjChildren(self, obj_attr, REQUEST):
      id = obj_attr['id']
      ids = []
      for ob in self.getChildNodes(REQUEST):
        if ob.id[:len(id)]==id:
          ids.append(ob.id)
      mandatory = obj_attr.get('mandatory',0)==1
      if mandatory:
        if len(ids) == 0:
          default  = obj_attr.get('custom')
          if default:
            _fileutil.import_zexp(self,default,obj_attr['id'],obj_attr['id'])
          else:
            if obj_attr['type'] == '*' and type( obj_attr['keys']) is list and len( obj_attr['keys']) > 0:
              obj_attr['type'] = obj_attr['keys'][0]
            self.initObjChild(obj_attr['id'],0,obj_attr['type'],REQUEST)
      repetitive = obj_attr.get('repetitive',0)==1
      if repetitive:
        if id in ids:
          new_id = self.getNewId(id)
          if _globals.debug( self):
            _globals.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(id,new_id))
          if new_id not in self.objectIds():
            self.manage_renameObject(id=id,new_id=new_id)
      else:
        if not id in ids and len(ids)>0:
          old_id = ids[0]
          if _globals.debug( self):
            _globals.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(old_id,id))
          if id not in self.objectIds():
            self.manage_renameObject(id=old_id,new_id=id)


    # --------------------------------------------------------------------------
    #	ObjChildren.initObjChildren
    # --------------------------------------------------------------------------
    def initObjChildren(self, REQUEST):
      if _globals.debug( self):
        _globals.writeLog( self, "[initObjChildren]")
      self.getObjProperty( 'initObjChildren' ,REQUEST)
      metaObj = self.getMetaobj(self.meta_id)
      metaObjIds = self.getMetaobjIds(sort=0)+['*']
      for metaObjAttrId in self.getMetaobjAttrIds( self.meta_id):
        metaObjAttr = self.getMetaobjAttr( self.meta_id, metaObjAttrId)
        if metaObjAttr['type'] in metaObjIds:
           self._initObjChildren( metaObjAttr, REQUEST)


    # --------------------------------------------------------------------------
    #  ObjChildren.getObjChildrenAttr:
    # --------------------------------------------------------------------------
    def getObjChildrenAttr(self, key, meta_type=None):
      meta_type = _globals.nvl(meta_type,self.meta_id)
      ##### Meta-Objects ####
      if meta_type in self.getMetaobjIds(sort=0) and key in self.getMetaobjAttrIds(meta_type):
        obj_attr = self.getMetaobjAttr(meta_type,key)
      ##### Default ####
      else:
        obj_attr = {'id':key,'repetitive':1,'mandatory':0}
      return obj_attr


    # --------------------------------------------------------------------------
    #  ObjChildren.getObjChildren
    # --------------------------------------------------------------------------
    def getObjChildren(self, id, REQUEST, meta_types=None):
      objAttr = self.getObjChildrenAttr(id)
      reid = None
      if id:
        if objAttr.get('repetitive'):
          reid = id+'$'+'|'+id+'\\d+'
        else:
          reid = id
      return self.getChildNodes(REQUEST,meta_types,reid)


    """
    ############################################################################
    ###
    ###  Action-List
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ObjChildren.filtered_container_actions_objChildren:
    #
    #  Object-actions of management interface.
    # --------------------------------------------------------------------------
    def filtered_container_actions_objChildren(self, objAttr, path, REQUEST):
      actions = []
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      #-- Actions.
      repetitive = objAttr.get('repetitive',0)==1
      mandatory = objAttr.get('mandatory',0)==1
      if len(path) > 0:
        if self.getAutocommit() or self.getPrimaryLanguage() == lang or self.getDCCoverage(REQUEST).startswith('local.'):
          actions.append((self.getZMILangStr('BTN_EDIT'),path + 'manage_main'))
          if repetitive or not mandatory and (self.getAutocommit() or self.inObjStates(['STATE_NEW'],REQUEST) or not self.getHistory()):
            if self.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST):
              actions.append((self.getZMILangStr('BTN_UNDO'),'manage_undoObjs'))
            can_delete = not self.inObjStates( [ 'STATE_DELETED'], REQUEST)
            if can_delete:
              ob_access = self.getObjProperty('manage_access',REQUEST)
              can_delete = can_delete and ((not type(ob_access) is dict) or (ob_access.get( 'delete') is None) or (len( self.intersection_list( ob_access.get( 'delete'), self.getUserRoles(auth_user))) > 0))
              metaObj = self.getMetaobj( self.meta_id)
              can_delete = can_delete and ((metaObj.get( 'access') is None) or (metaObj.get( 'access', {}).get( 'delete') is None) or (len( self.intersection_list( metaObj.get( 'access').get( 'delete'), self.getUserRoles(auth_user))) > 0))
            if can_delete:
              actions.append((self.getZMILangStr('BTN_DELETE'),'manage_deleteObjs'))
            actions.append((self.getZMILangStr('BTN_CUT'),'manage_cutObjects'))
          actions.append((self.getZMILangStr('BTN_COPY'),'manage_copyObjects'))
          if repetitive or not mandatory: actions.append((self.getZMILangStr('ACTION_MOVEUP'),path + 'manage_moveObjUp'))
          if repetitive or not mandatory: actions.append((self.getZMILangStr('ACTION_MOVEDOWN'),path + 'manage_moveObjDown'))
      if (repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0) and (self.cb_dataValid()):
        if objAttr['type']=='*':
          meta_ids = objAttr['keys']
        else:
          meta_ids = [objAttr['type']]
        append = True
        try:
          for ob in self.cp_get_obs( REQUEST):
            metaObj = ob.getMetaobj( ob.meta_id)
            append = append and (ob.meta_id in meta_ids or 'type(%s)'%metaObj['type'] in meta_ids)
        except:
          append = False
        if append:
          actions.append((self.getZMILangStr('BTN_PASTE'),'manage_pasteObjs'))
      
      #-- Commands.
      actions.extend(self.filtered_command_actions(path,REQUEST))
      
      #-- Headline.
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('ACTION_SELECT')%self.getZMILangStr('ATTR_ACTION'),''))
      
      #-- Insert.
      if (repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0):
        ob = self
        if len( path) > 0:
          ob = self.getParentNode()
        actions.extend(ob.filtered_insert_actions(path,objAttr))
        
      # Return action list.
      return actions


    ############################################################################
    #  ObjChildren.manage_initObjChild: 
    #
    #  Create object-child.
    ############################################################################
    def manage_initObjChild(self, id, type, lang, REQUEST, RESPONSE=None): 
      """ ObjChildren.manage_initObjChild """
      
      # Create.      
      obj = self.initObjChild(id,self.getNewSortId(),type,REQUEST)
      
      # Return with message.
      if RESPONSE is not None:
        message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
        message = urllib.quote(message)
        target = REQUEST.get('manage_target','%s/manage_main'%obj.id)
        RESPONSE.redirect('%s?lang=%s&manage_tabs_message=%s'%(target,lang,message))

################################################################################
