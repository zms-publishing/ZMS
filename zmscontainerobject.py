################################################################################
# zmscontainerobject.py
#
# $Id: zmscontainerobject.py,v 1.10 2004/11/24 20:54:37 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.10 $
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
from App.Common import package_home
from Globals import HTMLFile
import AccessControl.Role
import copy
import string
import sys
import urllib
import time
# Product Imports.
from zmsobject import ZMSObject
import _accessmanager
import _fileutil
import _globals
import _importable
import _objattrs
import _scormlib
import _versionmanager

__all__= ['ZMSContainerObject']


# ------------------------------------------------------------------------------
#  zmscontainerobject.isPageWithElements:
# ------------------------------------------------------------------------------
def isPageWithElements(obs):
  for ob in obs:
    if ob.isPageElement():
      return True
  return False


# ------------------------------------------------------------------------------
#  zmscontainerobject.getPrevSibling: 
#
#  The node immediately preceding this node, otherwise returns None. 
# ------------------------------------------------------------------------------
def getPrevSibling(self, REQUEST, incResource=False):
  parent = self.getParentNode()
  if parent is not None:
    siblings = parent.getChildNodes(REQUEST,[self.PAGES,self.NORESOLVEREF]) 
    if self in siblings:
      i = siblings.index(self) - 1
      while i >= 0:
        ob = siblings[i]
        if ob.isVisible(REQUEST) and (incResource or not ob.isResource(REQUEST)):
          return ob
        i = i - 1
  return None

# ------------------------------------------------------------------------------
#  zmscontainerobject.getNextSibling: 
#
#  The node immediately following this node, otherwise returns None. 
# ------------------------------------------------------------------------------
def getNextSibling(self, REQUEST, incResource=False):
  parent = self.getParentNode()
  if parent is not None:
    siblings = parent.getChildNodes(REQUEST,[self.PAGES,self.NORESOLVEREF]) 
    siblingIds = map( lambda x: x.id, siblings)
    if self.id in siblingIds:
      i = siblingIds.index( self.id) + 1
      while i < len(siblings):
        ob = siblings[i]
        if ob.isVisible(REQUEST) and (incResource or not ob.isResource(REQUEST)):
          return ob
        i = i + 1
  return None



################################################################################
################################################################################
###
###   Abstract Class ZMSContainerObject
###
################################################################################
################################################################################
class ZMSContainerObject(
	ZMSObject,
	AccessControl.Role.RoleManager,		# Security manager.
	_accessmanager.AccessableContainer,	# Access manager.
	_importable.Importable,
	_scormlib.SCORMLib,
	_versionmanager.VersionManagerContainer
	):

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_system',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    # Interface.
    # ----------
    pageelement_TOC = HTMLFile('dtml/ZMSContainerObject/pageelement_toc', globals())
    
    # Management Interface.
    # ---------------------
    main_js = HTMLFile('dtml/ZMSContainerObject/main_js', globals()) # JavaScript
    manage_main = HTMLFile('dtml/ZMSContainerObject/manage_main', globals()) 
    manage_main_btn = HTMLFile('dtml/ZMSContainerObject/manage_main_btn', globals()) # Buttons
    manage_main_change = HTMLFile('dtml/ZMSContainerObject/manage_main_change', globals()) # Change (Author & Date)
    manage_main_actions = HTMLFile('dtml/ZMSContainerObject/manage_main_actions', globals()) # Actions
    manage_search = HTMLFile('dtml/ZMSContainerObject/manage_search', globals()) 
    manage_search_attrs = HTMLFile('dtml/ZMSContainerObject/manage_search_attrs', globals()) 
    manage_properties = HTMLFile('dtml/ZMSObject/manage_main', globals())
    manage_system = HTMLFile('dtml/ZMSContainerObject/manage_system', globals())
    manage_importexport = HTMLFile('dtml/ZMSContainerObject/manage_importexport', globals()) 
    manage_importexportFtp = HTMLFile('dtml/ZMSContainerObject/manage_importexportftp', globals()) 


    # Sitemap.
    # --------
    sitemap_layout0 = HTMLFile('dtml/ZMSContainerObject/sitemap/version0', globals()) 
    sitemap_layout1 = HTMLFile('dtml/ZMSContainerObject/sitemap/version1', globals()) 
    sitemap_layout2 = HTMLFile('dtml/ZMSContainerObject/sitemap/version2', globals())
    sitemap_layout3 = HTMLFile('dtml/ZMSContainerObject/sitemap/version3', globals())


    # Role Manager.
    # -------------
    def manage_addZMSCustom(self, meta_id, values={}, REQUEST=None):
      values['meta_id'] = meta_id
      return self.manage_addZMSObject('ZMSCustom',values,REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_addZMSObject:
    # --------------------------------------------------------------------------
    def manage_addZMSObject(self, meta_type, values, REQUEST):
      
      attrs = []
      for key in values.keys():
        attrs.extend([key,values[key]])
      
      # Get id.
      if 'id_prefix' in attrs:
        i = attrs.index('id_prefix')
        id_prefix = attrs[i+1]
        id = self.getNewId(id_prefix)
        del attrs[i] # Key.
        del attrs[i] # Value.
      elif 'id' in attrs:
        i = attrs.index('id')
        id = attrs[i+1]
        del attrs[i] # Key.
        del attrs[i] # Value.
      else:
        id = self.getNewId()
      
      # Get sort id.
      key = 'sort_id'
      if key in attrs and attrs.index(key)%2 == 0:
        i = attrs.index(key)
        sort_id = attrs[i+1]
        del attrs[i] # Key.
        del attrs[i] # Value.
      else:
        sort_id = 99999
      
      # Create new object.
      newNode = self.dGlobalAttrs[meta_type]['obj_class'](id,sort_id)
      self._setObject(newNode.id, newNode)
      node = getattr(self,newNode.id)
      
      # Init meta object.
      key = 'meta_id'
      if meta_type == 'ZMSCustom' and key in attrs and attrs.index(key)%2 == 0:
        i = attrs.index(key)
        meta_id = attrs[i+1]
        setattr(node,key,meta_id)
        del attrs[i] # Key.
        del attrs[i] # Value.
      
      # Object state.
      node.setObjStateNew(REQUEST)
      
      # Init properties.
      key = 'active'
      if not (key in attrs and attrs.index(key)%2 == 0):
        attrs.extend([key,1])
      for i in range(len(attrs)/2):
        key = attrs[i*2]
        value = attrs[i*2+1]
        node.setObjProperty(key,value,REQUEST['lang'])
      
      # Version manager.
      node.onChangeObj(REQUEST)
      
      # Normalize sort-ids.
      self.normalizeSortIds(_globals.id_prefix(id))
      
      # Return object.
      return node


    ############################################################################
    ###
    ###   Trashcan
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.moveObjsToTrashcan
    # --------------------------------------------------------------------------
    def moveObjsToTrashcan(self, ids, REQUEST):
      """
      Move objects to trashcan.
      @param ids: List of object-ids.
      @type ids: C{list}
      @rtype: C{None}
      """
      if self.meta_id == 'ZMSTrashcan':
        return
      trashcan = self.getTrashcan()
      # Move (Cut & Paste).
      try:
        cb_copy_data = self.manage_cutObjects(ids,REQUEST)
        trashcan.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
      except:
        if len(ids) > 1:
          except_ids = []
          for id in ids:
            try:
              cb_copy_data = self.manage_cutObjects([id],REQUEST)
              trashcan.manage_pasteObjects(cb_copy_data=None,REQUEST=REQUEST)
            except:
              except_ids.append(id)
        else:
          except_ids = ids
        if len(except_ids) > 0:
          _globals.writeException(self,'[moveObjsToTrashcan]: Unexpected Exception: ids=%s!'%str(except_ids))
      trashcan.normalizeSortIds()
      # Sort-IDs.
      self.normalizeSortIds()


    ############################################################################
    #  ZMSContainerObject.manage_eraseObjs:
    ############################################################################
    def manage_eraseObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """ 
      Delete a subordinate object physically:
      The objects specified in 'ids' get deleted.
      @param lang: Language-id.
      @type ids: C{string}
      @param ids: List of object-ids.
      @type ids: C{list}
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @param RESPONSE: the triggering request
      @type RESPONSE: ZPublisher.HTTPResponse
      """ 
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      count = len(ids)
      self.manage_delObjects(ids=ids)
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_DELETED')%count
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    ############################################################################
    #  ZMSContainerObject.manage_undoObjs:
    ############################################################################
    def manage_undoObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """
      Undo a subordinate object:
      The objects specified in 'ids' get undone (changes are rolled-back).
      @param lang: Language-id.
      @type ids: C{string}
      @param ids: List of object-ids.
      @type ids: C{list}
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @param RESPONSE: the triggering request
      @type RESPONSE: ZPublisher.HTTPResponse
      """ 
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      c = 0
      for child in self.getChildNodes():
        if child.id in ids:
          if child.inObjStates( [ 'STATE_NEW', 'STATE_MODIFIED', 'STATE_DELETED'], REQUEST):
            child.rollbackObjChanges( self, REQUEST)
            c += 1
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_UNDONE')%c
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    ############################################################################
    #  ZMSContainerObject.manage_deleteObjs:
    ############################################################################
    def manage_deleteObjs(self, lang, ids, REQUEST, RESPONSE=None):
      """
      Delete a subordinate object logically:
      The objects specified in 'ids' get deleted (moved to trashcan).
      @param lang: Language-id.
      @type ids: C{string}
      @param ids: List of object-ids.
      @type ids: C{list}
      @param REQUEST: the triggering request
      @type REQUEST: ZPublisher.HTTPRequest
      @param RESPONSE: the triggering request
      @type RESPONSE: ZPublisher.HTTPResponse
      """
      
      self._checkWebDAVLock()
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      versionMgrCntnrs = []
      for child in self.getChildNodes():
        if child.id in ids:
          if child.getAutocommit() or child.inObjStates(['STATE_NEW'],REQUEST):
            self.moveObjsToTrashcan([child.id], REQUEST)
          else:
            child.setObjStateDeleted(REQUEST)
            versionCntnr = child.getVersionContainer()
            if versionCntnr not in versionMgrCntnrs:
              versionMgrCntnrs.append( versionCntnr)
      
      ##### VersionManager ####
      for versionCntnr in versionMgrCntnrs:
        versionCntnr.onChangeObj(REQUEST)
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_TRASHED')%len(ids)
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('target','manage_main')
        return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getContentType
    # --------------------------------------------------------------------------
    def getContentType( self, REQUEST):
      """
      Returns MIME-type (text/html).
      @rtype: C{string}
      """
      return 'text/html'


    ############################################################################
    ###
    ###  Drag'n Drop
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_ajaxDragDrop:
    # --------------------------------------------------------------------------
    def manage_ajaxDragDrop( self, lang, target, REQUEST, RESPONSE):
      """ ZMSContainerObject.manage_ajaxDragDrop """
      rc = 0
      message = self.getZMILangStr('MSG_PASTED')
      try:
        before = False
        into = False
        if target.startswith('-'):
          before = True
          target = target[1:]
        elif target.endswith('-'):
          target = target[:-1]
        else:
          into = True
        ob = self.getLinkObj( target)
        sort_id = ob.getSortId()
        print "manage_ajaxDragDrop", self, "before=", before, "into=", into
        if into:
          sort_id = 0
        else:
          ob = ob.getParentNode()
          if before:
            sort_id = sort_id - 1
          else:
            sort_id = sort_id + 1
        setattr( self, 'sort_id', _globals.format_sort_id(sort_id))
        cb_copy_data = self.getParentNode().manage_cutObjects([self.id])
        ob.manage_pasteObjects(cb_copy_data)
        ob.normalizeSortIds()
      except:
        tp, vl, tb = sys.exc_info()
        rc = -1
        message = str(tp)+': '+str(vl)
        _globals.writeException(self,'[manage_ajaxDragDrop]')
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'manage_ajaxDragDrop.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = self.getXmlHeader()
      xml += '<result code="%i" message="%s">\n'%(rc,message)
      xml += "</result>\n"
      return xml


    ############################################################################
    ###
    ###  Page-Navigation
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getFirstPage:
    # --------------------------------------------------------------------------
    def getFirstPage(self, REQUEST, incResource=False, root=None):
      root = _globals.nvl(root,self.getDocumentElement())
      return root
    
    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getPrevPage:
    # --------------------------------------------------------------------------
    def getPrevPage(self, REQUEST, incResource=False, root=None):
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      while True:
        ob = getPrevSibling(self,REQUEST,incResource)
        if ob is None:
          parent = self.getParentNode()
          if parent is not None:
            ob = parent.getPrevPage(REQUEST,incResource,root)
        else:
          ob = ob.getLastPage(REQUEST,incResource,ob)
        if not ob is None and not ob.isMetaType(self.PAGES,REQUEST):
          ob = ob.getPrevPage(REQUEST,incResource,root)
        if ob is None or ob.isMetaType(self.PAGES,REQUEST):
          break
      return ob

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNextPage:
    # --------------------------------------------------------------------------
    def getNextPage(self, REQUEST, incResource=False, root=None): 
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      while True:
        children = self.filteredChildNodes(REQUEST,self.PAGES)
        if len(children) > 0:
          ob = children[0]
        else:
          current = self
          while ob is None and current is not None:
            ob = getNextSibling(current,REQUEST,incResource)
            current = current.getParentNode()
        if not ob is None and not ob.isMetaType(self.PAGES,REQUEST):
          ob = ob.getNextPage(REQUEST,incResource,root)
        if ob is None or ob.isMetaType(self.PAGES,REQUEST):
          break
      return ob

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getLastPage:
    # --------------------------------------------------------------------------
    def getLastPage(self, REQUEST, incResource=False, root=None):
      ob = None
      root = _globals.nvl(root,self.getDocumentElement())
      children = [root]
      while len( children) > 0:
        i = len( children)-1
        while i >= 0:
          if (incResource or not children[i].isResource(REQUEST)):
            ob = children[i]
            i = 0
          i = i - 1
        if ob == self:
          break
        children = ob.filteredChildNodes(REQUEST,self.PAGES)
      return ob


    ############################################################################
    ###  
    ###  Object-actions of management interface
    ### 
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.filtered_insert_actions:
    # --------------------------------------------------------------------------
    def filtered_insert_actions(self, path='', objAttr=None):
      actions = []
      if self.meta_id == 'ZMSTrashcan':
        return actions
      REQUEST = self.REQUEST
      lang = REQUEST['lang']
      auth_user = REQUEST['AUTHENTICATED_USER']
      
      if objAttr is None:
        objAttr = self.getMetaobjAttr( self.meta_id, 'e')
      
      #-- Objects.
      repetitive = objAttr.get('repetitive',0)==1
      if repetitive or len(self.getObjChildren(objAttr['id'],REQUEST))==0:
        meta_ids = []
        if objAttr['type']=='*':
          for meta_id in objAttr['keys']:
            if meta_id.startswith('type(') and meta_id.endswith(')'):
              for metaObjId in self.getMetaobjIds():
                metaObj = self.getMetaobj( metaObjId)
                if metaObj['type'] == meta_id[5:-1] and metaObj['enabled'] == 1:
                  meta_ids.append( metaObj['id'])
            else:
              meta_ids.append( meta_id)
        else:
          meta_ids.append( objAttr['type'])
        for meta_id in meta_ids:
          metaObj = self.getMetaobj(meta_id)
          ob_access = True
          ob_manage_access = self.getMetaobjAttr(meta_id,'manage_access')
          if ob_manage_access is not None:
            try:
              ob_access = _globals.dt_html(self,ob_manage_access['custom'],REQUEST)
            except:
              _globals.writeException( self, '[filtered_insert_actions]: can\'t get manage_access from %s'%meta_id)
          can_insert = True
          if objAttr['type']=='*':
            can_insert = can_insert and (type(ob_access) is not dict) or (ob_access.get( 'insert') is None) or (len( self.intersection_list( ob_access.get( 'insert'), self.getUserRoles(auth_user))) > 0)
            can_insert = can_insert and ((metaObj.get( 'access') is None) or (metaObj.get( 'access', {}).get( 'insert') is None) or (len( self.intersection_list( metaObj.get( 'access').get( 'insert'), self.getUserRoles(auth_user))) > 0))
            can_insert = can_insert and ((metaObj.get( 'access') is None) or (metaObj.get( 'access', {}).get( 'insert_custom','{$}') == '{$}') or (len( filter( lambda x: (self.absolute_url()+'/').find(x)==0, map( lambda x: self.getDocumentElement().absolute_url()+'/'+x[2:-1]+'/', self.string_list(metaObj.get( 'access', {}).get( 'insert_custom','{$}'))))) > 0))
          if can_insert:
            if meta_id in self.dGlobalAttrs.keys():
              value = 'manage_addProduct/zms/%s'%self.dGlobalAttrs[meta_id]['constructor']
            else:
              if metaObj['type']=='ZMSModule':
                value = 'manage_addZMSModule'
              else:
                value = 'manage_addProduct/zms/manage_addzmscustomform'
            action = (self.display_type(REQUEST,meta_id),value)
            if action not in actions:
              actions.append( action)
      
      #-- Sort.
      actions.sort()
      
      #-- Headline,
      if len(actions) > 0:
        actions.insert(0,('----- %s -----'%self.getZMILangStr('ACTION_INSERT')%self.display_type(REQUEST),''))
      
      # Return action list.
      return actions


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.ajaxFilteredContainerActions:
    # --------------------------------------------------------------------------
    def ajaxFilteredContainerActions(self, REQUEST):
      """
      Returns AJAX-XML with filtered-child-actions.
      """
      
      #-- Get actions.
      path = ''
      cmdpath = ''
      if self.getLevel() > 0:
        path = '../'
        cmdpath = self.id + '/'
      actions = []
      actions.extend( self.filtered_insert_actions())
      actions.extend( map( lambda x: (x[0], path+x[1]), filter(lambda x: path == '' or x[1].find(path) < 0, self.filtered_edit_actions(path,cmdpath))))
      actions.extend( self.filtered_workflow_actions())
      
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxFilteredContainerActions.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      self.f_standard_html_request( self, REQUEST)
      xml = self.getXmlHeader()
      xml += "<select id=\""+self.id+"\">\n"
      for action in actions:
        xml += "<option label=\"" + _globals.html_quote(action[0]) + "\" value=\"" + action[1] + "\"/>\n"
      xml += "</select>\n"
      return xml


    ############################################################################
    ###
    ###  HTML-Presentation
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNavItems:
    #
    #  Items of main-navigation in content-area.
    #
    #	@param	current	the currently displayed page
    #	@param	REQUEST	the triggering http-request
    #	@param	opt	the dictionary of options:
    #			'id' (string='')		= id of base ul-element
    #			'add_self' (boolean=False)	= add self to list
    #			'deep' (boolean=True)		= process child nodes
    #			'complete' (boolean=False)	= process complete subtree
    #			'maxdepth' (int=100)	= limits node list to a given depth
    #			'maxlevel' (int=100)	= limits node list to a given level
    # --------------------------------------------------------------------------
    def getNavItems(self, current, REQUEST, opt={}, depth=0):
      items = []
      obs = []
      if opt.get('add_self',False):
        obs.append( self)
        opt['add_self'] = False
      obs.extend( self.filteredChildNodes(REQUEST,self.PAGES))
      for ob in obs:
        if not ob.isResource(REQUEST):
          if len( items) == 0:
            items.append( '<ul')
            if opt.get('id',''):
              items.append( ' id="%s"'%opt.get('id',''))
              opt['id'] = ''
            items.append('>\n')
          css = []
          if ob.id == current.id:
            css.append( 'current')
            css.append( 'active')
            css.append( ob.meta_id + '1') 
          elif ob.id != self.id and ob.id in current.getPhysicalPath():
            css.append( 'active')
            css.append( ob.meta_id + '1') 
          else: 
            css.append( 'inactive')
            css.append( ob.meta_id + '0')            
          items.append('<li')
          items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<a ')
          items.append(' href="%s"'%ob.getHref2IndexHtml(REQUEST))
          items.append(' title="%s"'%_globals.html_quote(ob.getTitle(REQUEST)))
          if len(css) > 0:
            items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<span>%s</span>'%_globals.html_quote(ob.getTitlealt(REQUEST)))
          items.append('</a>')
          if (depth < opt.get('maxdepth',100)) and \
             (ob.getLevel() < opt.get('maxlevel',100)) and \
             ((opt.get('complete',False)) or \
              (opt.get('deep',True) and ob.id != self.id and ob.id in current.getPhysicalPath())):
            items.append( ob.getNavItems( current, REQUEST, opt, depth+1))
          items.append('</li>\n')
      if len( items) > 0:
        items.append( '</ul>\n')
      return ''.join(items)


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNavElements: 
    #
    #  Elements of main-navigation in content-area.
    # --------------------------------------------------------------------------
    def getNavElements(self, REQUEST, expand_tree=1, current_child=None, subElements=[]):
      elmnts = []
      # Child navigation.
      obs = self.filteredChildNodes(REQUEST)
      if not expand_tree and \
         current_child is not None and \
         current_child.meta_id in ['ZMS','ZMSFolder'] and \
         isPageWithElements(obs) and \
         self.getLevel() > 0:
        obs = [current_child]
      for ob in obs:
        if ob.isPage() and not ob.isResource(REQUEST): 
          elmnts.append(ob)
        if current_child is not None and \
           current_child.id == ob.id:
          elmnts.extend(subElements)
      # Parent navigation.
      parent = self.getParentNode()
      if parent is not None:
        elmnts = parent.getNavElements(REQUEST,expand_tree,self,elmnts)
      # Return elements.
      return elmnts


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getIndexNavElements: 
    #
    #  Elements of index-navigation in content-area.
    # --------------------------------------------------------------------------
    def getIndexNavElements(self, REQUEST):
      indexNavElmnts = []
      # Retrieve elements.
      if REQUEST.get('op','')=='':
        indexNavElmnts = filter(lambda ob: ob.isPage() and ob.isMetaType(['ZMSDocument','ZMSCustom']) and not ob.isResource(REQUEST),self.filteredChildNodes(REQUEST,self.PAGES))
      # Return elements.
      return indexNavElmnts


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.printHtml:
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      """
      Renders print presentation of a container-object.
      """
      html = ''
      
      # Title.
      sectionizer.processLevel( level)
      title = self.getTitle( REQUEST)
      title = '%s %s'%(str(sectionizer),title)
      REQUEST.set( 'ZMS_SECTIONIZED_TITLE', '<h%i>%s</h%i>'%( level, title, level))
      
      # pageregionBefore
      attr = REQUEST.get( 'ZMS_PAGEREGION_BEFORE', 'pageregionBefore')
      if hasattr( self, attr):
        html += getattr( self, attr)( self, REQUEST)
      elif hasattr( self, 'bodyContent_PagePre'):
        html += getattr( self, 'bodyContent_PagePre')( self,REQUEST)
    
      # bodyContent
      subsectionizer = {}
      for ob in self.filteredChildNodes( REQUEST, self.PAGEELEMENTS):
        if not subsectionizer.has_key( ob.meta_type):
          subsectionizer[ob.meta_type] = sectionizer.clone()
        subsectionizer[ob.meta_type].processLevel(level+1)
        html += ob.printHtml( level+1, subsectionizer[ob.meta_type], REQUEST)
      
      # pageregionAfter
      attr = REQUEST.get( 'ZMS_PAGEREGION_AFTER', 'pageregionAfter')
      if hasattr( self, attr):
        html += getattr( self, attr)( self, REQUEST)
      elif hasattr( self ,'bodyContent_PagePost'):
        html += getattr( self ,'bodyContent_PagePost')( self,REQUEST)
      
      # Container-Objects.
      if deep:
        for ob in self.filteredChildNodes(REQUEST,self.PAGES):
          html += ob.printHtml( level+1, sectionizer, REQUEST, deep)
      
      return html


    ############################################################################
    ###
    ###   DOM-Methods
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.filteredTreeNodes:
    #
    # --------------------------------------------------------------------------
    def filteredTreeNodes(self, REQUEST, meta_types, order_by=None, order_dir=None, max_len=None, recursive=True):
      """
      Returns a NodeList that contains all visible children of this subtree 
      in correct order. If none, this is a empty NodeList. 
      """
      rtn = []
      
      #-- Process tree.
      if not self.meta_type == 'ZMSLinkElement':
        obs = self.getChildNodes(REQUEST)
        for ob in obs:
          append = True
          append = append and ob.isMetaType(meta_types)
          append = append and ob.isVisible(REQUEST)
          if append: 
            rtn.append(ob)
          if not append or (append and recursive):
            if ob.isPage():
              rtn.extend(ob.filteredTreeNodes(REQUEST,meta_types,None,order_dir,None,recursive))
      
      #-- Order.
      if order_by is not None:
      
        # order by select-options of special object
        options = []
        if type(meta_types) is str and meta_types in self.getMetaobjIds():
          metaObj = self.getMetaobj(meta_types)
          attrs = metaObj['attrs']
          for attr in attrs:
            if attr['id'] == order_by:
              options = attr.get('keys',[])
      
        # collect object-items
        tmp = []
        for ob in rtn:
          value = ob.getObjProperty(order_by,REQUEST)
          if value in options:
            value = options.index(value)
          tmp.append((value,ob))
        
        # sort object-items
        tmp.sort()
        
        # truncate sort-id from sorted object-items
        rtn = map( lambda ob: ob[1], tmp)
        if order_dir == 'desc': 
          rtn.reverse()
      
      #-- Size.
      if max_len is not None:
        if len(rtn) > max_len:
          rtn = rtn[:max_len]
      
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.firstFilteredChildNode:
    # --------------------------------------------------------------------------
    def firstFilteredChildNode(self, REQUEST={}, meta_types=None):
      """
      Returns the first visible child of this node.
      """
      for node in self.getChildNodes(REQUEST,meta_types):
        if node.isVisible(REQUEST):
          return node
      return None


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.filteredChildNodes:
    #
    # --------------------------------------------------------------------------
    def filteredChildNodes(self, REQUEST={}, meta_types=None):
      """
      Returns a NodeList that contains all visible children of this node in 
      correct order. If none, this is a empty NodeList. 
      """
      return filter(lambda ob: ob.isVisible(REQUEST),self.getChildNodes(REQUEST,meta_types))


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getChildNodes:
    #
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST=None, meta_types=None):
      """
      Returns a NodeList that contains all children of this node in correct 
      order. If none, this is a empty NodeList. 
      """
      obs = []
      try:
        types = self.dGlobalAttrs.keys()
        # Get all object-items.
        if REQUEST is None:
          obs = map( lambda x: ( getattr( x, 'sort_id', ''), x), self.objectValues( types))
        # Get selected object-items.
        else:
          lang = REQUEST.get('lang',None)
          # Get coverages.
          multilang = lang is not None and len(self.getLangs().keys()) > 1
          if multilang:
            key_coverage = 'attr_dc_coverage'
            prim_lang = self.getPrimaryLanguage()
            coverages = []
            coverages.extend(['global.'+lang,'local.'+lang])
            for parent in self.getParentLanguages( lang):
              coverages.append('global.'+parent)
          for ob in filter( lambda x: x.isMetaType( meta_types, REQUEST), self.objectValues( types)):
            if multilang:
              obj_vers = ob.getObjVersion( REQUEST)
              coverage = getattr( obj_vers, key_coverage, '')
              if coverage in [ '', None]: coverage = 'global.' + prim_lang
            if not multilang or coverage in coverages:
              proxy = ob.__proxy__()
              if proxy is not None:
                sort_id = getattr( ob, 'sort_id', '')
                if ob.isPage():
                  sort_id = 's' + sort_id
                obs.append( ( sort_id, proxy))
        # Sort child-nodes.
        obs.sort()
      except Exception, exc:
        if self.getConfProperty('ZMS.protected_mode',0):
          _globals.writeException(self,'[getChildNodes.protected]')
        else:
          raise exc
      # Return child-nodes in correct sort-order.
      return map(lambda ob: ob[1],obs)


    ############################################################################
    ###  
    ###  Sort-Order
    ### 
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.normalizeSortIds:
    #
    #  Normalizes sort-ids for all children of this node 
    # --------------------------------------------------------------------------
    def normalizeSortIds(self, id_prefix='e'):
      # Get all object-items.
      obs = []
      for ob in self.objectValues( self.dGlobalAttrs.keys()):
        sort_id = getattr( ob, 'sort_id', '')
        proxy = ob.__proxy__()
        if proxy is not None:
          sort_id = getattr( ob, 'sort_id', '')
          if proxy.isPage(): sort_id = 's%s'%sort_id
          obs.append((sort_id,ob))
      # Sort child-nodes.
      obs.sort()
      # Normalize sort-order.
      new_sort_id = 10
      for ( sort_id, ob) in obs:
       if ob.id[:len(id_prefix)] == id_prefix:
         ob.setSortId( new_sort_id)
         new_sort_id  += 10


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNewSortId:
    #
    #  Get new Sort-ID.
    # --------------------------------------------------------------------------
    def getNewSortId(self):
      new_sort_id = 0
      for ob in self.getChildNodes():
        sort_id = ob.getSortId()
        if sort_id > new_sort_id:
          new_sort_id = sort_id
      new_sort_id = new_sort_id + 10
      return new_sort_id


    ############################################################################
    #
    #   Module
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_addZMSModule:
    # --------------------------------------------------------------------------
    def manage_addZMSModule(self, lang, _sort_id, custom, REQUEST, RESPONSE):
      """
      Add module.
      """
      meta_id = self.getMetaobjId( custom)
      metaObj = self.getMetaobj( meta_id)
      key = self.getMetaobjAttrIds( meta_id)[0]
      attr = self.getMetaobjAttr( meta_id, key)
      zexp = attr[ 'custom']
      filename = zexp.getFilename()
      fileid = filename[:filename.find('.')]
      path = package_home(globals()) + '/import/'
      _fileutil.exportObj( zexp, path + filename)
      _fileutil.importZexp( self, path, filename)
      _fileutil.remove( path + filename)
      
      ##### Create ####
      id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
      newid = self.getNewId(id_prefix)
      
      ##### Rename ####
      self.manage_renameObject(fileid,newid)
      
      ##### Normalize Sort-IDs ####
      obj = getattr( self, newid)
      obj.sort_id = _sort_id
      self.normalizeSortIds( id_prefix)
      
      # Return with message.
      message = self.getZMILangStr('MSG_INSERTED')%custom
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),newid,lang,urllib.quote(message)))

################################################################################

