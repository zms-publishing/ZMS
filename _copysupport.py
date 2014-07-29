################################################################################
# _copysupport.py
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
import copy
import string
import time
import urllib
from OFS import Moniker
from OFS.CopySupport import _cb_decode, _cb_encode, absattr, CopyError, eNoData, eNotFound, eInvalid
# Product Imports.
import _globals


################################################################################
################################################################################
###
###   C l a s s   C o p y S u p p o r t 
###
################################################################################
################################################################################
class CopySupport:

    # --------------------------------------------------------------------------
    #  CopySupport._get_cb_copy_data:
    # --------------------------------------------------------------------------
    def _get_cb_copy_data(self, cb_copy_data=None, REQUEST=None):
      cp=None
      if cb_copy_data is not None:
        cp=cb_copy_data
      else:
        if REQUEST and REQUEST.has_key('__cp'):
          cp=REQUEST['__cp']
      if cp is None:
        raise CopyError, eNoData
      
      try: 
        cp=_cb_decode(cp)
      except: 
        _globals.writeError( self, '[_get_cb_copy_data]: eInvalid')
        raise CopyError, eInvalid
      
      return cp

    # --------------------------------------------------------------------------
    #  CopySupport._get_obs:
    # --------------------------------------------------------------------------
    def _get_obs(self, cp):
        
        try: 
          cp=_cb_decode(cp)
        except: 
          _globals.writeError( self, '[_get_obs]: eInvalid')
          raise CopyError, eInvalid
        
        oblist=[]
        op=cp[0]
        app = self.getPhysicalRoot()
        
        for mdata in cp[1]:
          m = Moniker.loadMoniker(mdata)
          try: 
            ob = m.bind(app)
          except: 
            _globals.writeError( self, '[_get_obs]: eNotFound')
            raise CopyError, eNotFound
          self._verifyObjectPaste(ob)
          oblist.append(ob)
        
        return oblist

    def cp_get_obs(self, REQUEST):
      cp = self._get_cb_copy_data(cb_copy_data=None,REQUEST=REQUEST)
      op = cp[0]
      cp = (0,cp[1])
      cp = _cb_encode(cp)
      return self._get_obs( cp)


    # --------------------------------------------------------------------------
    #  CopySupport._get_ids:
    # --------------------------------------------------------------------------
    def _get_ids(self, cp):
      return map(lambda ob: self._get_id(absattr(ob.id)),self._get_obs(cp))


    # --------------------------------------------------------------------------
    #  CopySupport._get_id:
    #
    #  Allow containers to override the generation of
    #  object copy id by attempting to call its _get_id
    #  method, if it exists.
    # --------------------------------------------------------------------------
    def _get_id(self, id):
      return 'copy_of_%s'%id 


    # --------------------------------------------------------------------------
    #  CopySupport._set_sort_ids:
    # 
    #  Group all objects to be copied / moved at new position (given by _sort_id) 
    #  in correct sort-order.
    # --------------------------------------------------------------------------
    def _set_sort_ids(self, ids, op, REQUEST):
      _globals.writeLog( self, "[_set_sort_ids]: %s"%self.absolute_url())
      
      copy_of_prefix = 'copy_of_'
      sort_id = REQUEST.get('_sort_id',0) + 1
      for ob in self.getChildNodes():
        id = absattr(ob.id)
        if id in ids or (op==1 and copy_of_prefix + id in ids):
          setattr( ob, 'sort_id', _globals.format_sort_id(sort_id))
          sort_id = sort_id + 1


    # --------------------------------------------------------------------------
    #  CopySupport._normalize_ids_after_copy:
    # --------------------------------------------------------------------------
    def _normalize_ids_after_copy(self, ids=[], forced=0, REQUEST=None):
      _globals.writeLog( self, "[_normalize_ids_after_copy]: %s"%self.absolute_url())
      
      copy_of_prefix = 'copy_of_'
      id_prefix = REQUEST.get( 'id_prefix')
      REQUEST.set( 'id_prefix', None)
      ob_ids = copy.copy(self.objectIds( self.dGlobalAttrs.keys()))
      for ob in self.objectValues( self.dGlobalAttrs.keys()):
        id = absattr(ob.id)
        if forced or id in ids:
          _globals.writeBlock( self, '[_normalize_ids_after_copy]: %s(%s)'%(id,ob.meta_id))
          
          if id_prefix:
            id_prefix = _globals.id_prefix(id_prefix)
            if id_prefix != _globals.id_prefix(id): 
              new_id = self.getNewId(id_prefix)
              _globals.writeBlock( self, '[_normalize_ids_after_copy]: Rename %s(%s) to %s'%(id,ob.meta_id,new_id))
              self.manage_renameObject(id=id,new_id=new_id)
              self.initObjChildren(REQUEST)
              id = new_id
          
          # Assign new id.
          prefix = _globals.id_prefix(id)
          if prefix.find(copy_of_prefix)==0:
            prefix = prefix[len(copy_of_prefix):]
          if prefix != id:
            new_id = self.getNewId(prefix)
            self.manage_renameObject(id=id,new_id=new_id)
            self.initObjChildren(REQUEST)
          
          bk_lang = REQUEST.get('lang')
          for lang in self.getLangIds():
            REQUEST.set('lang',lang)
            if forced==0:
              # Object-State and Version-Manager.
              if not ob.getAutocommit():
                ob.setObjStateNew(REQUEST,reset=0)
                ob.onChangeObj(REQUEST)
            # Process referential integrity.
            ob.onCopyRefObj(REQUEST)
          
          REQUEST.set('lang',bk_lang)
          
          # Process tree.
          ob._normalize_ids_after_copy(ids=ids,forced=1,REQUEST=REQUEST)


    # --------------------------------------------------------------------------
    #  CopySupport._normalize_ids_after_move:
    # --------------------------------------------------------------------------
    def _normalize_ids_after_move(self, ids=[], forced=0, REQUEST=None):
      _globals.writeLog( self, "[_normalize_ids_after_move]: %s"%self.absolute_url())
      
      copy_of_prefix = 'copy_of_'
      id_prefix = REQUEST.get( 'id_prefix')
      REQUEST.set( 'id_prefix', None)
      ob_ids = copy.copy(self.objectIds( self.dGlobalAttrs.keys()))
      for ob in self.objectValues( self.dGlobalAttrs.keys()):
        id = absattr(ob.id)
        if forced or (id in ids and not copy_of_prefix + id in ob_ids) or (copy_of_prefix + id in ids):
          _globals.writeBlock( self, '[_normalize_ids_after_move]: %s(%s)'%(id,ob.meta_id))
          
          if id_prefix:
            id_prefix = _globals.id_prefix(id_prefix)
            if id_prefix != _globals.id_prefix(id): 
              new_id = self.getNewId(id_prefix)
              _globals.writeBlock( self, '[_normalize_ids_after_move]: Rename %s(%s) to %s'%(id,ob.meta_id,new_id))
              self.manage_renameObject(id=id,new_id=new_id)
              self.initObjChildren(REQUEST)
              id = new_id
          
          # Re-Assign old id.
          if id.find(copy_of_prefix)==0:
            try:
              new_id = id[len(copy_of_prefix):]
              self.manage_renameObject(id=id,new_id=new_id)
              self.initObjChildren(REQUEST)
            except:
              pass
            
          bk_lang = REQUEST.get('lang')
          for lang in self.getLangIds():
            REQUEST.set('lang',lang)
            if forced==0:
              # Object-State and Version-Manager.
              if not ob.getAutocommit():
                ob.setObjStateModified(REQUEST)
                ob.onChangeObj(REQUEST)
            # Process referential integrity.
            ob.onMoveRefObj(REQUEST)
          
          REQUEST.set('lang',bk_lang)
          
          # Process tree.
          ob._normalize_ids_after_move(ids=ids,forced=1,REQUEST=REQUEST)


    ############################################################################
    # CopySupport.manage_cutObjects:
    ############################################################################
    def manage_cutObjects(self, ids=None, REQUEST=None):
      """Put a reference to the objects named in ids in the clip board"""
      _globals.writeLog( self, "[manage_pasteObjs]")
      super( self.__class__, self).manage_cutObjects( ids, REQUEST)
      # Return with message.
      if REQUEST is not None:
        message = ''
        REQUEST.RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(REQUEST['lang'],urllib.quote(message)))


    ############################################################################
    # CopySupport.manage_pasteObjs:
    #
    # Paste previously copied objects into the current object.
    # If calling manage_pasteObjects from python code, pass
    # the result of a previous call to manage_cutObjects or
    # manage_copyObjects as the first argument.
    ############################################################################
    def manage_pasteObjs(self, REQUEST, RESPONSE=None):
      """ CopySupport.manage_pasteObjs """
      _globals.writeBlock( self, "[manage_pasteObjs]")
      t0 = time.time()
      
      # Analyze request
      cp=self._get_cb_copy_data(cb_copy_data=None,REQUEST=REQUEST)
      op=cp[0]
      cp = (0,cp[1])
      cp = _cb_encode(cp)
      ids = self._get_ids(cp)
      oblist = self._get_obs(cp)
      
      # Paste objects.
      self.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
      
      # Sort order (I).
      self._set_sort_ids(ids=ids,op=op,REQUEST=REQUEST)
      
      # Move objects.
      if op==1:
        self._normalize_ids_after_move(ids=ids,forced=0,REQUEST=REQUEST)
      # Copy objects.
      else:
        self._normalize_ids_after_copy(ids=ids,forced=0,REQUEST=REQUEST)
      
      # Keep links (ref_by) synchron.
      if self.getConfProperty('ZMS.InternalLinks.keepsynchron',0)==1:
        obs  = _globals.objectTree( self)
        for ob in obs:
          self.synchronizeRefToObjs()
          self.synchronizeRefByObjs()
      
      # Sort order (II).
      self.normalizeSortIds()
      
      # Return with message.
      if RESPONSE is not None:
        message = self.getZMILangStr('MSG_PASTED')
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(REQUEST['lang'],urllib.quote(message)))

################################################################################
