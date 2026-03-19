"""
_objchildren.py

Internal helpers for objchildren in ZMS.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Product Imports.
from Products.zms import _fileutil
from Products.zms import standard


class ObjChildren(object):

    """Manage child-object creation and filtered child lookups."""

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
      'manage_initObjChild',
    )
    __ac_permissions__=(
      ('ZMS Author', __authorPermissions__),
    )

    def initObjChild(self, id, _sort_id, type, REQUEST):
      """Create and initialize a child object for the current container.

      @param id: Base object id.
      @type id: C{str}
      @param _sort_id: Sort position before normalization.
      @type _sort_id: C{int}
      @param type: Child meta type.
      @type type: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: The created or reused child object.
      @rtype: C{object}
      """
      ##### ID ####
      metaObjAttr = self.getObjChildrenAttr(id)
      repetitive = metaObjAttr.get('repetitive', 0)==1
      if repetitive:
        id += str(self.getSequence().nextVal())
      
      ##### Create ####
      oItem = getattr(self, id, None)
      if oItem is None or id not in self.objectIds():
        globalAttr = self.dGlobalAttrs.get(type, self.dGlobalAttrs['ZMSCustom'])
        constructor = globalAttr.get('obj_class', self.dGlobalAttrs['ZMSCustom']['obj_class'])
        newNode = constructor(id, _sort_id+1, type)
        self._setObject(newNode.id, newNode)
        oItem = getattr(self, id)
      
      ##### Object State ####
      oItem.setObjStateNew(REQUEST)
      ##### Init Properties ####
      oItem.setObjStateModified(REQUEST)
      for lang in self.getLangIds():
        oItem.setObjProperty('active', 1, lang)
      ##### VersionManager ####
      oItem.onChangeObj(REQUEST)
          
      ##### Normalize Sort-IDs ####
      self.normalizeSortIds(standard.id_prefix(id))
        
      return oItem


    def _initObjChildren(self, obj_attr, REQUEST):
      """Ensure mandatory and repetitive child objects match metaobject rules.

      @param obj_attr: Metaobject child attribute definition.
      @type obj_attr: C{dict}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      """
      id = obj_attr['id']
      ids = [x.getId() for x in self.getChildNodes() if x.getId().startswith(id)]
      mandatory = obj_attr.get('mandatory',0)
      if mandatory:
        if len(ids) == 0:
          default  = obj_attr.get('custom')
          if default:
            _fileutil.import_zexp(self, default, obj_attr['id'], obj_attr['id'])
          else:
            if obj_attr['type'] == '*' and isinstance(obj_attr['keys'], list) and len( obj_attr['keys']) > 0:
              obj_attr['type'] = obj_attr['keys'][0]
            self.initObjChild(obj_attr['id'], 0, obj_attr['type'], REQUEST)
      repetitive = obj_attr.get('repetitive',0)
      if repetitive:
        if id in ids:
          new_id = self.getNewId(id)
          standard.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(id, new_id))
          if new_id not in self.objectIds():
            try:
              self.manage_renameObject(id=id, new_id=new_id)
            except:
              ob = getattr(self, id)
              ob._setId(new_id) 
      else:
        if not id in ids and len(ids)>0:
          old_id = ids[0]
          standard.writeLog( self, "[_initObjChildren]: Rename %s to %s"%(old_id, id))
          if id not in self.objectIds():
            try:
              self.manage_renameObject(id=old_id, new_id=id)
            except:
              ob = getattr(self, old_id)
              ob._setId(id) 


    def initObjChildren(self, REQUEST):
      """Initialize all configured child objects for the current metaobject.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      """
      standard.writeLog( self, "[initObjChildren]")
      self.getObjProperty( 'initObjChildren', REQUEST)
      metaObj = self.getMetaobj(self.meta_id)
      metaObjIds = self.getMetaobjIds()+['*']
      for metaObjAttrId in self.getMetaobjAttrIds( self.meta_id):
        metaObjAttr = self.getMetaobjAttr( self.meta_id, metaObjAttrId)
        if metaObjAttr['type'] in metaObjIds:
           self._initObjChildren( metaObjAttr, REQUEST)


    def getObjChildrenAttr(self, key, meta_type=None):
      """Return the configured child definition for an object key.

      @param key: Child attribute key.
      @type key: C{str}
      @param meta_type: Optional metaobject type override.
      @type meta_type: C{str}
      @return: Child attribute configuration.
      @rtype: C{dict}
      """
      meta_type = standard.nvl(meta_type, self.meta_id)
      ##### Meta-Objects ####
      if meta_type in self.getMetaobjIds() and key in self.getMetaobjAttrIds(meta_type):
        obj_attr = self.getMetaobjAttr(meta_type, key)
      ##### Default ####
      else:
        obj_attr = {'id':key,'repetitive':1,'mandatory':0}
      return obj_attr


    def getObjChildren(self, id, REQUEST, meta_types=None):
      """Return child nodes matching the configured child attribute.

      @param id: Child attribute key.
      @type id: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param meta_types: Optional meta type filter.
      @type meta_types: C{list}
      @return: Matching child nodes in document order.
      @rtype: C{list}
      """
      objAttr = self.getObjChildrenAttr(id)
      reid = None
      if id:
        if objAttr.get('repetitive'):
          reid = id+'$'+'|'+id+'\\d+'
        else:
          reid = id
      return self.getChildNodes(REQUEST, meta_types, reid)


    def filteredObjChildren(self, id, REQUEST, meta_types=None):
      """Return visible child nodes matching the configured child attribute.

      @param id: Child attribute key.
      @type id: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param meta_types: Optional meta type filter.
      @type meta_types: C{list}
      @return: Visible matching child nodes.
      @rtype: C{list}
      """
      return [x for x in self.getObjChildren(id, REQUEST, meta_types) if x.isVisible(REQUEST)]


    def manage_initObjChild(self, id, type, lang, REQUEST, RESPONSE=None): 
      """Handle ZMI creation of a new child object.

      @param id: Base object id.
      @type id: C{str}
      @param type: Child meta type.
      @type type: C{str}
      @param lang: Active UI language.
      @type lang: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: Optional HTTP response for redirects.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Redirect response when C{RESPONSE} is provided.
      @rtype: C{object}
      """
      
      # Create.      
      obj = self.initObjChild(id, self.getNewSortId(), type, REQUEST)
      
      # Return with message.
      if RESPONSE is not None:
        message = self.getZMILangStr('MSG_INSERTED')%obj.display_type()
        message = standard.url_quote(message)
        target = REQUEST.get('manage_target', '%s/manage_main'%obj.id)
        RESPONSE.redirect('%s?lang=%s&manage_tabs_message=%s'%(target, lang, message))

