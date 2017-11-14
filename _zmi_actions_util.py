# -*- coding: utf-8 -*- 
################################################################################
# _zmi_actions_util.py
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

# Product imports.
import standard

def zmi_actions(container, context, attr_id='e'):
  """
  Returns list of actions.
  """
  actions = []
  
  REQUEST = container.REQUEST
  objAttr = standard.nvl(container.getMetaobjAttr( container.meta_id, attr_id),{})
  objChildren = len(container.getObjChildren(attr_id,REQUEST))
  objPath = ''
  if context is not None and context != container:
    objPath = context.id+'/'
  
  #-- Action: Separator.
  actions.append(('----- %s -----'%container.getZMILangStr('ACTION_SELECT')%container.getZMILangStr('ATTR_ACTION'),'select-action'))
  actions.extend(zmi_basic_actions(container, context, objAttr, objChildren, objPath))
  actions.extend(zmi_insert_actions(container, context, objAttr, objChildren, objPath))
  
  # Return action list.
  return actions


def zmi_basic_actions(container, context, objAttr, objChildren, objPath=''):
  """
  Returns sorted list of basic actions (undo, delete, cut, copy, paste, 
  move up/down) and custom commands.
  """
  actions = []
  
  REQUEST = container.REQUEST
  lang = REQUEST['lang']
  auth_user = REQUEST['AUTHENTICATED_USER']
  
  repetitive = objAttr.get('repetitive',0)==1
  mandatory = objAttr.get('mandatory',0)==1
  
  #-- Action: Edit.
  if context is not None:
    userdef_roles = list(container.getRootElement().aq_parent.userdefined_roles())+list(container.getRootElement().userdefined_roles())
    user_roles = filter(lambda x: x in userdef_roles,context.getUserRoles(auth_user,resolve=False))
    can_edit = True
    constraints = context.attr('check_constraints')
    if type(constraints) is dict and 'RESTRICTIONS' in constraints.keys():
      for restriction in constraints.get('RESTRICTIONS'):
        permissions = restriction[2]
        for permission in permissions:
          can_edit = auth_user.has_permission(permission,context)
          if not can_edit:
            break
    if can_edit:
      actions.append((container.getZMILangStr('BTN_EDIT'),objPath+'manage_main','icon-edit'))
    if context.getLevel() > 0:
      if repetitive or not mandatory:
        #-- Action: Undo.
        can_undo = context.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST)
        if can_undo:
          actions.append((container.getZMILangStr('BTN_UNDO'),'manage_undoObjs','icon-undo'))
        #-- Action: Delete.
        if not objAttr.keys():
          actions.append((container.getZMILangStr('BTN_DELETE'),'manage_eraseObjs','icon-trash'))
        else:
          can_delete = not context.inObjStates( [ 'STATE_DELETED'], REQUEST) and context.getAutocommit() or context.getDCCoverage(REQUEST).endswith('.'+lang)
          if can_delete:
            ob_access = context.getObjProperty('manage_access',REQUEST)
            can_delete = can_delete and ((not type(ob_access) is dict) or (ob_access.get( 'delete') is None) or (len( standard.intersection_list( ob_access.get( 'delete'), user_roles)) > 0))
            metaObj = container.getMetaobj( context.meta_id)
            mo_access = metaObj.get('access',{})
            mo_access_deny = mo_access.get('delete_deny',[])
            can_delete = can_delete and len(filter(lambda x: x not in mo_access_deny, user_roles)) > 0
            can_delete = can_delete or auth_user.has_role('Manager')
          if can_delete:
            actions.append((container.getZMILangStr('BTN_DELETE'),'manage_deleteObjs','icon-trash'))
        #-- Action: Cut.
        can_cut = not context.inObjStates( [ 'STATE_DELETED'], REQUEST) and context.getAutocommit() or context.getDCCoverage(REQUEST).endswith('.'+lang)
        if can_cut:
          actions.append((container.getZMILangStr('BTN_CUT'),'manage_cutObjects','icon-cut')) 
      #-- Action: Copy.
      actions.append((container.getZMILangStr('BTN_COPY'),'manage_copyObjects','icon-copy'))
      #-- Actions: Move.
      can_move = objChildren > 1
      if can_move:
        actions.append((container.getZMILangStr('ACTION_MOVEUP'),objPath+'manage_moveObjUp','icon-double-angle-up'))
        actions.append((container.getZMILangStr('ACTION_MOVEDOWN'),objPath+'manage_moveObjDown','icon-double-angle-down'))
  
  #-- Action: Paste.
  if repetitive or objChildren==0:
    if container.cb_dataValid():
      if objAttr['type']=='*':
        meta_ids = objAttr['keys']
      else:
        meta_ids = [objAttr['type']]
      # dynamic list of types
      if standard.dt_executable(container,'\n'.join(meta_ids)):
        meta_ids = standard.dt_exec(container,'\n'.join(meta_ids))
      append = True
      try:
        for ob in container.cp_get_obs( REQUEST):
          metaObj = ob.getMetaobj( ob.meta_id)
          append = append and (ob.meta_id in meta_ids or 'type(%s)'%metaObj['type'] in meta_ids)
      except:
        append = False
      if append:
        actions.append((container.getZMILangStr('BTN_PASTE'),'manage_pasteObjs','icon-paste'))
  
  #-- Custom Commands.
  actions.extend(zmi_command_actions(context, stereotype='', objPath=objPath))
  
  # Return action list.
  return actions


def zmi_insert_actions(container, context, objAttr, objChildren, objPath=''):
  """
  Returns sorted list of insert actions. 
  """
  actions = []
  if not objAttr.keys():
    return actions
  
  REQUEST = container.REQUEST
  auth_user = REQUEST['AUTHENTICATED_USER']
  absolute_url = '/'.join(list(container.getPhysicalPath())+[''])
  userdef_roles = list(container.getRootElement().aq_parent.userdefined_roles())+list(container.getRootElement().userdefined_roles())
  user_roles = filter(lambda x: x in userdef_roles,container.getUserRoles(auth_user,resolve=False))
  
  repetitive = objAttr.get('repetitive',0)==1
  mandatory = objAttr.get('mandatory',0)==1
  
  #-- Objects.
  if repetitive or len(container.getObjChildren(objAttr['id'],REQUEST))==0:
    metaObjIds = container.getMetaobjIds(sort=True)
    meta_ids = []
    if objAttr['type']=='*':
      # get types
      meta_keys = objAttr['keys']
      # dynamic list of types
      if standard.dt_executable(container,'\n'.join(meta_keys)):
        meta_keys = standard.dt_exec(container,'\n'.join(meta_keys))
      # iterate types
      metaobj_manager = container.getMetaobjManager()
      for meta_id in meta_keys:
        if meta_id.startswith('type(') and meta_id.endswith(')'):
          for metaObjId in metaObjIds:
            metaObj = metaobj_manager.getMetaobj( metaObjId,aq_attrs=['enabled'])
            if metaObj['type'] == meta_id[5:-1] and metaObj['enabled'] == 1:
              meta_ids.append( metaObj['id'])
        elif meta_id in metaObjIds:
          meta_ids.append( meta_id)
        else:
          container.writeError( '[zmi_insert_actions]: %s.%s contains invalid meta_id \'%s\''%(container.meta_id,objAttr['id'],meta_id))
    else:
      meta_ids.append( objAttr['type'])
    for meta_id in meta_ids:
      metaObj = container.getMetaobj(meta_id)
      ob_access = True
      ob_manage_access = container.getMetaobjAttr(meta_id,'manage_access')
      if ob_manage_access is not None:
        try:
          ob_access = standard.dt_exec(container,ob_manage_access['custom'])
        except:
          standard.writeError(container,'[zmi_insert_actions]: can\'t get manage_access from %s'%meta_id)
      can_insert = True
      if objAttr['type']=='*':
        can_insert = can_insert and ((type(ob_access) is not dict) or (ob_access.get( 'insert') is None) or (len( standard.intersection_list( ob_access.get( 'insert'), user_roles)) > 0))
        mo_access = metaObj.get('access',{})
        mo_access_deny = mo_access.get('insert_deny',[])
        can_insert = can_insert and len(filter(lambda x: x not in mo_access_deny, user_roles)) > 0
        can_insert = can_insert or auth_user.has_role('Manager')
        mo_access_insert_nodes = standard.string_list(mo_access.get('insert_custom','{$}'))
        sl = []
        sl.extend(map( lambda x: (container.getHome().id+'/content/'+x[2:-1]+'/').replace('//','/'),filter(lambda x: x.find('@')<0,mo_access_insert_nodes)))
        sl.extend(map( lambda x: (x[2:-1].replace('@','/content/')+'/').replace('//','/'),filter(lambda x: x.find('@')>0,mo_access_insert_nodes)))
        can_insert = can_insert and len( filter( lambda x: absolute_url.find(x)>=0, sl)) > 0
      if can_insert:
        if meta_id in container.dGlobalAttrs.keys() and container.dGlobalAttrs[meta_id].has_key('constructor'):
          value = 'manage_addProduct/zms/%s'%container.dGlobalAttrs[meta_id]['constructor']
        elif metaObj['type']=='ZMSModule':
          value = 'manage_addZMSModule'
        elif objAttr['type'] in meta_ids and repetitive and objAttr.get('custom'):
          value = 'manage_addZMSCustomDefault'
        else:
          value = 'manage_addProduct/zms/manage_addzmscustomform'
        action = (container.display_type(REQUEST,meta_id),value,container.display_icon(REQUEST,meta_id))
        if action not in actions:
          actions.append( action)
  
  #-- Insert Commands.
  actions.extend(zmi_command_actions(container, stereotype='insert'))
  
  #-- Sort.
  actions.sort()
  
  #-- Headline.
  if len(actions) > 0:
    actions.insert(0,('----- %s -----'%container.getZMILangStr('ACTION_INSERT')%container.display_type(REQUEST),'insert-action'))
  
  # Return action list.
  return actions


def zmi_command_actions(context, stereotype='', objPath=''):
  """
  Returns list of custom commands.
  """
  actions = []
  
  #-- Context Commands.
  if context is not None:
    for metaCmd in filter(lambda x:x['stereotype']==stereotype,context.getMetaCmds(context,stereotype)):
      l = [metaCmd['name'],objPath+'manage_executeMetacmd?id='+metaCmd['id']]
      if metaCmd.get('icon_clazz'):
        l.append(metaCmd.get('icon_clazz'))
      if metaCmd.get('title'):
        l.append(metaCmd.get('title'))
      actions.append(tuple(l))
  
  #-- Sort.
  actions.sort()
  
  # Return sorted action list
  return actions

################################################################################