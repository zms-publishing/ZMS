################################################################################
# _versionmanager.py
#
# $Id: _versionmanager.py,v 1.12 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.12 $
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
from Globals import HTMLFile
import copy
import operator
import sys
import time
import urllib
# Product Imports.
import _globals 
import _blobfields 
import _workflowmanager
import _zmsattributecontainer


# ------------------------------------------------------------------------------
#  _versionmanager.triggerEvent:
#
#  Hook for trigger of custom event (if there is one)
# ------------------------------------------------------------------------------
def triggerEvent(self, name, REQUEST):
  metaObjAttr = self.getMetaobjAttr(self.meta_id,name)
  if metaObjAttr is not None:
    try: REQUEST.set('preview','preview')
    except: REQUEST['preview'] = 'preview'
    v = self.getObjProperty(name,REQUEST)
  ob = self
  ob_ids = []
  while ob is not None:
    for ob_id in ob.getHome().objectIds():
      if ob_id not in ob_ids and ob_id.find( name) == 0:
        try: REQUEST.set('preview','preview')
        except: REQUEST['preview'] = 'preview'
        v = getattr(self,ob_id)(context=self,REQUEST=REQUEST)
        ob_ids.append(ob_id)
    ob = ob.getPortalMaster()


# ------------------------------------------------------------------------------
#  _versionmanager.getObjStates:
#
#  Returns a list of object-states (including language suffixes).
# ------------------------------------------------------------------------------
def getObjStates(self):
  # Get object-states.
  if not hasattr(self,'__work_state__'):
    self.__work_state__ = _globals.MyClass()
  states = getattr(self.__work_state__,'states',[])
  # Make object-states unique.
  d = {}
  map(lambda x: operator.setitem(d, x, None), states)
  states = d.keys()
  # Return object-states.
  return states


# ------------------------------------------------------------------------------
#  _versionmanager.setChangedBy:
#
#  Applies information about user-id and date of change.
# ------------------------------------------------------------------------------
def setChangedBy(self, REQUEST, createWorkAttrCntnr=True):
  prim_lang = self.getPrimaryLanguage()
  lang = REQUEST.get('lang',prim_lang)
  auth_user = REQUEST.get('AUTHENTICATED_USER',None)
  if auth_user is not None:
    #-- Create new work-version.
    if createWorkAttrCntnr:
      has_version_work = self.version_work_id is not None and self.version_work_id != self.version_live_id and hasattr( self, self.version_work_id)
      has_version_live = self.version_live_id is not None and hasattr( self, self.version_live_id)
      if has_version_work:
        oldAttrCntnr = getattr( self, self.version_work_id)
      elif has_version_live:
        oldAttrCntnr = getattr( self, self.version_live_id)
      if ((lang == prim_lang or self.getDCCoverage(REQUEST).find('.%s'%lang) > 0) and self.getHistory()) or not has_version_work:
        request = {'lang':'*'}
        newAttrCntnr = _zmsattributecontainer.manage_addZMSAttributeContainer(self)
        if _globals.debug( self):
          _globals.writeLog( self, "[setChangedBy]: Create new work-version: %s"%newAttrCntnr.id)
        self.cloneObjAttrs(oldAttrCntnr,newAttrCntnr,request)
        self.version_work_id = newAttrCntnr.id
      #-- Set minor-version.
      if ((lang == prim_lang or self.getDCCoverage(REQUEST).find('.%s'%lang) > 0) and self.getHistory()) or not has_version_work:
        minor_version = self.getObjProperty( 'minor_version', REQUEST) + 1
        self.setObjProperty( 'minor_version' ,minor_version, lang)
        if _globals.debug( self):
          _globals.writeLog( self, "[setChangedBy]: Set minor-version: %i"%minor_version)
    #-- Set properties.
    self.setObjProperty( 'change_uid' ,str(auth_user) ,lang)
    self.setObjProperty( 'change_dt' ,_globals.getDateTime( time.time()) ,lang)


# ------------------------------------------------------------------------------
#  _versionmanager.setCreatedBy:
#
#  Applies information about user-id and date of creation.
# ------------------------------------------------------------------------------
def setCreatedBy(self, REQUEST):
  auth_user = REQUEST.get('AUTHENTICATED_USER',None)
  if auth_user is not None:
    #-- Set properties.
    if _globals.debug( self):
      _globals.writeLog( self, "[setCreatedBy]: Set created by: %s"%str(auth_user))
    self.setObjProperty( 'created_uid' ,str(auth_user))
    self.setObjProperty( 'created_dt' ,_globals.getDateTime( time.time()))


# ------------------------------------------------------------------------------
#  _versionmanager.getObjStateName:
#
#  Returns name object state in given language.
# ------------------------------------------------------------------------------
def getObjStateName(obj_state, lang):
  obj_state_name = obj_state
  if lang is not None:
    obj_state_name += '_'+lang.upper()
  return obj_state_name


# ------------------------------------------------------------------------------
#  _versionmanager.doAutocommit:
#
#  Commit pending changes of all objects.
# ------------------------------------------------------------------------------
def doAutocommit(self, REQUEST): 
  
  ##### Auto-Commit ####
  if len( getObjStates( self)) > 0:
    
    if self.inObjStates(['STATE_DELETED'],REQUEST):
       parent = self.getParentNode()
       parent.moveObjsToTrashcan([self.id], REQUEST)
       return
    
    if self.version_work_id is not None:
      if self.version_live_id is not None and \
         self.version_live_id in self.objectIds( self.dGlobalAttrs.keys()):
        ids = [ self.version_live_id]
        self.manage_delObjects( ids=ids)
      self.version_live_id = self.version_work_id
      self.version_work_id = None
    self.initializeWorkVersion()
  
  ##### Process child-objects ####
  for ob in self.getChildNodes():
    doAutocommit( ob, REQUEST)


################################################################################
################################################################################
###
###   class VersionItem
###
################################################################################
################################################################################
class VersionItem: 

    # Management Interface.
    # ---------------------
    version_object_state = HTMLFile('dtml/versionmanager/version_object_state', globals())


    # --------------------------------------------------------------------------
    #  VersionItem.tagObjVersions:
    #
    #  Tag object-versions.
    # --------------------------------------------------------------------------
    def tagObjVersions(self, master_version, REQUEST, checkPending=None):
      if _globals.debug( self): 
        _globals.writeLog( self, "[tagObjVersions]")
      count = 1
      if checkPending is None:
        self.tagObjVersions( master_version, REQUEST, checkPending=True)
        self.tagObjVersions( master_version, REQUEST, checkPending=False)
      else:
        if checkPending:
          #-- Check for pending changes.
          if self.getObjStateNames(REQUEST):
            raise "Can't tagObjVersions: %s@%s has pending changes %s"%(self.meta_id,self.absolute_url(),str(self.getObjStateNames(REQUEST)))
        else:
          #-- Tag master-version.
          obj_version = None
          if obj_version is None and self.version_live_id is not None and hasattr( self, self.version_live_id):
            obj_version = getattr( self, self.version_live_id)
          if obj_version is None and self.version_work_id is not None and hasattr( self, self.version_work_id):
            obj_version = getattr( self, self.version_work_id)
          if 'change_history' in self.getObjAttrs().keys():
            change_history = []
            record = {}
            record[ 'version_dt'] = _globals.getDateTime( time.time())
            record[ 'version_uid'] = str( REQUEST.get( 'AUTHENTICATED_USER'))
            record[ 'master_version'] = master_version
            record[ 'major_version'] = 0
            change_history.append( record)
            setattr( obj_version, 'change_history', change_history)
          setattr( obj_version, 'master_version', master_version)
          setattr( obj_version, 'major_version', 0)
          setattr( obj_version, 'minor_version', 0)
          self.version_live_id = obj_version.id
          self.version_work_id = None
          ids = []
          for obj_version in self.getObjVersions():
            if obj_version.id != self.version_live_id:
              ids.append( obj_version.id)
          self.manage_delObjects( ids=ids)
        #-- Recursion.
        for ob in self.getChildNodes():
          count += ob.tagObjVersions( master_version, REQUEST, checkPending)
      return count


    """
    ############################################################################
    #  Workflow
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.getWfStates
    # --------------------------------------------------------------------------
    def getWfStates(self, REQUEST):
      states = getObjStates(self)
      lang = REQUEST.get('lang',None)
      obj_states = []
      wfActivitiesIds = self.getWfActivitiesIds()
      for obj_state in wfActivitiesIds:
        obj_state_name = getObjStateName(obj_state,lang)
        if obj_state_name in states:
          obj_states.append(obj_state)
      if len( obj_states) == 0 and \
         len( wfActivitiesIds) > 0 and \
         lang is not None and \
        ( 'STATE_NEW_%s'%lang.upper() in states or \
          'STATE_MODIFIED_%s'%lang.upper() in states or \
          'STATE_DELETED_%s'%lang.upper() in states):
        obj_states.append( wfActivitiesIds[0])
      return obj_states


    # --------------------------------------------------------------------------
    #  VersionItem.getVersionItems
    #  
    #  Returns all version-items.
    # --------------------------------------------------------------------------
    def getVersionItems(self, REQUEST, recursive=False):
      pc = self.isPageContainer()
      children = []
      types = self.getMetaobjIds(sort=0)+['*']
      for metaobjAttrId in self.getMetaobjAttrIds( self.meta_id, types=types):
        for child in self.getObjChildren( metaobjAttrId , REQUEST):
          if recursive or not pc or not child.isPage():
            children.append( child)
            if not pc:
              children.extend( child.getVersionItems( REQUEST, recursive=True))
      return children


    # --------------------------------------------------------------------------
    #  VersionItem.isObjModified:
    #
    #  Returns true if version-item is modified, false otherwise.
    # --------------------------------------------------------------------------
    def isObjModified(self, REQUEST):
      return self.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST)


    # --------------------------------------------------------------------------
    #  VersionItem.hasObjModifiedChildren:
    #
    #  Returns true if object has modified children, false otherwise.
    # --------------------------------------------------------------------------
    def hasObjModifiedChildren(self, REQUEST):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'hasObjModifiedChildren'
      try:
        rtnVal = self.fetchReqBuff( reqBuffId, REQUEST)
        return rtnVal
      except:
        
        rtnVal = False
        for child in self.getVersionItems( REQUEST):
          if child.isObjModified(REQUEST):
            rtnVal = True
          else:
            rtnVal = child.hasObjModifiedChildren( REQUEST)
          if rtnVal:
            break
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, rtnVal, REQUEST)


    # --------------------------------------------------------------------------
    #  VersionItem.resetObjTranslation:
    #
    #  Resets translation.
    # --------------------------------------------------------------------------
    def resetObjTranslation(self):
      prim_lang = self.getPrimaryLanguage()
      for ob in self.getObjVersions():
        for lang in self.getLangIds():
          if lang != prim_lang:
            setattr(ob,'change_uid_%s'%lang,'')


    # --------------------------------------------------------------------------
    #  VersionItem.initializeWorkVersion:
    #
    #  Initializes work-version of object-attributes.
    # --------------------------------------------------------------------------
    def initializeWorkVersion(self):
      # States.
      self.__work_state__ = _globals.MyClass()
      # Create new work-version.
      if len(self.objectValues(['ZMSAttributeContainer']))==0:
        newAttrCntnr = _zmsattributecontainer.manage_addZMSAttributeContainer(self)
        if _globals.debug( self):
          _globals.writeLog( self, "[initializeWorkVersion]: Create new work-version: %s"%newAttrCntnr.id)
        self.version_work_id = newAttrCntnr.id
        self.version_live_id = None


    # --------------------------------------------------------------------------
    #  VersionItem.isCommitted:
    #
    #  Checks if object can by displayed.
    # --------------------------------------------------------------------------
    def isCommitted(self, REQUEST):
      if _globals.isPreviewRequest( REQUEST):
        committed = not self.inObjStates( [ 'STATE_DELETED'], REQUEST)
      else:
        committed = not self.inObjStates( [ 'STATE_NEW'], REQUEST)
      return committed


    """
    ############################################################################
    #  API object-state
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.setObjState:
    #
    #  Sets object-state.
    # --------------------------------------------------------------------------
    def setObjState(self, obj_state, lang):
      state = getObjStateName(obj_state,lang)
      states = getObjStates(self)
      if not state in states:
        states.append(state)
      self.__work_state__.states = copy.deepcopy(states)
      self.__work_state__ = copy.deepcopy(self.__work_state__)

    # --------------------------------------------------------------------------
    #  VersionItem.delObjStates:
    #
    #  Deletes object-state of this object.
    # --------------------------------------------------------------------------
    def delObjStates(self, obj_states=[], REQUEST={}):
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      states = getObjStates(self)
      for obj_state in obj_states:
        while obj_state in states:
          del states[states.index(obj_state)]
        while getObjStateName(obj_state,lang) in states:
          del states[states.index(getObjStateName(obj_state,lang))]
      self.__work_state__.states = copy.deepcopy(states)
      self.__work_state__ = copy.deepcopy(self.__work_state__)


    # --------------------------------------------------------------------------
    #  VersionItem.resetObjStates:
    #
    #  Resets object-state of this object.
    # --------------------------------------------------------------------------
    def resetObjStates(self, REQUEST=None):
      if REQUEST is None:
        self.version_live_id = self.version_work_id
        self.version_work_id = None
        self.__work_state__.states = []
        self.__work_state__ = copy.deepcopy(self.__work_state__)
      else:
        self.delObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST)


    # --------------------------------------------------------------------------
    #  VersionItem.inObjStates:
    #
    #  Checks if given states are in object-states of this object.
    # --------------------------------------------------------------------------
    def inObjStates(self, obj_states, REQUEST):
      states = getObjStates(self)
      states.extend(self.getObjStateNames(REQUEST))
      if len(states) > 0:
        prim_lang = self.getPrimaryLanguage()
        lang = REQUEST.get('lang',prim_lang)
        for obj_state in obj_states:
          obj_state_name = getObjStateName( obj_state, lang)
          if obj_state_name in states:
            return True
      return False


    # --------------------------------------------------------------------------
    #  VersionItem.filteredObjStates:
    #
    #  Checks if given states are in object-states of this object.
    # --------------------------------------------------------------------------
    def filteredObjStates(self, REQUEST):
      obj_states = []
      states = getObjStates(self)
      if len(states) > 0:
        lang = REQUEST.get('lang',self.getPrimaryLanguage())
        for obj_state in [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED']:
          obj_state_name = getObjStateName(obj_state,lang)
          if obj_state_name in states:
            obj_states.append( obj_state)
      return obj_states


    # --------------------------------------------------------------------------
    #  VersionItem.getObjStateNames:
    #
    #  Returns a list of normalized object-states (language suffixes stripped off).
    # --------------------------------------------------------------------------
    def getObjStateNames(self, REQUEST):
      lang = REQUEST.get('lang')
      
      # Current Object.
      states = getObjStates(self)
      obj_states = []
      for obj_state in [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED']:
        obj_state_name = getObjStateName(obj_state,lang)
        if obj_state_name in states:
          obj_states.append(obj_state_name)
      
      # Return value.
      return obj_states


    """
    ############################################################################
    #  Change object-state.
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.setObjStateNew
    # --------------------------------------------------------------------------
    def setObjStateNew(self, REQUEST, reset=1):
      obj_state = 'STATE_NEW'
      if reset: self.initializeWorkVersion()
      setChangedBy( self, REQUEST)
      setCreatedBy( self, REQUEST)
      #-- Set Master-Version.
      parent = self.getParentNode()
      master_version = 0
      if parent is not None:
        master_version = parent.getObjProperty( 'master_version', REQUEST)
      self.setObjProperty( 'master_version', master_version)
      self.setObjState(obj_state,REQUEST['lang'])

    # --------------------------------------------------------------------------
    #  VersionItem.setObjStateModified
    # --------------------------------------------------------------------------
    def setObjStateModified(self, REQUEST):
      obj_state = 'STATE_MODIFIED'
      setChangedBy( self, REQUEST)
      self.setObjState(obj_state,REQUEST['lang'])

    # --------------------------------------------------------------------------
    #  VersionItem.setObjStateDeleted
    # --------------------------------------------------------------------------
    def setObjStateDeleted(self, REQUEST):
      obj_state = 'STATE_DELETED'
      setChangedBy( self, REQUEST)
      self.setObjState(obj_state,REQUEST['lang'])


    """
    ############################################################################
    #
    #   Commit
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.onChangeObj:
    # --------------------------------------------------------------------------
    def onChangeObj(self, REQUEST, forced=False, do_history=True):
      _globals.writeLog( self, "[onChangeObj]")
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
      ##### Trigger thumbnail generation of image fields ####
      _blobfields.thumbnailImageFields(self,lang,REQUEST)
      
      ##### Trigger custom onChangeObj-Event (if there is one) ####
      triggerEvent( self, 'onChangeObjEvt', REQUEST)
      
      ##### Commit or initiate workflow transition ####
      if self.getAutocommit() or forced:
        self.commitObj(REQUEST,forced,do_history)
      else:
        self.autoWfTransition(REQUEST)
      _globals.writeLog( self, "[onChangeObj]: Finished!")

    # --------------------------------------------------------------------------
    #  VersionItem.onSynchronizeObj:
    # --------------------------------------------------------------------------
    def onSynchronizeObj(self, REQUEST):
      _globals.writeLog( self, "[onSynchronizeObj]")
      #-- Catalog
      ob = self.getCatalogItem()
      obs = REQUEST.get('ZMS_SYNCHRONIZE_CATALOG',[])
      if ob not in obs:
        obs.append(ob)
        try:
          REQUEST.set('ZMS_SYNCHRONIZE_CATALOG',obs)
        except:
          REQUEST['ZMS_SYNCHRONIZE_CATALOG'] = obs
      #-- Cache
      self.synchronizeCachePage(REQUEST)
      #-- Access
      self.synchronizePublicAccess()
      #-- References
      self.synchronizeRefToObjs()
      self.synchronizeRefByObjs()


    # --------------------------------------------------------------------------
    #  VersionItem.commitObjChanges
    # --------------------------------------------------------------------------
    def _commitObjChanges(self, parent, REQUEST, forced=False, do_history=True, do_delete=True):
      if _globals.debug( self):
        _globals.writeLog( self, "[_commitObjChanges]: forced=%s, do_history=%s, do_delete=%s"%(str(forced),str(do_history),str(do_delete)))
      delete = False
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
      ##### Trigger custom beforeCommitObjChanges-Event (if there is one) ####
      triggerEvent( self, 'beforeCommitObjChangesEvt', REQUEST)

      ##### Commit delete. ####
      if self.inObjStates(['STATE_DELETED'],REQUEST):
        if do_delete:
          parent.moveObjsToTrashcan([self.id], REQUEST)
        delete = True

      ##### Commit modifications. ####
      modified = self.getObjStateNames(REQUEST) or forced
      if modified:

        if (lang == prim_lang or self.getDCCoverage(REQUEST).find('.%s'%lang) > 0) and (self.getHistory() and do_history):
          version_hist_id = None
          if self.getObjStateNames(REQUEST) and \
             self.version_work_id is not None:
            # Clone current live-version to history-version.
            if self.version_live_id is not None and self.version_live_id in self.objectIds(['ZMSAttributeContainer']):
              request = {'lang':'*'}
              histAttrCntnr = _zmsattributecontainer.manage_addZMSAttributeContainer(self)
              self.cloneObjAttrs(getattr(self,self.version_live_id),histAttrCntnr,request)
              version_hist_id = histAttrCntnr.id
            # Replace current live-version by work-version.
            if self.version_work_id is not None and self.version_work_id in self.objectIds(['ZMSAttributeContainer']):
              self.version_live_id = self.version_work_id
              self.version_work_id = None
          # Increase version-number.
          major_version = self.getObjProperty( 'major_version', REQUEST)
          self.setObjProperty( 'major_version', major_version + 1)
          self.setObjProperty( 'minor_version' ,0)
          # Remove previous minor-versions.
          ids = []
          for ob_version in self.getObjVersions():
            if ob_version.id != version_hist_id and \
               ob_version.getObjProperty('major_version',REQUEST) == major_version:
              ids.append( ob_version.id)
          if _globals.debug( self):
            _globals.writeLog( self, "[_commitObjChanges]: Remove previous minor-versions: ids=%s"%str(ids))
          self.manage_delObjects( ids=ids)
        
        else:
          if self.getObjStateNames(REQUEST) and \
             self.version_work_id is not None:
            if self.version_live_id is None:
              self.version_live_id = self.version_work_id
            if self.getAutocommit():
              # Replace current live-version by work-version.
              self.version_live_id = self.version_work_id
              self.version_work_id = None
            elif self.version_live_id != self.version_work_id:
              # Clone current work-version to live-version.
              self.cloneObjAttrs(getattr(self,self.version_work_id),getattr(self,self.version_live_id),REQUEST)
          # Reset version-number.
          if self.getHistory() and not do_history:
            self.setObjProperty( 'major_version', 0)
            self.setObjProperty( 'minor_version' ,0)
          
      ##### Commit version-items. ####
      if not delete:
        ids = []
        for child in self.getVersionItems( REQUEST):
          delete_child = child._commitObjChanges( self, REQUEST, False, do_history, False)
          if delete_child:
            ids.append( child.id)
        if len( ids) > 0:
          self.moveObjsToTrashcan( ids, REQUEST)
      
      ##### Reset object-state. ####
      self.resetObjStates(REQUEST)
      # Remove work-version.
      attrCntnrIds = self.objectIds(['ZMSAttributeContainer'])
      if (self.getAutocommit() or len( filter( lambda x: x.find( 'STATE_') == 0, getObjStates( self))) == 0) and getattr( self, 'version_live_id', None) is not None:
        if self.version_live_id in attrCntnrIds:
          ids = []
          if self.version_live_id != self.version_work_id and self.version_work_id in attrCntnrIds:
            ids.append( self.version_work_id)
          if self.getAutocommit() and not (self.getHistory() and do_history):
            for id in attrCntnrIds:
              if id != self.version_live_id and id != self.version_work_id:
                ids.append( id)
          self.version_work_id = None
          if len( ids) > 0:
            if _globals.debug( self):
              _globals.writeLog( self, "[_commitObjChanges]: Remove work-version: ids=%s"%str(ids))
          self.manage_delObjects( ids=ids)
        elif self.version_work_id in attrCntnrIds:
          self.version_live_id = self.version_work_id
          self.version_work_id = None
      
      ##### Synchronize listeners. ####
      if modified:
        self.onSynchronizeObj(REQUEST)
        
      ##### Trigger custom afterCommitObjChanges-Event (if there is one) ####
      triggerEvent( self, 'afterCommitObjChangesEvt', REQUEST)

      # Return flag for deleted objects.
      return delete

    def commitObjChanges(self, parent, REQUEST, forced=False, do_history=True, do_delete=True):
      delete = self._commitObjChanges( parent, REQUEST, forced, do_history, do_delete)
      ##### Synchronize catalog. ####
      obs = REQUEST.get('ZMS_SYNCHRONIZE_CATALOG',[])
      for ob in obs:
        ob.synchronizeSearch(REQUEST)
      # Return flag for deleted objects.
      return delete


    """
    ############################################################################
    #
    #   Rollback
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.rollbackObjChanges
    # --------------------------------------------------------------------------
    def _rollbackObjChanges(self, parent, REQUEST, forced=0, do_delete=True):
      if _globals.debug( self):
        _globals.writeLog( self, "[_rollbackObjChanges]")
      delete = False
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
      ##### Trigger custom beforeRollbackObjChanges-Event (if there is one) ####
      triggerEvent( self, 'beforeRollbackObjChangesEvt', REQUEST)

      ##### Rollback insert. ####
      # Self.
      if self.inObjStates(['STATE_NEW'],REQUEST):
        if do_delete:
          parent.moveObjsToTrashcan([self.id], REQUEST)
        delete = True
      
      ##### Rollback modifications. ####
      modified = self.getObjStateNames(REQUEST) or forced
      if modified and not delete:

        if (lang == prim_lang or self.getDCCoverage(REQUEST).find('.%s'%lang) > 0) and self.getHistory():
          # Reset work-version.
          self.version_work_id = None
          # Current version-number.
          major_version = self.getObjProperty( 'major_version', REQUEST)
          # Remove next minor-versions.
          ids = []
          for ob_version in self.getObjVersions():
            if ob_version.getObjProperty('major_version',REQUEST) == major_version and \
               ob_version.getObjProperty('minor_version',REQUEST) > 0:
              ids.append( ob_version.id)
          if _globals.debug( self):
            _globals.writeLog( self, "[_rollbackObjChanges]: Remove next minor-versions: ids=%s"%str(ids))
          self.manage_delObjects( ids=ids)
        
        else:
          if self.getObjStateNames(REQUEST) and \
             self.version_work_id is not None:
            if self.version_live_id is None:
              self.version_live_id = self.version_work_id
            if self.getAutocommit():
              # Remove current work-version.
              self.version_work_id = None
            elif self.version_live_id is not None and self.version_live_id != self.version_work_id:
              # Clone current live-version to work-version.
              if _globals.debug( self):
                _globals.writeLog( self, "[_rollbackObjChanges]: Clone current live-version '%s' to work-version '%s'"%(self.version_live_id,self.version_work_id))
              self.cloneObjAttrs(getattr(self,self.version_live_id),getattr(self,self.version_work_id),REQUEST)
      
      ##### Rollback version-items. ####
      if not delete:
        ids = []
        for child in self.getVersionItems( REQUEST):
          delete_child = child._rollbackObjChanges( self, REQUEST, 0, False)
          if delete_child:
            ids.append( child.id)
        if len( ids) > 0:
          self.moveObjsToTrashcan( ids, REQUEST)
      
      ##### Reset object-state. ####
      self.resetObjStates(REQUEST)
      # Remove work-version.
      attrCntnrIds = self.objectIds(['ZMSAttributeContainer'])
      if (self.getAutocommit() or len( filter( lambda x: x.find( 'STATE_') == 0, getObjStates( self))) == 0) and getattr( self, 'version_live_id', None) is not None:
        if self.version_live_id in attrCntnrIds:
          ids = []
          if self.version_live_id != self.version_work_id and self.version_work_id in attrCntnrIds:
            ids.append( self.version_work_id)
          if self.getAutocommit() and not self.getHistory():
            for id in attrCntnrIds:
              if id != self.version_live_id and id != self.version_work_id:
                ids.append( id)
          self.version_work_id = None
          if len( ids) > 0:
            if _globals.debug( self):
              _globals.writeLog( self, "[_rollbackObjChanges]: Remove work-version: ids=%s"%str(ids))
          self.manage_delObjects( ids=ids)
        elif self.version_work_id in attrCntnrIds:
          self.version_live_id = self.version_work_id
          self.version_work_id = None
      
      ##### Synchronize listeners. ####
      if modified and not delete:
        self.onSynchronizeObj(REQUEST)
      
      ##### Trigger custom afterRollbackObjChanges-Event (if there is one) ####
      triggerEvent( self, 'afterRollbackObjChangesEvt', REQUEST)
      
      # Return flag for deleted objects.
      return delete

    def rollbackObjChanges(self, parent, REQUEST, forced=0, do_delete=True):
      delete = self._rollbackObjChanges( parent, REQUEST, forced, do_delete)
      ##### Synchronize catalog. ####
      obs = REQUEST.get('ZMS_SYNCHRONIZE_CATALOG',[])
      for ob in obs:
        ob.synchronizeSearch(REQUEST)
      # Return flag for deleted objects.
      return delete


    """
    ############################################################################
    #
    #   History
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionItem.packHistory:
    #
    #  Pack history.
    # --------------------------------------------------------------------------
    def packHistory(self):
      count = 0
      if not self.getHistory():
        #-- Remove version-attribute-containers.
        ids = []
        for id in self.objectIds(['ZMSAttributeContainer']):
          if id not in [ self.version_work_id, self.version_live_id]:
            ids.append( id)
        count += len( ids)
        self.manage_delObjects( ids=ids)
        #-- Remove version-attributes.
        for key in ['master_version','major_version', 'minor_version', 'change_history']:
          for id in [ self.version_work_id, self.version_live_id]:
            if id is not None:
              ob = getattr( self, id, None)
              if ob is not None:
                try:
                  delattr( ob, key)
                except:
                  pass
        #-- Recursion.
        for ob in self.objectValues( self.dGlobalAttrs.keys()):
          count += ob.packHistory()
      return count


    # --------------------------------------------------------------------------
    #  VersionItem.getHistory:
    #
    #  Returns true if history is active, false otherwise.
    # --------------------------------------------------------------------------
    def getHistory( self):
      active = True
      if active:
        active = active and self.getConfProperty('ZMS.Version.active',0)==1
      if active:
        baseurl = self.getDocumentElement().absolute_url()
        url = self.absolute_url()
        if len( url) >= len( baseurl):
          url = url[ len( baseurl)+1:]
        url = '$'+url
        found = False
        nodes = self.getConfProperty('ZMS.Version.nodes',['{$}'])
        for node in nodes:
          if node[1:-1] == '$' or (url+'/').find(node[1:-1]+'/') == 0:
            found = True
            break
        active = active and found
      return active
    

    # --------------------------------------------------------------------------
    #  VersionItem.ajaxBodyContentObjHistory:
    # --------------------------------------------------------------------------
    def ajaxBodyContentObjHistory(self, version_nr, REQUEST):
      """
      Returns ajax-xml with body-content of object-history for given version-nr.
      """
      
      #-- Get versions.
      master_version = int( version_nr[ :version_nr.find( '.')])
      major_version = int( version_nr[ version_nr.find( '.')+1: version_nr.rfind( '.')])
      minor_version = int( version_nr[ version_nr.rfind( '.')+1:])
      REQUEST.set( 'ZMS_VERSION_%s'%self.id, None)
      version_dt = None
      if 'change_history' in self.getObjAttrs().keys():
        change_history = copy.copy( self.getObjProperty( 'change_history', REQUEST))
        change_history.reverse()
        for item in change_history:
          if version_dt is None and \
             item.get( 'master_version', 0) <= master_version and \
             item.get( 'major_version', 0) <= major_version:
            version_dt = item[ 'version_dt']
            break
      
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxBodyContentObjHistory.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = self.getXmlHeader()
      xml += "<BodyContentObjHistory version_nr=\""+version_nr+"\">\n"
      if self.meta_type == 'ZMSCustom':
        obj_version = self.getObjHistory( version_nr, REQUEST, False)
        REQUEST.set( 'ZMS_VERSION_%s'%self.id, obj_version.id)
        xml += '<ObjHistory id="' + obj_version.id + '">'
        xml += '<![CDATA[' + obj_version.getBodyContent( REQUEST) + ']]>'
        xml += '</ObjHistory>\n'
      else:
        obj_history = self.getObjHistory( version_nr, REQUEST)
        for history_version in obj_history:
          if history_version.isActive(REQUEST):
            xml += '<ObjHistory id="' + history_version.id + '">'
            xml += '<![CDATA[' + history_version.renderShort( REQUEST) + ']]>'
            xml += '</ObjHistory>\n'
      xml += "</BodyContentObjHistory>\n"
      return xml


    # --------------------------------------------------------------------------
    #  VersionItem.getObjHistory:
    #
    #  Returns object-history for given version-nr.
    # --------------------------------------------------------------------------
    def getObjHistory(self, version_nr, REQUEST, children=True, deleted=True):
      if _globals.debug( self):
        _globals.writeLog( self, '[getObjHistory]: version_nr=%s'%str(version_nr))
      obs = []
      ZMS_VERSION = REQUEST.get( 'ZMS_VERSION_%s'%self.id)
      master_version = int( version_nr[ :version_nr.find( '.')])
      major_version = int( version_nr[ version_nr.find( '.')+1: version_nr.rfind( '.')])
      minor_version = int( version_nr[ version_nr.rfind( '.')+1:])
      REQUEST.set( 'ZMS_VERSION_%s'%self.id, None)
      version_dt = None
      change_history = []
      if 'change_history' in self.getObjAttrs().keys():
        change_history = copy.copy( self.getObjProperty( 'change_history', REQUEST))
        change_history.reverse()
        for item in change_history:
          if version_dt is None and \
             item.get( 'master_version', 0) <= master_version and \
             item.get( 'major_version', 0) <= major_version:
            version_dt = item[ 'version_dt']
            break
      if _globals.debug( self):
        _globals.writeLog( self, '[getObjHistory]: version_dt=%s'%str(version_dt))
      found = False
      last_ob_version = None
      for ob_version in self.getObjVersions():
        REQUEST.set( 'ZMS_VERSION_%s'%self.id, ob_version.id)
        last_ob_version = ob_version
        ob_version_master_version = getattr( ob_version, 'master_version', 0)
        ob_version_major_version = getattr( ob_version, 'major_version', 0)
        ob_version_minor_version = getattr( ob_version, 'minor_version', 0)
        ob_version_nr = '%i.%i.%i'%(ob_version_master_version,ob_version_major_version,ob_version_minor_version)
        ob_version_change_dt = ob_version.getObjProperty( 'change_dt', REQUEST, {'fetchReqBuff':0})
        if ob_version_nr <= version_nr:
          if not children:
            if _globals.debug( self):
              _globals.writeLog( self, '[getObjHistory]: return %s'%str(last_ob_version.id))
            return last_ob_version
          for ob_child in self.getVersionItems( REQUEST, recursive=True):
            for ob_child_version in ob_child.getObjVersions():
              REQUEST.set( 'ZMS_VERSION_%s'%ob_child.id, ob_child_version.id)
              ob_child_master_version = getattr( ob_child_version, 'master_version', 0)
              ob_child_major_version = getattr( ob_child_version, 'major_version', 0)
              ob_child_minor_version = getattr( ob_child_version, 'minor_version', 0)
              ob_child_nr = '%i.%i.%i'%(ob_child_master_version,ob_child_major_version,ob_child_minor_version)
              ob_child_change_dt = ob_child.getObjProperty( 'change_dt', REQUEST, {'fetchReqBuff':0})
              if ( version_dt is None and \
                   ((ob_child_master_version == 0 and ob_child_major_version == 0 and ob_child_minor_version == 0) or \
                    (len( change_history) == 0 and ob_version_change_dt >= ob_child_change_dt))) or \
                 ( version_dt >= ob_child_change_dt) or \
                 ( minor_version > 0 and ob_child_minor_version > 0) or \
                 ( minor_version > 0 and ob_child_change_dt > version_dt):
                obs.append( ob_child_version)
                break
          found = True
          break
      if not found:
        if not children:
          if _globals.debug( self):
            _globals.writeLog( self, '[getObjHistory]: return %s'%str(last_ob_version.id))
          return last_ob_version
        for ob_child in self.getVersionItems( REQUEST, recursive=True):
          for ob_child_version in ob_child.getObjVersions():
            REQUEST.set( 'ZMS_VERSION_%s'%ob_child.id, ob_child_version.id)
            ob_child_master_version = getattr( ob_child_version, 'master_version', 0)
            ob_child_major_version = getattr( ob_child_version, 'major_version', 0)
            ob_child_minor_version = getattr( ob_child_version, 'minor_version', 0)
            ob_child_nr = '%i.%i.%i'%(ob_child_master_version,ob_child_major_version,ob_child_minor_version)
            ob_child_change_dt = ob_child.getObjProperty( 'change_dt', REQUEST)
            if ( version_dt is None and ob_child_master_version == 0 and ob_child_major_version == 0 and ob_child_minor_version == 0) or \
               ( ob_child_change_dt <= version_dt):
              obs.append( ob_child_version)
              break
      REQUEST.set( 'ZMS_VERSION_%s'%self.id, ZMS_VERSION)
      return obs

    # --------------------------------------------------------------------------
    #  VersionItem.getObjVersion:
    #
    #  Returns attribute-container. If Http-Request has key >ZMS_VERSION< the 
    #  desired version is returned, if Http-Request has key >preview< the work-
    #  version is returned, else the live-version is returned.
    # --------------------------------------------------------------------------
    def getObjVersion(self, REQUEST={}):
      try:
        ob = None
        id = REQUEST.get( 'ZMS_VERSION_%s'%self.id, None)
        if id is not None and id not in self.objectIds(['ZMSAttributeContainer']):
          id = None
        if id is None:
          preview = _globals.isPreviewRequest( REQUEST)
          has_version_work = self.version_work_id is not None and hasattr( self, self.version_work_id)
          has_version_live = self.version_live_id is not None and hasattr( self, self.version_live_id)
          if (preview and has_version_work) or not (has_version_live):
            id = self.version_work_id
          elif (has_version_live) or not (preview and has_version_work):
            id = self.version_live_id
        ob = getattr( self, id)
        s = ob.id # Never delete this line!
        return ob
      except:
        preview = _globals.isPreviewRequest( REQUEST)
        has_version_work = self.version_work_id is not None and hasattr( self, self.version_work_id)
        has_version_live = self.version_live_id is not None and hasattr( self, self.version_live_id)
        raise _globals.writeException( self, '[getObjVersion]: an unexpected error occured!')


    # --------------------------------------------------------------------------
    #  VersionItem.getObjVersions:
    #
    #  Returns all attribute-containers.
    # --------------------------------------------------------------------------
    def getObjVersions(self):
      try:
        obs = []
        for ob in self.objectValues(['ZMSAttributeContainer']):
          obs.insert(0,(getattr( ob,'master_version',0) * 10000 + getattr( ob,'major_version',0) * 100 + getattr( ob,'minor_version',0),ob))
        # sort object-items
        obs.sort()
        obs.reverse()
        # truncate version-nr from sorted object-items
        obs = map( lambda ob: ob[1], obs)
        # return object-items
        return obs
      except:
        raise _globals.writeException( self, '[getObjVersions]: an unexpected error occured!')


    # --------------------------------------------------------------------------
    #  VersionItem.restoreObjVersion:
    #
    #  Restore object-version.
    # --------------------------------------------------------------------------
    def restoreObjVersion( self, ob_version, REQUEST):
      if ob_version is not None and \
         ob_version.id != self.version_work_id:
        REQUEST.set( 'ZMS_VERSION_%s'%self.id, None)
        if 'change_history' in self.getObjAttrs().keys():
          change_history = self.getObjProperty('change_history',REQUEST)
        master_version = self.getObjProperty('master_version',REQUEST)
        major_version = self.getObjProperty('major_version',REQUEST)
        minor_version = self.getObjProperty('minor_version',REQUEST) + 1
        # Restore attributes.
        self.setObjStateModified( REQUEST)
        self.cloneObjAttrs(ob_version,getattr(self,self.version_work_id),REQUEST)
        setChangedBy(self, REQUEST, createWorkAttrCntnr=False)
        if 'change_history' in self.getObjAttrs().keys():
          self.setObjProperty('change_history',change_history)
        self.setObjProperty('master_version',master_version)
        self.setObjProperty('major_version',major_version)
        self.setObjProperty('minor_version',minor_version)
        self.onChangeObj(REQUEST)
        return True
      return False


    ############################################################################
    #  VersionItem.manage_UndoVersion:
    #
    #  Undo version changes.
    ############################################################################
    manage_VersionLangModified = HTMLFile('dtml/versionmanager/manage_versionlangmodified', globals())
    manage_UndoVersionForm = HTMLFile('dtml/versionmanager/manage_undoversionform', globals())
    def manage_UndoVersion(self, lang, REQUEST):
      """ VersionItem.manage_UndoVersion """
      message = ''
      
      # Reset.
      # ------
      if REQUEST.get('btn','') == self.getZMILangStr('BTN_RESET'):
        version_nrs = REQUEST.get('version_nrs',[])
        if len(version_nrs) == 1:
          version_nr = version_nrs[0]
          ob_version = self.getObjHistory( version_nr, REQUEST, children=False)
          if self.restoreObjVersion( ob_version, REQUEST):
            # Restore children.
            ob_child_versions = self.getObjHistory( version_nr, REQUEST, children=True)
            for ob_child_version in ob_child_versions:
              ob_child = ob_child_version.aq_parent
              ob_child.restoreObjVersion( ob_child_version, REQUEST)
          message = self.getZMILangStr('MSG_CHANGED')

      # Return with message.
      message = urllib.quote(message)
      return REQUEST.RESPONSE.redirect('manage_UndoVersionForm?lang=%s&manage_tabs_message=%s'%(lang,message))


################################################################################
################################################################################
###
###   class VersionManagerContainer
###
################################################################################
################################################################################
class VersionManagerContainer: 

    # --------------------------------------------------------------------------
    #  VersionItem.isVersionContainer
    # --------------------------------------------------------------------------
    def isVersionContainer(self):
      b = False
      b = b or (self.isPage() and self.isPageContainer())
      b = b or (self.isPage() and self.meta_id == 'ZMSLinkElement' and self.isEmbedded(self.REQUEST))
      if not b:
        parent = self.getParentNode()
        b = parent is not None and parent.isPageContainer() and self.isPage()
      return b

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.getVersionContainer
    # --------------------------------------------------------------------------
    def getVersionContainer(self):
      if self.isVersionContainer():
        return self
      return self.getParentNode().getVersionContainer()


    """
    ############################################################################
    #  Notification
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.getRecipientWf
    # --------------------------------------------------------------------------
    def getRecipientWf(self, REQUEST=None):
      recipient = ''
      name = self.getObjProperty('work_uid',REQUEST)
      mto = self.getUserAttr(name,'email','')
      if len(mto) > 0:
        recipient = name + ' <' + mto + '>'
      return recipient
    
    # --------------------------------------------------------------------------
    #  VersionManagerContainer.getRecipientsByRole
    # --------------------------------------------------------------------------
    def getRecipientsByRole(self, roles=['ZMSEditor'], REQUEST=None):
      recipients = ''
      langs = [REQUEST['lang']]
      ob = self
      while ob is not None and len(recipients) == 0:
        for local_role in ob.get_local_roles():
          name = local_role[0]
          userObj = self.findUser(name)
          mto = self.getUserAttr(name,'email','')
          if userObj is not None and \
	     len(mto) > 0 and \
             len(self.intersection_list(roles, ob.getUserRoles(userObj, aq_parent=0))) > 0 and \
             len(self.intersection_list(langs, ob.getUserLangs(userObj, aq_parent=0))) > 0:
            if len(recipients) > 0:
              recipients += ', '
            recipients += name + ' <' + mto + '>'
        ob = ob.getParentNode()
      return recipients

    """
    ############################################################################
    #  Workflow
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.resetWfStates:
    #
    #  Resets information about workflow-events.
    # --------------------------------------------------------------------------
    def resetWfStates(self, REQUEST):
      lang = REQUEST['lang']
      self.delObjStates(self.getWfActivitiesIds(), REQUEST)
      self.autoWfTransition(REQUEST)

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.autoWfTransition
    # --------------------------------------------------------------------------
    def autoWfTransition(self, REQUEST):
      if _globals.debug( self):
        _globals.writeLog( self, "[autoWfTransition]")
      lang = REQUEST['lang']
      # Enter Container.
      if not self.isVersionContainer():
        return self.getVersionContainer().autoWfTransition(REQUEST)
        return
      # Enter Workflow.
      enter = len(self.getWfStates(REQUEST)) == 0
      modified = self.isObjModified(REQUEST) or self.hasObjModifiedChildren(REQUEST)
      if not enter:
        wfStates = self.getWfStates(REQUEST)
        for wfTransition in self.getWfTransitions():
          enter = enter or \
             (len(self.intersection_list(wfStates, wfTransition.get('from',[]))) > 0 and \
              len(wfTransition.get('to',[])) == 0)
          if enter:
            break
      if enter and modified:
        for wfTransition in self.getWfTransitions():
          if len(wfTransition.get('from',[])) == 0 and \
             len(wfTransition.get('to',[])) > 0:
            if _globals.debug( self): 
              _globals.writeLog( self, "[autoWfTransition]: name=%s, id=%s"%(wfTransition['name'],wfTransition['id']))
            # Delete old state.
            self.delObjStates(self.getWfStates(REQUEST), REQUEST)
            # Add new state.
            self.setObjState(wfTransition.get('to',[])[0], lang)
            # Set Properties.
            self.setObjProperty('work_uid',str(REQUEST.get('AUTHENTICATED_USER')),lang)
            self.setObjProperty('work_dt',_globals.getDateTime( time.time()),lang)
            break
      elif not enter and not modified:
        # Delete old state.
        self.delObjStates(self.getWfStates(REQUEST), REQUEST)


    ############################################################################
    #  VersionManagerContainer.manage_wfTransition:
    #
    #  Workflow transition.
    ############################################################################
    def manage_wfTransition(self, lang, custom, REQUEST, RESPONSE):
      """ WorkflowContainer.manage_wfTransition """
      if _globals.debug( self):
        _globals.writeLog( self, "[manage_wfTransition]")
      wfTransitions = self.getWfTransitions()
      for wfTransition in filter(lambda x: x['name']==custom, wfTransitions):
        dtml = wfTransition.get('dtml','')
        if len(dtml) > 0:
	  return _globals.dt_html(self, dtml, REQUEST) 
	else:
	  return self.manage_wfTransitionFinalize(lang, custom, REQUEST, RESPONSE)


    ############################################################################
    #  VersionManagerContainer.manage_wfTransitionFinalize:
    #
    #  Workflow transition finalize.
    ############################################################################
    def manage_wfTransitionFinalize(self, lang, custom, REQUEST, RESPONSE=None):
      """ WorkflowContainer.manage_wfTransitionFinalize """
      if _globals.debug( self):
        _globals.writeLog( self, "[manage_wfTransitionFinalize]")
      url = ''
      message = ''
      wfTransitions = self.getWfTransitions()
      for wfTransition in filter(lambda x: x['name']==custom, wfTransitions):
        # Delete old state.
        self.delObjStates(self.getWfStates(REQUEST), REQUEST)
        # Add new state.
        for wfState in wfTransition.get('to',[]):
          if _globals.debug( self): 
            _globals.writeLog( self, "[manage_wfTransition]: Add %s"%wfState)
          self.setObjState(wfState, lang)
          message += REQUEST.get('manage_tabs_message', filter(lambda x: x['id']==wfState,self.getWfActivities())[0]['name'])
        # Set Properties.
        work_dt = _globals.getDateTime( time.time())
        work_uid = str(REQUEST.get('AUTHENTICATED_USER'))
        work_desc = REQUEST.get('work_desc','')
        self.setObjProperty('work_uid',work_uid,lang)
        self.setObjProperty('work_dt',work_dt,lang)
        # Log Protocol.
        log = ''
        log = log + self.getLangFmtDate(work_dt,lang,'%Y-%m-%d %H:%M:%S') + '\t'
        log = log + wfTransition['id'] + '\t'
        log = log + self.absolute_url()[len(self.getHome().absolute_url()):] + '\t'
        log = log + self.display_type(REQUEST) + '\t'
        log = log + work_uid + '\t'
        log = log + work_desc
        _workflowmanager.writeProtocol(self, log)
      self.autoWfTransition(REQUEST)
      # Return with message.
      if RESPONSE is not None:
        return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),lang,message))


    """
    ############################################################################
    #  Tasks 
    ############################################################################
    """

    # Management Interface.
    # ---------------------
    manage_tasks = HTMLFile('dtml/versionmanager/manage_tasks', globals()) 
    task_wf = HTMLFile('dtml/versionmanager/tasklist0', globals()) 
    task_zmsnote = HTMLFile('dtml/versionmanager/tasklist1', globals()) 
    task_untranslated = HTMLFile('dtml/versionmanager/tasklist2', globals()) 
    task_changed_by_date = HTMLFile('dtml/versionmanager/tasklist3', globals()) 


    """
    ############################################################################
    #  Commit
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.commitObj:
    #
    #  Commit container.
    # --------------------------------------------------------------------------
    def commitObj(self, REQUEST={}, forced=False, do_history=True):
      if _globals.debug( self): 
        _globals.writeLog( self, "[commitObj]: forced=%s, do_history=%s"%(str(forced),str(do_history)))
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
      ##### Version ####
      if (lang == prim_lang or self.getDCCoverage(REQUEST).find('.%s'%lang) > 0) and (self.getHistory() and do_history):
        version_items = self.getVersionItems( REQUEST, recursive=True)
        is_modified = self.isObjModified( REQUEST)
        has_modified_children = self.hasObjModifiedChildren( REQUEST)
        forced = forced or not is_modified and has_modified_children
        if is_modified or has_modified_children:
          change_history = self.getObjProperty( 'change_history', REQUEST)
          if type( change_history) is list:
            if len( change_history) == 0:
              version_dt = self.getObjProperty( 'change_dt', REQUEST)
              for version_item in version_items:
                change_dt = version_item.getObjProperty( 'change_dt', REQUEST)
                if version_dt is None or version_dt < change_dt:
                  change_dt = version_dt
              record = {}
              record[ 'version_dt'] = version_dt
              record[ 'version_uid'] = self.getObjProperty( 'change_uid', REQUEST)
              record[ 'master_version'] = self.getObjProperty( 'master_version', REQUEST)
              record[ 'major_version'] = self.getObjProperty( 'major_version', REQUEST)
              change_history.append( record)
            record = {}
            record[ 'version_dt'] = _globals.getDateTime( time.time())
            record[ 'version_uid'] = str( REQUEST.get( 'AUTHENTICATED_USER', None))
            record[ 'master_version'] = self.getObjProperty( 'master_version', REQUEST)
            record[ 'major_version'] = self.getObjProperty( 'major_version', REQUEST) + 1
            change_history.append( record)
            self.setObjProperty( 'change_history', change_history)
      
      ##### Self ####
      if REQUEST.has_key('lang'): 
        self.resetWfStates(REQUEST)
      parent = self.getParentNode()
      delete = self.commitObjChanges(parent,REQUEST,forced,do_history)
      url = self.absolute_url()
      if delete: 
        url = parent.absolute_url()
        try: REQUEST.set('ZMS_REDIRECT_PARENT',True)
        except: REQUEST['ZMS_REDIRECT_PARENT'] = True
        
      # Return new URL.
      _globals.writeLog( self, "[commitObj]: Finished!")
      return url


    """
    ############################################################################
    #  Rollback
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  VersionManagerContainer.rollbackObj
    # --------------------------------------------------------------------------
    def rollbackObj(self, REQUEST):
      if _globals.debug( self): 
        _globals.writeLog( self, "[rollbackObj]")
        
      ##### Self ####
      if REQUEST.has_key('lang'): self.resetWfStates(REQUEST)
      parent = self.getParentNode()
      delete = self.rollbackObjChanges(parent,REQUEST)
      url = self.absolute_url()
      if delete: 
        url = parent.absolute_url()
        try: REQUEST.set('ZMS_REDIRECT_PARENT',True)
        except: REQUEST['ZMS_REDIRECT_PARENT'] = True
        
      _globals.writeLog( self, "[rollbackObj]: Finished!")
      # Return new URL.
      return url

################################################################################
