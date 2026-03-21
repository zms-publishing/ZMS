"""
zmsproxyobject.py - ZMS Proxy Object

Provides ZMSProxyObject for core content-object traversal and manipulation.

The ZMSProxyObject class is a wrapper/proxy object used throughout the ZMS runtime to:
  - Enable transparent traversal of ZMS content hierarchies by encapsulating access to underlying 
    content objects and their metadata.
  - Provide a consistent interface for accessing object attributes, child nodes, and properties 
    while delegating actual operations to the proxied object.
  - Support recursive traversal of nested content structures, allowing child nodes to be wrapped 
    as proxy objects for uniform access patterns.
  - Implement metadata access protocols (IZMSMetamodelProvider, IZMSFormatProvider) for 
    introspection of object type definitions and text formatting capabilities.
  - Handle URL construction and physical path resolution within the ZMS content tree.
  - Facilitate request/response handling and access control checks across the object hierarchy.
  - Enable lazy evaluation and computed properties without exposing underlying implementation details.

This abstraction enables flexible content traversal strategies, caching mechanisms, and 
alternative rendering pipelines while maintaining a unified API for ZMS components that work 
with content objects.

Key responsibilities:
  - Wrapping proxied ZMS objects with additional traversal metadata (root, base, url_base)
  - Delegating method calls to the proxied object while transforming return values as needed
  - Supporting both simple and recursive child node traversal patterns
  - Managing object hierarchy relationships (parent/child navigation, physical paths)
  - Providing unified access to metadata definitions and format specifications

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSMetamodelProvider, IZMSFormatProvider
from Products.zms import zmscontainerobject


@implementer(
      IZMSMetamodelProvider.IZMSMetamodelProvider,
      IZMSFormatProvider.IZMSFormatProvider)
class ZMSProxyObject(zmscontainerobject.ZMSContainerObject):
    """Provide helpers for ZMSProxyObject."""

    def __init__(self, root, base, url_base, id, proxy, recursive=False):
      """ Constructor """
      self.__root__ = root
      self.base = base
      self.url_base = url_base
      self.meta_type = proxy.meta_type
      self.meta_id = proxy.meta_id
      self.dGlobalAttrs = proxy.dGlobalAttrs
      self.REQUEST = proxy.REQUEST
      self.id = id
      self.proxy = proxy
      self.recursive = recursive


    def __proxy__(self):
      """Implement '__proxy__'."""
      return self


    def getProxy(self):
      """Return proxy."""
      return self


    def getPhysicalPath(self):
      """Return physicalpath."""
      rtn = list( self.__root__.getPhysicalPath())
      for id in list( self.base.getPhysicalPath())+[self.id]:
        if id not in rtn:
          rtn.append( id)
      return tuple( rtn)


    def __request__(self, REQUEST):
      """Implement '__request__'."""
      proxy = self.proxy
      if isinstance(REQUEST, bytes) or isinstance(REQUEST, str):
        return proxy.REQUEST
      return REQUEST


    def absolute_url(self, relative=0):
      """Implement 'absolute_url'."""
      url_base = self.url_base
      rtn = url_base
      return rtn


    def getMetaobjAttrIds(self, meta_id, types=[]):
      """Return metaobjattrids."""
      proxy = self.proxy
      rtn = proxy.getMetaobjAttrIds( meta_id, types)
      return rtn


    def getMetaobjAttr(self, meta_id, key):
      """Return metaobjattr."""
      proxy = self.proxy
      rtn = proxy.getMetaobjAttr( meta_id, key)
      return rtn


    def getConfProperty(self, key, default=None):
      """Return confproperty."""
      proxy = self.proxy
      rtn = proxy.getConfProperty( key, default)
      return rtn


    def getObjAttrs(self, meta_type=None):
      """Return objattrs."""
      proxy = self.proxy
      rtn = proxy.getObjAttrs( meta_type)
      return rtn


    def _getObjAttrValue(self, obj_attr, obj_vers, lang):
      """Implement '_getObjAttrValue'."""
      proxy = self.proxy
      rtn = proxy._getObjAttrValue( obj_attr, obj_vers, lang)
      return rtn


    def getObjAttrValue(self, obj_attr, REQUEST):
      """Return objattrvalue."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getObjAttrValue( obj_attr, req)
      return rtn


    def getRootElement(self):
      """Return rootelement."""
      base = self.base
      rtn = base.getRootElement( )
      return rtn


    def getDocumentElement(self):
      """Return documentelement."""
      base = self.base
      rtn = base.getDocumentElement( )
      return rtn


    def getHome(self):
      """Return home."""
      base = self.base
      rtn = base.getHome( )
      return rtn


    def getDCCoverage(self, REQUEST={}):
      """Return dccoverage."""
      proxy = self.proxy
      rtn = proxy.getDCCoverage( REQUEST)
      return rtn


    def getDCDescription(self, REQUEST):
      """Return dcdescription."""
      proxy = self.proxy
      rtn = proxy.getDCDescription( REQUEST)
      return rtn


    def getUserAttr(self, user, name, default, flag=0):
      """Overrides AccessManager.getUserAttr."""
      proxy = self.proxy
      rtn = proxy.getUserAttr( user, name, default, flag)
      return rtn


    def getPageExt(self, REQUEST):
      """Return pageext."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getPageExt( req)
      return rtn


    def getTitle(self, REQUEST):
      """Return title."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getTitle( req)
      return rtn


    def getTitlealt(self, REQUEST):
      """Return titlealt."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getTitlealt( req)
      return rtn


    def getPenetrance(self, REQUEST):
      """Return penetrance."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getPenetrance( req)
      return rtn


    def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
      """Return childnodes."""
      rtn = []
      recursive = self.recursive
      if recursive:
        proxy = self.proxy
        req = self.__request__( REQUEST)
        if hasattr( proxy, 'getChildNodesPROXY'):
          rtn = [ZMSProxyObject( self.__root__, self, self.absolute_url()+'/'+x.id, x.id, x, recursive) for x in proxy.getChildNodesPROXY( proxy, req, meta_types, reid)]
        else:
          rtn = [ZMSProxyObject( self.__root__, self, self.absolute_url()+'/'+x.id, x.id, x, recursive) for x in proxy.getChildNodes( req, meta_types, reid)]
      return rtn


    def getSecNo(self):
      """Return secno."""
      proxy = self.proxy
      rtn = proxy.getSecNo( )
      return rtn


    def getLevel(self):
      """Return level."""
      proxy = self.proxy
      base = self.base
      rtn = base.getLevel( ) + 1
      recursive = self.recursive
      if proxy is not None and proxy is ZMSProxyObject:
        if hasattr( proxy, 'getLevelPROXY'):
          rtn = proxy.getLevelPROXY( proxy)
        else:
          rtn = proxy.getLevel()
      return rtn


    def getObjProperty(self, key, REQUEST={}, default=None):
      """Return objproperty."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      if hasattr( proxy, 'getObjPropertyPROXY'):
        rtn = proxy.getObjPropertyPROXY( proxy, key, req, default)
      else:
        rtn = proxy.getObjProperty( key, req, default)
      return rtn


    getParentNode__roles__ = None
    def getParentNode(self):
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      rtn = self.base
      return rtn


    def getType(self):
      """Return type."""
      proxy = self.proxy
      rtn = proxy.getType()
      return rtn


    def isActive(self, REQUEST):
      """Return whether active."""
      proxy = self.proxy
      root = self.__root__
      rtn = proxy.isActive(REQUEST) and root.isActive(REQUEST)
      return rtn


    def isMetaType(self, meta_type, REQUEST={'preview':'preview'}):
      """Return whether metatype."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isMetaType( meta_type, req)
      return rtn


    def isResource(self, REQUEST):
      """Return whether resource."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isResource( req)
      return rtn


    def isPage(self):
      """Return whether page."""
      proxy = self.proxy
      rtn = proxy.isPage( )
      return rtn


    def isPageElement(self):
      """Return whether pageelement."""
      proxy = self.proxy
      rtn = proxy.isPageElement( )
      return rtn


    def isVisible(self, REQUEST):
      """Return whether visible."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.isVisible( req)
      return rtn


    def _getBodyContent(self, REQUEST):
      """Implement '_getBodyContent'."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy._getBodyContent( req)
      return rtn

    def getBodyContent(self, REQUEST, forced=False):
      """
      HTML presentation in body-content. 
      """
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getBodyContent( req)
      return rtn


    def display_icon(self, *args, **kwargs): 
      """Implement 'display_icon'."""
      proxy = self.proxy
      rtn = proxy.display_icon(args, kwargs)
      return rtn


    def getLangIds(self, sort=False):
      """Return langids."""
      proxy = self.proxy
      rtn = proxy.getLangIds( sort)
      return rtn


    def get_manage_lang(self):
      """Return manage lang."""
      proxy = self.proxy
      rtn = proxy.get_manage_lang( )
      return rtn


    def getZMILangStr(self, key, REQUEST=None, RESPONSE=None):
      """Return zmilangstr."""
      proxy = self.proxy
      rtn = proxy.getZMILangStr( key, REQUEST, RESPONSE)
      return rtn


    def getLangStr(self, key, lang=None):
      """Return langstr."""
      proxy = self.proxy
      rtn = proxy.getLangStr( key, lang)
      return rtn


    def getPrimaryLanguage(self):
      """Return primarylanguage."""
      proxy = self.proxy
      rtn = proxy.getPrimaryLanguage()
      return rtn
    

    def hasAccess(self, REQUEST):
      """Return whether access."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.hasAccess( req)
      return rtn


    def getObjVersion(self, REQUEST={}):
      """Return objversion."""
      proxy = self.proxy
      req = self.__request__( REQUEST)
      rtn = proxy.getObjVersion( req)
      return rtn


    def breadcrumbs_obj_path(self, portalMaster=True):
      """Implement 'breadcrumbs_obj_path'."""
      proxy = self.proxy
      base = self.base
      rtn = base.breadcrumbs_obj_path( ) + [ self]
      recursive = self.recursive
      if proxy is not None and proxy is ZMSProxyObject:
        if hasattr( proxy, 'breadcrumbs_obj_pathPROXY'):
          rtn = proxy.breadcrumbs_obj_pathPROXY( proxy, portalMaster)
        else:
          rtn = proxy.breadcrumbs_obj_path(portalMaster)
      return rtn


    def getDeclUrl(self, REQUEST={}):
      """Return declurl."""
      if self.getConfProperty('ZMS.pathhandler', 0) == 0:
        rtn = self.absolute_url()
      else:
        base = self.base
        req = self.__request__( REQUEST)
        rtn = base.getDeclUrl( req)
        rtn += '/' + self.getDeclId( req)
      return rtn


    def getHref2IndexHtml(self, REQUEST, deep=1): 
      """Return href2indexhtml."""
      proxy = self.proxy
      rtn = zmscontainerobject.ZMSContainerObject.getHref2IndexHtml( self, REQUEST, deep)
      return rtn


    def getStylesheet(self, id=None):
      """Return stylesheet."""
      base = self.base
      rtn = base.getStylesheet( id)
      return rtn


    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      """Implement 'printHtml'."""
      proxy = self.proxy
      rtn = proxy.printHtml( level, sectionizer, REQUEST, deep)
      return rtn


    ############################################################################
    # Interface IZMSMetamodelProvider: delegate to proxy
    ############################################################################

    def getMetaobjId(self, name):
      """Return metaobjid."""
      return self.proxy.getMetaobjId( name)

    def getMetaobjIds(self, sort=None, excl_ids=[]):
      """Return metaobjids."""
      return self.proxy.getMetaobjIds( sort, excl_ids)

    def getMetaobj(self, id):
      """Return metaobj."""
      return self.proxy.getMetaobj( id)

    def getMetaobjAttrIds(self, meta_id, types=[]):
      """Return metaobjattrids."""
      return self.proxy.getMetaobjAttrIds( meta_id, types)

    def getMetaobjAttr(self, meta_id, key):
      """Return metaobjattr."""
      return self.proxy.getMetaobjAttr( meta_id, key)


    ############################################################################
    # Interface IZMSFormatProvider: delegate to proxy
    ############################################################################

    def getTextFormatDefault(self):
      """Return textformatdefault."""
      return self.proxy.getTextFormatDefault()

    def getTextFormat(self, id, REQUEST):
      """Return textformat."""
      return self.proxy.getTextFormat(id, REQUEST)

    def getTextFormats(self, REQUEST):
      """Return textformats."""
      return self.proxy.getTextFormats(REQUEST)

    def getCharFormats(self):
      """Return charformats."""
      return self.proxy.getCharFormats()

