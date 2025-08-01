################################################################################
# zmsobject.py
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
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from DateTime.DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import ZPublisher.HTTPRequest
import collections
import re
import time
# Product Imports.
from Products.zms import _accessmanager
from Products.zms import _blobfields
from Products.zms import _cachemanager
from Products.zms import _copysupport
from Products.zms import _deprecatedapi
from Products.zms import _exportable
from Products.zms import _globals
from Products.zms import _multilangmanager
from Products.zms import _objattrs
from Products.zms import _objchildren
from Products.zms import _objinputs
from Products.zms import _objtypes
from Products.zms import _pathhandler
from Products.zms import _versionmanager
from Products.zms import _xmllib
from Products.zms import _textformatmanager
from Products.zms import _zreferableitem
from Products.zms import ZMSItem
from Products.zms import ZMSWorkflowItem
from Products.zms import standard
from Products.zms import zopeutil
from zope.globalrequest import getRequest


__all__= ['ZMSObject']


################################################################################
################################################################################
###
###   Abstract Class ZMSObject
###
################################################################################
################################################################################
class ZMSObject(ZMSItem.ZMSItem,
  #CatalogPathAwareness.CatalogAware,  # Catalog awareness.
  _accessmanager.AccessableObject,	# Access manager.
  _versionmanager.VersionItem,		# Version Item.
  ZMSWorkflowItem.ZMSWorkflowItem,
  _copysupport.CopySupport,		# Copy Support (Paste Objects).
  _cachemanager.ReqBuff,		# Request Buffer (Cache).
  _deprecatedapi.DeprecatedAPI,		# Deprecated API.
  _multilangmanager.MultiLanguageObject,	# Multi-Language.
  _exportable.Exportable,			# XML Export.
  _objattrs.ObjAttrs,			# Object-Attributes.
  _objchildren.ObjChildren,		# Object-Children.
  _objinputs.ObjInputs,			# Object-Inputs.
  _objtypes.ObjTypes,			# Object-Types.
  _pathhandler.PathHandler,		# Path-Handler.
  _textformatmanager.TextFormatObject,	# Text-Formats.
  _zreferableitem.ZReferableItem		# ZReferable Item.
  ):

    # Documentation string.
    __doc__ = """ZMS product module."""
    # Version string.
    __version__ = '0.1'

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Properties.
    # -----------
    QUOT = chr(34)
    MISC_ZMS = '/++resource++zms_/img/'
    FORM_LABEL_MANDATORY = '<sup style="color:red">*</sup>'
    spacer_gif = '/++resource++zms_/img/spacer.gif'

    # ZPT Templates.
    # --------------
    zmi_navbar_brand = PageTemplateFile('zpt/common/zmi_navbar_brand', globals())
    zmi_breadcrumbs = PageTemplateFile('zpt/common/zmi_breadcrumbs', globals())
    zmi_breadcrumbs_obj_path = PageTemplateFile('zpt/common/zmi_breadcrumbs_obj_path', globals())
    zmi_manage_tabs_message = PageTemplateFile('zpt/common/zmi_manage_tabs_message', globals())
    zmi_html_head = PageTemplateFile('zpt/common/zmi_html_head', globals())
    zmi_body_header = PageTemplateFile('zpt/common/zmi_body_header', globals())
    zmi_body_footer = PageTemplateFile('zpt/common/zmi_body_footer', globals())
    zmi_html_foot = PageTemplateFile('zpt/common/zmi_html_foot', globals())
    zmi_pagination = PageTemplateFile('zpt/common/zmi_pagination', globals())
    zmi_tabs = PageTemplateFile('zpt/common/zmi_tabs', globals())
    zmi_tabs_sub = PageTemplateFile('zpt/common/zmi_tabs_sub', globals())
    zmi_ace_editor = PageTemplateFile('zpt/common/zmi_ace_editor', globals())

    # Templates.
    # ----------
    f_recordset_grid = PageTemplateFile('zpt/object/f_recordset_grid', globals()) # ZMI RecordSet::Grid
    preview_html = PageTemplateFile('zpt/object/preview', globals())
    preview_top_html = PageTemplateFile('zpt/object/preview_top', globals())
    f_api_html = PageTemplateFile('zpt/object/f_api', globals())
    f_api_top_html = PageTemplateFile('zpt/object/f_api_top', globals())
    obj_input_fields = PageTemplateFile('zpt/ZMSObject/input_fields', globals())
    obj_input_elements = PageTemplateFile('zpt/ZMSObject/input_elements', globals())


    ############################################################################
    #  ZMSObject.__init__:
    #
    #  Constructor (initialise a new instance of ZMSObject).
    ############################################################################
    def __init__(self, id='', sort_id=0):
      """ ZMSObject.__init__ """
      self.id = id
      self.ref_by = []
      self.setSortId(sort_id)

    def getPath(self, *args, **kwargs):
      ids = self.getPhysicalPath()
      # avoid content/content (seen in xml-import of zms-default-content)
      ids = [ids[x] for x in range(len(ids)) if x == 0 or not ids[x-1] == ids[x]]
      return '/'.join(ids)


    # --------------------------------------------------------------------------
    #  ZMSObject.f_css_defaults:
    #
    #  @deprecated
    # --------------------------------------------------------------------------
    def f_css_defaults(self, REQUEST=None):
      """ ZMSObject.f_css_defaults """
      if REQUEST is None:
        REQUEST = self.REQUEST
      return self.zmi_css_defaults(REQUEST)

    def zmi_css_defaults(self, REQUEST):
      """ ZMSObject.zmi_css_defaults """
      RESPONSE = REQUEST.RESPONSE
      RESPONSE.setHeader('Last-Modified', DateTime(self.getConfProperty('last_modified')-10000).toZone('GMT+1').rfc822())
      if 'cache-control' not in RESPONSE.headers:
        RESPONSE.setHeader('Cache-Control', 'public, max-age=3600')
      REQUEST.RESPONSE.setHeader('Content-Type', 'text/css')
      l = []
      available_objs = self.metaobj_manager.objectIds()
      for metaObjId in self.getMetaobjIds():
        metaObj = self.getMetaobj(metaObjId)
        for metaObjAttr in [x for x in metaObj.get('attrs', []) if ( x['id'] == 'f_css_defaults' ) ]:
          id = metaObjAttr['id']
          s = '%s.%s'%(metaObjId, id)
          try:
            if s in available_objs:
              l.append('@import url("%s/metaobj_manager/%s");'%(self.getDocumentElement().absolute_url(), s) )
          except:
            l.append('/* >>>>>>>>>> ERROR in %s <<<<<<<<<< */'%standard.writeError(self, "[zmi_css_defaults]: %s"%s))
      return '\n'.join([x for x in l])

    ############################################################################
    #
    # ZMS Object Index
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.get_uid:
    # --------------------------------------------------------------------------
    def get_uid(self, forced=False):
      import uuid
      uid = getattr(self,'_uid','')
      new_uid = None
      if forced \
          or '_uid' not in self.__dict__ \
          or len(uid) == 0 \
          or len(uid.split('-')) < 5:
        new_uid = str(uuid.uuid4())
      if uid.startswith('!uid:'):
        new_uid = uid[len('!uid:'):]
      if new_uid:
        self._uid = new_uid
      return 'uid:%s'%self._uid

    # --------------------------------------------------------------------------
    #  ZMSObject.set_uid:
    # --------------------------------------------------------------------------
    def set_uid(self, uid):
      self._uid = uid.replace('uid:', '')

    # --------------------------------------------------------------------------
    #  ZMSObject.get_oid:
    # --------------------------------------------------------------------------
    def get_oid(self):
      try:
        from Shared.DC.xml.ppml import u64 as decodeObjectId
      except:
        from ZODB.utils import u64 as decodeObjectId
      oid = None
      if self._p_oid is not None:
        oid = decodeObjectId(self._p_oid)
      return 'oid:%s'%oid

    # --------------------------------------------------------------------------
    #  ZMSObject.set_request_context:
    # --------------------------------------------------------------------------
    def set_request_context(self, REQUEST, d):
      prefix = '%s_'%(standard.id_quote(self.get_oid()))
      # Remove old context-values.
      for key in [x for x in REQUEST.keys() if x.startswith(prefix)]:
        standard.writeLog(self, "[set_request_context]: DEL "+key)
        REQUEST.set(key, None)
      # Set new context-values.
      for key in d:
        context = prefix+key
        value = d[key]
        standard.writeLog(self, "[set_request_context]: SET "+context+"="+str(value))
        REQUEST.set(context, value)

    # --------------------------------------------------------------------------
    #  ZMSObject.get_request_context:
    # --------------------------------------------------------------------------
    def get_request_context(self, REQUEST, key, defaultValue=None):
      context = '%s_%s'%(standard.id_quote(self.get_oid()), key)
      # Get context-value.
      value = REQUEST.get(context, None)
      if value is not None:
        standard.writeLog(self, "[get_request_context]: GET "+context+"="+str(value))
        return value
      return REQUEST.get(key, defaultValue)

    # --------------------------------------------------------------------------
    #  ZMSObject.title:
    # --------------------------------------------------------------------------
    def title(self):
      try:
        return self.attr('title')
      except:
        return 'ZMS'

    # --------------------------------------------------------------------------
    #  ZMSObject.__proxy__:
    # --------------------------------------------------------------------------
    def __proxy__(self):
      return self

    # --------------------------------------------------------------------------
    #  ZMSObject.FileFromData
    # --------------------------------------------------------------------------
    def FileFromData( self, data, filename='', content_type=None):
        """
        Creates a new instance of a file from given data.
        @param data: File-data (binary)
        @type data: C{string}
        @param filename: Filename
        @type filename: C{string}
        @return: New instance of file.
        @rtype: L{MyFile}
        """
        file = {}
        file['data'] = data
        file['filename'] = filename
        if content_type: file['content_type'] = content_type
        return _blobfields.createBlobField( self, _blobfields.MyFile, file=file)


    # --------------------------------------------------------------------------
    #  ZMSObject.ImageFromData:
    # --------------------------------------------------------------------------
    def ImageFromData( self, data, filename='', content_type=None):
        file = {}
        file['data'] = data
        file['filename'] = filename
        if content_type: file['content_type'] = content_type
        return _blobfields.createBlobField( self, _blobfields.MyImage, file=file)


    # --------------------------------------------------------------------------
    #  ZMSObject.isMetaType:
    # --------------------------------------------------------------------------
    def isMetaType(self, meta_type, REQUEST={}):
      if meta_type is None:
        return True
      if not isinstance(meta_type, list):
        meta_type = [meta_type]
      b = self.meta_type in meta_type or self.meta_id in meta_type
      if not b and self.PAGES in meta_type:
        b = b or self.isPage()
      elif not b and self.PAGEELEMENTS in meta_type:
        b = b or self.isPageElement()
      return b


    # --------------------------------------------------------------------------
    #  ZMSObject.isPageContainer:
    # --------------------------------------------------------------------------
    def isPageContainer(self):
      return self.getType() in [ 'ZMSDocument']


    # --------------------------------------------------------------------------
    #  ZMSObject.isPage:
    # --------------------------------------------------------------------------
    def isPage(self):
      return self.getType() in [ 'ZMSDocument', 'ZMSReference'] \
        and not self.meta_id in [ 'ZMSNote', 'ZMSTeaserContainer']


    # --------------------------------------------------------------------------
    #  ZMSObject.isPageElement:
    # --------------------------------------------------------------------------
    def isPageElement(self):
      return self.getType() in [ 'ZMSObject', 'ZMSRecordSet' ] \
        and not self.meta_id in [ 'ZMSNote', 'ZMSTeaserContainer']


    # --------------------------------------------------------------------------
    #  ZMSObject.getTitle
    # --------------------------------------------------------------------------
    def getTitle( self, REQUEST):
      s = self.getObjProperty('title', REQUEST)
      if s is None or len(s) == 0:
        if self.isPage():
          metaObjAttrs = self.getMetaobj( self.meta_id).get( 'attrs', [])
          offs = 1
          c = 0
          for metaObjAttr in metaObjAttrs:
            if metaObjAttr[ 'type'] in [ 'constant', 'method', 'py', 'string', 'select', 'color']:
              if c == offs:
                v = self.getObjProperty( metaObjAttr[ 'id'], REQUEST)
                if isinstance(v, bytes) or isinstance(v, str):
                  s = v
                  break
              c = c + 1
      if not s:
        s = self.display_type()
      if self.isPage():
        sec_no = self.getSecNo()
        if len(sec_no) > 0:
          s = sec_no + ' ' + s
      # FIXME TypeError: 'str' does not support the buffer interface
      #s = s.replace(' & ', ' &amp; ')
      return s


    # --------------------------------------------------------------------------
    #  ZMSObject.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST):
      s = self.getObjProperty('titlealt', REQUEST) or self.getObjProperty('titlealt', {'lang':self.getPrimaryLanguage()})
      if not s:
        s = self.display_type()
      if not s:
        if self.isPage():
          metaObjAttrs = self.getMetaobj( self.meta_id).get( 'attrs', [])
          offs = 0
          c = 0
          for metaObjAttr in metaObjAttrs:
            if metaObjAttr[ 'type'] in [ 'constant', 'method', 'py', 'string', 'select','color']:
              if c == offs:
                v = self.getObjProperty( metaObjAttr[ 'id'], REQUEST)
                if isinstance(v, bytes) or isinstance(v, str):
                  s = v
                  break
              c = c + 1
      if self.isPage():
        sec_no = self.getSecNo()
        if len(sec_no) > 0:
          s = sec_no + ' ' + s
      # FIXME TypeError: 'str' does not support the buffer interface
      #s = s.replace(' & ', ' &amp; ')
      return s


    # --------------------------------------------------------------------------
    #  ZMSObject.getType
    #
    #  Returns type of object. Valid types are:
    #  <li>ZMSDocument: Page</li>
    #  <li>ZMSObject: Page-Element</li>
    #  <li>ZMSTeaserElement: Teaser-Element</li>
    #  <li>ZMSRecordSet</li>
    #  <li>ZMSResource</li>
    #  <li>ZMSReference</li>
    #  <li>ZMSLibrary</li>
    #  <li>ZMSPackage</li>
    #  <li>ZMSModule</li>
    # --------------------------------------------------------------------------
    def getType(self):
      metaObj = self.getMetaobj(self.meta_id)
      return metaObj.get('type', 'ZMSDocument')


    # --------------------------------------------------------------------------
    #  ZMSObject.is_resource:
    #
    #  alias for isResource(request)
    # --------------------------------------------------------------------------
    def is_resource(self):
      return self.isResource(self.REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSObject.isResource
    # --------------------------------------------------------------------------
    def isResource(self, REQUEST):
      return self.getObjProperty('attr_dc_type', REQUEST) == 'Resource' or \
        self.id in REQUEST.get( 'ZMS_IDS_RESOURCE', [])


    # --------------------------------------------------------------------------
    #  ZMSObject.is_translated:
    #
    #  alias for isTranslated(lang,request)
    # --------------------------------------------------------------------------
    def is_translated(self, lang):
      return self.isTranslated(lang, self.REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSObject.isTranslated
    #
    #  Returns True if current object is translated to given language.
    # --------------------------------------------------------------------------
    def isTranslated(self, lang, REQUEST):
      rtnVal = False
      req = {'lang':lang,'preview':REQUEST.get('preview', '')}
      value = self.getObjProperty('change_uid', req)
      rtnVal = value is not None and len(value) > 0
      return rtnVal


    # --------------------------------------------------------------------------
    #  ZMSObject.isModifiedInParentLanguage
    #
    #  Returns True if current object is modified in parent language.
    # --------------------------------------------------------------------------
    def isModifiedInParentLanguage(self, lang, REQUEST):
      rtnVal = False
      parent = self.getParentLanguage(lang)
      if parent is not None:
        req = {'lang':lang, 'preview':REQUEST.get('preview', '') }
        change_dt_lang = self.getObjProperty('change_dt', req)
        req = {'lang':parent, 'preview':REQUEST.get('preview', '') }
        change_dt_parent = self.getObjProperty('change_dt', req)
        try:
          if change_dt_lang is not None and change_dt_parent is not None:
            rtnVal = standard.compareDate(change_dt_lang, change_dt_parent) > 0
        except:
          standard.writeError(self, "[isModifiedInParentLanguage]: Unexpected exception: change_dt_lang=%s, change_dt_parent=%s!"%(str(change_dt_lang), str(change_dt_parent)))
      return rtnVal


    # --------------------------------------------------------------------------
    #  ZMSObject.visible:
    #
    #  alias for isVisible(request)
    # --------------------------------------------------------------------------
    def is_visible(self):
      return self.isVisible(self.REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSObject.isVisible:
    #
    #  Returns 1 if current object is visible.
    # --------------------------------------------------------------------------
    def isVisible(self, REQUEST):
      request = getattr(self, 'REQUEST', getRequest())
      REQUEST = standard.nvl(REQUEST, request)
      lang = standard.nvl(REQUEST.get('lang'), self.getPrimaryLanguage())
      visible = True
      visible = visible and self.isTranslated(lang, REQUEST) # Object is translated.
      visible = visible and self.isCommitted(REQUEST) # Object has been committed.
      visible = visible and self.isActive(REQUEST) # Object is active.
      visible = visible and not '/'.join(self.getPhysicalPath()+('',)).startswith('/'.join(self.getTrashcan().getPhysicalPath()+('',))) # Object is not in trashcan.
      return visible


    # --------------------------------------------------------------------------
    #  ZMSObject.get_size
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def get_size(self, REQUEST={}):
      size = 0
      keys = self.getObjAttrs().keys()
      if self.getType() == 'ZMSRecordSet':
        keys = [self.getMetaobjAttrIds(self.meta_id,types=['list'])[0]]
      for key in keys:
        objAttr = self.getObjAttr(key)
        value = self.getObjAttrValue( objAttr, REQUEST)
        size = size + _globals.get_size(value)
      return size


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCCoverage
    #
    #  Returns "Dublin Core: Coverage".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      obj_vers = self.getObjVersion(REQUEST)
      obj_attr = {'id':'attr_dc_coverage'}
      return _objattrs.getobjattr(self, obj_vers, obj_attr, REQUEST.get('lang'))


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCDescription
    #
    #  Returns "Dublin Core: Description".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCDescription(self, REQUEST):
      return self.getObjProperty('attr_dc_description', REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSObject.getSelf:
    # --------------------------------------------------------------------------
    def getSelf(self, meta_type=None):
      ob = self
      if meta_type is not None and not ob.isMetaType( meta_type):
        parent = ob.getParentNode()
        if parent is not None:
          ob = parent.getSelf(meta_type)
      return ob


    # --------------------------------------------------------------------------
    #  ZMSObject.zmi_icon:
    # --------------------------------------------------------------------------
    def zmi_icon(self,*args, **kwargs):
      """ ZMSObject.zmi_icon """
      if 'name' in kwargs:
        clazz = kwargs['name'].replace('icon-','fas fa-')
      else:
        id = self.meta_id
        if args:
          id = args[0]
        clazz = self.evalMetaobjAttr( '%s.%s'%(id, 'icon_clazz'))
        if not clazz:
          meta_obj = self.getMetaobj(id)
          clazzes = {'ZMSResource':'fas fa-asterisk',
              'ZMSLibrary':'fas fa-flask',
              'ZMSPackage':'fas fa-suitcase',
              'ZMSRecordSet':'far fa-list-alt',
              'ZMSReference':'fas fa-link'}
          clazz = clazzes.get(meta_obj.get('type'))
        if not clazz:
          meta_cmd = self.getMetaCmd(id)
          if meta_cmd is not None:
            clazz = meta_cmd.get('icon_clazz')
          elif id == 'workflow':
            clazz = 'fas fa-cog'
        if not clazz:
          clazz = 'far fa-file undefined'
      return clazz


    # --------------------------------------------------------------------------
    #  ZMSObject.display_icon:
    #
    #  @param meta_id
    #  @deprecated @param meta_type
    # --------------------------------------------------------------------------
    def display_icon(self, *args, **kwargs):
      """ ZMSObject.display_icon """
      meta_id = self.meta_id
      if len(args) == 2 and not kwargs:
         meta_id = len(args[1]) > 0 and args[1] or meta_id
      else:
        meta_id = kwargs.get('meta_id', kwargs.get('meta_type', meta_id))
      name = 'fas fa-exclamation-triangle'
      title = bool(meta_id) and self.display_type(meta_id=meta_id) or self.meta_id
      extra = ''
      if meta_id in self.getMetaobjIds( sort=False) + ['ZMSTrashcan']:
        name = self.evalMetaobjAttr( '%s.%s'%(meta_id, 'icon_clazz'))
        if not name:
          names = {'ZMSResource':'fas fa-asterisk icon-asterisk','ZMSLibrary':'fas fa-flask icon-beaker','ZMSPackage':'fas fa-suitcase icon-suitcase','ZMSRecordSet':'far fa-list-alt icon-list','ZMSReference':'fas fa-link icon-link','ZMSTrashcan':'fas fa-trash'}
          name = names.get(meta_id, 'fas fa-file-alt icon-file-alt')
        if meta_id is None:
          constraints = self.attr('check_constraints')
          if isinstance(constraints, dict):
            if len(constraints) > 0:
              name += ' constraint'
            if 'ERRORS' in constraints:
              name += ' constraint-error'
              title += '; '+';'.join(['ERROR: '+x[1] for x in constraints['ERRORS']])
            elif 'WARNINGS' in constraints:
              name += ' constraint-warning'
              title += '; '+'; '.join(['WARNING: '+x[1] for x in constraints['WARNINGS']])
            elif 'RESTRICTIONS' in constraints:
              name += ' constraint-restriction'
              title += '; '+'; '.join(['RESTRICTION: '+x[1] for x in constraints['RESTRICTIONS']])
      else:
        name = 'fas fa-exclamation-triangle constraint-error'
        title = '%s not found!'%str(bool(meta_id) or 'Meta-ID')
      return '<i class="%s" title="%s"%s></i>'%(name,title,extra)


    # --------------------------------------------------------------------------
    #  ZMSObject.display_type:
    #
    #  @param meta_id
    #  @deprecated @param meta_type
    # --------------------------------------------------------------------------
    def display_type(self, *args, **kwargs):
      meta_id = self.meta_id
      if len(args) == 2 and not kwargs:
         meta_id = args[1]
      else:
        meta_id = kwargs.get('meta_id', kwargs.get('meta_type', meta_id))
      metaObj = self.getMetaobj( meta_id)
      if isinstance(metaObj, dict) and 'name' in metaObj:
        meta_id = metaObj[ 'name']
      lang_key = 'TYPE_%s'%meta_id.upper()
      lang_str = self.getZMILangStr( lang_key)
      if lang_key == lang_str:
        return meta_id
      else:
        return lang_str


    # --------------------------------------------------------------------------
    #  ZMSObject.breadcrumbs_obj_path:
    # --------------------------------------------------------------------------
    def breadcrumbs_obj_path(self, portalMaster=True):
      def is_reserved_name(name):
        import keyword
        return keyword.iskeyword(name) or name in dir(__builtins__)
      # Handle This.
      phys_path = list(self.getPhysicalPath())
      phys_path = phys_path[phys_path.index('content'):]
      rtn = [is_reserved_name(id) and getattr(self.getParentNode(),id) or getattr(self, id) for id in phys_path]
      # Handle Portal Master.
      if portalMaster and self.getConfProperty('Portal.Master', ''):
        try:
          thisHome = self.getHome()
          masterHome = getattr(thisHome, self.getConfProperty('Portal.Master', ''), None)
          if masterHome is not None:
            masterDocElmnt = masterHome.content
            obj_item = masterDocElmnt.breadcrumbs_obj_path()
            obj_item.extend(rtn)
            rtn = obj_item
        except:
          standard.writeError( self, '[breadcrumbs_obj_path]: An unexpected error occured while handling portal master!')
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.changeProperties:
    # --------------------------------------------------------------------------
    def changeProperties(self, lang):
      request = self.REQUEST
      request['lang'] = lang or self.getPrimaryLanguage() # ensure correct language is set

      ##### Resources #####
      if 'resources' in self.getMetaobjAttrIds( self.meta_id):
        resources = self.getObjProperty( 'resources', request)
        l = [0 for x in range(len(resources))]
        for key in self.getObjAttrs():
          obj_attr = self.getObjAttr(key)
          el_name = self.getObjAttrName( obj_attr, lang)
          if el_name in request and 'resource_%s'%el_name in request:
            el_value = request.get( el_name)
            if el_value is not None:
              for i in range( len( resources)):
                v = resources[ i]
                if el_value.find( '/'+v.getFilename()) > 0:
                  l[ i] = l[ i] + 1
        c = 0
        for i in range( len( resources)):
          v = resources[ c]
          if l[ i] == 0:
            del resources[ c]
          else:
            src_old = '%s/@%i/%s'%(self.id, i, v.getFilename())
            src_new = '%s/@%i/%s'%(self.id, c, v.getFilename())
            for key in self.getObjAttrs():
              obj_attr = self.getObjAttr(key)
              el_name = self.getObjAttrName( obj_attr, lang)
              if el_name in request and 'resource_%s'%el_name in request:
                el_value = request.get( el_name)
                if el_value is not None:
                  el_value = el_value.replace( src_old, src_new)
                  request.set( el_name, el_value)
            c = c + 1
        for key in self.getObjAttrs():
          obj_attr = self.getObjAttr(key)
          el_name = self.getObjAttrName( obj_attr, lang)
          if el_name in request and 'resource_%s'%el_name in request:
            v = request.get( 'resource_%s'%el_name)
            if isinstance(v, ZPublisher.HTTPRequest.FileUpload):
              if len(getattr(v, 'filename', ''))>0:
                v = _blobfields.createBlobField(self, _blobfields.MyFile, v)
                resources.append( v)
                el_value = request.get( el_name)
                if el_value is not None:
                  src_new = '%s/@%i/%s'%(self.absolute_url(), len(resources)-1, v.getFilename())
                  if v.getContentType().find( 'image/') == 0:
                    el_value = el_value + '<img src="%s" alt="" border="0" align="absmiddle"/>'%src_new
                  else:
                    el_value = el_value + '<a href="%s" target="_blank">%s</a>'%(src_new, v.getFilename())
                  request.set( el_name, el_value)
                  redirect_self = True
        self.setObjProperty( 'resources', resources, lang)

      ##### Primitives #####
      for key in self.getObjAttrs():
        if key not in ['resources']:
          self.setReqProperty(key, request)

      ##### VersionManager ####
      self.onChangeObj(request)

      ##### Resource-Objects #####
      metaObjIds = self.getMetaobjIds()
      metaObjAttrIds = self.getMetaobjAttrIds(self.meta_id)
      for metaObjAttrId in metaObjAttrIds:
        metaObjAttr = self.getMetaobjAttr(self.meta_id, metaObjAttrId)
        if metaObjAttr['type'] in metaObjIds and \
           self.getMetaobj(metaObjAttr['type'])['type'] == 'ZMSResource':
          for childNode in self.getObjChildren(metaObjAttrId, request):
            request.set('objAttrNamePrefix', childNode.id+'_')
            # Object State
            self.setObjStateModified(request)
            # Change Properties
            childNode.changeProperties( lang)
            request.set('objAttrNamePrefix', '')


    ############################################################################
    #  ZMSObject.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE=None):
      """ ZMSObject.manage_changeProperties """
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()

      redirect_self = False
      redirect_self = redirect_self or REQUEST.get('btn', '') == ''
      redirect_self = redirect_self or self.isPage()
      for attr in self.getMetaobj(self.meta_id)['attrs']:
        attr_type = attr['type']
        redirect_self = redirect_self or attr_type in self.getMetaobjIds()+['*']
      redirect_self = redirect_self and (self.isPageContainer() or not REQUEST.get('btn') in [ 'BTN_CANCEL', 'BTN_BACK'])

      if REQUEST.get('btn', '') not in [ 'BTN_CANCEL', 'BTN_BACK']:
        try:
          # Object State
          self.setObjStateModified(REQUEST)
          # Change Properties
          self.changeProperties(lang)
          # Message
          message = self.getZMILangStr('MSG_CHANGED')
        except:
          message = standard.writeError(self, "[manage_changeProperties]")
          messagekey = 'manage_tabs_error_message'
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'

      # Return with message.
      target_ob = self.getParentNode()
      if redirect_self or target_ob is None or REQUEST.get('menulock',0) == 1:
        target_ob = self
        if REQUEST.get('menulock',0) == 1:
          # Remain in Current Menu
          REQUEST.set( 'manage_target', '%s/manage_properties'%target_ob.absolute_url())
      elif REQUEST.get('preview','preview')=='contentEditable':
        target_ob = self
        REQUEST.set( 'manage_target', '%s/preview_html'%target_ob.absolute_url())
      target = REQUEST.get( 'manage_target', '%s/manage_main'%target_ob.absolute_url())
      target = standard.url_append_params( target, { 'lang': lang, messagekey: message},sep='&')
      target = '%s#zmi_item_%s'%( target, self.id)
      if RESPONSE is not None:
        return RESPONSE.redirect( target)


    ############################################################################
    ###
    ###  Common Functions
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.getDeclId:
    #
    #  Returns declarative id.
    # --------------------------------------------------------------------------
    def getDeclId(self, REQUEST={}):
      declId = ''
      try:
        if self.getConfProperty( 'ZMS.pathhandler', 0) != 0:
          for key in [ 'attr_dc_identifier_doi', 'attr_dc_identifier_url_node']:
            declId = self.getObjProperty( key, REQUEST)
            if len( declId) > 0:
              break
          if len(declId) == 0:
            declId = self.getTitlealt( REQUEST)
          mapping = standard.dict_list(self.getConfProperty('ZMS.pathhandler.id_quote.mapping', ' _-_/_\'_'))
          declId = standard.id_quote( declId, mapping)
      except:
        standard.writeError(self, '[getDeclId]: can\'t get declarative id')
      if len( declId) == 0:
        declId = self.id
      return declId


    # --------------------------------------------------------------------------
    #  ZMSObject.aq_absolute_url:
    #
    #  Object is called in a different context and we want to use acquisition.
    # --------------------------------------------------------------------------
    def aq_absolute_url(self, relative=0):
      abs_url = self.absolute_url( relative)
      i = abs_url.find('/content')
      if i > 0:
        home_id = abs_url[:i]
        home_id = home_id[home_id.rfind('/')+1:]
        home_abs_url = self.getHome().absolute_url()
        if home_id in home_abs_url.split('/'):
          abs_url = home_abs_url + abs_url[i:]
      return abs_url


    # --------------------------------------------------------------------------
    #  ZMSObject.getDeclUrl:
    #
    #  Returns declarative url.
    # --------------------------------------------------------------------------
    def getDeclUrl(self, REQUEST={}):
      if self.getConfProperty('ZMS.pathhandler', 0) == 0 or REQUEST.get('preview', '')=='preview':
        url = self.aq_absolute_url()
      else:
        ob = self.getDocumentElement()
        url = ob.aq_absolute_url()
        for id in self.aq_absolute_url()[len(url):].split('/'):
          if len(id) > 0:
            ob = getattr(ob, id, None)
            if ob is None: break
            url += '/' + ob.getDeclId(REQUEST)
      return url


    # --------------------------------------------------------------------------
    #  ZMSObject.getPageExt:
    #
    #  Get page-extension.
    # --------------------------------------------------------------------------
    def getPageExt(self, REQUEST):
      pageexts = ['.html']
      if 'attr_pageext' in self.getObjAttrs():
        obj_attr = self.getObjAttr('attr_pageext')
        if 'keys' in obj_attr and len(obj_attr.get('keys')) > 0:
          pageexts = obj_attr.get('keys')
      pageext = self.getObjProperty('attr_pageext', REQUEST)
      if pageext == '' or pageext is None:
        pageext = pageexts[0]
      return pageext


    # --------------------------------------------------------------------------
    #  ZMSObject.getHref2Html:
    #  ZMSObject.getHref2IndexHtml:
    #
    #  "Sans-Document"-Navigation: reference to first page that contains visible
    #  page-elements.
    # --------------------------------------------------------------------------
    def getHref2Html(self, fct, pageext, REQUEST):
      if not self.isPage():
        parent = self.getParentNode()
        pageext = parent.getPageExt(REQUEST)
        href = parent.getHref2Html( fct, pageext, REQUEST)
        if href.find('#') > 0:
          href = href[:href.find('#')]
        href += '#' + self.id
      else:
        href = self.getDeclUrl(REQUEST)+'/'
        # Assemble href.
        if REQUEST.get('ZMS_INDEX_HTML', 0)==1 or fct != 'index' or len(self.getLangIds())>1:
          href += '%s_%s%s'%(fct, REQUEST.get('lang', self.getPrimaryLanguage()), pageext)
        if REQUEST.get('preview', '')=='preview': href=standard.url_append_params(href, {'preview':'preview'})
      if (REQUEST.get('ZMS_PATHCROPPING', False) or self.getConfProperty('ZMS.pathcropping', 0)==1) and REQUEST.get('export_format', '') == '':
        base = REQUEST.get('BASE0', '')
        if href.find( base) == 0:
          href = href[len(base):]
      return href

    # --------------------------------------------------------------------------
    #  ZMSObject.getAbsoluteUrlInContext:
    #  @param context the current context
    #  @param abs_url e.g. file.getHref(request)
    #  @param forced if True ignore any other conditions
    #  @Configuration
    #  ZMSObject.getAbsoluteUrlInContext=True
    #  ASP.protocol=[http]
    #  ASP.ip_or_domain=[Not empty]
    #
    #  Contextualize absolute_url used in ZMI with subdomain from
    #  config-properties.
    #  Used to keep ZMS-users in configured subdomain-context.
    # --------------------------------------------------------------------------
    def getAbsoluteUrlInContext(self, context, abs_url=None, forced=False):
      context = standard.nvl(context,self)
      if abs_url is None:
        abs_url = self.absolute_url()
      def default(*args, **kwargs):
        context = args[1]['context']
        abs_url = args[1]['abs_url']
        forced = args[1]['forced']
        if context.getConfProperty('ZMSObject.getAbsoluteUrlInContext', False):
          if context.getHome() != self.getHome():
            protocol = context.getConfProperty('ASP.protocol', 'http')
            domain = context.getConfProperty('ASP.ip_or_domain', None)
            if domain:
              l = abs_url.split('/')
              if 'content' in l:
                i = l.index('content')
                if l[i-1] != context.getHome().id and context.getRootElement().getHome().id in l:
                  i = l.index(context.getRootElement().getHome().id)
                else:
                  i += 1
                l = l[i:]
                abs_url = protocol + '://' + domain
                if l:
                  abs_url = abs_url + '/' + '/'.join(l)
        return abs_url
      return self.evalExtensionPoint('ExtensionPoint.ZMSObject.getAbsoluteUrlInContext',default,context=context,abs_url=abs_url,forced=forced)

    # --------------------------------------------------------------------------
    #  ZMSObject.getHref2IndexHtmlInContext:
    #  @param context the current-context
    #  @param index_html the index-html
    #  @param REQUEST the http-request
    #  @param deep the depth-parameter passed to fallback getHref2IndexHtml
    #
    #  Contextualize index_html with subdomain from config-properties.
    # --------------------------------------------------------------------------
    def getHref2IndexHtmlInContext(self, context, index_html=None, REQUEST=None, deep=1):
      context = standard.nvl(context,self)
      if index_html is None:
        index_html = self.getHref2IndexHtml(REQUEST, deep)
      if REQUEST.get('ZMS_CONTEXT_URL', False) or self.getConfProperty('ZMSObject.getHref2IndexHtmlInContext.forced', False) or self.getHome() != context.getHome():
        protocol = self.getConfProperty('ASP.protocol', 'http')
        domain = self.getConfProperty('ASP.ip_or_domain', None)
        if domain is not None and len(domain) > 0:
          l = index_html.split('/')
          if 'content' in l:
            i = l.index('content')
            if l[i-1] != self.getHome().id and self.getRootElement().getHome().id in l:
              i = l.index(self.getRootElement().getHome().id)
            else:
              i += 1
            l = l[i:]
            index_html = protocol + '://' + domain + '/' + '/'.join(l)
      elif REQUEST.get('ZMS_RELATIVATE_URL', True) and self.getConfProperty('ZMSObject.getHref2IndexHtmlInContext.relativate', True) and self.getHome() == context.getHome():
        path = REQUEST.get('URL')
        if path:
          path = re.sub(r'\/index_(.*?)\/index_html$','/index_\\1',path)
          path = re.sub(r'\/index_html$','/',path)
          index_html = self.getRelativeUrl(path,index_html)
      return index_html

    #++
    def getHref2IndexHtml(self, REQUEST, deep=1):
      deep = int(self.getConfProperty('ZMSObject.getHref2IndexHtml.deep', deep))
      ob = self
      if 'getHref2IndexHtml' in ob.getMetaobjAttrIds(ob.meta_id):
        value = ob.attr('getHref2IndexHtml')
      else:
        fct = REQUEST.get('ZMS_SKIN', 'index')
        if fct == 'index' and 'index_html' in self.objectIds():
          value = self.absolute_url()
          for param in ['lang', 'preview']:
            if REQUEST.get(param, '') != '':
              value = standard.url_append_params(value, {param:REQUEST[param]})
        else:
          if deep:
            def get_page_with_elements(node):
              if node.isPageContainer():
                for childNode in node.getChildNodes(REQUEST):
                  if childNode.isVisible(REQUEST):
                    if childNode.isPageElement():
                      return node
                    elif childNode.isPage():
                      return get_page_with_elements(childNode)
              return node
            ob = get_page_with_elements(self)
          value = ob.getHref2Html( fct, ob.getPageExt(REQUEST), REQUEST)
      return value


    ############################################################################
    ###
    ###  DOM-Methods
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.getLevel:
    #
    #  The hierarchical level of this node.
    # --------------------------------------------------------------------------
    def getLevel(self):
      docElmnt = self.getDocumentElement()
      docPath = docElmnt.getPhysicalPath()
      path = self.getPhysicalPath()
      return len(path)-len(docPath)


    # --------------------------------------------------------------------------
    #  ZMSObject.is_child:
    #  @param ob the object
    #
    #  True if self is child of given object.
    # --------------------------------------------------------------------------
    def is_child_of(self, ob):
      if ob is not None:
        path = '/'.join(self.getPhysicalPath())
        obPath = '/'.join(ob.getPhysicalPath())
        return path.startswith(obPath)
      return False


    # --------------------------------------------------------------------------
    #  ZMSObject.isAncestor:
    #  @param ob the object
    #
    #  True if self is ancestor of given object.
    # --------------------------------------------------------------------------
    def isAncestor(self, ob):
      if ob is not None:
        path = '/'.join(self.getPhysicalPath())
        obPath = '/'.join(ob.getPhysicalPath())
        return obPath.startswith(path)
      return False


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentByDepth:
    #  @param deep the depth
    #
    #  The parent of this node by depth.
    # --------------------------------------------------------------------------
    def getParentByDepth(self, deep):
      rtn = self
      for i in range(deep):
        rtn = rtn.getParentNode()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentByLevel:
    #  @param level the level
    #
    #  The parent of this node by level.
    # --------------------------------------------------------------------------
    def getParentByLevel(self, level):
      rtn = self
      while rtn.getLevel() > level:
        rtn = rtn.getParentNode()
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getParentNode:
    #
    #  The parent of this node.
    #  All nodes except root may have a parent.
    # --------------------------------------------------------------------------
    def getParentNode(self):
      rtn = getattr(self, 'aq_parent', None)
      # Handle ZMSProxyObjects.
      if hasattr( rtn, 'is_blob') or hasattr( rtn, 'base'):
        rtn = getattr( self, self.absolute_url().split( '/')[-2], None)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getTreeNodes:
    #
    #  Returns a NodeList that contains all children of this subtree in correct order.
    #  If none, this is a empty NodeList.
    # --------------------------------------------------------------------------
    def getTreeNodes(self, REQUEST={}, meta_types=None):
      rtn = []
      for ob in self.getChildNodes(REQUEST):
        if ob.isMetaType(meta_types): rtn.append(ob)
        rtn.extend(ob.getTreeNodes(REQUEST, meta_types))
      return rtn


    ############################################################################
    ###
    ###  Sort-Order
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.setSortId:
    #
    #  Sets Sort-ID (integer).
    # --------------------------------------------------------------------------
    def setSortId(self, sort_id):
      sort_id = '0000%i'%sort_id
      sort_id = 's' + sort_id[-4:]
      self.sort_id = sort_id


    # --------------------------------------------------------------------------
    #  ZMSObject.getSortId:
    #
    #  Returns Sort-ID (integer).
    # --------------------------------------------------------------------------
    def getSortId(self):
      rtnVal = 0
      sort_id = getattr( self, 'sort_id','')
      if sort_id:
        rtnVal = int(sort_id[len(standard.id_prefix(sort_id)):])
      return rtnVal


    ############################################################################
    # ZMSObject.manage_moveObjUp:
    #
    # Moves an object up in sort order.
    ############################################################################
    def manage_moveObjUp(self, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_moveObjUp """
      parent = self.getParentNode()
      sort_id = self.getSortId()
      self.setSortId(sort_id - 15)
      parent.normalizeSortIds(standard.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJUP')%("<i>%s</i>"%self.display_type())
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(), lang, standard.url_quote(message), self.id))


    ############################################################################
    # ZMSObject.manage_moveObjDown:
    #
    # Moves an object down in sort order.
    ############################################################################
    def manage_moveObjDown(self, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_moveObjDown """
      parent = self.getParentNode()
      sort_id = self.getSortId()
      self.setSortId(sort_id + 15)
      parent.normalizeSortIds(standard.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJDOWN')%("<i>%s</i>"%self.display_type())
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(), lang, standard.url_quote(message), self.id))


    ############################################################################
    # ZMSObject.manage_moveObjToPos:
    #
    # Moves an object to specified position in sort order.
    ############################################################################
    def manage_moveObjToPos(self, lang, pos, fmt=None, REQUEST=None, RESPONSE=None):
      """ ZMSObject.manage_moveObjToPos """
      parent = self.getParentNode()
      if parent is not None:
        id_prefix = standard.id_prefix(self.id)
        childNodes = parent.getObjChildren(id_prefix,REQUEST)
        old = childNodes.index(self)
        sibling_sort_ids = [x.sort_id for x in childNodes]
        sibling_sort_ids.remove(self.sort_id)
        pos = pos - 1
        if pos < len(sibling_sort_ids):
          new_sort_id = int(sibling_sort_ids[pos][1:])-1
        else:
          new_sort_id = int(sibling_sort_ids[-1][1:])+1
        self.setSortId(new_sort_id)
        parent.normalizeSortIds(id_prefix)
      else:
        id = REQUEST['URL'].split('/')[-2]
        ids = self.getConfProperty('Portal.Clients',[])
        if id in ids:
          offset = len(self.getChildNodes(REQUEST))
          old = ids.index(id)
          pos = pos - offset - 1
          ids.insert(pos, ids.pop(old))
          self.setConfProperty('Portal.Clients',ids)
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJ%s'%['UP','DOWN'][int(old<pos)])%("<i>%s</i>"%self.display_type())
      if fmt == 'json':
        return self.str_json(message)
      else:
        RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(),lang,standard.url_quote(message),self.id))


    ############################################################################
    #  MetacmdObject.manage_executeMetacmd:
    #
    #  Execute Meta-Command.
    ############################################################################
    def manage_executeMetacmd(self, id, REQUEST, RESPONSE=None, context=None):
      """ MetacmdObject.manage_executeMetacmd """
      if RESPONSE:
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
      lang = REQUEST.get('lang')
      value = None
      message = ''
      target = self
      zmscontext = standard.nvl(context, self)

      # METAOBJ
      metaObjAttr = zmscontext.getMetaobjAttr(zmscontext.meta_id, id)
      if metaObjAttr is not None:
        # Execute directly.
        return zmscontext.attr(id)

      # METACMD
      metaCmd = self.getMetaCmd(id)
      if metaCmd is not None:
        # Execute metacmd.
        ob = zopeutil.getObject(self, id)
        # Proceed with generating message for executed metacmd.
        if bool(metaCmd.get('execution')) and not metaCmd['id'].startswith('manage_tab_'):
          value = zopeutil.callObject(ob, zmscontext=zmscontext)
          if isinstance(value, str):
            message = value
          elif isinstance(value, tuple):
            target = value[0]
            message = value[1]
        # Proceed with redirecting to tab view.
        else:
          loc = '%s/%s?lang=%s'%(target.absolute_url(),metaCmd['id'],lang)
          status = 302
          if REQUEST.method == 'GET':
            value = zopeutil.callObject(ob, zmscontext=zmscontext)
            status = 201 # Turbolinks
            RESPONSE.setHeader('Location',loc)
            RESPONSE.setHeader('Turbolinks-Location',loc)
          if RESPONSE:
            RESPONSE.redirect(loc,status=status)
          return value

      # Return with message.
      if RESPONSE:
        message = standard.url_quote(message)
        if message == 'ERROR':
          return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_error_message=ERROR'%(target.absolute_url(), lang))
        return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s'%(target.absolute_url(), lang, message))


    # --------------------------------------------------------------------------
    #  ZMSObject.getBodyContent:
    # --------------------------------------------------------------------------
    def _getBodyContentContentEditable(self, html):
      request = self.REQUEST
      if standard.isPreviewRequest(request) and \
         (request.get('URL').find('/manage')>0 or self.getConfProperty('ZMS.preview.contentEditable', 1)==1):
        css = ['contentEditable', self.meta_id, self.isPage() and 'zms-page' or 'zms-pageelement']
        html = '<div class="%s" data-absolute-url="%s">%s</div>'%(' '.join(css), self.absolute_url()[len(self.REQUEST['BASE0']):], html)
      return html

    def _getBodyContent(self, REQUEST):
      rtn = self._getBodyContentContentEditable(self.metaobj_manager.renderTemplate( self))
      return rtn

    security.declareProtected('View', 'ajaxGetBodyContent')
    def ajaxGetBodyContent(self, REQUEST, forced=False):
      """
      HTML presentation in body-content. 
      """
      return self.getBodyContent(REQUEST, forced)

    def getBodyContent(self, REQUEST, forced=False):
      html = ''
      if forced or self.isVisible( REQUEST):
        html = self._getBodyContent( REQUEST)
        # Process custom hook.
        name = 'getCustomBodyContent'
        if hasattr(self, name):
          html = getattr(self, name)(context=self, html=html, REQUEST=REQUEST)
      return html


    # --------------------------------------------------------------------------
    #  ZMSObject.renderShort:
    #
    #  Renders short presentation of object.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST, manage_main=False):
      html = ''
      metaObjAttrIds = self.getMetaobjAttrIds(self.meta_id)
      try:
        if 'renderShort' in metaObjAttrIds and (not manage_main or 'standard_html' in metaObjAttrIds or "bodyContentZMSCustom_%s"%self.meta_id in metaObjAttrIds):
          html = self._getBodyContentContentEditable(self.attr('renderShort'))
        elif self.isPage() or manage_main:
          if manage_main:
            html = '<h1>'
            html += self.getTitle(REQUEST)
            desc = self.getDCDescription(REQUEST)
            if desc:
              html += '<small>%s</small>'%desc
            html+= '</h1>'
          else:
            html = self.getTitlealt(REQUEST)
          html = self._getBodyContentContentEditable(html)
        else:
          html = self._getBodyContent(REQUEST)
      except:
        html = standard.writeError(self, "[renderShort]")
        html = '<br/>'.join(standard.html_quote(html).split('\n'))
      # Return <html>.
      return html


    ############################################################################
    ###
    ###  Printable
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.printHtml:
    #
    #  Renders printable presentation.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      html = ''

      # Title.
      sectionizer.processLevel( level)
      title = self.getTitle( REQUEST)
      title = '%s %s'%(str(sectionizer), title)
      REQUEST.set( 'ZMS_SECTIONIZED_TITLE', '<h%i>%s</h%i>'%( level, title, level))

      # bodyContent
      html += self._getBodyContent(REQUEST)

      # Container-Objects.
      if deep:
        for ob in self.filteredChildNodes(REQUEST, self.PAGES):
          html += ob.printHtml( level+1, sectionizer, REQUEST, deep)

      # Return <html>.
      return html


    ############################################################################
    ###
    ###  XML-Builder
    ###
    ############################################################################

    ############################################################################
    # ZMSObject.xmlOnStartElement(self, dTagName, dAttrs, oCurrNodes):
    # ZMSObject.xmlOnCharacterData(self, data, bInCData):
    # ZMSObject.xmlOnEndElement(self):
    # ZMSObject.xmlOnUnknownStartTag(self, sTagName, dTagAttrs)
    # ZMSObject.xmlOnUnknownEndTag(self, sTagName)
    # ZMSObject.xmlGetParent(self):
    #
    # handler for XML-Builder (_builder.py)
    ############################################################################
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode):
        standard.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)

        self.dTagStack    = collections.deque()
        self.dValueStack  = collections.deque()

        # WORKAROUND! The member variable "aq_parent" does not contain the right
        # parent object at this stage of the creation process (it will later
        # on!). Therefore, we introduce a special attribute containing the
        # parent object, which will be used by xmlGetParent() (see below).
        self.oParent = oParentNode


    def xmlOnEndElement(self):
        self.initObjChildren( self.REQUEST)


    def xmlOnCharacterData(self, sData, bInCData):
        return _xmllib.xmlOnCharacterData(self, sData, bInCData)


    def xmlOnUnknownStartTag(self, sTagName, dTagAttrs):
        return _xmllib.xmlOnUnknownStartTag(self, sTagName, dTagAttrs)


    def xmlOnUnknownEndTag(self, sTagName):
        return _xmllib.xmlOnUnknownEndTag(self, sTagName)


    def xmlGetParent(self):
        return self.oParent


# call this to initialize framework classes, which
# does the right thing with the security assertions.
InitializeClass(ZMSObject)

################################################################################
