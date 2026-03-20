"""
zmslinkelement.py

Link element implementation for ZMS content trees.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
import json
import sys
# Product Imports.
from Products.zms import rest_api
from Products.zms import standard
from Products.zms import zmscontainerobject
from Products.zms import zmscustom
from Products.zms import zmsobject
from Products.zms import zmsproxyobject
from Products.zms import zmslinkelement
from zope.globalrequest import getRequest


"""
################################################################################
# class ConstraintViolation(Exception):
#
# General exception class to indicate constraint violations.
################################################################################
"""
class ConstraintViolation(Exception):
  """Signal that a link element update violates an embedding constraint."""
  pass


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMSLinkElement(zmscustom.ZMSCustom):
    """
    Represent a link element that can resolve, embed, or proxy other content.
    """

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSLinkElement"

    # Management Options.
    # -------------------
    def manage_options(self):
      """Handle the ZMI action 'manage_options'."""
      return ( 
        {'label': 'TAB_EDIT',    'action': 'manage_main'},
        {'label': 'TAB_HISTORY', 'action': 'manage_UndoVersionForm'},
        )

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
        'manage', 'manage_main', 'manage_workspace',
        'manage_changeProperties', 'manage_changeTempBlobjProperty',
        'manage_moveObjUp', 'manage_moveObjDown', 'manage_moveObjToPos',
        'manage_cutObjects', 'manage_copyObjects', 'manage_pasteObjs',
        'manage_ajaxDragDrop', 'manage_ajaxZMIActions',
        'manage_userForm', 'manage_user',
        )
    __ac_permissions__=(
        ('ZMS Author', __authorPermissions__),
        )


    def getSelfPROXY(self, proxy, meta_type=None):
      """
      Resolve the effective object for the proxy context.

      @param proxy: Proxy or referenced object to resolve against.
      @type proxy: C{object}
      @param meta_type: Optional meta type constraint.
      @type meta_type: C{str} | C{None}
      @return: The resolved object for the current proxy context.
      @rtype: C{object}
      """
      return zmsobject.ZMSObject.getSelf( proxy, meta_type)


    def getSelf(self, meta_type=None):
      """
      Return the effective object for this link element.

      @param meta_type: Optional meta type constraint.
      @type meta_type: C{str} | C{None}
      @return: The resolved object for this element or its proxy.
      @rtype: C{object}
      """
      proxy = self.getProxy()
      rtn = self.getSelfPROXY( proxy, meta_type)
      return rtn


    def getEmbedType(self):
      """
      Return the configured embedding mode for this link element.

      Special handling for _embed_type, because it is a raw attribute and not a property.
      The value is stored as the raw attribute C{_embed_type}. If it is not set,
      the method falls back to the legacy object property C{attr_type}.

      @return: Embedding mode such as C{'embed'}, C{'recursive'}, C{'remote'},
        or an empty value.
      @rtype: C{str} | C{None}
      """
      # _embed_type is a raw attribute and should be accessed directly
      embed_type = getattr(self, '_embed_type', None)
      # if _embed_type is not set, try to get it from the property (for backward compatibility)
      if embed_type is None:
        request = getattr(self, 'REQUEST', getRequest())
        embed_type = self.getObjAttrValue( self.getObjAttr( 'attr_type'), request)
      return embed_type


    def setEmbedType(self, REQUEST):
      """
      Persist the requested embedding mode on the raw C{_embed_type} attribute.

      Special handling for _embed_type, because it is a raw attribute 
      and not a property. If the selected mode would recursively embed an 
      ancestor, the value is replaced with C{'cyclic'} so callers can react 
      to the invalid state.

      @param REQUEST: Request carrying the submitted C{attr_type} value.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: None
      @rtype: C{None}
      """
      embed_type = REQUEST.get('attr_type', '')
      if embed_type in [ 'embed', 'recursive', 'remote']:
        # check for cyclic embedding
        ref_obj = self.getRefObj()
        if ref_obj is not None and ref_obj.isAncestor( self):
          embed_type = 'cyclic' # Error!
      self._embed_type = embed_type


    def isEmbedded(self, REQUEST=None):
      """Return whether this element renders another object inline."""
      rtn = self.getEmbedType() in [ 'embed', 'recursive', 'remote']
      return rtn


    def isEmbeddedRecursive(self, REQUEST=None):
      """Return whether this element uses recursive embedding."""
      rtn = self.getEmbedType() in [ 'recursive']
      return rtn


    ############################################################################
    # Properties
    ############################################################################

    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """
      Update link element properties from the ZMI form submission.

      The method stores XML-backed properties, marks the object as modified,
      recalculates the raw embed type, and redirects back to the management UI
      with a status message.

      @param lang: Active management language.
      @type lang: C{str}
      @param REQUEST: Current ZMI request.
      @type REQUEST: ZPublisher.HTTPRequest
      @param RESPONSE: Response used for the redirect.
      @type RESPONSE: ZPublisher.HTTPResponse
      @return: Redirect response pointing back to the management form.
      @rtype: ZPublisher.HTTPResponse
      """

      target_ob = self.getParentNode()
      if REQUEST.get('menulock',0) == 1:
        # Remain in Current Menu
        target_ob = self
      target = REQUEST.get( 'manage_target', '%s/manage_main'%target_ob.absolute_url())
      message = ''
      if REQUEST.get('btn', '') not in  [ 'BTN_CANCEL', 'BTN_BACK']:
        try:
          # Object State
          self.setObjStateModified(REQUEST)
          # Properties
          for key in self.getObjAttrs():
            obj_attr = self.getObjAttr(key)
            if obj_attr['xml']:
              self.setReqProperty(key, REQUEST)
          # VersionManager
          self.onChangeObj(REQUEST)
          # Special handling for _embed_type, because it is a raw attribute and not a property
          self.setEmbedType(REQUEST)
          # Success Message
          message = self.getZMILangStr('MSG_CHANGED')
        # Failure Message
        except ConstraintViolation:
          target = REQUEST.get( 'manage_target', '%s/manage_main'%self.absolute_url())
          message = "[ConstraintViolation]: " + str( sys.exc_info()[1])
      
      # Return with message.
      target = standard.url_append_params( target, { 'lang': lang, 'manage_tabs_message': message})
      target = '%s#zmi_item_%s'%( target, self.id)
      return RESPONSE.redirect( target)


    def getRef(self):
      """
      Return the stored link target reference.

      The reference is read from C{attr_ref} in the language derived from the
      current coverage value.

      @return: Link target reference string.
      @rtype: C{str}
      """
      coverage = self.getDCCoverage()
      req = {'preview':'preview','lang':coverage[coverage.find('.')+1:]}
      ref = self.getObjAttrValue( self.getObjAttr( 'attr_ref'), req) 
      return ref


    def getRefObj(self):
      """
      Resolve and cache the referenced object for this link element.

      The lookup result is buffered in the request to avoid repeated traversal
      and link resolution while rendering a page.

      @return: Referenced object or C{None} if the target cannot be resolved.
      @rtype: C{object} | C{None}
      """
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      docelmnt = self.getDocumentElement()
      reqBuffId = 'getRefObj.%s'%self.get_uid()
      try: return docelmnt.fetchReqBuff(reqBuffId)
      except: pass
      ref_obj = self.getLinkObj(self.getRef())
      if ref_obj == self:
        ref_obj = None
      if ref_obj is not None and ref_obj.meta_type == 'ZMSLinkElement':
        ref_obj = ref_obj.getRefObj()
      #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
      return docelmnt.storeReqBuff(reqBuffId, ref_obj)


    def getRemoteObj(self):
      """
      Fetch remote metadata for a link element with embed type C{'remote'}.

      The returned mapping is expected to be JSON produced by the remote REST
      API endpoint for the current language.

      @return: Parsed JSON payload from the remote object, or an empty mapping
        on failure.
      @rtype: C{dict}
      """
      value = {}
      ref = self.getRef()
      remote_ref = rest_api.get_rest_api_url( ref)  
      try:
        lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
        value = self.http_import( '%s/%s'%(remote_ref,lang))
        value = json.loads(value)
      except:
        standard.writeError(self, '[getRemoteObj]: can\'t embed from remote: ref=%s'%ref)
      return value


    def isMetaTypePROXY(self, proxy, meta_type, REQUEST={'preview':'preview'}):
      """
      Check whether this element or its resolved target matches a meta type.

      For recursively embedded elements the check is delegated to the proxy.
      For directly embedded elements it also checks the referenced object unless
      the special C{NOREF} or C{NORESOLVEREF} markers suppress resolution.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param meta_type: Meta type or list of meta types to test.
      @type meta_type: C{str} | C{list}
      @param REQUEST: Request context used by downstream checks.
      @type REQUEST: C{dict}
      @return: C{True} if the element or resolved target matches.
      @rtype: C{bool}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        b = proxy.isMetaType( meta_type, REQUEST)
      else:
        b = False
        if not (self.NOREF == meta_type or (isinstance(meta_type, list) and self.NOREF in meta_type)):
          b = b or zmsobject.ZMSObject.isMetaType(self, meta_type, REQUEST)
          if self.isEmbedded():
            ref_obj = self.getRefObj()
            if ref_obj is not None and not (self.NORESOLVEREF == meta_type or (isinstance(meta_type, list) and self.NORESOLVEREF in meta_type)):
              b = b or ref_obj.isMetaType(meta_type, REQUEST)
      return b

    def isMetaType(self, meta_type, REQUEST={'preview':'preview'}):
      """
      Return whether this element matches the requested meta type.

      @param meta_type: Meta type or list of meta types to test.
      @type meta_type: C{str} | C{list}
      @param REQUEST: Request context used by downstream checks.
      @type REQUEST: C{dict}
      @return: C{True} if this element or its resolved target matches.
      @rtype: C{bool}
      """
      proxy = self.getProxy()
      rtn = self.isMetaTypePROXY( proxy, meta_type, REQUEST)
      return rtn


    def getLevelPROXY(self, proxy):
      """
      Return the level resolved through the active proxy context.
      For recursively embedded elements the level is delegated to the proxy.
      For directly embedded elements the level is calculated based on the parent
      node level unless the parent is the same as the proxy, in which case it is
      treated as the root of the embedding context and assigned level 0.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @return: Effective hierarchy level for this element.
      @rtype: C{int}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getLevel()
      else:
        rtn = self.getParentNode().getLevel() + 1
      return rtn


    def getLevel(self):
      """Return the effective hierarchy level of this element."""
      proxy = self.getProxy()
      rtn = self.getLevelPROXY( proxy)
      return rtn


    def getParentNodePROXY(self, proxy):
      """Return the parent node visible through the current proxy context."""
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getParentNode()
      else:
        rtn = getattr( self, 'aq_parent', getattr( self, 'base', None))
      return rtn


    getParentNode__roles__ = None
    def getParentNode(self):
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      proxy = self.getProxy()
      rtn = self.getParentNodePROXY( proxy)
      return rtn


    def getTitlealtPROXY(self, proxy, REQUEST):
      """
      Resolve the alternate title through the proxy or reference chain.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Alternate title resolved for the current embedding context.
      @rtype: C{str}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getTitlealt( REQUEST)
      else:
        rtn = self.getObjProperty('titlealt', REQUEST)
        if len(rtn) == 0:
          ref_obj = self.getRefObj()
          if ref_obj is None:
            rtn = super(ZMSLinkElement, self).getTitlealt(REQUEST)
          else:
            rtn = ref_obj.getTitlealt(REQUEST)
      return rtn


    def getTitlealt(self, REQUEST):
      """
      Return the alternate title for this element.

      Remote embeddings read the value from the remote payload; other modes use
      the local proxy or referenced object and fall back to the display type.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Alternate title string.
      @rtype: C{str}
      """
      rtn = ''
      if self.getEmbedType() == 'remote':
        return self.getRemoteObj().get('titlealt','Unknown')
      else:
        proxy = self.getProxy()
        rtn = self.getTitlealtPROXY( proxy, REQUEST)
      if not rtn:
        rtn = self.display_type(meta_id=self.meta_id)
      return rtn


    def getTitlePROXY(self, proxy, REQUEST):
      """
      Resolve the title through the proxy or reference chain.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Title resolved for the current embedding context.
      @rtype: C{str}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getTitle( REQUEST)
      else:
        rtn = self.getObjProperty('title', REQUEST)
        if len(rtn) == 0:
          ref_obj = self.getRefObj()
          if ref_obj is None:
            rtn = super(ZMSLinkElement, self).getTitle(REQUEST)
          else:
            rtn = ref_obj.getTitle(REQUEST)
      return rtn


    def getTitle(self, REQUEST):
      """
      Return the display title for this element.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Resolved title or a fallback display type label.
      @rtype: C{str}
      """
      rtn = ''
      if self.getEmbedType() == 'remote':
        return self.getRemoteObj().get('title','Unknown')
      else:
        proxy = self.getProxy()
        rtn = self.getTitlePROXY( proxy, REQUEST)
      if len(rtn) == 0:
        rtn = self.display_type()
      return rtn


    def display_icon(self, *args, **kwargs): 
      """
      Return the icon markup for this element or its referenced target.

      @param args: Positional arguments for the icon display.
      @type args: tuple
      @param kwargs: Keyword arguments for the icon display.
      @type kwargs: dict
      @return: Icon markup for this element or its referenced target.
      @rtype: C{str}
      """
      context = self
      if self.isEmbedded():
        ref_obj = self.getRefObj()
        if ref_obj is not None:
          context = ref_obj
      return zmsobject.ZMSObject.display_icon(context, args, kwargs)


    def isActive(self, REQUEST):
      """
      Return whether the element is active in the current request context.

      Embedded and remote link elements additionally respect the resolved target
      activity state.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: C{True} if the element should be treated as active.
      @rtype: C{bool}
      """
      active = super(ZMSLinkElement, self).isActive(REQUEST) 
      if self.getEmbedType() == 'remote':
        return self.getRemoteObj().get('active',False)
      else:
        ref_obj = self.getRefObj()
        if ref_obj is not None:
            active = active and ref_obj.isActive(REQUEST)
      return active


    def isPageContainer(self):
      """
      Return C{False} because link elements are never page containers.

      @return: C{False} because link elements are never page containers.
      @rtype: C{bool}
      """
      return False


    def isPage(self):
      """
      Return whether this element resolves to a page-like target.
      Embedded and remote link elements are treated as pages when their resolved
      target has the corresponding flag set.

      @return: C{True} if this element should be treated as a page-like target.
      @rtype: C{bool}
       """
      rtnVal = False
      if self.getEmbedType() == 'remote':
        return self.getRemoteObj().get('is_page',False)
      elif self.isEmbedded():
        ref_obj = self.getRefObj()
        if ref_obj is not None:
          rtnVal = rtnVal or ref_obj.isPage()
      return rtnVal


    def isPageElement(self):
      """
      Return whether this element behaves like a page element.
      Embedded and remote link elements are treated as page elements when their
      resolved target has the corresponding flag set.
      @return: C{True} if this element should be treated as a page element.
      @rtype: C{bool}
      """
      request = getattr(self, 'REQUEST', getRequest())
      rtnVal = False
      if self.getEmbedType() == 'remote':
        return self.getRemoteObj().get('is_page_element',False)
      else:
        if self.isEmbedded():
          ref_obj = self.getRefObj()
          if ref_obj is not None:
            rtnVal = rtnVal or ref_obj.isPageElement()
          else:
            rtnVal = rtnVal or True
        elif self.getObjProperty('align', request) not in ['', 'NONE']:
          rtnVal = rtnVal or True
      return rtnVal


    def getTypePROXY(self, proxy): 
      """
      Return the effective type resolved through embedding or proxying.
      Overrides getType of zmscustom.ZMSCustom.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @return: Effective type.
      @rtype: C{str}
      """
      rtn = 'ZMSObject'
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getType()
      elif self.isEmbedded():
        ref_obj = self.getRefObj()
        if ref_obj is not None:
           rtn = ref_obj.getType()
      return rtn


    def getType(self): 
      """Return the effective type for this link element."""
      proxy = self.getProxy()
      rtn = self.getTypePROXY( proxy)
      return rtn


    def getObjPropertyPROXY(self, proxy, key, REQUEST={}, default=None):
      """
      Read an object property directly from the supplied proxy object.
      Overrides getObjProperty of _objattrs.ObjAttrs. 

      @param proxy: Object or proxy that owns the attribute.
      @type proxy: C{object}
      @param key: Attribute identifier.
      @type key: C{str}
      @param REQUEST: Request context used for multilingual values.
      @type REQUEST: C{dict}
      @param default: Unused compatibility parameter.
      @type default: C{any}
      @return: Attribute value resolved from the proxy.
      @rtype: C{any}
      """
      obj_attr = proxy.getObjAttr( key)
      value = proxy.getObjAttrValue( obj_attr, REQUEST) 
      return value


    def getObjProperty(self, key, REQUEST={}, default=None):
      """
      Return a property value from this element, its proxy, or its reference.

      The method first checks the link element itself, then falls back to the
      local base implementation, recursive proxies, or the referenced object,
      depending on the embedding mode.

      @param key: Attribute identifier.
      @type key: C{str}
      @param REQUEST: Request context used for multilingual and preview values.
      @type REQUEST: C{dict}
      @param default: Default value when no property can be resolved.
      @type default: C{any}
      @return: Resolved property value.
      @rtype: C{any}
      """
      value = None
      value = self.getObjPropertyPROXY( self, key, REQUEST, default)
      # First exit...
      if (value is None or value=='' or (value==0 and not isinstance(value, bool))) and \
        key in self.getMetaobjAttrIds( self.meta_id):
        value = zmsobject.ZMSObject.getObjProperty( self, key, REQUEST, default)
      # Second exit...
      if (value is None or value=='' or (value == 0 and not isinstance(value, bool))) and \
          key not in ['active', 'change_uid', 'change_dt', 'work_uid', 'work_dt', 'internal_dict', 'attr_ref', 'attr_dc_coverage']:
        recursive = self.isEmbeddedRecursive()
        if recursive:
          proxy = self.getProxy()
          if proxy != self and proxy is not None:
            value = self.getObjPropertyPROXY( proxy, key, REQUEST, default)
        else:
          ref_obj = self.getRefObj()
          if ref_obj != self and ref_obj is not None:
            value = self.getObjPropertyPROXY( ref_obj, key, REQUEST, default)
          # Last exit...
          if (value is None or len(str(value)) == 0 or (value == 0 and not isinstance(value, bool))):
            value = zmsobject.ZMSObject.getObjProperty( self, key, REQUEST, default)
      return value


    def getNavItemsPROXY(self, proxy, current, REQUEST, opt={}, depth=0):
      """
      Return navigation items for the current proxy context.
      Overrides getNavItems of zmscontainerobject.ZMSContainerObject.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param current: Current navigation node.
      @type current: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param opt: Navigation options.
      @type opt: C{dict}
      @param depth: Current navigation depth.
      @type depth: C{int}
      @return: Navigation items visible through the embedding context.
      @rtype: C{list}
      """
      rtn = []
      recursive = self.isEmbeddedRecursive()
      if proxy != self and proxy is not None and recursive:
        rtn = proxy.getNavItems( current, REQUEST, opt, depth)
      else:
        ref_obj = self.getRefObj()
        if isinstance(ref_obj, zmscontainerobject.ZMSContainerObject):
          rtn = super(zmslinkelement.ZMSLinkElement, self).getNavItems( current, REQUEST, opt, depth)
      return rtn


    def getNavItems(self, current, REQUEST, opt={}, depth=0):
      """
      Return navigation items for this element.

      @param current: Current navigation node.
      @type current: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param opt: Navigation options.
      @type opt: C{dict}
      @param depth: Current navigation depth.
      @type depth: C{int}
      @return: Navigation items visible for this element.
      @rtype: C{list}
      """
      proxy = self.getProxy()
      rtn = self.getNavItemsPROXY( proxy, current, REQUEST, opt, depth)
      return rtn


    def getNavElementsPROXY(self, proxy, REQUEST, expand_tree=1, current_child=None, subElements=[]):
      """
      Return navigation elements for the current proxy context.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param expand_tree: Flag controlling tree expansion.
      @type expand_tree: C{int}
      @param current_child: Currently selected child node.
      @type current_child: C{object} | C{None}
      @param subElements: Accumulator for nested elements.
      @type subElements: C{list}
      @return: Navigation elements visible through the embedding context.
      @rtype: C{list}
      """
      rtn = []
      recursive = self.isEmbeddedRecursive()
      if proxy != self and proxy is not None and recursive:
        rtn = proxy.getNavElements( REQUEST, expand_tree, current_child, subElements)
      elif self.isEmbedded():
        ref_obj = self.getRefObj()
        if isinstance(ref_obj, zmscontainerobject.ZMSContainerObject):
          rtn = super(zmslinkelement.ZMSLinkElement, zself).getNavElements( REQUEST, expand_tree, current_child, subElements)
      return rtn


    def getNavElements(self, REQUEST, expand_tree=1, current_child=None, subElements=[]):
      """
      Return navigation elements for this link element.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param expand_tree: Flag controlling tree expansion.
      @type expand_tree: C{int}
      @param current_child: Currently selected child node.
      @type current_child: C{object} | C{None}
      @param subElements: Accumulator for nested elements.
      @type subElements: C{list}
      @return: Navigation elements visible for this element.
      @rtype: C{list}
      """
      proxy = self.getProxy()
      rtn = self.getNavElementsPROXY( proxy, REQUEST, expand_tree, current_child, subElements)
      return rtn


    ############################################################################
    # HTML-Presentation
    ############################################################################

    def getHref2IndexHtmlPROXY(self, proxy, REQUEST, deep=1): 
      """
      Return the index HTML URL resolved through the current proxy context.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param deep: Depth flag forwarded to the base implementation.
      @type deep: C{int}
      @return: Resolved index HTML URL.
      @rtype: C{str}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.getHref2IndexHtml( REQUEST, deep)
      else:
        rtn = zmsobject.ZMSObject.getHref2IndexHtml( proxy, REQUEST, deep)
      return rtn


    def getHref2IndexHtml(self, REQUEST, deep=1): 
      """
      Return the index HTML URL for this link element.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @param deep: Depth flag forwarded to the proxy lookup.
      @type deep: C{int}
      @return: Resolved index HTML URL.
      @rtype: C{str}
      """
      proxy = self.getProxy()
      rtn = self.getHref2IndexHtmlPROXY( proxy, REQUEST, deep)
      return rtn


    def embedRemoteContent(self, REQUEST):
      """
      Retrieve rendered body content from a remote reference.

      The remote endpoint is only contacted when the embed type is C{'remote'}.

      @param REQUEST: Current request context.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Remote HTML fragment or C{None} when remote embedding is not
        active.
      @rtype: C{str} | C{None}
      """
      rtn = None
      if self.getEmbedType() == 'remote':
        ref = self.getObjProperty('attr_ref', REQUEST)
        remote_ref = rest_api.get_rest_api_url( ref)  
        try: 
          rtn = self.http_import( remote_ref + '/get_body_content') 
        except: 
          rtn = standard.writeError(self, '[_getBodyContent]: can\'t embed from remote_ref=%s'%remote_ref)
      return rtn


    def _getBodyContent(self, REQUEST):
      """
      Render the body content for the link element (as HTML).

      Depending on the embedding mode this may use remote content, a recursive
      proxy, the referenced object, or the local template output.

      @param REQUEST: Current rendering request.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Rendered HTML body for the element.
      @rtype: C{str}
      """
      rtn = self.embedRemoteContent( REQUEST)
      if rtn is None:
        if self.isEmbedded():
          REQUEST.set('ZMS_RELATIVATE_URL', False)
        proxy = self.getProxy()
        if proxy != self and proxy is not None and self.isEmbeddedRecursive():
          rtn = proxy._getBodyContent(REQUEST)
        elif proxy == self and proxy is not None and self.isEmbedded():
          ref_obj = self.getRefObj()
          if ref_obj is not None and ref_obj != self:
            rtn = ref_obj._getBodyContent( REQUEST)
        else:
          rtn = self._getBodyContentContentEditable(self.metaobj_manager.renderTemplate( self))
        if self.isEmbedded():
          REQUEST.set('ZMS_RELATIVATE_URL', True)
      return rtn


    def renderShort(self, REQUEST):
      """
      Render the compact presentation of the link element.

      Embedded links delegate to the referenced object when possible, while
      non-embedded links fall back to the regular body rendering.

      @param REQUEST: Current rendering request.
      @type REQUEST: ZPublisher.HTTPRequest
      @return: Short HTML rendering for the element.
      @rtype: C{str}
      """
      rtn = self.embedRemoteContent( REQUEST)
      if rtn is None:
        if self.isEmbedded(): 
          REQUEST.set('ZMS_RELATIVATE_URL', False)
          ref_obj = self.getRefObj()
          if ref_obj is None or ref_obj.isPage(): 
            rtn = super(ZMSLinkElement, self).renderShort(REQUEST) 
          elif ref_obj != self: 
            rtn = ref_obj.renderShort(REQUEST) 
          REQUEST.set('ZMS_RELATIVATE_URL', True)
        else: 
          rtn = self._getBodyContent( REQUEST) 
      return rtn


    ############################################################################
    # DOM-Methods
    ############################################################################

    def breadcrumbs_obj_pathPROXY(self, proxy, portalMaster=True):
      """
      Return the breadcrumb path resolved through the current proxy context.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param portalMaster: Include the portal master in the breadcrumb path.
      @type portalMaster: C{bool}
      @return: Breadcrumb object path.
      @rtype: C{list}
      """
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        rtn = proxy.breadcrumbs_obj_path()
      else:
        rtn = zmsobject.ZMSObject.breadcrumbs_obj_path( proxy, portalMaster)
      return rtn


    def breadcrumbs_obj_path(self, portalMaster=True):
      """
      Return the breadcrumb path for this element.

      @param portalMaster: Include the portal master in the breadcrumb path.
      @type portalMaster: C{bool}
      @return: Breadcrumb object path.
      @rtype: C{list}
      """
      proxy = self.getProxy()
      rtn = self.breadcrumbs_obj_pathPROXY( proxy, portalMaster)
      return rtn


    def getTreeNodes(self, REQUEST={}, meta_types=None):
      """
      Return an empty tree node list for link elements.

      Link elements do not contribute their own tree structure here.
      If none, this is a empty node list.

      @param REQUEST: Current request context.
      @type REQUEST: C{dict}
      @param meta_types: Optional meta type filter.
      @type meta_types: C{list} | C{None}
      @return: Empty node list.
      @rtype: C{list}
      """
      return []


    def initProxy(self, base, url_base, proxy, recursive=False):
      """
      Create a C{ZMSProxyObject} for a resolved embedded target.

      @param base: Acquisition base for the proxy.
      @type base: C{object}
      @param url_base: Absolute URL base for the proxy.
      @type url_base: C{str}
      @param proxy: Referenced object that should be exposed as proxy.
      @type proxy: C{object}
      @param recursive: Flag indicating recursive embedding.
      @type recursive: C{bool}
      @return: Proxy object wrapping the referenced node.
      @rtype: ZMSProxyObject
      """
      return zmsproxyobject.ZMSProxyObject( self, base, url_base, proxy.id, proxy, recursive)


    def __proxy__(self):
      """
      Build the proxy object used for recursive embedded traversal.

      @return: This element itself or a proxy wrapping the referenced object.
      @rtype: C{object}
      """
      rtn = self
      req = getattr(self, 'REQUEST', getRequest())
      if req.get( 'URL', '').find( '/manage') < 0 or req.get( 'ZMS_PATH_HANDLER', False):
        if self.isEmbeddedRecursive():
          ref_obj = self.getRefObj()
          if ref_obj is not None:
            recursive = True
            rtn = zmsproxyobject.ZMSProxyObject( self, self.aq_parent, self.absolute_url(), self.id, ref_obj, recursive)
      return rtn


    def getProxy(self):
      """
      Return the cached proxy object for this (embedding) link element.

      The proxy is stored in the request so repeated rendering and traversal use
      the same resolved object.

      @return: This element or its request-cached proxy.
      @rtype: C{object}
      """
      req = getattr(self, 'REQUEST', getRequest())
      key = 'ZMS_PROXY_%s'%self.id
      rtn = req.get(key, None)
      if not rtn:
        rtn = self.__proxy__()
        if rtn != self:
          req.set(key, rtn)
      return rtn


    def getChildNodesPROXY(self, proxy, REQUEST={}, meta_types=None, reid=None):
      """
      Return child nodes for the active proxy or referenced object.

      Recursively embedded elements expose proxied child nodes. Direct embedded
      elements expose non-page children of the referenced object.  
      Overrides original method of zmscontainerobject.ZMSContainerObject.

      @param proxy: Active proxy object.
      @type proxy: C{object}
      @param REQUEST: Current request context.
      @type REQUEST: C{dict}
      @param meta_types: Optional meta type filter.
      @type meta_types: C{list} | C{None}
      @param reid: Optional regular-expression id filter.
      @type reid: C{str} | C{None}
      @return: Child nodes visible through the embedding context.
      @rtype: C{list}
      """
      rtn = []
      if proxy != self and proxy is not None and self.isEmbeddedRecursive():
        recursive = True
        rtn = [self.initProxy( proxy, proxy.absolute_url()+'/'+x.id, x, recursive) for x in proxy.getChildNodes( REQUEST, meta_types, reid)]
      elif proxy == self and proxy is not None and self.isEmbedded():
        ref_obj = self.getRefObj()
        if ref_obj is not None:
          for ob in ref_obj.getChildNodes( REQUEST, meta_types, reid):
            if not ob.isPage():
              rtn.append( ob)
      return rtn

    def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
      """
      Return child nodes visible for this link element.

      @param REQUEST: Current request context.
      @type REQUEST: C{dict}
      @param meta_types: Optional meta type filter.
      @type meta_types: C{list} | C{None}
      @param reid: Optional regular-expression id filter.
      @type reid: C{str} | C{None}
      @return: Resolved child node list.
      @rtype: C{list}
      """
      proxy = self.getProxy()
      rtn = self.getChildNodesPROXY( proxy, REQUEST, meta_types, reid)
      return rtn


    ############################################################################
    # Printable
    ############################################################################

    def printHtmlPROXY(self, proxy, level, sectionizer, REQUEST, deep=True):
      """
      Render the printable HTML through the current proxy or reference.

      Recursive embeddings delegate to the proxy tree, while direct embeddings
      delegate to the referenced object.

      @param proxy: Active proxy object for recursive rendering.
      @type proxy: C{object}
      @param level: Current print depth.
      @type level: C{int}
      @param sectionizer: Helper used to build printable section numbering.
      @type sectionizer: C{any}
      @param REQUEST: Current rendering request.
      @type REQUEST: ZPublisher.HTTPRequest
      @param deep: If true, render nested content recursively.
      @type deep: C{bool}
      @return: Printable HTML fragment.
      @rtype: C{str}
      """
      rtn = ''
      recursive = self.isEmbeddedRecursive()
      if proxy != self and proxy is not None and recursive:
        rtn = proxy.printHtml( level, sectionizer, REQUEST, deep)
      elif self.isEmbedded():
        ref_obj = self.getRefObj()
        if ref_obj is not None:
          rtn = ref_obj.printHtml( level, sectionizer, REQUEST, deep)
      return rtn

    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      """
      Return the printable HTML for this link element.

      @param level: Current print depth.
      @type level: C{int}
      @param sectionizer: Helper used to build printable section numbering.
      @type sectionizer: C{any}
      @param REQUEST: Current rendering request.
      @type REQUEST: ZPublisher.HTTPRequest
      @param deep: If true, render nested content recursively.
      @type deep: C{bool}
      @return: Printable HTML fragment.
      @rtype: C{str}
      """
      proxy = self.getProxy()
      rtn = self.printHtmlPROXY( proxy, level, sectionizer, REQUEST, deep)
      return rtn


# call this to initialize framework classes, which
# does the right thing with the security assertions.
InitializeClass(ZMSLinkElement)
