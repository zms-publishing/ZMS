"""
_copysupport.py - ZMS Copy and Move Support

This module provides support for copying and moving ZMS objects, 
including normalization of IDs, handling of BLOB fields, and 
clipboard operations.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
import time
import shutil
from OFS import Moniker
from OFS.CopySupport import _cb_decode, _cb_encode, CopyError
# Product Imports.
from Products.zms import standard
from Products.zms import _globals


OP_COPY = 0 # Constant for copy operation
OP_MOVE = 1 # Constant for move operation

################################################################################
# Module-level helper functions
################################################################################

def normalize_ids_after_copy(node, id_prefix='e', ids=None, processed_uids=set()):
    """ 
    The ids of copied objects are normalized to the context-node's id_prefix
    and the ZMS-client's sequence incrementing (acl_sequence).
    After the objects are moved to their new position their ids are normalized,
    that means they are reset to a new id that consists of the id_prefix of the 
    target-context and the next increment of the ZMS-object sequence counter.

    Hint: This function is called after manage_pasteObjs() has moved the objects.

    @param node: context-node
    @param id_prefix: id_prefix of context-node
    @param ids: list of ids to be normalized, None or '*' for all
    @param processed_uids: Set of node IDs already processed (to prevent duplicate onChangeObj calls)
    """
    if ids is None:
        ids = []
    # Determine if this is the initial node being processed (the one directly pasted into) or a child node
    is_initial_target = '*' not in ids
        
    request = node.REQUEST
    copy_of_prefix = 'copy_of_'
    normalized_objs = []

    def switch_languages_and_apply(target_node, func):
        """Helper to apply a function for each language."""
        current_lang = request.get('lang')
        for lang_id in target_node.getLangIds():
            request.set('lang', lang_id)
            func()
        request.set('lang', current_lang)

    # [A] Rename objects in the new context
    for child in node.getChildNodes():
        obj_id = child.getId()
        needs_normalizing = obj_id in ids or obj_id.startswith(copy_of_prefix) or not is_initial_target

        if not needs_normalizing: 
            continue

        # Determine new ID
        new_id_prefix = id_prefix if is_initial_target else standard.id_prefix(obj_id)
        new_id = node.getNewId(new_id_prefix)

        # Perform rename if needed
        if new_id and new_id != obj_id and child.getParentNode() == node:
            standard.writeBlock(
                node, 
                '[CopySupport._normalize_ids_after_copy]: rename %s(%s) to %s' % 
                (child.absolute_url(), child.meta_id, new_id)
            )
            node.manage_renameObject(id=obj_id, new_id=new_id)
            normalized_objs.extend(node.getChildNodes(reid=new_id))

    # [B] Reset backlink-attribute and trigger onChangeObj for all copied child-nodes
    normalized_pages = [e for e in normalized_objs if e.isPage()]
    if normalized_pages:
        # [B1] Inserting page-object(s) with tree-recursion
        for page in normalized_pages:
            page_uid = id(page)  # Use object identity to track processing

            # Skip if already processed
            if page_uid in processed_uids:
                continue

            # Reset ref_by
            page.ref_by = []

            # Handle state and onChange based on context
            if is_initial_target:
                # Only process if not already handled
                def update_page():
                    # Only set STATE_NEW for subpages, not the initial node
                    # is_initial_node=False for all normalized_pages since they are children
                    if not node.getAutocommit():
                        page.setObjStateNew(request, reset=0)
                    page.onChangeObj(request)

                switch_languages_and_apply(page, update_page)
                processed_uids.add(page_uid)

            # Recursively process tree nodes
            tree_pages = page.getTreeNodes(request, node.PAGES)
            if tree_pages:
                for tree_page in tree_pages: 
                    # Recursive call
                    normalize_ids_after_copy(
                        tree_page, 
                        id_prefix, 
                        ids=['*'], 
                        processed_uids=processed_uids
                    )
    else:
        # [B2] Inserting pageelement-object(s)
        # Only trigger onChangeObj on the initial node if it hasn't been processed
        node_uid = id(node)
        if node_uid not in processed_uids:
            def update_node():
                if (not node.getAutocommit()):
                    if not is_initial_target:
                        node.setObjStateNew(request, reset=0)
                    else:
                        # Handle pageelements of initial node
                        normalized_pageelements = [e for e in normalized_objs if not e.isPage()]
                        for normalized_pageelement in normalized_pageelements:
                            normalized_pageelement.setObjStateNew(request,reset=0)
                node.onChangeObj(request)

            switch_languages_and_apply(node, update_node)
            processed_uids.add(node_uid)


def normalize_ids_after_move(node, id_prefix='e', ids=[]):
    """
    Normalize the IDs of moved objects after they are pasted into a new context.

    @param node: The context node where objects are pasted.
    @type node: C{ZMSNode}
    @param id_prefix: The ID prefix for the new context.
    @type id_prefix: C{str}
    @param ids: List of IDs to normalize, or '*' for all.
    @type ids: C{list}
    """
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
                    request.set('lang', langId)
                    childNode.setObjStateModified(request)
                    childNode.onChangeObj(request)
                request.set('lang', lang)
                # new id
                if id.startswith(copy_of_prefix):
                    new_id = id[len(id.startswith(copy_of_prefix)):]
                elif standard.id_prefix(id) != id_prefix:
                    new_id = node.getNewId(id_prefix)
            # reset id
            if new_id is not None and new_id != id:
                standard.writeBlock(node, '[CopySupport._normalize_ids_after_move]: rename %s(%s) to %s' % (childNode.absolute_url(), childNode.meta_id, new_id))
                node.manage_renameObject(id=id, new_id=new_id)


################################################################################
# CLASS CopySupport
################################################################################

class CopySupport(object):
    """
    Provides copy and move support for ZMS objects, including clipboard operations,
    BLOB field handling, and normalization of object IDs after paste.
    """

    def _get_cb_copy_data(self, cb_copy_data=None, REQUEST=None):
        """
        Retrieve and decode clipboard copy data from the request or argument.

        @param cb_copy_data: Encoded clipboard data (optional)
        @type cb_copy_data: C{any}
        @param REQUEST: Zope request object (optional)
        @type REQUEST: C{ZPublisher.HTTPRequest}
        @return: Decoded clipboard data
        @rtype: C{tuple}
        @raise CopyError: If no data or invalid data is found
        """
        cp = None
        if cb_copy_data is not None:
            cp = cb_copy_data
        else:
            if REQUEST and '__cp' in REQUEST:
                cp = REQUEST['__cp']
        if cp is None:
            raise CopyError('No Data')

        try:
            cp = _cb_decode(cp)
        except:
            raise CopyError('Invalid')

        return cp


    def _get_obs(self, cp):
        """
        Decode clipboard data and return the list of objects to be pasted.

        @param cp: Encoded clipboard data
        @type cp: C{any}
        @return: List of objects to paste
        @rtype: C{list}
        @raise CopyError: If data is invalid or objects not found
        """
        try:
            cp = _cb_decode(cp)
        except:
            raise CopyError('Invalid')

        oblist = []
        op = cp[0]
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
        """
        Get the list of objects from the clipboard for the current request.

        @param REQUEST: Zope request object
        @type REQUEST: C{ZPublisher.HTTPRequest}
        @return: List of objects to paste
        @rtype: C{list}
        """
        cp = self._get_cb_copy_data(cb_copy_data=None, REQUEST=REQUEST)
        op = cp[0]
        cp = (0, cp[1])
        cp = _cb_encode(cp)
        return self._get_obs(cp)


    def _get_id(self, id):
        """
        Generate a new ID for a copied object.
        Allow containers to override the generation of
        object copy id by attempting to call its _get_id
        method, if it exists.

        @param id: Original object ID
        @type id: C{str}
        @return: New object ID with 'copy_of_' prefix
        @rtype: C{str}
        """
        copy_of_prefix = 'copy_of_'
        return copy_of_prefix + id


    def _set_sort_ids(self, ids, op, REQUEST):
        """
        Group all objects to be copied / moved at new position (given by _sort_id)
        in correct sort-order.

        @param ids: List of object IDs to sort
        @type ids: C{list}
        @param op: Operation type (OP_COPY or OP_MOVE)
        @type op: C{int}
        @param REQUEST: Zope request object
        @type REQUEST: C{ZPublisher.HTTPRequest}
        """
        standard.writeLog(self, "[CopySupport._set_sort_ids]: %s" % self.absolute_url())
        copy_of_prefix = 'copy_of_'
        sort_id = REQUEST.get('_sort_id', 0) + 1
        for ob in self.getChildNodes():
            id = ob.getId()
            if (id in ids) or (op == OP_MOVE and copy_of_prefix + id in ids):
                ob.setSortId(sort_id)
                sort_id += 1


    def _copy_blobs_if_other_mediadb(self, **kwargs):
        """
        If source and target have different mediadb folder settings,
        then the data of blob fields is copied as well
        to avoid missing images and files due to invalid references.

        @param kwargs: mode ('read_from_source' or 'copy_to_target'), oblist (list of objects)
        @type kwargs: C{dict}
        """
        mode = kwargs.get('mode', None)
        oblist = kwargs.get('oblist', [])
        # identify all BLOB fields
        if mode == 'read_from_source':
            if len(oblist) > 0 and oblist[0].getMediaDb() is not None:
                self.REQUEST.set('mediadb_source_location', oblist[0].getMediaDb().getLocation())
            self.blobfields = []
            tree_objs = []
            for obj in oblist:
                lang = obj.REQUEST.get('lang')
                tree_objs.append(obj)
                if obj.getTreeNodes():
                    tree_objs.extend(obj.getTreeNodes())
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
            except:
                standard.writeError(self, '[CopySupport._copy_blobs_if_other_mediadb]')
            finally:
                self.blobfields = []


    def manage_copyObject(self, ids=[], REQUEST=None, RESPONSE=None):
        """
        Put a reference to the objects named in ids in the clipboard.

        @param ids: List of object IDs to copy (optional)
        @type ids: C{list}
        @param REQUEST: Zope request object (optional)
        @type REQUEST: C{ZPublisher.HTTPRequest}
        @param RESPONSE: Zope response object (optional)
        @type RESPONSE: C{ZPublisher.HTTPResponse}
        """
        context = self
        if not ids:
            ids = [self.getId()]
            context = self.aq_parent
        context.manage_copyObjects(ids, REQUEST, RESPONSE)
        # Return with message.
        message = self.getZMILangStr('MSG_COPIEDOBJS')
        if RESPONSE is None:
            RESPONSE = self.REQUEST.RESPONSE
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s' % (REQUEST.get('lang', context.getPrimaryLanguage()), message))


    def manage_cutObject(self, ids=[], REQUEST=None, RESPONSE=None):
        """
        Put a reference to the objects named in ids in the clipboard for cutting.

        @param ids: List of object IDs to cut (optional)
        @type ids: C{list}
        @param REQUEST: Zope request object (optional)
        @type REQUEST: C{ZPublisher.HTTPRequest}
        @param RESPONSE: Zope response object (optional)
        @type RESPONSE: C{ZPublisher.HTTPResponse}
        """
        context = self
        if not ids:
            ids = [self.getId()]
            context = self.aq_parent
        context.manage_cutObjects(ids, REQUEST)
        # Return with message.
        message = self.getZMILangStr('MSG_CUTOBJS')
        if RESPONSE is None:
            RESPONSE = self.REQUEST.RESPONSE
        RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s' % (REQUEST.get('lang', context.getPrimaryLanguage()), message)) 


    def manage_pasteObjs(self, REQUEST, RESPONSE=None):
        """
        Paste previously copied or cut objects into the current object.

        Handles both copy and move operations, manages BLOB data if necessary,
        triggers before/after events, normalizes object IDs, and ensures correct
        sort order after the paste.

        @param REQUEST: The current Zope request object.
        @type REQUEST: C{ZPublisher.HTTPRequest}
        @param RESPONSE: Optional Zope response object.
        @type RESPONSE: C{ZPublisher.HTTPResponse} or C{None}
        @return: None. Redirects to the management interface with a status message.
        """
        id_prefix = REQUEST.get('id_prefix', 'e')
        standard.writeBlock(self, "[CopySupport.manage_pasteObjs]")
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
        action = ['Copy', 'Move'][op == OP_MOVE]
        standard.triggerEvent(self, 'before%sObjsEvt' % action)
        self.manage_pasteObjects(cb_copy_data=None, REQUEST=REQUEST)
        standard.triggerEvent(self, 'after%sObjsEvt' % action)

        if self.getMediaDb():
            self._copy_blobs_if_other_mediadb(mode='copy_to_target')

        # Sort order (I).
        self._set_sort_ids(ids=ids, op=op, REQUEST=REQUEST)

        # Move objects.
        if op == OP_MOVE:
            normalize_ids_after_move(self, id_prefix=id_prefix, ids=ids)
        # Copy objects.
        else:
            normalize_ids_after_copy(self, id_prefix=id_prefix, ids=ids)

        # Sort order (II).
        self.normalizeSortIds()

        # Return with message.
        if RESPONSE is not None:
            message = self.getZMILangStr('MSG_PASTED')
            message += ' (in ' + str(int((time.time() - t0) * 100.0) / 100.0) + ' secs.)'
            RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s' % (REQUEST['lang'], standard.url_quote(message)))
