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
import time
import shutil
from OFS import Moniker
from OFS.CopySupport import _cb_decode, _cb_encode, CopyError
# Product Imports.
from Products.zms import standard
from Products.zms import _globals


# ------------------------------------------------------------------------------
#  CopySupport
# ------------------------------------------------------------------------------
OP_COPY = 0
OP_MOVE = 1


# ------------------------------------------------------------------------------
#  CopySupport._normalize_ids_after_copy:
# ------------------------------------------------------------------------------
def normalize_ids_after_copy(node, id_prefix='e', ids=[]):
  request = node.REQUEST
  copy_of_prefix = 'copy_of_'
  for childNode in node.getChildNodes():
    # validate id
    id = childNode.getId()
    new_id = None
    if '*' in ids or id in ids or id.startswith(copy_of_prefix):
      # reset ref_by
      childNode.ref_by = []
      # init object-state
      if not '*' in ids:
        lang = request.get('lang')
        for langId in node.getLangIds():
          request.set('lang',langId)
          if not node.getAutocommit():
            childNode.setObjStateNew(request,reset=0)
          childNode.onChangeObj(request)
        request.set('lang',lang)
        # new id
        new_id = node.getNewId(id_prefix)
      else:
        # new id
        new_id = node.getNewId(standard.id_prefix(id))
      # reset id
      if new_id is not None and new_id != id and childNode.getParentNode() == node:
        standard.writeBlock(node,'[CopySupport._normalize_ids_after_copy]: rename %s(%s) to %s'%(childNode.absolute_url(),childNode.meta_id,new_id))
        node.manage_renameObject(id=id,new_id=new_id)
      # traverse tree
      normalize_ids_after_copy(childNode, id_prefix, ids=['*'])


# ------------------------------------------------------------------------------
#  CopySupport._normalize_ids_after_move:
# ------------------------------------------------------------------------------
def normalize_ids_after_move(node, id_prefix='e', ids=[]):
  request = node.REQUEST
  copy_of_prefix = 'copy_of_'
  for childNode in node.getChildNodes():
    # validate id
    id = childNode.getId()
    new_id = None
    if '*' in ids or id in ids or id.startswith(copy_of_prefix):
      # init object-state
      if not '*' in ids:
        lang = request.get('lang')
        for langId in node.getLangIds():
          request.set('lang',langId)
          childNode.setObjStateModified(request)
          childNode.onChangeObj(request)
        request.set('lang',lang)
        # new id
        if id.startswith(copy_of_prefix):
          new_id = id[len(id.startswith(copy_of_prefix)):]
        elif standard.id_prefix(id) != id_prefix:
          new_id = node.getNewId(id_prefix)
      # reset id
      if new_id is not None and new_id != id:
        standard.writeBlock(node,'[CopySupport._normalize_ids_after_move]: rename %s(%s) to %s'%(childNode.absolute_url(),childNode.meta_id,new_id))
        node.manage_renameObject(id=id,new_id=new_id)


################################################################################
################################################################################
###
###   class CopySupport
###
################################################################################
################################################################################
class CopySupport(object):

    # --------------------------------------------------------------------------
    #  CopySupport._get_cb_copy_data:
    # --------------------------------------------------------------------------
    def _get_cb_copy_data(self, cb_copy_data=None, REQUEST=None):
      cp=None
      if cb_copy_data is not None:
        cp=cb_copy_data
      else:
        if REQUEST and '__cp' in REQUEST:
          cp=REQUEST['__cp']
      if cp is None:
        raise CopyError('No Data')

      try:
        cp=_cb_decode(cp)
      except:
        raise CopyError('Invalid')

      return cp


    # --------------------------------------------------------------------------
    #  CopySupport._get_obs:
    # --------------------------------------------------------------------------
    def _get_obs(self, cp):

        try:
          cp=_cb_decode(cp)
        except:
          raise CopyError('Invalid')

        oblist=[]
        op=cp[0]
        app = self.getPhysicalRoot()

        for mdata in cp[1]:
          m = Moniker.loadMoniker(mdata)
          try:
            ob = m.bind(app)
          except:
            raise CopyError('Not Found')
          self._verifyObjectPaste(ob)
          oblist.append(ob)

        return oblist

    def cp_get_obs(self, REQUEST):
      cp = self._get_cb_copy_data(cb_copy_data=None, REQUEST=REQUEST)
      op = cp[0]
      cp = (0, cp[1])
      cp = _cb_encode(cp)
      return self._get_obs( cp)


    # --------------------------------------------------------------------------
    #  CopySupport._get_id:
    #
    #  Allow containers to override the generation of
    #  object copy id by attempting to call its _get_id
    #  method, if it exists.
    # --------------------------------------------------------------------------
    def _get_id(self, id):
      copy_of_prefix = 'copy_of_'
      return copy_of_prefix+id


    # --------------------------------------------------------------------------
    #  CopySupport._set_sort_ids:
    #
    #  Group all objects to be copied / moved at new position (given by _sort_id)
    #  in correct sort-order.
    # --------------------------------------------------------------------------
    def _set_sort_ids(self, ids, op, REQUEST):
      standard.writeLog( self, "[CopySupport._set_sort_ids]: %s"%self.absolute_url())
      copy_of_prefix = 'copy_of_'
      sort_id = REQUEST.get('_sort_id', 0) + 1
      for ob in self.getChildNodes():
        id = ob.getId()
        if (id in ids) or (op == OP_MOVE and copy_of_prefix+id in ids):
          ob.setSortId(sort_id)
          sort_id += 1

    # --------------------------------------------------------------------------
    #  CopySupport._copy_blobs_between_clients_with_different_mediadb
    #
    #  If source and target have different mediadb folder settings,
    #  then the data of blob fields is copied as well
    #  to avoid missing images and files due to invalid references.
    # --------------------------------------------------------------------------
    def _copy_blobs_if_other_mediadb(self, **kwargs):
        mode = kwargs.get('mode', None)
        oblist = kwargs.get('oblist', [])
        # identify all BLOB fields
        if mode == 'read_from_source':
            self.REQUEST.set('mediadb_source_location', oblist[0].getMediaDb().getLocation())
            self.blobfields = []
            tree_objs = []
            for obj in oblist:
                lang = obj.REQUEST.get('lang')
                tree_objs.append(obj)
                if obj.getTreeNodes():
                    tree_objs.extend(obj)
                for ob in tree_objs:
                    for langId in ob.getLangIds():
                        for key in ob.getObjAttrs():
                            # TODO: discuss handling of getObjVersions...!? (preview vs live, activated workflow)
                            obj_attr = ob.getObjAttr(key)
                            datatype = obj_attr['datatype_key']
                            if datatype in _globals.DT_BLOBS:
                                ob.REQUEST.set('lang', langId)
                                if ob.attr(key) is not None:
                                    self.blobfields.append({
                                        'id': ob.getId(),
                                        'key': key,
                                        'lang': langId,
                                        'filename': ob.attr(key).getFilename(),
                                        'mediadbfile': ob.attr(key).getMediadbfile(),
                                    })
                                ob.REQUEST.set('lang', lang)

        # copy these files from source to target's MediaDb folder at os-level
        # do nothing if target and source have the same MediaDb folder
        # -> the new pasted object references the same MediaDb file as the source object
        # -> this is true until the next change/upload of a new BLOB in either source or target object
        if mode == 'copy_to_target':
            mediadb_source_location = self.REQUEST.get('mediadb_source_location')
            mediadb_target_location = self.getMediaDb().getLocation()
            try:
                if mediadb_target_location and (mediadb_target_location != mediadb_source_location):
                    for blob in self.blobfields:
                        mediadb_file = blob.get('mediadbfile')
                        if mediadb_file is not None:
                            shutil.copy(f'{mediadb_source_location}/{mediadb_file}', mediadb_target_location)
                            # TODO: remove print
                            print(f'{self.mediadb_source_location}/{mediadb_file}', mediadb_target_location)
            except:
                standard.writeError(self, '[CopySupport._copy_blobs_if_other_mediadb]')
            finally:
                self.blobfields = []


    ############################################################################
    # CopySupport.manage_copyObjects:
    ############################################################################
    def manage_copyObjects(self, ids=None, REQUEST=None, RESPONSE=None):
      """Put a reference to the objects named in ids in the clip board"""
      standard.writeLog( self, "[CopySupport.manage_copyObjects]")
      super( self.__class__, self).manage_copyObjects( ids, REQUEST, RESPONSE)
      # Return with message.
      if RESPONSE is not None:
        message = ''
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(REQUEST['lang'], standard.url_quote(message)))


    ############################################################################
    # CopySupport.manage_cutObjects:
    ############################################################################
    def manage_cutObjects(self, ids=None, REQUEST=None, RESPONSE=None):
      """Put a reference to the objects named in ids in the clip board"""
      standard.writeLog( self, "[CopySupport.manage_cutObjects]")
      cb_copy_data = super( self.__class__, self).manage_cutObjects( ids, REQUEST, RESPONSE)
      # Return with message.
      if RESPONSE is not None:
        message = ''
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(REQUEST['lang'], standard.url_quote(message)))


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
      id_prefix = REQUEST.get('id_prefix','e')
      standard.writeBlock( self, "[CopySupport.manage_pasteObjs]")
      t0 = time.time()

      # Analyze request
      cb_copy_data = self._get_cb_copy_data(cb_copy_data=None, REQUEST=REQUEST)
      op = cb_copy_data[0]
      cp = (op, cb_copy_data[1])
      cp = _cb_encode(cp)
      ids = [self._get_id(x.getId()) for x in self._get_obs(cp)]
      oblist = self._get_obs(cp)

      if self.getMediaDb():
        self._copy_blobs_if_other_mediadb(mode='read_from_source', oblist=oblist)

      # Paste objects.
      action = ['Copy','Move'][op==OP_MOVE]
      standard.triggerEvent(self,'before%sObjsEvt'%action)
      self.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
      standard.triggerEvent(self,'after%sObjsEvt'%action)

      if self.getMediaDb():
        self._copy_blobs_if_other_mediadb(mode='copy_to_target')

      # Sort order (I).
      self._set_sort_ids(ids=ids, op=op, REQUEST=REQUEST)

      # Move objects.
      if op == OP_MOVE:
        normalize_ids_after_move(self,id_prefix=id_prefix,ids=ids)
      # Copy objects.
      else:
        normalize_ids_after_copy(self,id_prefix=id_prefix,ids=ids)

      # Sort order (II).
      self.normalizeSortIds()

      # Return with message.
      if RESPONSE is not None:
        message = self.getZMILangStr('MSG_PASTED')
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(REQUEST['lang'], standard.url_quote(message)))

################################################################################
