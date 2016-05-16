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
from DateTime.DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from types import StringTypes
import Globals
import ZPublisher.HTTPRequest
import urllib
import string
import time
# Product Imports.
import zmscontainerobject
import ZMSItem
import ZMSGlobals
import ZMSWorkflowItem
import _accessmanager
import _blobfields
import _cachemanager
import _confmanager
import _copysupport
import _deprecatedapi
import _exportable
import _globals
import _multilangmanager
import _objattrs
import _objchildren
import _objinputs
import _objtypes
import _pathhandler
import _versionmanager
import _xmllib
import _textformatmanager
import _zcatalogmanager
import _zmsattributecontainer
import _zreferableitem

__all__= ['ZMSObject']


################################################################################
################################################################################
###
###   Abstract Class ZMSObject
###
################################################################################
################################################################################
class ZMSObject(ZMSItem.ZMSItem,
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
	_zcatalogmanager.ZCatalogItem,		# ZCatalog Item.
	ZMSGlobals.ZMSGlobals,			# ZMS Global Functions and Definitions.
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
    MISC_ZMS = '/misc_/zms/'
    FORM_LABEL_MANDATORY = '<sup style="color:red">*</sup>'
    spacer_gif = '/misc_/zms/spacer.gif'

    # ZPT Templates.
    # --------------
    zmi_navbar_brand = PageTemplateFile('zpt/common/zmi_navbar_brand', globals())
    zmi_icon = PageTemplateFile('zpt/common/zmi_icon', globals())
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
    zmi_ace_editor = PageTemplateFile('zpt/common/zmi_ace_editor',globals())

    # Templates.
    # ----------
    f_display_icon = PageTemplateFile('zpt/object/f_display_icon', globals()) # ZMI Display-Icon
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
      self.sort_id = _globals.format_sort_id(sort_id)
      self.ref_by = []


    # --------------------------------------------------------------------------
    #  ZMSObject.f_css_defaults:
    # --------------------------------------------------------------------------
    def f_css_defaults(self, REQUEST=None):
      """ ZMSObject.f_css_defaults """
      if REQUEST is None:
        REQUEST = self.REQUEST
      return self.zmi_css_defaults(REQUEST)

    def zmi_css_defaults(self, REQUEST):
      """ ZMSObject.zmi_css_defaults """
      RESPONSE = REQUEST.RESPONSE
      RESPONSE.setHeader('Last-Modified',DateTime(self.getConfProperty('last_modified')-10000).toZone('GMT+1').rfc822())
      if not RESPONSE.headers.has_key('cache-control'):
        RESPONSE.setHeader('Cache-Control','public, max-age=3600')
      REQUEST.RESPONSE.setHeader('Content-Type','text/css')
      l = []
      for metaObjId in self.getMetaobjIds(sort=0):
        metaObj = self.getMetaobj(metaObjId)
        for metaObjAttr in filter(lambda x: x['type']=='css' or x['id']=='f_css_defaults', metaObj.get('attrs',[])):
            id = metaObjAttr['id']
            s = '%s.%s'%(metaObjId,id)
            l.append('/* %s */'%('#'*len(s)))
            l.append('/* %s */'%(s))
            l.append('/* %s */'%('#'*len(s)))
            try:
              l.append(self.attr(s))
            except:
              l.append('/* >>>>>>>>>> ERROR in %s <<<<<<<<<< */'%_globals.writeError(self,"[zmi_css_defaults]: %s"%s))
      return '\n'.join(map(lambda x:str(x),l))

    ############################################################################
    #
    # ZMS Object Index
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSObject.get_uid:
    # --------------------------------------------------------------------------
    def get_uid(self, forced=False, implementation=None):
      def default(*args, **kwargs):
        self = args[0]
        forced = args[1]['forced']
        root_id = self.getRootElement().getHome().id
        physical_path = self.getPhysicalPath()
        home_path = physical_path[physical_path.index(root_id):physical_path.index('content')]
        object_path = physical_path[physical_path.index('content')+1:]
        return '%s@%s'%('/'.join(home_path),'/'.join(object_path))
      can_ep = True
      if type(implementation) is str:
        ep = self.getConfProperty('ExtensionPoint.ZMSObject.get_uid','')
        can_ep = ep.startswith(implementation)
      if can_ep:
        uid = self.evalExtensionPoint('ExtensionPoint.ZMSObject.get_uid',default,forced=forced)
      else:
        uid = default(self,{'forced':forced})
      return uid

    # --------------------------------------------------------------------------
    #  ZMSObject.set_uid:
    # --------------------------------------------------------------------------
    def set_uid(self, uid):
      self._uid = uid.replace('uid:','')

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
      prefix = '%s_'%(self.id_quote(self.get_oid()))
      # Remove old context-values.
      for key in filter(lambda x:x.startswith(prefix),REQUEST.keys()):
        _globals.writeLog(self,"[set_request_context]: DEL "+key)
        REQUEST.set(key,None)
      # Set new context-values.
      for key in d.keys():
        context = prefix+key
        value = d[key]
        _globals.writeLog(self,"[set_request_context]: SET "+context+"="+str(value))
        REQUEST.set(context,value)

    # --------------------------------------------------------------------------
    #  ZMSObject.get_request_context:
    # --------------------------------------------------------------------------
    def get_request_context(self, REQUEST, key, defaultValue=None):
      context = '%s_%s'%(self.id_quote(self.get_oid()),key)
      # Get context-value.
      value = REQUEST.get(context,None)
      if value is not None:
        _globals.writeLog(self,"[get_request_context]: GET "+context+"="+str(value))
        return value 
      return REQUEST.get(key,defaultValue)

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
    #  ZMSObject.get_conf_blob:
    # --------------------------------------------------------------------------
    security.declarePublic('get_conf_blob')
    def get_conf_blob(self, path, REQUEST, RESPONSE):
      """ ZMS.get_conf_blob """
      v = self.getConfProperties()
      try:
        for id in path.split('/'):
          if type(v) is dict:
            v = v[id]
          elif type(v) is list:
            if id.find( ':int') > 0:
              v = v[ int( id[:id.find( ':int')])]
            elif id in v:
              v = v[ v.index(id)+1]
            else:
              l = filter(lambda x: x.get('id',None)==id, v)
              if len( l) > 0:
                v = l[ 0]
        RESPONSE.setHeader( 'Cache-Control', 'public, max-age=3600')
        RESPONSE.setHeader( 'Content-Type', v.getContentType())
        RESPONSE.setHeader( 'Content-Disposition', 'inline;filename="%s"'%v.getFilename())
        v = v.getData()
      except:
        masterId = self.getConfProperty('Portal.Master','')
        if len(masterId) > 0:
          masterHome = getattr(self.getHome(),masterId)
          masterDocElmnt = masterHome.content
          v = masterDocElmnt.get_conf_blob(path, REQUEST, RESPONSE)
        else:
          _globals.writeError(self,"[get_conf_blob]: path=%s"%str(path))
      return v

    # --------------------------------------------------------------------------
    #  ZMSObject.isMetaType:
    # --------------------------------------------------------------------------
    def isMetaType(self, meta_type, REQUEST={}):
      if meta_type is None:
        return True
      if type(meta_type) is not list:
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
      return self.getType() in [ 'ZMSObject', 'ZMSRecordSet'] \
        and not self.meta_id in [ 'ZMSNote', 'ZMSTeaserContainer']


    # --------------------------------------------------------------------------
    #  ZMSObject.getTitle
    # --------------------------------------------------------------------------
    def getTitle( self, REQUEST):
      s = self.getObjProperty('title',REQUEST)
      if s is None or len(s) == 0:
        if self.isPage():
          metaObjAttrs = self.getMetaobj( self.meta_id).get( 'attrs', [])
          offs = 1
          c = 0
          for metaObjAttr in metaObjAttrs:
            if metaObjAttr[ 'type'] in [ 'constant', 'method', 'py', 'string', 'select']:
              if c == offs:
                v = self.getObjProperty( metaObjAttr[ 'id'], REQUEST)
                if type(v) in StringTypes:
                  s = v
                  break
              c = c + 1
      if s is None or len(s) == 0:
        s = self.display_type(REQUEST)
      if self.isPage():
        sec_no = self.getSecNo()
        if len(sec_no) > 0:
          s = sec_no + ' ' + s
      s = s.replace(' & ',' &amp; ')
      return s


    # --------------------------------------------------------------------------
    #  ZMSObject.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST):
      s = self.getObjProperty('titlealt',REQUEST)
      if s is None or len(s) == 0: 
        s = self.display_type(REQUEST)
      if s is None or len(s) == 0:
        if self.isPage():
          metaObjAttrs = self.getMetaobj( self.meta_id).get( 'attrs', [])
          offs = 0
          c = 0
          for metaObjAttr in metaObjAttrs:
            if metaObjAttr[ 'type'] in [ 'constant', 'method', 'py', 'string', 'select']:
              if c == offs:
                v = self.getObjProperty( metaObjAttr[ 'id'], REQUEST)
                if type(v) in StringTypes:
                  s = v
                  break
              c = c + 1
      if self.isPage():
        sec_no = self.getSecNo()
        if len(sec_no) > 0:
          s = sec_no + ' ' + s
      s = s.replace(' & ',' &amp; ')
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
      return metaObj.get('type','ZMSDocument')


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
      return self.getObjProperty('attr_dc_type',REQUEST) == 'Resource' or \
        self.id in REQUEST.get( 'ZMS_IDS_RESOURCE', [])


    # --------------------------------------------------------------------------
    #  ZMSObject.is_translated:
    #
    #  alias for isTranslated(lang,request)
    # --------------------------------------------------------------------------
    def is_translated(self,lang):
      return self.isTranslated(lang,self.REQUEST)

    # --------------------------------------------------------------------------
    #  ZMSObject.isTranslated
    #
    #  Returns True if current object is translated to given language.
    # --------------------------------------------------------------------------
    def isTranslated(self, lang, REQUEST):
      rtnVal = False
      req = {'lang':lang,'preview':REQUEST.get('preview','')}
      value = self.getObjProperty('change_uid',req)
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
        req = {'lang':lang, 'preview':REQUEST.get('preview','') }
        change_dt_lang = self.getObjProperty('change_dt',req)
        req = {'lang':parent, 'preview':REQUEST.get('preview','') }
        change_dt_parent = self.getObjProperty('change_dt',req)
        try:
          if change_dt_lang is not None and change_dt_parent is not None:
            rtnVal = _globals.compareDate(change_dt_lang, change_dt_parent) > 0
        except:
          _globals.writeError(self,"[isModifiedInParentLanguage]: Unexpected exception: change_dt_lang=%s, change_dt_parent=%s!"%(str(change_dt_lang),str(change_dt_parent)))
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
      REQUEST = _globals.nvl(REQUEST,self.REQUEST)
      lang = REQUEST.get('lang',self.getPrimaryLanguage())
      visible = True
      visible = visible and self.isTranslated(lang,REQUEST) # Object is translated.
      visible = visible and self.isCommitted(REQUEST) # Object has been committed.
      visible = visible and self.isActive(REQUEST) # Object is active.
      return visible


    # --------------------------------------------------------------------------
    #  ZMSObject.get_size
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def get_size(self, REQUEST={}):
      size = 0
      keys = self.getObjAttrs().keys()
      if self.getType()=='ZMSRecordSet':
        keys = [self.getMetaobjAttrIds(self.meta_id)[0]]
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
      key_coverage = 'attr_dc_coverage'
      obj_vers = self.getObjVersion(REQUEST)
      coverage = getattr( obj_vers, key_coverage, '') # Take a performant shortcut to get object-property.
      coverages = [ '', 'obligation', None]
      if coverage in coverages: 
        coverage = 'global.' + self.getPrimaryLanguage()
      return coverage


    # --------------------------------------------------------------------------
    #  ZMSObject.getDCDescription
    #
    #  Returns "Dublin Core: Description".
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def getDCDescription(self, REQUEST):
      return self.getObjProperty('attr_dc_description',REQUEST)


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
    #  ZMSObject.icon:
    # --------------------------------------------------------------------------
    def icon(self):
      return "++resource++zms_/img/ZMSObject.png"


    # --------------------------------------------------------------------------
    #  ZMSObject.display_icon:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_icon(self, REQUEST={}, meta_type=None, key='icon', zpt=True):
      """ ZMSObject.display_icon """
      id = _globals.nvl(meta_type,self.meta_id)
      icon_title = self.display_type(meta_type=id)
      if id in self.getMetaobjIds( sort=0):
        name = self.evalMetaobjAttr( '%s.%s'%(id,'icon_clazz'))
        if name is None:
          value = self.evalMetaobjAttr( '%s.%s'%(id,key)) 
          if value is not None and type(value) is not str:
            return '<img src="%s" title="%s"/>'%(value.absolute_url(),icon_title)
          else:
            metaObj = self.getMetaobj(id)
            names = {'ZMSResource':'icon-asterisk','ZMSLibrary':'icon-beaker','ZMSPackage':'icon-suitcase','ZMSRecordSet':'icon-list','ZMSReference':'icon-link'}
            name = names.get(metaObj.get('type'),'icon-file-alt')
        if meta_type is None:
          constraints = self.attr('check_constraints')
          if type(constraints) is dict:
            if len(constraints.keys()) > 0:
              name += ' constraint'
            if constraints.has_key('ERRORS'):
              name += ' constraint-error'
              icon_title += '; '+';'.join(map(lambda x:'ERROR: '+x[1],constraints['ERRORS']))
            elif constraints.has_key('WARNINGS'):
              name += ' constraint-warning'
              icon_title += '; '+'; '.join(map(lambda x:'WARNING: '+x[1],constraints['WARNINGS']))
            elif constraints.has_key('RESTRICTIONS'):
              name += ' constraint-restriction'
              icon_title += '; '+'; '.join(map(lambda x:'RESTRICTION: '+x[1],constraints['RESTRICTIONS']))
      else:
        name = 'icon-warning-sign constraint-error'
        icon_title = '%s not found!'%str(id)
      return self.zmi_icon(self,name=name,extra='title="%s"'%(unicode(icon_title,'utf-8').replace('"','\'')))


    # --------------------------------------------------------------------------
    #  ZMSObject.display_type:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_type(self, REQUEST={}, meta_type=None):
      meta_type = _globals.nvl( meta_type, self.meta_id)
      metaObj = self.getMetaobj( meta_type)
      if type( metaObj) is dict and metaObj.has_key( 'name'):
        meta_type = metaObj[ 'name']
      lang_key = 'TYPE_%s'%meta_type.upper()
      lang_str = self.getZMILangStr( lang_key)
      if lang_key == lang_str:
        return meta_type
      else:
        return lang_str


    # --------------------------------------------------------------------------
    #  ZMSObject.breadcrumbs_obj_path:
    # --------------------------------------------------------------------------
    def breadcrumbs_obj_path(self, portalMaster=True):
      REQUEST = self.REQUEST
      # Handle This.
      rtn = []
      obj = self
      for lvl in range(self.getLevel()+1):
        if obj is not None:
          obj_item = [obj]
          obj_item.extend(rtn)
          rtn = obj_item
          obj = obj.getParentNode()
      # Handle Portal Master.
      if portalMaster and self.getConfProperty('Portal.Master',''):
        try:
          thisHome = self.getHome()
          masterHome = getattr(thisHome,self.getConfProperty('Portal.Master',''),None)
          if masterHome is not None:
            masterDocElmnt = masterHome.content
            obj_item = masterDocElmnt.breadcrumbs_obj_path()
            obj_item.extend(rtn)
            rtn = obj_item
        except:
          _globals.writeError( self, '[breadcrumbs_obj_path]: An unexpected error occured while handling portal master!')
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.changeProperties:
    # --------------------------------------------------------------------------
    def changeProperties(self, lang):
      request = self.REQUEST
      request['lang'] = lang # ensure correct language is set
      
      ##### Resources #####
      if 'resources' in self.getMetaobjAttrIds( self.meta_id):
        resources = self.getObjProperty( 'resources', request)
        l = map( lambda x: 0, range( len( resources)))
        for key in self.getObjAttrs().keys():
          obj_attr = self.getObjAttr( key)
          el_name = self.getObjAttrName( obj_attr, lang)
          if request.has_key( el_name) and request.has_key( 'resource_%s'%el_name):
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
            src_old = '%s/@%i/%s'%(self.id,i,v.getFilename())
            src_new = '%s/@%i/%s'%(self.id,c,v.getFilename())
            for key in self.getObjAttrs().keys():
              obj_attr = self.getObjAttr( key)
              el_name = self.getObjAttrName( obj_attr, lang)
              if request.has_key( el_name) and request.has_key( 'resource_%s'%el_name):
                el_value = request.get( el_name)
                if el_value is not None:
                  el_value = el_value.replace( src_old, src_new)
                  request.set( el_name, el_value)
            c = c + 1
        for key in self.getObjAttrs().keys():
          obj_attr = self.getObjAttr( key)
          el_name = self.getObjAttrName( obj_attr, lang)
          if request.has_key( el_name) and request.has_key( 'resource_%s'%el_name):
            v = request.get( 'resource_%s'%el_name)
            if isinstance(v,ZPublisher.HTTPRequest.FileUpload):
              if len(getattr(v,'filename',''))>0:
                v = _blobfields.createBlobField(self,_globals.DT_FILE,v)
                resources.append( v)
                el_value = request.get( el_name)
                if el_value is not None:
                  src_new = '%s/@%i/%s'%(self.absolute_url(),len(resources)-1,v.getFilename())
                  if v.getContentType().find( 'image/') == 0:
                    el_value = el_value + '<img src="%s" alt="" border="0" align="absmiddle"/>'%src_new
                  else:
                    el_value = el_value + '<a href="%s" target="_blank">%s</a>'%(src_new,v.getFilename())
                  request.set( el_name, el_value)
                  redirect_self = True
        self.setObjProperty( 'resources', resources, lang)
      
      ##### Primitives #####
      for key in self.getObjAttrs().keys():
        if key not in ['resources']:
          self.setReqProperty(key,request)
      
      ##### VersionManager ####
      self.onChangeObj(request)
      
      ##### Resource-Objects #####
      metaObjIds = self.getMetaobjIds(sort=0)
      metaObjAttrIds = self.getMetaobjAttrIds(self.meta_id)
      for metaObjAttrId in metaObjAttrIds:
        metaObjAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrId)
        if metaObjAttr['type'] in metaObjIds and \
           self.getMetaobj(metaObjAttr['type'])['type'] == 'ZMSResource':
          for childNode in self.getObjChildren(metaObjAttrId,request):
            request.set('objAttrNamePrefix',childNode.id+'_')
            # Object State
            self.setObjStateModified(request)
            # Change Properties
            childNode.changeProperties( lang)
            request.set('objAttrNamePrefix','')


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
      redirect_self = redirect_self or REQUEST.get('btn','') == ''
      redirect_self = redirect_self or self.isPage()
      for attr in self.getMetaobj(self.meta_id)['attrs']:
        attr_type = attr['type']
        redirect_self = redirect_self or attr_type in self.getMetaobjIds()+['*']
      redirect_self = redirect_self and (self.isPageContainer() or not REQUEST.get('btn','') in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')])
      
      if REQUEST.get('btn','') not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
          # Object State
          self.setObjStateModified(REQUEST)
          # Change Properties
          self.changeProperties(lang)
          # Message
          message = self.getZMILangStr('MSG_CHANGED')
        except:
          message = _globals.writeError(self,"[manage_changeProperties]")
          messagekey = 'manage_tabs_error_message'
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      target_ob = self.getParentNode()
      if redirect_self or target_ob is None:
        target_ob = self
      target = REQUEST.get( 'manage_target', '%s/manage_main'%target_ob.absolute_url())
      target = self.url_append_params( target, { 'lang': lang, messagekey: message})
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
          obj_attrs_keys = self.getMetaobjAttrIds(self.meta_id)
          for key in [ 'attr_dc_identifier_doi', 'attr_dc_identifier_url_node']:
            if key in obj_attrs_keys:
              declId = self.getObjProperty( key, REQUEST)
              if len( declId) > 0:
                break
          if len(declId) == 0:
            declId = self.getTitlealt( REQUEST)
          mapping = self.dict_list(self.getConfProperty('ZMS.pathhandler.id_quote.mapping',' _-_/_\'_'))
          declId = self.id_quote( declId, mapping)
      except:
        _globals.writeError(self,'[getDeclId]: can\'t get declarative id')
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
      if self.getConfProperty('ZMS.pathhandler',0) == 0 or REQUEST.get('preview','')=='preview':
        url = self.aq_absolute_url()
      else:
        ob = self.getDocumentElement()
        url = ob.aq_absolute_url()
        for id in self.aq_absolute_url()[len(url):].split('/'):
          if len(id) > 0:
            ob = getattr(ob,id,None)
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
      if 'attr_pageext' in self.getObjAttrs().keys():
        obj_attr = self.getObjAttr('attr_pageext')
        if obj_attr.has_key('keys') and len(obj_attr.get('keys')) > 0:
          pageexts = obj_attr.get('keys')
      pageext = self.getObjProperty('attr_pageext',REQUEST)
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
        if REQUEST.get('ZMS_INDEX_HTML',0)==1 or fct != 'index' or len(self.getLangIds())>1:
          href += '%s_%s%s'%(fct,REQUEST.get('lang',self.getPrimaryLanguage()),pageext)
        if REQUEST.get('preview','')=='preview': href=self.url_append_params(href,{'preview':'preview'})
      if (REQUEST.get('ZMS_PATHCROPPING',False) or self.getConfProperty('ZMS.pathcropping',0)==1) and REQUEST.get('export_format','') == '':
        base = REQUEST.get('BASE0','')
        if href.find( base) == 0:
          href = href[len(base):]
      return href
      
    #++
    def getHref2IndexHtmlInContext(self, context, index_html, REQUEST, deep=1):
      if self.getConfProperty('ZMSObject.getHref2IndexHtmlInContext.forced',False) or self.getHome() != context.getHome():
        protocol = self.getConfProperty('ASP.protocol','http')
        domain = self.getConfProperty('ASP.ip_or_domain',None)
        if domain is not None:
          l = index_html.split('/')
          if 'content' in l:
            i = l.index('content')
            if l[i-1] != self.getHome().id and self.getRootElement().getHome().id in l:
              i = l.index(self.getRootElement().getHome().id)
            else:
              i += 1
            l = l[i:]
            index_html = protocol + '://' + domain + '/' + '/'.join(l)
      elif REQUEST.get('ZMS_RELATIVATE_URL',True) and self.getConfProperty('ZMSObject.getHref2IndexHtmlInContext.relativate',True) and self.getHome() == context.getHome():
        path = REQUEST.get('URL',context.getHref2IndexHtml(REQUEST,deep))
        index_html = self.getRelativeUrl(path,index_html)
      return index_html
    
    #++
    def getHref2IndexHtml(self, REQUEST, deep=1):
      deep = int(self.getConfProperty('ZMSObject.getHref2IndexHtml.deep',deep))
      ob = self
      fct = REQUEST.get('ZMS_SKIN','index')
      fct = {'sitemap':'index','search':'index'}.get(fct,fct)
      if fct == 'index' and 'index_html' in self.objectIds():
        value = self.absolute_url()
        if REQUEST.get('lang','') != '': 
          value = self.url_append_params(value,{'lang':REQUEST['lang']})
        if REQUEST.get('preview','') != '': 
          value = self.url_append_params(value,{'preview':REQUEST['preview']})
      else:
        if deep:
          ob = _globals.getPageWithElements( self, REQUEST)
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
    # --------------------------------------------------------------------------
    security.declarePublic('getParentNode')
    def getParentNode(self):
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      rtn = getattr(self, 'aq_parent', None)
      # Handle ZMSProxyObjects.
      if hasattr( rtn, 'is_blob') or hasattr( rtn, 'base'):
        rtn = getattr( self, self.absolute_url().split( '/')[-2], None)
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.getTreeNodes:
    # --------------------------------------------------------------------------
    def getTreeNodes(self, REQUEST={}, meta_types=None):
      """
      Returns a NodeList that contains all children of this subtree in correct order.
      If none, this is a empty NodeList. 
      """
      rtn = []
      for ob in self.getChildNodes(REQUEST):
        if ob.isMetaType(meta_types): rtn.append(ob)
        rtn.extend(ob.getTreeNodes(REQUEST,meta_types))
      return rtn


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxGetNodes:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ajaxGetNodes')
    def ajaxGetNodes(self, context=None, lang=None, xml_header=True, REQUEST=None):
      """ ZMSObject.ajaxGetNodes """
      context = _globals.nvl(context,self)
      refs = REQUEST.get('refs',[])
      if len(refs)==0:
        for key in REQUEST.keys():
          if key.startswith('ref') and key[3:].isdigit():
            refs.append((int(key[3:]),REQUEST[key]))
        refs.sort()
        refs = map(lambda x:x[1],refs)
      
      #-- Build xml.
      xml = ''
      if xml_header:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/plain; charset=utf-8'
        filename = 'ajaxGetNodes.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        self.f_standard_html_request( self, REQUEST)
        xml += self.getXmlHeader()
      xml += '<pages>'
      for ref in refs:
        ob = self.getLinkObj(ref)
        if ob is None:
          xml += '<page ref="%s" not_found="1"/>'%ref
        else:
          xml += ob.ajaxGetNode(context=context,lang=lang,xml_header=False,REQUEST=REQUEST)
      xml += "</pages>"
      return xml


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxGetNode:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ajaxGetNode')
    def ajaxGetNode(self, context=None, lang=None, xml_header=True, meta_types=None, REQUEST=None):
      """ ZMSObject.ajaxGetNode """
      
      #-- Build xml.
      xml = ''
      if xml_header:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/xml; charset=utf-8'
        filename = 'ajaxGetNode.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        self.f_standard_html_request( self, REQUEST)
        xml += self.getXmlHeader()
      xml += '<page'
      xml += " absolute_url=\"%s\""%str(self.absolute_url())
      xml += " physical_path=\"%s\""%('/'.join(self.getPhysicalPath()))
      xml += " access=\"%s\""%str(int(self.hasAccess(REQUEST)))
      xml += " active=\"%s\""%str(int(self.isActive(REQUEST)))
      try:
        xml += " display_icon=\"%s\""%unicode(self.display_icon(REQUEST)).encode('utf8').replace('"','&quot;').replace('<','&lt;')
      except:
        xml += " display_icon=\"&lt;i class=&quot;icon-file-alt&quot; title=&quot;ICON ERROR&quot;>&lt;/i>\""
      xml += " display_type=\"%s\""%str(self.display_type(REQUEST))
      xml += " uid=\"{$%s}\""%(self.get_uid(implementation=self.getConfProperty('ExtensionPoint.ZMSObject.get_uid.implementation','undefined')))
      xml += " id=\"%s_%s\""%(self.getHome().id,self.id)
      xml += " home_id=\"%s\""%(self.getHome().id)
      xml += " index_html=\"%s\""%_globals.html_quote(self.getHref2IndexHtml(REQUEST))
      xml += " is_page=\"%s\""%str(int(self.isPage()))
      xml += " is_pageelement=\"%s\""%str(int(self.isPageElement()))
      xml += " meta_id=\"%s\""%(self.meta_id)
      xml += " title=\"%s\""%_globals.html_quote(self.getTitle(REQUEST))
      xml += " titlealt=\"%s\""%_globals.html_quote(self.getTitlealt(REQUEST))
      xml += " restricted=\"%s\""%str(self.hasRestrictedAccess())
      xml += " attr_dc_type=\"%s\""%(self.attr('attr_dc_type'))
      xml += ">"
      if REQUEST.form.get('get_attrs', 1):
        obj_attrs = self.getObjAttrs()
        for key in filter(lambda x: x not in ['title','titlealt','change_dt','change_uid','change_history','created_dt','created_uid','attr_dc_coverage','attr_cacheable','work_dt','work_uid'],obj_attrs.keys()):
          obj_attr = obj_attrs[ key]
          if obj_attr['datatype_key'] in _globals.DT_TEXTS or \
             obj_attr['datatype_key'] in _globals.DT_NUMBERS or \
             obj_attr['datatype_key'] in _globals.DT_DATETIMES:
            v = self.attr(key)
            if v:
              xml += "<%s>%s</%s>"%(key,self.toXmlString(v),key)
          elif obj_attr['datatype_key'] in _globals.DT_BLOBS:
            v = self.attr(key)
            if v:
              xml += "<%s>"%key
              xml += "<href>%s</href>"%_globals.html_quote(v.getHref(REQUEST))
              xml += "<filename>%s</filename>"%_globals.html_quote(v.getFilename())
              xml += "<content_type>%s</content_type>"%_globals.html_quote(v.getContentType())
              xml += "<size>%s</size>"%self.getDataSizeStr(v.get_size())
              xml += "<icon>%s</icon>"%self.getMimeTypeIconSrc(v.getContentType())
              xml += "</%s>"%key
      xml += "</page>"
      return xml


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxGetParentNodes:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ajaxGetParentNodes')
    def ajaxGetParentNodes(self, lang, xml_header=True, meta_types=None, REQUEST=None):
      """ ZMSObject.ajaxGetParentNodes """
      # Get context.
      context = self
      for id in REQUEST.get('physical_path','').split('/'):
        if id and context is not None:
          context = getattr(context,id,None)
          if context is None:
            context = self
            break
      # Build xml.
      xml = ''
      if xml_header:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/xml; charset=utf-8'
        filename = 'ajaxGetParentNodes.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        self.f_standard_html_request( self, REQUEST)
        xml += self.getXmlHeader()
      # Start-tag.
      xml += "<pages"
      for key in REQUEST.form.keys():
        if key.find('get_') < 0 and key not in ['lang','preview','http_referer','meta_types']:
          xml += " %s=\"%s\""%(key,str(REQUEST.form.get(key)))
      xml += " level=\"%i\""%self.getLevel()
      xml += ">\n"
      # Process nodes.
      REQUEST.form['get_attrs'] = REQUEST.form.get('get_attrs', 0)
      for node in self.breadcrumbs_obj_path():
        xml += node.ajaxGetNode( context=context, lang=lang, xml_header=False, meta_types=meta_types, REQUEST=REQUEST)
      # End-tag.
      xml += "</pages>"
      # Return xml.
      return xml


    # --------------------------------------------------------------------------
    #  ZMSObject.ajaxGetChildNodes:
    # --------------------------------------------------------------------------
    security.declareProtected('View', 'ajaxGetChildNodes')
    def manage_ajaxGetChildNodes(self, lang, xml_header=True, meta_types=None, REQUEST=None):
      """ ZMSObject.manage_ajaxGetChildNodes """
      return self.ajaxGetChildNodes(lang, xml_header, meta_types, REQUEST)
    def ajaxGetChildNodes(self, lang, xml_header=True, meta_types=None, REQUEST=None):
      """ ZMSObject.ajaxGetChildNodes """
      # Get context.
      context = self
      for id in REQUEST.get('physical_path','').split('/'):
        if id and context is not None:
          context = getattr(context,id,None)
          if context is None:
            context = self
            break
      # Build xml.
      xml = ''
      if xml_header:
        RESPONSE = REQUEST.RESPONSE
        content_type = 'text/xml; charset=utf-8'
        filename = 'ajaxGetChildNodes.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        self.f_standard_html_request( self, REQUEST)
        xml += self.getXmlHeader()
      
      xml += "<pages"
      for key in REQUEST.form.keys():
        if key.find('get_') < 0 and key not in ['lang','preview','http_referer','meta_types']:
          xml += " %s=\"%s\""%(key,str(REQUEST.form.get(key)))
      xml += " level=\"%i\""%self.getLevel()
      xml += ">\n"
      
      if type(meta_types) is str and meta_types.find(',') > 0:
        meta_types = meta_types.split(',')
      if type(meta_types) is list:
        new_meta_types = []
        for meta_type in meta_types:
          try:
            new_meta_types.append( int( meta_type))
          except:
            new_meta_types.append( meta_type)
        meta_types = new_meta_types
      if REQUEST.form.get('http_referer'):
        REQUEST.set('URL',REQUEST.form.get('http_referer'))
      obs = []
      # Add child-nodes.
      obs.extend( self.getChildNodes(REQUEST,meta_types))
      # Add trashcan.
      if ( self.meta_type == 'ZMS') and \
         ( ( type( meta_types) is list and 'ZMSTrashcan' in meta_types) or \
           ( type( meta_types) is string and 'ZMSTrashcan' == meta_types)):
        obs.append( self.getTrashcan())
      if self.meta_type == 'ZMS':
        obs.extend( self.getPortalClients())
      
      for ob in obs:
        xml += ob.ajaxGetNode( context=context, lang=lang, xml_header=False, meta_types=meta_types, REQUEST=REQUEST)
      
      xml += "</pages>"
      
      if REQUEST.RESPONSE.getHeader('Location'):
        del REQUEST.RESPONSE.headers['location']
      
      return xml


    # --------------------------------------------------------------------------
    #  ZMSObject.getChildNodes:
    #
    #  Returns a NodeList that contains all children of this node, 
    #  if none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
      return []


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
      setattr( self, 'sort_id', _globals.format_sort_id(sort_id))


    # --------------------------------------------------------------------------
    #  ZMSObject.getSortId:
    #
    #  Returns Sort-ID (integer).
    # --------------------------------------------------------------------------
    def getSortId(self, REQUEST=None): 
      try:
        sort_id = getattr( self, 'sort_id')
        rtnVal = string.atoi(sort_id[len(_globals.id_prefix(sort_id)):])
      except:
        rtnVal = 0
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
      parent.normalizeSortIds(_globals.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJUP')%("<i>%s</i>"%self.display_type(REQUEST))
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


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
      parent.normalizeSortIds(_globals.id_prefix(self.id))
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJDOWN')%("<i>%s</i>"%self.display_type(REQUEST))
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


    ############################################################################
    # ZMSObject.manage_moveObjToPos:
    #
    # Moves an object to specified position in sort order.
    ############################################################################
    def manage_moveObjToPos(self, lang, pos, fmt=None, REQUEST=None, RESPONSE=None):
      """ ZMSObject.manage_moveObjToPos """
      parent = self.getParentNode()
      if parent is not None:
        sibling_sort_ids = map(lambda x: x.sort_id,parent.getChildNodes(REQUEST))
        sibling_sort_ids.remove(self.sort_id)
        pos = pos - 1
        if pos < len(sibling_sort_ids):
          new_sort_id = int(sibling_sort_ids[pos][1:])-1
        else:
          new_sort_id = int(sibling_sort_ids[-1][1:])+1
        self.setSortId(new_sort_id)
        parent.normalizeSortIds(_globals.id_prefix(self.id))
      else:
        id = REQUEST['URL'].split('/')[-2]
        ids = self.getConfProperty('Portal.Clients',[])
        if id in ids:
          offset = len(self.getChildNodes(REQUEST))
          pos = pos - offset - 1
          ids.insert(pos, ids.pop(ids.index(id)))
          self.setConfProperty('Portal.Clients',ids)
      # Return with message.
      message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%self.display_type(REQUEST)),(pos+1))
      if fmt == 'json':
        return self.str_json(message)
      else:
        RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(parent.absolute_url(),lang,urllib.quote(message),self.id))


    ############################################################################
    #  MetacmdObject.manage_executeMetacmd:
    #
    #  Execute Meta-Command.
    ############################################################################
    def manage_executeMetacmd(self, lang, REQUEST, RESPONSE):
      """ MetacmdObject.manage_executeMetacmd """
      message = ''
      target = self
      
      # METAOBJ
      metaObjAttr = self.getMetaobjAttr(self.meta_id,REQUEST.get('id'))
      if metaObjAttr is not None:
        # Execute directly.
        return self.attr(REQUEST.get('id'))
      
      # METACMD
      metaCmd = self.getMetaCmd(id=REQUEST.get('id'),name=REQUEST.get('custom'))
      if metaCmd is not None:
        # Execute directly.
        if metaCmd.get('exec',0) == 1:
          ob = getattr(self,metaCmd['id'],None)
          if ob.meta_type in ['DTML Method','DTML Document']:
            value = ob(self,REQUEST,RESPONSE)
          elif ob.meta_type in ['External Method','Page Template','Script (Python)']:
            value = ob()
          if type(value) is str:
            message = value
          elif type(value) is tuple:
            target = value[0]
            message = value[1]
        # Execute redirect.
        else:
          params = {'lang':REQUEST.get('lang'),'id_prefix':REQUEST.get('id_prefix'),'ids':REQUEST.get('ids',[])}
          return RESPONSE.redirect(self.url_append_params(metaCmd['id'],params,sep='&'))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s'%(target.absolute_url(),lang,message))


    # --------------------------------------------------------------------------
    #  ZMSObject.getBodyContent:
    # --------------------------------------------------------------------------
    def _getBodyContentContentEditable(self, html):
      request = self.REQUEST
      if _globals.isPreviewRequest(request) and \
         (request.get('URL').find('/manage')>0 or self.getConfProperty('ZMS.preview.contentEditable',1)==1):
        css = ['contentEditable', self.meta_id]
        html = '<div class="%s" data-absolute-url="%s">%s</div>'%(' '.join(css),self.absolute_url()[len(self.REQUEST['BASE0']):],html)
      return html

    def _getBodyContent(self, REQUEST):
      rtn = self._getBodyContentContentEditable(self.metaobj_manager.renderTemplate( self))
      return rtn

    security.declareProtected('View', 'ajaxGetBodyContent')
    def ajaxGetBodyContent(self, REQUEST, forced=False):
      """
      HTML presentation in body-content. 
      """
      return self.getBodyContent(REQUEST,forced)

    def getBodyContent(self, REQUEST, forced=False):
      html = ''
      if forced or self.isVisible( REQUEST):
        html = self._getBodyContent( REQUEST)
        # Process custom hook.
        name = 'getCustomBodyContent'
        if hasattr(self,name):
          html = getattr(self,name)(context=self,html=html,REQUEST=REQUEST)
        # Process inline links.
        html = self.validateInlineLinkObj(html)
      return html


    # --------------------------------------------------------------------------
    #  ZMSObject.renderShort:
    #
    #  Renders short presentation of object.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      html = ''
      try:
        if 'renderShort' in self.getMetaobjAttrIds(self.meta_id):
          html = self._getBodyContentContentEditable(self.attr('renderShort'))
        elif self.isPage():
          if  self.id in REQUEST['URL']:
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
        # Process html <form>-tags.
        html = _globals.form_quote(html,REQUEST)
        # Process inline links.
        html = self.validateInlineLinkObj(html)
      except:
        html = _globals.writeError(self,"[renderShort]")
        html = '<br/>'.join(html.split('\n'))
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
    #  Renders print presentation.
    # --------------------------------------------------------------------------
    def printHtml(self, level, sectionizer, REQUEST, deep=True):
      html = ''
      
      # Title.
      sectionizer.processLevel( level)
      title = self.getTitle( REQUEST)
      title = '%s %s'%(str(sectionizer),title)
      REQUEST.set( 'ZMS_SECTIONIZED_TITLE', '<h%i>%s</h%i>'%( level, title, level))
      
      # bodyContent
      html += self._getBodyContent(REQUEST)
      
      # Container-Objects.
      if deep:
        for ob in self.filteredChildNodes(REQUEST,self.PAGES):
          html += ob.printHtml( level+1, sectionizer, REQUEST, deep)
      
      # Return <html>.
      return html


    ############################################################################
    ###
    ###  XML-Builder
    ###
    ############################################################################

    ############################################################################
    # ZMSObject.xmlOnStartElement(self, dTagName, dAttrs, oCurrNodes, oRoot):
    # ZMSObject.xmlOnCharacterData(self, data, bInCData):
    # ZMSObject.xmlOnEndElement(self):
    # ZMSObject.xmlOnUnknownStartTag(self, sTagName, dTagAttrs)
    # ZMSObject.xmlOnUnknownEndTag(self, sTagName)
    # ZMSObject.xmlGetParent(self):
    #
    # handler for XML-Builder (_builder.py)
    ############################################################################
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode, oRoot):
        _globals.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)
        
        self.dTagStack    = _globals.MyStack()
        self.dValueStack  = _globals.MyStack()
        
        # WORKAROUND! The member variable "aq_parent" does not contain the right 
        # parent object at this stage of the creation process (it will later 
        # on!). Therefore, we introduce a special attribute containing the 
        # parent object, which will be used by xmlGetParent() (see below).
        self.oParent = oParentNode


    def xmlOnEndElement(self): 
        self.initObjChildren( self.REQUEST)


    def xmlOnCharacterData(self, sData, bInCData):
        return _xmllib.xmlOnCharacterData(self,sData,bInCData)


    def xmlOnUnknownStartTag(self, sTagName, dTagAttrs):
        return _xmllib.xmlOnUnknownStartTag(self,sTagName,dTagAttrs)


    def xmlOnUnknownEndTag(self, sTagName):
        return _xmllib.xmlOnUnknownEndTag(self,sTagName)


    def xmlGetParent(self):
        return self.oParent


# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ZMSObject)

################################################################################