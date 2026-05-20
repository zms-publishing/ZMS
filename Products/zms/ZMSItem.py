"""
ZMSItem.py - ZMS Base Content Object

Defines ZMSItem as the base class for all ZMS content objects, 
providing core Zope integration, persistence, and basic content 
management functionality. ZMSItem serves as the foundation for all 
ZMS content types, offering a unified interface for request handling, 
page rendering, access control, and a readme endpoint for documentation. 
Subclasses extend ZMSItem with domain-specific features while 
inheriting its core capabilities.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from DateTime.DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from Acquisition import Implicit
import OFS.SimpleItem, OFS.ObjectManager
import os
import markdown
# Product Imports.
from Products.zms import standard
from Products.zms import _accessmanager


class ZMSItem(
    OFS.ObjectManager.ObjectManager,
    OFS.SimpleItem.Item,
    Persistent,  # Persistent.
    Implicit,    # Acquisition.
    ):
    """ZMS base infrastructure class providing core Zope integration and basic content management.
    
    ZMSItem serves as the foundation for all ZMS content objects. It provides:
    
        - Core Zope integration through ObjectManager and SimpleItem
        - ZODB persistence and Acquisition support
        - ZMI (Zope Management Interface) utilities and templates
        - Request handling and page rendering
        - Access control permissions framework
        - Readme endpoint for documentation
    
    Subclasses extend ZMSItem with domain-specific functionality.
    """

    __viewPermissions__ = (
        'manage_page_header', 'manage_page_footer', 'manage_tabs',
        'manage', 'manage_main', 'manage_workspace', 'manage_menu',
        'readme',
      )
    __ac_permissions__=(
      ('View', __viewPermissions__),
      )

    # Templates.
    # ----------
    manage = PageTemplateFile('zpt/object/manage', globals())
    manage_workspace = PageTemplateFile('zpt/object/manage', globals())
    manage_main = PageTemplateFile('zpt/ZMSObject/manage_main', globals())
    readme_html = PageTemplateFile('zpt/object/readme_html', globals())

    # --------------------------------------------------------------------------
    #  ZMSItem.readme:
    #  Unified endpoint for readme content rendered as HTML.
    #  1. ZODB attribute 'readme' (content objects with attr())
    #  2. ZODB OFS.File in metacmd_readme/ (imported metacommands — via ZMSMetacmdProvider)
    #  3. Filesystem zpt/<ClassName>/readme.md or conf/metacmd_manager/metacms_readme/<id>_readme (dev/bundled)
    # --------------------------------------------------------------------------
    def get_readme_path(self, REQUEST=None):
      """Return filesystem path to a readme.md for the current admin context."""
      pkg_home = os.path.dirname(standard.__file__)
      class_name = self.__class__.__name__
      return os.path.join(pkg_home, 'zpt', class_name, 'readme.md')


    def readme(self, REQUEST=None, RESPONSE=None):
      """Returns readme rendered as HTML"""
      if REQUEST is None:
        REQUEST = self.REQUEST
      if RESPONSE is None:
        RESPONSE = self.REQUEST.RESPONSE
      RESPONSE.setHeader('Content-Type', 'text/html;charset=utf-8')
      # 1. Try ZODB attribute 'readme' (content objects)
      if hasattr(self.aq_base, 'attr'):
        raw = self.attr('readme')
        if raw:
          if not isinstance(raw, (bytes,str)):
            raw = raw.getData().decode('utf-8')
          return '<article class="zmi-readme">%s</article>'%self.renderText('markdown', 'text', raw, REQUEST)
      # 2. ZODB OFS.File readme (imported metacommands — sentinel tuple from ZMSMetacmdProvider)
      readme_path = self.get_readme_path(REQUEST)
      if isinstance(readme_path, tuple) and readme_path[0] == 'zodb':
        raw = readme_path[1].data
        if isinstance(raw, bytes):
          raw = raw.decode('utf-8')
        return '<article class="zmi-readme">%s</article>'%markdown.markdown(raw, extensions=['tables', 'fenced_code'])
      # 3. Fall back to filesystem readme.md (bundled core commands, dev mode)
      if isinstance(readme_path, str) and os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
          raw = f.read()
        return '<article class="zmi-readme">%s</article>'%markdown.markdown(raw, extensions=['tables', 'fenced_code'])
      return ''


    def zmi_body_content(self, *args, **kwargs):
      """Implement 'zmi_body_content'."""
      request = self.REQUEST
      response = request.RESPONSE
      return self.getBodyContent(request)


    def zmi_manage_menu(self, *args, **kwargs):
      """Implement 'zmi_manage_menu'."""
      return self.manage_menu(args, kwargs)


    def zmi_body_class(self, *args, **kwargs):
      """Implement 'zmi_body_class'."""
      request = self.REQUEST
      l = ['zmi','zms', 'loading']
      l.append(request.get('lang'))
      l.append('lang-%s'%(request.get('lang')))
      l.extend(kwargs.values())
      l.append(self.meta_id)
      # FOR EVALUATION: adding node specific css classes [list]
      internal_dict = self.attr('internal_dict')
      if isinstance(internal_dict, dict) and internal_dict.get('css_classes', None):
        l.extend( internal_dict['css_classes'] )
      l.extend(self.getUserRoles(request['AUTHENTICATED_USER']))
      # Additionally configured css classes [string]
      l.append(self.getConfProperty('ZMS.added.zmi.body_class',''))
      return ' '.join(l)


    def _zmi_page_request(self, *args, **kwargs):
      """Implement '_zmi_page_request'."""
      request = self.REQUEST
      request.set( 'ZMS_THIS', self.getSelf())
      request.set( 'ZMS_DOCELMNT', self.breadcrumbs_obj_path()[0])
      request.set( 'ZMS_ROOT', request['ZMS_DOCELMNT'].absolute_url())
      request.set( 'ZMS_COMMON', getattr(self, 'common', self.getHome()).absolute_url())
      request.set( 'ZMI_TIME', DateTime().timeTime())
      request.set( 'ZMS_CHARSET', request.get('ZMS_CHARSET', 'utf-8'))
      if not request.get('HTTP_ACCEPT_CHARSET'):
        request.set('HTTP_ACCEPT_CHARSET', '%s;q=0.7,*;q=0.7'%request['ZMS_CHARSET'])
      if (request.get('ZMS_PATHCROPPING', False) or self.getConfProperty('ZMS.pathcropping', 0)==1) and request.get('export_format', '')=='':
        base = request.get('BASE0', '')
        if request['ZMS_ROOT'].startswith(base):
          request.set( 'ZMS_ROOT', request['ZMS_ROOT'][len(base):])
          request.set( 'ZMS_COMMON', request['ZMS_COMMON'][len(base):])
    
    def zmi_page_request(self, *args, **kwargs):
      """Implement 'zmi_page_request'."""
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      self._zmi_page_request()
      RESPONSE.setHeader('Expires', DateTime(request['ZMI_TIME']-10000).toZone('GMT+1').rfc822())
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'text/html;charset=%s'%request['ZMS_CHARSET'])
      request.set( 'is_zmi', True)
      if not request.get( 'preview'):
        request.set( 'preview', 'preview')
      langs = self.getLanguages(request)
      if request.get('lang') not in langs:
        request.set('lang', langs[0])
      if not request.get('manage_tabs_message'):
        request.set( 'manage_tabs_message', self.getConfProperty('ZMS.manage_tabs_message', ''))
      if not request.get('manage_tabs_warning_message'):
        request.set( 'manage_tabs_warning_message',self.getConfProperty('ZMS.manage_tabs_warning_message',''))
      if not request.get('manage_tabs_danger_message'):
        request.set( 'manage_tabs_danger_message',self.getConfProperty('ZMS.manage_tabs_danger_message',''))
      if 'zmi-manage-system' in request.form:
        standard.set_session_value(self,'zmi-manage-system',int(request.get('zmi-manage-system',0)))
      # AccessableObject
      _accessmanager.AccessableObject.zmi_page_request(self, args, kwargs)
      # avoid declarative urls
      path_to_handle = request['URL0'][len(request['BASE0']):]
      qs = request['QUERY_STRING']
      path = path_to_handle.split('/')
      if not path[-2] in self.objectIds() \
          and len([x for x in path[:-1] if x.find('.')>0 or x.startswith('manage')])==0:
        new_path = self.absolute_url()+'/'+path[-1]
        if not new_path.endswith(path_to_handle):
          if qs:
            new_path += '?' + qs
          request.RESPONSE.redirect(new_path)
      RESPONSE.setHeader('HX-Push-Url', '%s?%s'%(path_to_handle, qs))

    def f_standard_html_request(self, *args, **kwargs):
      """
      Set up request for standard HTML page rendering, 
      including headers and context variables.
      """
      request = self.REQUEST
      self._zmi_page_request()
      if not request.get( 'lang'):
        request.set( 'lang', self.getLanguage(request))


    def display_icon(self, *args, **kwargs):
      """
      Returns the icon for the object.
       - If meta_id is provided, return the icon for the specified meta_id
       - Otherwise, return the default icon for the object
      """
      meta_id = kwargs.get('meta_id')
      if meta_id is None:
        return self.icon
      else:
        return self.aq_parent.display_icon(meta_id=meta_id)


    def getTitlealt( self, REQUEST):
      """
      Returns the translated meta_type as title alt text for icons and links.
       - If meta_type is defined in self.getZMILangStr, return the translated string
       - Otherwise, return the raw meta_type
      """
      return self.getZMILangStr( self.meta_type)


    def breadcrumbs_obj_path(self, portalMaster=True):
      """
      Return the acquisition path of objects from the root to self's parent as a list.
      If portalMaster is True, the path is returned from the portal master object; 
      otherwise, from the root of the acquisition context.
      """
      return self.aq_parent.breadcrumbs_obj_path(portalMaster)

