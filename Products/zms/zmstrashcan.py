"""
zmstrashcan.py

Defines ZMSTrashcan for trashcan management, deletion recovery, and object lifecycle cleanup.
It retains recently deleted objects, enables recovery, and enforces retention policies.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import time
# Product Imports.
from Products.zms import standard
from Products.zms import zmscontainerobject


class ZMSTrashcan(zmscontainerobject.ZMSContainerObject):

    """Store deleted ZMS objects until garbage collection removes them."""

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSTrashcan"
    zmi_icon = "fas fa-trash"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    def manage_options(self):
      """Return the trashcan management tabs shown in the ZMI."""
      return ( 
        {'label': 'TYPE_ZMSTRASHCAN', 'action': 'manage_main'},
        {'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
        ) 

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
        'manage', 'manage_main', 'manage_container', 'manage_workspace',
        'manage_eraseObjs', 'manage_moveObjUp', 'manage_moveObjDown', 'manage_cutObjects',
        'manage_ajaxDragDrop', 'manage_ajaxZMIActions',
        'manage_userForm', 'manage_user',
        )
    __ac_permissions__=(
        ('ZMS Author', __authorPermissions__),
        )

    # Management Interface.
    # ---------------------
    manage_properties = PageTemplateFile('zpt/ZMSTrashcan/manage_properties', globals())


    def __init__(self):
      """Initialize the trashcan container."""
      id = 'trashcan'
      sort_id = 0
      zmscontainerobject.ZMSContainerObject.__init__(self, id, sort_id)


    def manage_changeProperties(self, lang, REQUEST=None): 
      """Handle trashcan property updates from the ZMI.

      @param lang: Active UI language.
      @type lang: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Redirect response when triggered from the ZMI.
      @rtype: C{object}
      """
      
      if REQUEST.get('btn') in  [ 'BTN_CANCEL', 'BTN_BACK']:
        return REQUEST.RESPONSE.redirect('manage_main?lang=%s'%lang)
        
      ##### Garbage Collection #####
      setattr(self, 'garbage_collection', REQUEST.get('garbage_collection', ''))
      self.run_garbage_collection(forced=1)
      
      # Return with message.
      message = self.getZMILangStr('MSG_CHANGED')
      if REQUEST and hasattr(REQUEST, 'RESPONSE'):
        if REQUEST.RESPONSE:
          return REQUEST.RESPONSE.redirect('manage_properties?lang=%s&manage_tabs_message=%s'%(lang, standard.url_quote(message)))


    def run_garbage_collection(self, forced=0):
      """Delete expired trashcan entries.

      @param forced: Run the cleanup regardless of the last execution time.
      @type forced: C{int}
      """
      now = time.time()
      last_run = getattr(self, 'last_garbage_collection', None)
      if forced or \
         last_run is None or \
         standard.daysBetween(last_run, now)>1:
        # Get days.
        days = int(getattr(self, 'garbage_collection', '2'))
        # Get IDs.
        ids = []
        for context in self.objectValues(self.dGlobalAttrs):
          delete = True
          try:
            delete = delete and standard.daysBetween(context.del_dt, now) > days
          except:
            pass
          if delete:
            ids.append(context.id)
        # Delete objects.
        if 0 != len(ids):
            self.manage_delObjects(ids=ids)
        # Update time-stamp.
        setattr(self, 'last_garbage_collection', now)


    def _verifyObjectPaste(self, object, validate_src=1): 
      """Allow paste operations into the trashcan without additional checks."""
      return


    def getDCCoverage(self, REQUEST={}):
      """Return global DC coverage for trashcan content.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{dict}
      @return: Global coverage namespace.
      @rtype: C{str}
      """
      return 'global.'+self.getPrimaryLanguage()


    def isActive(self, REQUEST):
      """Return whether the trashcan currently contains objects.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: C{True} when the trashcan has child nodes.
      @rtype: C{bool}
      """
      return len(self.getChildNodes(REQUEST))>0


    def isPage(self):
      """Return whether the trashcan behaves like a page.

      @return: Always C{False}.
      @rtype: C{bool}
      """
      return False


    def isPageContainer(self):
      """Return whether the trashcan can contain page-like children.

      @return: Always C{True}.
      @rtype: C{bool}
      """
      return True


    def getObjProperty(self, key, REQUEST={}, par=None):
      """Return an empty property value for synthetic trashcan attributes.

      @param key: Property identifier.
      @type key: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{dict}
      @param par: Optional parent context.
      @type par: C{object}
      @return: Always an empty string.
      @rtype: C{str}
      """
      return ''


    def getTitle(self, REQUEST):
      """Return the localized trashcan title including the object count.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Localized title with item count.
      @rtype: C{str}
      """
      return self.display_type() + " (" + str(len(self.getChildNodes(REQUEST))) + " " + self.getLangStr('ATTR_OBJECTS', REQUEST['lang']) + ")"

