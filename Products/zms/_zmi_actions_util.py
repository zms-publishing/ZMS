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
from Products.zms import standard

def zmi_actions(container, context, attr_id='e'):
  """
  Returns list of actions.
  """
  actions = []
  
  REQUEST = container.REQUEST
  objAttr = standard.nvl(container.getMetaobjAttr( container.meta_id, attr_id), {})
  objChildren = len(container.getObjChildren(attr_id, REQUEST))
  objPath = ''
  if context is not None and context != container:
    objPath = context.id+'/'
  
  #-- Action: Separator.
  actions.append(('----- %s -----'%container.getZMILangStr('ACTION_SELECT')%container.getZMILangStr('ATTR_ACTION'), 'select-action'))
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
  
  repetitive = objAttr.get('repetitive', 0)==1
  mandatory = objAttr.get('mandatory', 0)==1
  
  #-- Action: Edit.
  if context is not None:
    userdef_roles = list(container.getRootElement().aq_parent.userdefined_roles())+list(container.getRootElement().userdefined_roles())
    user_roles = [x for x in context.getUserRoles(auth_user, resolve=False) if x in userdef_roles]
    can_edit = True
    constraints = context.attr('check_constraints')
    if isinstance(constraints, dict) and 'RESTRICTIONS' in constraints:
      for restriction in constraints.get('RESTRICTIONS'):
        permissions = restriction[2]
        for permission in permissions:
          can_edit = auth_user.has_permission(permission, context)
          if not can_edit:
            break
    if can_edit:
      actions.append((container.getZMILangStr('BTN_EDIT'), objPath+'manage_main', 'fas fa-pencil-alt'))
    if context.getLevel() > 0:
      if repetitive or not mandatory:
        #-- Action: Undo.
        can_undo = context.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST)
        if can_undo:
          actions.append((container.getZMILangStr('BTN_UNDO'), 'manage_undoObjs', 'fas fa-undo'))
        #-- Action: Delete.
        if not objAttr:
          actions.append((container.getZMILangStr('BTN_DELETE'), 'manage_eraseObjs', 'fas fa-times'))
        else:
          can_delete = not context.inObjStates( [ 'STATE_DELETED'], REQUEST) and context.getAutocommit() or context.getDCCoverage(REQUEST).endswith('.'+lang)
          if can_delete:
            ob_access = context.getObjProperty('manage_access', REQUEST)
            can_delete = can_delete and ((not isinstance(ob_access, dict)) or (ob_access.get( 'delete') is None) or (len( standard.intersection_list( ob_access.get( 'delete'), user_roles)) > 0))
            metaObj = container.getMetaobj( context.meta_id)
            mo_access = metaObj.get('access', {})
            mo_access_deny = mo_access.get('delete_deny', [])
            can_delete = can_delete and len([x for x in user_roles if x not in mo_access_deny]) > 0
            can_delete = can_delete or auth_user.has_role('Manager')
          if can_delete:
            actions.append((container.getZMILangStr('BTN_DELETE'), 'manage_deleteObjs', 'fas fa-trash-alt'))
        #-- Action: Cut.
        can_cut = not context.inObjStates( [ 'STATE_DELETED'], REQUEST) and context.getAutocommit() or context.getDCCoverage(REQUEST).endswith('.'+lang)
        if can_cut:
          actions.append((container.getZMILangStr('BTN_CUT'), 'manage_cutObjects', 'fas fa-cut')) 
      #-- Action: Copy.
      can_copy = context.getParentByLevel(1).meta_id!='ZMSTrashcan'
      if can_copy: 
        actions.append((container.getZMILangStr('BTN_COPY'), 'manage_copyObjects', 'fas fa-copy'))
      #-- Actions: Move.
      can_move = objChildren > 1
      if can_move:
        actions.append((container.getZMILangStr('ACTION_MOVEUP'), objPath+'manage_moveObjUp', 'fas fa-angle-up'))
        actions.append((container.getZMILangStr('ACTION_MOVEDOWN'), objPath+'manage_moveObjDown', 'fas fa-angle-down'))
  
  #-- Action: Paste.
  if repetitive or objChildren==0:
    if container.cb_dataValid():
      if objAttr['type']=='*':
        meta_ids = objAttr['keys']
      else:
        meta_ids = [objAttr['type']]
      append = True
      # dynamic list of types
      if standard.dt_executable('\n'.join(meta_ids)):
        meta_ids = standard.dt_exec(container,'\n'.join(meta_ids))
      try:
        for ob in container.cp_get_obs( REQUEST):
          metaObj = ob.getMetaobj( ob.meta_id)
          append = append and (ob.meta_id in meta_ids or 'type(%s)'%metaObj['type'] in meta_ids)
      except:
        append = False
      if append:
        actions.append((container.getZMILangStr('BTN_PASTE'), 'manage_pasteObjs', 'fas fa-paste'))
  
  #-- Custom Commands.
  actions.extend(zmi_command_actions(context, stereotype='', objPath=objPath))
  
  # Return action list.
  return actions


def zmi_insert_actions(container, context, objAttr, objChildren, objPath=''):
  """
  Returns sorted list of insert actions. 
  """
  actions = []
  if not objAttr:
    return actions
  
  REQUEST = container.REQUEST
  auth_user = REQUEST['AUTHENTICATED_USER']
  absolute_url = '/'.join(list(container.getPhysicalPath())+[''])
  userdef_roles = list(container.getRootElement().aq_parent.userdefined_roles())+list(container.getRootElement().userdefined_roles())
  user_roles = [x for x in container.getUserRoles(auth_user, resolve=False) if x in userdef_roles]
  
  repetitive = objAttr.get('repetitive', 0)==1
  mandatory = objAttr.get('mandatory', 0)==1
  
  #-- Objects.
  if repetitive or len(container.getObjChildren(objAttr['id'], REQUEST))==0:
    metaObjIds = container.getMetaobjIds(sort=True)
    meta_ids = []
    if objAttr['type']=='*':
      # get types
      meta_keys = objAttr['keys']
      # dynamic list of types
      if standard.dt_executable('\n'.join(meta_keys)):
        meta_keys = standard.dt_exec(container, '\n'.join(meta_keys))
      # typed meta-ids (resolves type(ZMS...))
      meta_ids = container.getMetaobjManager().getTypedMetaIds(meta_keys)
    else:
      meta_ids.append( objAttr['type'])
    for meta_id in meta_ids:
      metaObj = container.getMetaobj(meta_id)
      ob_access = True
      ob_manage_access = container.getMetaobjAttr(meta_id, 'manage_access')
      if ob_manage_access is not None:
        try:
          ob_access = standard.dt_exec(container, ob_manage_access['custom'])
        except:
          standard.writeError(container, '[zmi_insert_actions]: can\'t get manage_access from %s'%meta_id)
      can_insert = True
      if objAttr['type']=='*':
        can_insert = can_insert and ((not isinstance(ob_access, dict)) or (ob_access.get( 'insert') is None) or (len( standard.intersection_list( ob_access.get( 'insert'), user_roles)) > 0))
        mo_access = metaObj.get('access', {})
        mo_access_deny = mo_access.get('insert_deny', [])
        can_insert = can_insert and len([x for x in user_roles if x not in mo_access_deny]) > 0
        can_insert = can_insert or auth_user.has_role('Manager')
        mo_access_insert_nodes = standard.string_list(mo_access.get('insert_custom', '{$}'))
        sl = []
        for x in mo_access_insert_nodes:
          if x.find('@')<0:
            si = (container.getHome().id+'/content/'+x[2:-1]+'/').replace('//', '/')
          else:
            si = (x[2:-1].replace('@', '/content/')+'/').replace('//', '/')
          sl.append(si)
        can_insert = can_insert and len([x for x in sl if absolute_url.find(x)>=0]) > 0
      if can_insert:
        if meta_id in container.dGlobalAttrs and 'constructor' in container.dGlobalAttrs[meta_id]:
          value = 'manage_addProduct/zms/%s'%container.dGlobalAttrs[meta_id]['constructor']
        elif metaObj['type']=='ZMSModule':
          value = 'manage_addZMSModule'
        elif objAttr['type'] in meta_ids and repetitive and objAttr.get('custom'):
          value = 'manage_addZMSCustomDefault'
        else:
          value = 'manage_addProduct/zms/manage_addzmscustomform'
        tooltip_key = '%s.TOOLTIP'%meta_id
        tooltip_val = context.getLangStr(tooltip_key)
        tooltip_val = tooltip_val if tooltip_val != tooltip_key else meta_id
        icon_clazz = container.display_icon(meta_id=meta_id)
        action = (meta_id, container.display_type(meta_id=meta_id), value, icon_clazz, meta_id, tooltip_val)
        if action not in actions:
          actions.append( action)
  
  #-- Insert Commands.
  actions.extend(zmi_command_actions(container, stereotype='insert'))
  
  #-- Pre-Sort by display-label.
  actions.sort(key=lambda x: x[1])
  actions = [[len(actions)+actions.index(x)]+list(x) for x in actions]
  #-- Sort by custom-sort-id.
  def get_sort(x):
    sort_key = '%s.SORT'%x[1]
    # Default sort value is display-label
    sort_val = x[0]
    # If SORT key (integer!) found, use it.
    if context.getLangStr(sort_key) != sort_key:
      try:
        sort_val = int(context.getLangStr(sort_key))
      except:
        pass
    return sort_val
  actions = [[get_sort(x)]+x[2:] for x in actions]
  actions.sort()
  actions = [tuple(x[1:]) for x in actions]
  
  #-- Headline.
  if len(actions) > 0:
    actions.insert(0, ('----- %s -----'%container.getZMILangStr('ACTION_INSERT')%container.display_type(REQUEST), 'insert-action'))
  
  # Return action list.
  return actions


def zmi_command_actions(context, stereotype='', objPath=''):
  """
  Returns list of custom commands.
  """
  actions = []
  
  #-- Context Commands.
  if context is not None:
    for metaCmd in [x for x in context.getMetaCmds(context, stereotype) if x['stereotype']==stereotype]:
      action = (metaCmd['id'], metaCmd['name'], metaCmd['action'].replace('%s',objPath),metaCmd.get('icon_clazz','fas fa-cog'),metaCmd['id'],metaCmd.get('title'))
      actions.append(action)
  
  #-- Sort.
  actions.sort()
  
  # Return sorted action list
  return actions

################################################################################