################################################################################
# zmscontainerobject.py
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
from App.Common import package_home
from OFS.role import RoleManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import re
import string
import sys
import urllib
import time
# Product Imports.
from zmsobject import ZMSObject
import _accessmanager
import _confmanager
import _fileutil
import _globals
import _objattrs
import _versionmanager
import _zmi_actions_util

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
    RoleManager,
    _accessmanager.AccessableContainer,
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

    # Management Interface.
    # ---------------------
    manage_main = PageTemplateFile('zpt/ZMSObject/manage_main', globals())
    zmi_manage_main_change = PageTemplateFile('zpt/ZMSContainerObject/zmi_manage_main_change', globals())
    zmi_manage_main_grid = PageTemplateFile('zpt/ZMSContainerObject/main_grid', globals())
    manage_container = PageTemplateFile('zpt/ZMSContainerObject/manage_main', globals())
    manage_search = PageTemplateFile('zpt/ZMSContainerObject/manage_search', globals())
    manage_properties = PageTemplateFile('zpt/ZMSObject/manage_main', globals())
    manage_system = PageTemplateFile('zpt/ZMSContainerObject/manage_system', globals())
    manage_importexport = PageTemplateFile('zpt/ZMSContainerObject/manage_importexport', globals())
    manage_tasks = PageTemplateFile('zpt/versionmanager/manage_tasks', globals())


    # Role Manager.
    # -------------
    def manage_addZMSCustom(self, meta_id, values={}, REQUEST=None):
      values['meta_id'] = meta_id
      return self.manage_addZMSObject('ZMSCustom',values,REQUEST)
    def zmi_manage_addZMSCustom(self, meta_id, values={}, REQUEST=None):
      return self.manage_addZMSCustom(meta_id, values, REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSContainerObject.manage_addZMSObject:
    # --------------------------------------------------------------------------
    def manage_addZMSObject(self, meta_type, values, REQUEST):
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
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
      key = 'attr_dc_coverage'
      if not (key in attrs and attrs.index(key)%2 == 0):
        attrs.extend([key,'global.%s'%lang])
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
    # Move objects to trashcan.
    #
    # @param ids: List of object-ids.
    # @type ids: C{list}
    # @rtype: C{None}
    # --------------------------------------------------------------------------
    def moveObjsToTrashcan(self, ids, REQUEST):
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
          _globals.writeError(self,'[moveObjsToTrashcan]: Unexpected Exception: ids=%s!'%str(except_ids))
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
      
      message = ''
      t0 = time.time()
      
      ##### Delete objects ####
      count = len(ids)
      self.manage_delObjects(ids=ids)
      
      # Return with message.
      if RESPONSE is not None:
        message += self.getZMILangStr('MSG_DELETED')%count
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
        target = REQUEST.get('manage_target','manage_main')
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
        target = REQUEST.get('manage_target','manage_main')
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
        target = REQUEST.get('manage_target','manage_main')
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
        _globals.writeError(self,'[manage_ajaxDragDrop]')
      #-- Build xml.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'manage_ajaxDragDrop.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
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
      """
      Returns the first page of the tree from root (or document-element if root
      is not given).
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: the first page
      @rtype: C{zmsobject.ZMSObject}
      """
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
            if self.getHref2IndexHtml(REQUEST) == parent.getHref2IndexHtml(REQUEST):
              ob = parent.getPrevPage(REQUEST,incResource,parent)
            else:
              ob = parent
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
      """
      Returns the last page of the tree from root (or document-element if root
      is not given).
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: the last page
      @rtype: C{zmsobject.ZMSObject}
      """
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

    def manage_ajaxZMIActions(self, context_id, REQUEST, RESPONSE):
      """
      Returns ZMI actions.
      
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: the response
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      """
      
      #-- Get actions.
      actions = []
      container = self
      objPath = ''
      context = None 
      if context_id == '':
        context = container
        actions.extend( _zmi_actions_util.zmi_actions(self,self))
      else:
        attr_id = _globals.id_prefix(context_id)
        if context_id in container.objectIds():
            context = getattr(container,context_id,None)
        actions.extend( _zmi_actions_util.zmi_actions(container,context,attr_id))
        if context is not None:
          objPath = context.id+'/'
      if context is not None:
        actions.extend( context.filtered_workflow_actions(objPath))
      
      #-- Build json.
      RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      rtn = self.str_json({'id':context_id,'actions':actions})
      return rtn


    ############################################################################
    ###
    ###  HTML-Presentation
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSContainerObject.getNavItems:
    # --------------------------------------------------------------------------
    def getNavItems(self, current, REQUEST, opt={}, depth=0):
      """
      Returns html-formatted (unordered) list of navigation-items.
      Uses the following classes
        - I{current} item is current-element
        - I{(in-)active} items is parent of current-element or current-element
        - I{restricted} item has restricted access
      @param current: the currently displayed page
      @type current: C{zmsobject.ZMSObject}
      @param REQUEST: the triggering request
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param opt: the dictionary of options
          - I{id} (C{string=''}) id of base ul-element
          - I{cssclass} (C{string=''}) css class of base ul-element
          - I{add_self} (C{boolean=False}) add self to list
          - I{deep} (C{boolean=True}) process child nodes
          - I{complete} (C{boolean=False}) process complete subtree
          - I{maxdepth} (C{int=100}) limits node list to a given depth
      @return: the Html
      @rtype: C{string}
      """
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
            if opt.get('cssclass',''):
              items.append( ' class="%s"'%opt.get('cssclass',''))
              opt['cssclass'] = ''
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
          if ob.attr( 'attr_dc_accessrights_restricted'):
            css.append( 'restricted')
          if len(ob.filteredChildNodes(REQUEST,self.PAGES))>0:
            css.append( 'childpages')
          items.append('<li')
          items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<a ')
          items.append(' href="%s"'%ob.getHref2IndexHtml(REQUEST))
          items.append(' title="%s"'%ob.getTitle(REQUEST))
          if len(css) > 0:
            items.append(' class="%s"'%(' '.join(css)))
          items.append('>')
          items.append('<span>%s</span>'%ob.getTitlealt(REQUEST))
          items.append('</a>')
          if (max(depth,ob.getLevel()) < opt.get('maxdepth',100)) and \
             ((opt.get('complete',False)) or \
              (opt.get('deep',True) and ob.id != self.id and \
                (ob.id in current.getPhysicalPath() or \
                 ob.id in REQUEST['URL'].split('/')))):
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
    def getChildNodes(self, REQUEST=None, meta_types=None, reid=None):
      """
      Returns a NodeList that contains all children of this node in correct 
      order. If none, this is a empty NodeList. 
      """
      childNodes = []
      types = self.dGlobalAttrs.keys()
      obs = self.objectValues( types)
      # Filter ids.
      if reid:
        pattern = re.compile( reid)
        obs = filter( lambda x: pattern.match( x.id), obs)
      # Get all object-items.
      if REQUEST is None:
        childNodes = map( lambda x: ( getattr( x, 'sort_id', ''), x), obs)
      # Get selected object-items.
      else:
        prim_lang = self.getPrimaryLanguage()
        lang = REQUEST.get('lang',None)
        # Get coverages.
        coverages = [ '', 'obligation', None]
        if lang is not None:
          coverages.extend( [ 'global.'+lang, 'local.'+lang])
          coverages.extend( map( lambda x: 'global.'+x, self.getParentLanguages( lang)))
        for ob in filter( lambda x: x.isMetaType( meta_types, REQUEST), obs):
          coverage = None
          if lang is not None:
            obj_vers = ob.getObjVersion( REQUEST)
            coverage = getattr( obj_vers, 'attr_dc_coverage', '')
          if coverage in coverages:
            proxy = ob.__proxy__()
            if proxy is not None:
              sort_id = getattr( ob, 'sort_id', '')
              if ob.isPage():
                sort_id = 's' + sort_id
              childNodes.append( ( sort_id, proxy))
      # Sort child-nodes.
      childNodes.sort()
      # Return child-nodes in correct sort-order.
      return map(lambda x: x[1],childNodes)


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
    #  ZMSContainerObject.manage_addZMSCustomDefault:
    # --------------------------------------------------------------------------
    def manage_addZMSCustomDefault(self, lang, id_prefix, _sort_id, REQUEST, RESPONSE):
      """
      Add default.
      """
      attr = self.getMetaobjAttr( self.meta_id, id_prefix)
      zexp = attr[ 'custom']
      new_id = self.getNewId(id_prefix)
      _fileutil.import_zexp(self,zexp,new_id,id_prefix,_sort_id)
      
      # Return with message.
      message = self.getZMILangStr('MSG_INSERTED')%attr['name']
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),new_id,lang,urllib.quote(message)))

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
      id_prefix = _globals.id_prefix(REQUEST.get('id_prefix','e'))
      new_id = self.getNewId(id_prefix)
      _fileutil.import_zexp(self,zexp,new_id,id_prefix,_sort_id)
      
      # Return with message.
      message = self.getZMILangStr('MSG_INSERTED')%custom
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),new_id,lang,urllib.quote(message)))

################################################################################