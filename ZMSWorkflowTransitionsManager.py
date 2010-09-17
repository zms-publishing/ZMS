################################################################################
# ZMSWorkflowTransitionsManager.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
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
import sys
import time
# Product Imports.
import _globals


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSWorkflowTransitionsManager:

  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  ZMSWorkflowTransitionsManager.setTransition
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def setTransition(self, id, newId, newName, newFrom, newTo, newPerformer=[], newDtml=''):
    message = ''
    obs = self.transitions
    # Remove exisiting entry.
    if id in obs:
      i = obs.index(id)
      del obs[i] 
      del obs[i] 
    else: 
      i = len(obs)
    if len(newTo) == 0:
      newTo = []
    elif type(newTo) is str:
      newTo = [newTo]
    # Parse Dtml.
    message = _globals.dt_parse(self,newDtml)
    if len( message) > 0:
      message = '<div style="color:red; background-color:yellow; ">%s</div>'%message
    # Values.
    newValues = {}
    newValues['name'] = newName
    newValues['from'] = newFrom
    newValues['to'] = newTo
    newValues['performer'] = newPerformer
    newValues['dtml'] = newDtml
    for obj_id in [str(id),str(newId)]:
      if obj_id in self.objectIds():
        self.manage_delObjects([obj_id])
    self.manage_addDTMLMethod(newId,newName,newDtml)
    # Update attribute.
    obs.insert(i,newValues)
    obs.insert(i,newId)
    self.transitions = copy.copy(obs)
    # Return with message.
    return message


  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  ZMSWorkflowTransitionsManager.getTransitions
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def getTransitions(self):
    obs = self.transitions
    transitions = []
    for i in range(len(obs)/2):
      id = obs[i*2]
      transition = obs[i*2+1].copy()
      transition['id'] = id
      transitions.append(transition)
    return transitions


  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  ZMSWorkflowTransitionsManager.getTransitionIds
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def getTransitionIds(self):
    obs = self.getTransitions()
    return map(lambda x: x['id'], obs) 


  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  ZMSWorkflowTransitionsManager.getTransition
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def getTransition(self, id):
    transition = filter(lambda x: x['id']==id, self.getTransitions())[0]
    transition = copy.deepcopy(transition)
    transition['dtml'] = getattr(self,transition['id']).raw
    return transition


  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  ZMSWorkflowTransitionsManager.manage_changeTransitions:
  """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def manage_changeTransitions(self, lang, btn='', REQUEST=None, RESPONSE=None):
    """ ZMSWorkflowTransitionsManager.manage_changeTransitions """
    message = ''
    id = REQUEST.get('id','')
    
    # Change.
    # -------
    if btn == self.getZMILangStr('BTN_SAVE'):
      item = self.getTransition(id)
      newId = REQUEST.get('inpId').strip()
      newName = REQUEST.get('inpName').strip()
      newFrom = REQUEST.get('inpFrom')
      newTo = REQUEST.get('inpTo')
      newPerformer = REQUEST.get('inpPerformer',[])
      newDtml = REQUEST.get('inpDtml','').strip()
      message += self.setTransition(self, item.get('id',None), newId, newName, newFrom, newTo, newPerformer, newDtml)
      message += self.getZMILangStr('MSG_CHANGED')
      id = newId
    
    # Delete.
    # -------
    elif btn in ['delete',self.getZMILangStr('BTN_DELETE')]:
      id = self.delItem(id, 'transitions')
      message = self.getZMILangStr('MSG_CHANGED')
    
    # Insert.
    # -------
    elif btn == self.getZMILangStr('BTN_INSERT'):
      item = {}
      newId = REQUEST.get('newId').strip()
      newName = REQUEST.get('newName').strip()
      newFrom = REQUEST.get('newFrom',[])
      newTo = REQUEST.get('newTo',[])
      newPerformer = REQUEST.get('newPerformer',[])
      newDtml = REQUEST.get('newDtml','').strip()
      message += self.setTransition(self, item.get('id',None), newId, newName, newFrom, newTo, newPerformer, newDtml)
      message += self.getZMILangStr('MSG_INSERTED')%id
      id = newId
    
    # Move to.
    # --------
    elif btn == 'move_to':
      pos = REQUEST['pos']
      self.moveItem(id, pos, 'transitions')
      message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%id),(pos+1))
      id = ''
    
    # Return with message.
    message = urllib.quote(message)
    return RESPONSE.redirect('manage_main?id=%s&lang=%s&manage_tabs_message=%s#_Transitions'%(id,lang,message))

################################################################################
