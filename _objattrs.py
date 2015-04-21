################################################################################
# _objattrs.py
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
from DateTime.DateTime import DateTime
from OFS.Image import Image, File
from types import StringTypes
import ZPublisher.HTTPRequest
import datetime
import string
import time
import urllib
import zExceptions
# Product Imports.
import _blobfields
import _globals
import ZMSMetaobjManager


# ------------------------------------------------------------------------------
#  _objattrs.utf8:
# ------------------------------------------------------------------------------
def utf8(v, encoding = 'latin-1'):
  if type( v) in StringTypes:
    cp1252_map = {
      "\x80" : "\xe2\x82\xac", # /* EURO SIGN */
      "\x82" : "\xe2\x80\x9a", # /* SINGLE LOW-9 QUOTATION MARK */
      "\x83" : "\xc6\x92",    # /* LATIN SMALL LETTER F WITH HOOK */
      "\x84" : "\xe2\x80\x9e", # /* DOUBLE LOW-9 QUOTATION MARK */
      "\x85" : "\xe2\x80\xa6", # /* HORIZONTAL ELLIPSIS */
      "\x86" : "\xe2\x80\xa0", # /* DAGGER */
      "\x87" : "\xe2\x80\xa1", # /* DOUBLE DAGGER */
      "\x88" : "\xcb\x86",    # /* MODIFIER LETTER CIRCUMFLEX ACCENT */
      "\x89" : "\xe2\x80\xb0", # /* PER MILLE SIGN */
      "\x8a" : "\xc5\xa0",    # /* LATIN CAPITAL LETTER S WITH CARON */
      "\x8b" : "\xe2\x80\xb9", # /* SINGLE LEFT-POINTING ANGLE QUOTATION */
      "\x8c" : "\xc5\x92",    # /* LATIN CAPITAL LIGATURE OE */
      "\x8e" : "\xc5\xbd",    # /* LATIN CAPITAL LETTER Z WITH CARON */
      "\x91" : "\xe2\x80\x98", # /* LEFT SINGLE QUOTATION MARK */
      "\x92" : "\xe2\x80\x99", # /* RIGHT SINGLE QUOTATION MARK */
      "\x93" : "\xe2\x80\x9c", # /* LEFT DOUBLE QUOTATION MARK */
      "\x94" : "\xe2\x80\x9d", # /* RIGHT DOUBLE QUOTATION MARK */
      "\x95" : "\xe2\x80\xa2", # /* BULLET */
      "\x96" : "\xe2\x80\x93", # /* EN DASH */
      "\x97" : "\xe2\x80\x94", # /* EM DASH */
      "\x98" : "\xcb\x9c",    # /* SMALL TILDE */
      "\x99" : "\xe2\x84\xa2", # /* TRADE MARK SIGN */
      "\x9a" : "\xc5\xa1",    # /* LATIN SMALL LETTER S WITH CARON */
      "\x9b" : "\xe2\x80\xba", # /* SINGLE RIGHT-POINTING ANGLE QUOTATION*/
      "\x9c" : "\xc5\x93",    # /* LATIN SMALL LIGATURE OE */
      "\x9e" : "\xc5\xbe",    # /* LATIN SMALL LETTER Z WITH CARON */
      "\x9f" : "\xc5\xb8"      # /* LATIN CAPITAL LETTER Y WITH DIAERESIS*/
    }
    if encoding == 'latin-1':
      n = ''
      for i in v:
        if i in cp1252_map.keys():
          c = '&#%i;'%ord( i)
          n += c
        else:
          n += i
      v = n
    v = unicode( v, encoding).encode( 'utf-8')
    if encoding == 'latin-1':
      for i in cp1252_map.keys():
        c = '&#%i;'%ord( i)
        j = 0
        while j >= 0:
          j = v.find( c)
          if j >= 0:
            v = v[:j] + cp1252_map[ i] + v[j+len(c):]
    return v
  elif type( v) is list:
    return map(lambda x: utf8( x, encoding), v)
  elif type( v) is tuple:
    return tuple(map(lambda x: utf8( x, encoding), list(v)))
  elif type( v) is dict:
    keys = v.keys()
    vals = map(lambda x: utf8(v[x],encoding), keys)
    return _globals.map_key_vals(keys, vals)
  else:
    return v


# ------------------------------------------------------------------------------
#  _objattrs.setutf8attr:
# ------------------------------------------------------------------------------
def setutf8attr(self, obj_vers, obj_attr, langId):
  charset = self.getLang(langId).get('charset','')
  if len(charset) == 0:
    charset = 'latin-1'
  key = self._getObjAttrName(obj_attr,langId)
  v = getattr(obj_vers,key,None)
  v = utf8(v,charset)
  setattr(obj_vers,key,v)


# ------------------------------------------------------------------------------
#  _objattrs.getobjattr:
# ------------------------------------------------------------------------------
def getobjattr(self, obj, obj_attr, lang):
  v = None
  key = self._getObjAttrName(obj_attr,lang)
  if key in obj.__dict__.keys():
    v = getattr(obj,key)
  # Default mono-lingual attributes to primary-lang.
  if v is None:
    key = self._getObjAttrName({'id':obj_attr['id'],'multilang':not obj_attr['multilang']},self.getPrimaryLanguage())
    if key in obj.__dict__.keys():
      v = getattr(obj,key)
  # Default value.
  if v is None:
    datatype = obj_attr['datatype_key']
    default = obj_attr.get('default',_globals.dtMapping[datatype][1])
    # Default inactive in untranslated languages.
    if obj_attr['id'] == 'active' and len(self.getLangIds()) > 1 and not self.isTranslated(lang,self.REQUEST):
        default = 0
    if default is not None:
      if datatype in _globals.DT_DATETIMES and default == '{now}':
        default = time.time()
      elif type(default) is list or type(default) is tuple:
        v = self.copy_list(default)
      elif type(default) is dict:
        v = default.copy()
      else:
        if type( default) is str and len( default) > 0:
          default = self.dt_exec(default)
        v = default
  return v

# ------------------------------------------------------------------------------
#  _objattrs.setobjattr:
# ------------------------------------------------------------------------------
def setobjattr(self, obj, obj_attr, value, lang):
  key = self._getObjAttrName(obj_attr,lang)
  # Assign value.
  setattr(obj,key,value)

# ------------------------------------------------------------------------------
#  _objattrs.cloneobjattr:
# ------------------------------------------------------------------------------
def cloneobjattr(self, src, dst, obj_attr, lang):
  _globals.writeLog( self, "[cloneobjattr]: Clone object-attributes from '%s' to '%s'"%(str(src),str(dst)))
  # Fetch value.
  v = getobjattr(self,src,obj_attr,lang)
  # Clone value.
  if v is not None:
    datatype = obj_attr['datatype_key']
    if datatype in _globals.DT_BLOBS:
      try:
        v = v._getCopy()
      except:
        e = "[cloneobjattr]: Can't clone object-attribute: obj_attr=%s, lang=%s, v=%s!"%(str(obj_attr), str(lang), str(v))
        _globals.writeError( self, e)
        raise zExceptions.InternalError(e)
    elif type(v) is list or type(v) is tuple:
      v = self.copy_list(v)
    elif type(v) is dict:
      v = v.copy()
  # Assign value.
  setobjattr(self,dst,obj_attr,v,lang)


################################################################################
################################################################################
###
###   Object Attributes
###
################################################################################
################################################################################
class ObjAttrs:

    # --------------------------------------------------------------------------
    #  ObjAttrs.ajaxGetObjOptions:
    # --------------------------------------------------------------------------
    def ajaxGetObjOptions(self, key, meta_id, fmt=None, REQUEST=None):
      """ ObjAttrs.ajaxGetObjOptions """
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/plain; charset=utf-8'
      filename = 'ajaxGetObjOptions.txt'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      obj_attr = self.getObjAttr( key, meta_id)
      l = map( lambda x: x[1], self.getObjOptions( obj_attr, REQUEST))
      q = REQUEST.get( 'q', '').upper()
      if q:
        l = filter( lambda x: x.upper().find( q) >= 0, l)
      limit = int(REQUEST.get('limit',self.getConfProperty('ZMS.input.autocomplete.limit',15)))
      if len(l) > limit:
        l = l[:limit]
      if fmt == 'json':
        return self.str_json(l)
      return '\n'.join(l)


    # --------------------------------------------------------------------------
    #  ObjAttrs.ajaxGetObjAttrs:
    # --------------------------------------------------------------------------
    def ajaxGetObjAttrs(self, meta_id, REQUEST):
      """ ObjAttrs.ajaxGetObjAttrs """
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'ajaxGetObjAttrs.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      return self.getXmlHeader() + self.toXmlString( self.getObjAttrs( meta_id))


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrs:
    #
    #  Returns object-attributes and resolves meta-dictionaries.
    # --------------------------------------------------------------------------
    def getObjAttrs(self, meta_id=None):
      meta_id = _globals.nvl( meta_id, self.meta_id)
      obj_attrs = getattr( self, 'dObjAttrs', {})
      return obj_attrs.get(meta_id,{})


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttr:
    # --------------------------------------------------------------------------
    def getObjAttr(self, key, meta_id=None):
      obj_attrs = self.getObjAttrs( meta_id)
      return obj_attrs.get(key,{'id':key,'key':key,'xml':False,'multilang':False,'lang_inherit':False,'name':'UNKNOWN','datatype':'string','datatype_key':_globals.DT_UNKNOWN})


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrLabel:
    # --------------------------------------------------------------------------
    def getObjAttrLabel(self, obj_attr):
      lang = self.REQUEST['lang']
      for key in [ 'name', 'id']:
        if obj_attr.has_key( key):
          name = obj_attr.get( key)
          lang_key = name
          lang_str = self.getLangStr( lang_key, lang)
          if lang_key != lang_str:
            return lang_str
          lang_key = name.upper()
          lang_str = self.getLangStr( lang_key, lang)
          if lang_key != lang_str:
            return lang_str
          lang_key = ('attr_'+name).upper()
          lang_str = self.getLangStr( lang_key, lang)
          if lang_key != lang_str:
            return lang_str
      return obj_attr.get('name',obj_attr['id'].capitalize())


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjOptions:
    # --------------------------------------------------------------------------
    def getObjOptions(self, obj_attr, REQUEST):
      optpl = []
      if obj_attr.has_key('options'):
        opts = []
        obj_attropts = obj_attr['options']
        if type(obj_attropts) is list:
          v = '\n'.join(map(lambda x: str(obj_attropts[x*2]),range(len(obj_attropts)/2)))
          if len(obj_attropts)==2 and self.getLinkObj(obj_attropts[0],REQUEST):
            ob = self.getLinkObj(obj_attropts[0],REQUEST)
            metaObj = self.getMetaobj(ob.meta_id)
            res = ob.getObjProperty(metaObj['attrs'][0]['id'],REQUEST)
            res = map(lambda x: {'key':x['key'],'value':x.get('value',x.get('value_%s'%REQUEST['lang']))},res)
            res = self.sort_list(res,'value','asc')
            opts = map(lambda x: [x['key'],x['value']],res)
          elif v.find('<dtml-') >= 0 or v.startswith('##') or v.find('<tal:') >= 0:
            try:
              opts = self.dt_exec(v)
            except:
              opts = _globals.writeError(self,'[getObjOptions]: key=%s'%obj_attr['id'])
          else:
            for i in range(len(obj_attropts)/2):
              opts.append([obj_attropts[i*2],obj_attropts[i*2+1]])
        elif type(obj_attropts) is dict:
          for k in obj_attropts.keys():
            opts.append([k,obj_attropts[k]])
        for opt in opts:
          lang_attr = 'OPT_'
          for skey in obj_attr['id'].split('_'):
            lang_attr += skey[0]
          lang_attr += '_' + str(opt[1]).replace(' ','')
          lang_attr = lang_attr.upper()
          lang_str = self.getZMILangStr(lang_attr)
          value = str(opt[0])
          display = str(opt[1])
          if lang_attr != lang_str:
            display = lang_str
          optpl.append([value,display])
      return optpl

    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrName:
    # --------------------------------------------------------------------------
    def _getObjAttrName(self, obj_attr, lang=None):
      attr = obj_attr['id']
      if obj_attr['multilang']:
        if lang is None: 
          lang = self.getPrimaryLanguage()
        attr = '%s_%s'%(attr,lang)
      return attr

    def getObjAttrName(self, obj_attr, lang=None):
      attr = self.REQUEST.get('objAttrNamePrefix','') + self._getObjAttrName(obj_attr, lang)
      return attr

    # --------------------------------------------------------------------------
    #  ObjAttrs.isDisabledAttr:
    # --------------------------------------------------------------------------
    def isDisabledAttr(self, obj_attr, REQUEST):
      lang = REQUEST.get('lang',self.getPrimaryLanguage())
      return REQUEST.get(obj_attr['id']+'-disabled',False) or not (obj_attr['multilang'] or REQUEST.get('ZMS_INSERT',None) is not None or self.getDCCoverage(REQUEST).find('.'+lang)>0)


    ############################################################################
    #
    #  INPUT-FIELDS
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrInput:
    # --------------------------------------------------------------------------
    def getObjAttrInput(self, fmName, obj_attr, value, REQUEST):
    
      #-- DATATYPE
      datatype = obj_attr['datatype_key']
      
      #-- NAME
      lang = REQUEST['lang']
      elName = self.getObjAttrName(obj_attr,lang)
      
      #-- INPUTTYPE
      inputtype = obj_attr.get('type','string')
      
      #-- ENABLED / DISABLED
      enabled = not self.isDisabledAttr(obj_attr,REQUEST)
      disabled = obj_attr['id'].find('_')==0
      
      #-- Meta-Object
      meta_id = REQUEST.get( 'ZMS_INSERT', self.meta_id)
      metaObj = self.getMetaobj( meta_id)
      
      #-- Label
      lang_str = self.getObjAttrLabel(obj_attr)
      
      #-- Mandatory
      mandatory = obj_attr.get('mandatory',0)
      
      #-- ID-Fields.
      if inputtype == 'identifier':
        if value == '': value = 'e%i'%self.getSequence().nextVal()
        return '<div class="form-control-static"><code><input type="hidden" name="%s" value="%s">%s</code></div>'%(elName,value,value)
      
      #-- Richtext-Fields.
      elif inputtype == 'richtext':
        REQUEST.set('data',value)
        form_fixed = False
        css = 'form-control'
        wrap = 'virtual'
        filteredMetaObjAttrs = filter( lambda x: x['id']=='format', metaObj['attrs'])
        if len(filteredMetaObjAttrs) == 1:
          if REQUEST.get('ZMS_INSERT'):
            default = self.dt_exec(str( filteredMetaObjAttrs[0].get('default','')))
            if default:
              fmt = default
            else:
              fmt = self.getTextFormatDefault()
            data = ''
          else:
            fmt = self.getObjProperty('format',REQUEST)
            txt = self.getObjProperty('text',REQUEST)
            data = self.renderText(None,'text',txt,REQUEST)
          REQUEST.set('format',fmt)
          REQUEST.set('data',data)
          text_fmt = self.getTextFormat(fmt,REQUEST)
          form_fixed = form_fixed or ( text_fmt is not None and not text_fmt.getTag() and not text_fmt.getSubTag())
        ltxt = str(value).lower()
        form_fixed = form_fixed or ( ltxt.find( '<form') >= 0 or ltxt.find( '<input') >= 0 or ltxt.find( '<script') >= 0)
        if form_fixed:
          css = 'form-control form-fixed'
          wrap = 'off'
        if disabled: 
          css += '-disabled'
        return self.f_selectRichtext(self,ob=self,fmName=fmName,elName=elName,cols=50,rows=15,value=value,key=obj_attr['id'],metaObj=metaObj,enabled=enabled,lang=lang,lang_str=lang_str,REQUEST=REQUEST,css=css,wrap=wrap)
      
      #-- Image-Fields.
      elif inputtype == 'image':
        return self.f_selectImage(self,ob=self,fmName=fmName,elName=elName,value=value,key=obj_attr['id'],metaObj=metaObj,lang=lang,REQUEST=REQUEST)
      
      #-- File-Fields.
      elif inputtype == 'file':
        return self.f_selectFile(self,ob=self,fmName=fmName,elName=elName,value=value,key=obj_attr['id'],metaObj=metaObj,lang=lang,REQUEST=REQUEST)
      
      #-- Password-Fields.
      if inputtype == 'password':
        return self.getPasswordInput(fmName=fmName,elName=elName,value=value)
      
      #-- Dictionary/List-Fields.
      elif inputtype in [ 'dictionary', 'list']:
        css = 'form-fixed form-control'
        wrap = 'virtual'
        if disabled: 
          css += '-disabled'
        cols = 35
        rows = 1
        inp = []
        inp.append(self.getTextArea(fmName,elName,cols,rows,self.toXmlString(value),enabled,REQUEST,css,wrap))
        return ''.join(inp)
      
      #-- Text-Fields.
      elif inputtype in [ 'text', 'xml']:
        css = 'form-control'
        wrap = 'virtual'
        if inputtype in ['xml']:
          css = 'form-fixed'
          wrap = 'off'
        if disabled: 
          css += '-disabled'
        cols = None
        rows = 5
        return self.getTextArea(fmName,elName,cols,rows,value,enabled,REQUEST,css,wrap)
      
      #-- Boolean-Fields.
      elif inputtype == 'boolean':
        return self.getCheckbox(fmName=fmName,elName=elName,elId=obj_attr['id'],value=value,enabled=enabled,hidden=False,btn=True,REQUEST=REQUEST)
      
      #-- Color-Fields.
      elif inputtype == 'color':
        return self.zmi_input_color(self,name=elName,value=value,type=inputtype,key=obj_attr['id'],lang_str=lang_str,enabled=enabled)
      
      #-- Autocomplete-Fields.
      elif inputtype in ['autocomplete','multiautocomplete']:
        return self.zmi_input_autocomplete(self,name=elName,value=value,type=inputtype,key=obj_attr['id'],lang_str=lang_str,enabled=enabled)
      
      #-- Select-Fields.
      elif inputtype in ['multiselect','select']:
        optpl = self.getObjOptions(obj_attr,REQUEST)
        return self.getSelect(fmName,elName,value,inputtype,lang_str,mandatory,optpl,enabled,REQUEST)
      
      #-- Input-Fields.
      else: 
        css = 'form-control'
        if disabled: css += '-disabled'
        if datatype in _globals.DT_DATETIMES:
          size = 12
          fmt_str = 'DATETIME_FMT'
          if datatype == _globals.DT_DATE:
            size = 8
            fmt_str = 'DATE_FMT'
          elif datatype == _globals.DT_TIME:
            size = 8
            fmt_str = 'TIME_FMT'
          return self.getDateTimeInput(fmName,elName,size,value,enabled,fmt_str,REQUEST,css)
        elif datatype == _globals.DT_URL:
          size = 22
          elTextName = ''
          return self.getUrlInput( fmName, elName, elTextName, size, value, enabled, REQUEST, css )
        else:
          size = None
          extra = ''
          if obj_attr.has_key('size'):
            size = obj_attr['size']
          elif datatype in [_globals.DT_INT]:
            size = 5
          elif datatype in [_globals.DT_FLOAT]:
            size = 8
          elif datatype in [_globals.DT_AMOUNT]:
            size = 8
            extra = 'style="text-align: right;"'
            if value is not None:
              try:
                value = '%1.2f'%float(value)
              except:
                pass
          inp = []
          inp.append(self.getTextInput( fmName, elName, size, value, 'text', enabled, REQUEST, css, extra ))
          if datatype in [_globals.DT_AMOUNT]:
            inp.append('&nbsp;'+self.getConfProperty('ZMS.locale.amount.unit','EUR'))
          return ''.join(inp)

    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjInput:
    # --------------------------------------------------------------------------
    def getObjInput(self, key, REQUEST):
      id = self.id
      fmName = REQUEST.get( 'fmName' ,REQUEST.get('fmName','form0_%s'%id))
      meta_id = REQUEST.get( 'ZMS_INSERT', None)
      obj_attr = self.getObjAttr( key, _globals.nvl( meta_id, self.meta_id))
      if meta_id is None:
        value = self.getObjAttrValue( obj_attr, REQUEST)
      else:
        default = ''
        datatype = obj_attr['datatype_key']
        if datatype == _globals.DT_BOOLEAN:
          default = 0
        value = REQUEST.get( '%s_value'%key, obj_attr.get( 'default', default))
      return self.getObjAttrInput( fmName, obj_attr, value, REQUEST)


    # --------------------------------------------------------------------------
    #  ObjAttrs.hasObjProperty:
    #
    #  Checks if object has specified property.
    # --------------------------------------------------------------------------
    def hasObjProperty(self, key, REQUEST):

      #-- REQUEST
      lang = REQUEST.get('lang',self.getPrimaryLanguage())
      
      #-- DEFINITION
      obj_attr = self.getObjAttr(key)
      
      #-- OBJECT (Live / Work).
      ob = self.getObjVersion(REQUEST)
      
      #-- ATTR
      attr = self._getObjAttrName(obj_attr,lang)
      
      #-- Return true if object has specified property, false else.
      return ob.__dict__.get(attr,None) is not None


    """
    ############################################################################
    #
    #  Get
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ObjAttrs._getObjAttrValue:
    # --------------------------------------------------------------------------
    def _getObjAttrValue(self, obj_attr, obj_vers, lang):
      
      datatype = obj_attr['datatype_key']
      set, value = False, getobjattr(self,obj_vers,obj_attr,lang)
      
      obj_default = _globals.dtMapping[datatype][1]
      
      #-- Blob-Fields
      if datatype in _globals.DT_BLOBS:
        if type(value) in StringTypes:
          set, value = True, None
        elif value is not None:
          value = value._createCopy( self, obj_attr['id'])
          value.lang = lang
      
      #-- DateTime-Fields.
      elif datatype in _globals.DT_DATETIMES:
        if value is not None:
          if type(value) in StringTypes: 
            fmt_str = 'DATETIME_FMT'
            if datatype == _globals.DT_DATE:
              fmt_str = 'DATE_FMT'
            elif datatype == _globals.DT_TIME:
              fmt_str = 'TIME_FMT'
            _globals.writeLog( self, "[_getObjAttrValue]: type(value) is type(string) - parseLangFmtDate(%s)"%(str(value)))
            set, value = True, self.parseLangFmtDate(value)
          elif type(value) is not time.struct_time:
            _globals.writeLog( self, "[_getObjAttrValue]: type(value) is not time.struct_time - getDateTime(%s)"%(str(value)))
            set, value = True, _globals.getDateTime(value)
      
      #-- List-Fields.
      elif datatype == _globals.DT_LIST:
        if not type(value) is type(obj_default):
          set, value = True, [value]
      
      #-- Integer-Fields.
      elif datatype in _globals.DT_INTS and not type(value) is type(obj_default):
        try:
          set, value = type( value) is not int, int(value)
        except:
          value = obj_default
      
      #-- Float-Fields.
      elif datatype == _globals.DT_FLOAT and not type(value) is type(obj_default):
        try:
          set, value = type( value) is not float, float( value)
        except:
          value = obj_default
      
      #-- Text-Fields
      elif datatype == _globals.DT_TEXT:
        old = value
        value = self.validateInlineLinkObj(value)
        set = old != value
      
      #-- Url-Fields
      elif datatype == _globals.DT_URL:
        old = value
        value = self.validateLinkObj(value)
        set = old != value
      
      #-- SET?
      if set: 
        attr = self._getObjAttrName( obj_attr, lang)
        _globals.writeLog( self, "[_getObjAttrValue]: setattr(%s,%s)"%(attr,str(value)))
        setattr(obj_vers,attr,value)
      
      # Return value.
      return value


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrValue:
    # --------------------------------------------------------------------------
    def getObjAttrValue(self, obj_attr, REQUEST):
      datatype = obj_attr['datatype_key']
      obj_vers = self.getObjVersion(REQUEST)
      lang = REQUEST.get('lang',self.getPrimaryLanguage())
      while True:
        value = self._getObjAttrValue(obj_attr,obj_vers,lang)
        empty = False
        if obj_attr['multilang'] and \
           obj_attr['lang_inherit']:
          lang = self.getParentLanguage(lang)
          if lang is not None:
            empty = empty or (value is None)
            empty = empty or (datatype in _globals.DT_NUMBERS and value==0)
            empty = empty or (datatype in _globals.DT_STRINGS and value=='')
            empty = empty or (datatype == _globals.DT_LIST and value==[])
        if not empty: break
      return value


    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjProperty:
    #
    #  Retrieves value for specified property.
    #
    #  @deprecated: use attr(key) instead! 
    # --------------------------------------------------------------------------
    def getObjProperty(self, key, REQUEST={}, par=None):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = '%s_%s'%('getObjProperty',key)
      try:
        if ( type( par) is dict and par.get( 'fetchReqBuff') in [ 0, False]) or \
           ( REQUEST.get( 'ZMS_VERSION_%s'%self.id) is not None):
          raise zExceptions.InternalError('ReqBuff set inactive!')
        forced = type( par) is dict and par.get( 'fetchReqBuff') in [ 1, True]
        value = self.fetchReqBuff( reqBuffId, REQUEST, forced)
        return value
      except:
        try:
          objAttrs = self.getObjAttrs()
          
          #-- Special attributes.
          if key not in objAttrs.keys():
            value = self.nvl(self.evalMetaobjAttr(key),'')
            if isinstance(value,Image) or isinstance(value,File):
              value = _blobfields.MyBlobWrapper(value)
          
          #-- Standard attributes.
          elif key in objAttrs.keys():
            objAttr = objAttrs[key]
            datatype = objAttr['datatype_key']
            value = self.getObjAttrValue( objAttr, REQUEST)
            if datatype == _globals.DT_TEXT and  type(value) in StringTypes and (value.find('<dtml-') >= 0 or value.startswith('##') or value.find('<tal:')>=0):
              value = self.dt_exec(value)
          
          #-- Undefined attributes.
          else:
            value = ''
        
        except:
          value = _globals.writeError(self,'[getObjProperty]: key=%s'%key)
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)


    # --------------------------------------------------------------------------
    #  ObjAttrs.attr:
    #
    #  Get one or set one or more attributes.
    #
    #  attr(key) -> getObjProperty(key,REQUEST)
    #  attr(key,value) -> setObjProperty(key,value)
    #  attr({key0:value0,...,keyN:valueN}) -> setObjProperty(key0,value0),...
    # --------------------------------------------------------------------------
    def attr(self, *args, **kwargs):
      request = self.REQUEST
      if len(args) == 1 and type(args[0]) is str:
        return self.getObjProperty( args[0], request, kwargs)
      elif len(args) == 2:
        self.setObjProperty( args[0], args[1], request.get('lang'))
      elif len(args) == 1 and type(args[0]) is dict:
        for key in args[0].keys():
          self.setObjProperty( key, args[0][key], request.get('lang'))


    # --------------------------------------------------------------------------
    #  ObjAttrs.evalMetaobjAttr
    # --------------------------------------------------------------------------
    def evalMetaobjAttr(self, *args, **kwargs):
      id = self.REQUEST.get('ZMS_INSERT',self.meta_id)
      attr_id = args[0]
      if attr_id.find('.')>0:
        id = attr_id[:attr_id.find('.')]
        attr_id = attr_id[attr_id.find('.')+1:]
      return self.getMetaobjManager().evalMetaobjAttr(id,attr_id,zmscontext=self,options=kwargs)


    """
    ############################################################################
    ###  
    ###  Active
    ### 
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ObjAttrs.isActive:
    # --------------------------------------------------------------------------
    def isActive(self, REQUEST):
      b = True
      if self.getType()=='ZMSRecordSet':
        return b
      v = self.attr('active')
      if type(v) is bool:
        return v
      v = self.attr('isActive')
      if type(v) is bool:
        b = b and v
      obj_vers = self.getObjVersion(REQUEST)
      obj_attrs = self.getObjAttrs()
      for key in ['active','attr_active_start','attr_active_end']:
        if obj_attrs.has_key(key):
          obj_attr = obj_attrs[key]
          lang = REQUEST.get('lang',self.getPrimaryLanguage())
          while True:
            value = self._getObjAttrValue(obj_attr,obj_vers,lang)
            empty = False
            lang = self.getParentLanguage(lang)
            if lang is not None:
              empty = value is None
            if not empty:
              break
          # Toggle.
          if key == 'active':
            b = b and value
          # Start time.
          elif key == 'attr_active_start':
            if value is not None:
              try:
                dt = DateTime(time.mktime(value))
                b = b and dt.isPast()
              except:
                # todo: consistent replacement of time by datetime
                dtValue = datetime.datetime(value[0],value[1],value[2],value[3],value[4],value[5],value[6])
                b = b and datetime.datetime.now() > dtValue
          # End time.
          elif key == 'attr_active_end':
            if value is not None:
              try:
                dt = DateTime(time.mktime(value))
                b = b and (dt.isFuture() or (dt.equalTo(dt.earliestTime()) and dt.latestTime().isFuture()))
              except:
                # todo: consistent replacement of time by datetime
                dtValue = datetime.datetime(value[0],value[1],value[2],value[3],value[4],value[5],value[6])
                b = b and dtValue < datetime.datetime.now()
          if not b: break
      return b


    """
    ############################################################################
    #
    #  Set
    #
    ############################################################################
    """
    
    # --------------------------------------------------------------------------
    #  ObjAttrs.formatObjAttrValue:
    # --------------------------------------------------------------------------
    def formatObjAttrValue(self, obj_attr, v, lang=None):
      
      #-- DATATYPE
      datatype = obj_attr.get('datatype_key',_globals.DT_UNKNOWN)
      
      #-- VALUE
      if type(v) in StringTypes:
        chars = ''.join(filter(lambda x: x!='\t',string.whitespace))
        v = v.strip(chars)
      # Retrieve v from options.
      if obj_attr.has_key('options'):
        options = obj_attr['options']
        try: 
          i = options.index(int(v))
          if i%2==1: v = options[i-1]
        except:
          try:
            i = options.index(str(v))
            if i%2==1: v = options[i-1]
          except:
            pass
      
      #-- Blob-Fields
      if datatype in _globals.DT_BLOBS:
        if self.getType()=='ZMSRecordSet' and \
           str(v) == str(_blobfields.createBlobField(self,datatype)):
          l = self.getObjProperty(self.getMetaobj(self.meta_id)['attrs'][0]['id'],self.REQUEST)
          r = filter(lambda x: v.equals(x.get(obj_attr['id'],None)),l)
          if len( r) == 0:
            v = None
          else:
            v = v._getCopy()
            v.aq_parent = self
            v.key = '%s:%i'%(obj_attr['id'],l.index(r[0]))
            v.lang = lang
        if isinstance(v,ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(v,'filename',''))==0:
            v = None
          else:
            v = _blobfields.createBlobField(self,datatype,v)
        if type(v) is dict:
          if len(v.get('filename',''))==0:
            v = None
          else:
            v = _blobfields.createBlobField(self,datatype,v)
      
      #-- DateTime-Fields.
      elif datatype in _globals.DT_DATETIMES:
        if type(v) in StringTypes:
          fmt_str = 'DATETIME_FMT'
          if datatype == _globals.DT_DATE:
            fmt_str = 'DATE_FMT'
          elif datatype == _globals.DT_TIME:
            fmt_str = 'TIME_FMT'
          v = self.parseLangFmtDate(v)
        elif type(v) is not time.struct_time:
          v = _globals.getDateTime(v)
      
      #-- Dictionary-Fields
      elif datatype == _globals.DT_DICT:
        if v is None:
          v = {}
        if type(v) in StringTypes:
          try:
           v = self.parseXmlString(self.getXmlHeader() + v)
          except:
            _globals.writeError( self, "[formatObjAttrValue]: can't parse dict from xml - exception ignored!")
            pass
        if type(v) is dict:
          v = v.copy()
      
      #-- List-Fields
      elif datatype == _globals.DT_LIST:
        if obj_attr['repetitive'] and not type(v) is list:
          if obj_attr['type'] in ['file','image']:
            l = self.getObjProperty(obj_attr['id'],self.REQUEST)
            r = filter(lambda x: v is not None and v.equals(x),l)
            if len( r) == 0:
              v = None
            else:
              v = v._getCopy()
              v.aq_parent = self
              v.key = '%s:%i'%(obj_attr['id'],l.index(r[0]))
              v.lang = lang
        else:
          if v is None:
            v = []
          if type(v) in StringTypes:
            try:
              l = self.parseXmlString(self.getXmlHeader() + v)
            except:
              _globals.writeError( self, "[formatObjAttrValue]: can't parse list from xml - exception ignored!")
              l = None
            if l is not None:
              v = l
            else:
              v = [v.strip()]
            if type(v) is list or type(v) is tuple:
              v = self.copy_list(v)
      
      #-- Integer-Fields
      elif datatype in _globals.DT_INTS:
        if type(v) in StringTypes and len(v) > 0:
          if v[-1] == '.':
            v = v[:-1]
          v = int(v)
      
      #-- Float-Fields
      elif datatype == _globals.DT_FLOAT:
        if type(v) in StringTypes and len(v) > 0:
          v = float(v)
      
      #-- String-Fields.
      elif datatype in _globals.DT_STRINGS:
        if v is None:
          v = ''
      
      #-- Text-Fields
      elif datatype == _globals.DT_TEXT:
        v = self.validateInlineLinkObj(v)
      
      #-- Url-Fields
      elif datatype == _globals.DT_URL:
        v = self.validateLinkObj(v)
      
      # Hook for custom formatting.
      name = 'formatCustomObjAttrValue'
      if hasattr(self,name):
        v = getattr(self,name)( context=self, obj_attr=obj_attr, v=v)
      
      return v


    # --------------------------------------------------------------------------
    #  ObjAttrs.setReqProperty:
    #
    #  Assigns value to specified property from Request-Object.
    # --------------------------------------------------------------------------
    def setReqProperty(self, key, REQUEST, forced=0):
    
      #-- REQUEST
      lang = REQUEST['lang']
      
      #-- DEFINTION
      obj_attr = self.getObjAttr(key)
      elName = self.getObjAttrName(obj_attr,lang)
      
      #-- ENABLED
      enabled = not self.isDisabledAttr(obj_attr,REQUEST)
      
      #-- DATATYPE
      datatype = obj_attr['datatype_key']
      
      #-- RETURN
      if ( not enabled) or \
         ( not obj_attr['xml']) or \
         ( obj_attr['id'].find('_') == 0 and not REQUEST.form.has_key(elName)) or \
         ( datatype == _globals.DT_UNKNOWN): 
        if not forced: 
          return
      
      #-- VALUE
      set, value =False, REQUEST.get(elName,None)
      
      #-- Blob-Fields
      if datatype in _globals.DT_BLOBS:
        
        # Upload
        if isinstance(value,ZPublisher.HTTPRequest.FileUpload) and len(value.filename) > 0:
          set, value = True, value
        
        # Delete
        elif REQUEST.has_key('del_%s'%elName) and int(REQUEST['del_%s'%elName]) == 1:
          set, value = True, None
        
        # Preload
        else:
          SESSION = REQUEST.get('SESSION',None)
          form_id = REQUEST.get('form_id',None)
          if SESSION is not None and form_id is not None:
            session_id = REQUEST.get('session_id',SESSION.getId())
            temp_folder = self.temp_folder
            id = session_id + '_' + form_id + '_' + key
            if id in temp_folder.objectIds():
              o = getattr( temp_folder, id)
              f = o.data
              filename = getattr( temp_folder, id).title
              mt, enc = _globals.guess_contenttype( filename, f)
              set, value = True, {'data':str(f),'filename':filename,'content_type':mt}
              if not self.pilutil().enabled() and datatype == _globals.DT_IMAGE and REQUEST.get('width_%s'%attr) and REQUEST.get('height_%s'%attr):
                w = REQUEST['width_%s'%attr]
                h = REQUEST['height_%s'%attr]
                if w != int(o.width) or h != int(o.height):
                  value = _blobfields.createBlobField( self, datatype, value)
                  value.width = w
                  value.height = h
              temp_folder.manage_delObjects([id])
      
      #-- Integer-Fields
      elif datatype in _globals.DT_INTS:
        if value is not None:
          if type(value) is str and len(value) == 0:
            set, value = True, None
          else:
            set, value = True, int(value)
      
      #-- Float-Fields
      elif datatype == _globals.DT_FLOAT:
        if value is not None:
          if type(value) is str and len(value) == 0:
            set, value = True, None
          else:
            set, value = True, float(value)
      
      #-- Other-Fields
      else:
        set, value = True, self.formatObjAttrValue(obj_attr,value,lang)
      
      #-- SET?
      if set:
        _globals.writeLog( self, "[setReqProperty] %s=%s"%(key,str(value)))
        self.setObjProperty(key,value,lang)


    # --------------------------------------------------------------------------
    #  ObjAttrs.setObjProperty:
    #
    #  Assigns value to specified property.
    #
    #  @deprecated: use attr(key,value) instead! 
    # --------------------------------------------------------------------------
    def setObjProperty(self, key, value, lang=None, forced=0):
      
      #-- [ReqBuff]: Clear buffered value from Http-Request.
      reqBuffId = '%s_%s'%('getObjProperty',key)
      self.clearReqBuff(reqBuffId,self.REQUEST)
      
      #-- CUSTOM
      if key not in self.getObjAttrs().keys():
        self.REQUEST.set('pKey',key)
        self.REQUEST.set('pValue',value)
        self.getObjProperty('setObjProperty',self.REQUEST)
        return
      
      #-- DEFINITION
      obj_attr = self.getObjAttr(key)
      
      #-- DATATYPE
      datatype = obj_attr['datatype_key']
      
      #-- VALUE
      value = self.formatObjAttrValue(obj_attr,value,lang)
      
      #-- Url-Fields
      if datatype == _globals.DT_URL:
        # Unregister old reference.
        req = {'lang' : lang, 'prevew' : 'preview'}
        old_value = self.getObjProperty(key,req)
        ref_obj = self.getLinkObj(old_value)
        if ref_obj is not None:
          ref_obj.unregisterRefObj(self,self.REQUEST)
        # Register new reference.
        ref_obj = self.getLinkObj(value)
        if ref_obj is not None:
          ref_obj.registerRefObj(self,self.REQUEST)
        value = self.validateLinkObj(value)
      
      #-- Notify metaobj_manager.
      self.notifyMetaobjAttrAboutValue( self.meta_id, key, value)
      
      #-- SET!
      _globals.writeLog( self, "[setObjProperty]: %s(%s)=%s"%(key,str(datatype),str(value)))
      ob = self.getObjVersion({'preview':'preview'})
      setobjattr(self,ob,obj_attr,value,lang)
      if forced:
        ob = self.getObjVersion()
        setobjattr(self,ob,obj_attr,value,lang)


    ############################################################################
    #  ObjAttrs.preloadObjProperty:
    #
    #  Preload property.
    ############################################################################
    def preloadObjProperty(self, REQUEST, RESPONSE=None):
      """ ObjAttrs.preloadObjProperty """
      content_type = 'text/plain'
      message = {}
      message['success'] = True
      # Additional parameters.
      for qs in REQUEST['QUERY_STRING'].split('&'):
        e = qs.find('=')
        if e >= 0:
          k = qs[:e]
          v = qs[e+1:]
          REQUEST.set(k,v)
      
      # Mandatory parameters.
      lang = REQUEST['lang']
      key = REQUEST['key']
      
      dataRequestKey = REQUEST.get('dataRequestKey')
      filenameUnescape = REQUEST.get('filenameUnescape')
      if dataRequestKey:
        value = REQUEST[dataRequestKey]
        if isinstance(value,ZPublisher.HTTPRequest.FileUpload):
          filename = value.filename
        else:
          filename = value
          value = REQUEST['BODY']
          if filenameUnescape:
            filename = _globals.unescape(filename)
      else:
        value = REQUEST['userfile[0]']
        filename = value.filename
      blob = self.ImageFromData(value,filename)
      filename = blob.getFilename()
      
      # Preload to temp-folder.
      session_id = REQUEST['session_id']
      form_id = REQUEST['form_id']
      temp_folder = self.temp_folder
      id = session_id + '_' + form_id + '_' + key
      if id in temp_folder.objectIds():
        temp_folder.manage_delObjects([id])
      meta_id = REQUEST.get('meta_id',self.meta_id)
      obj_attr = self.getObjAttr(key,meta_id)
      datatype = obj_attr['datatype_key']
      if datatype == _globals.DT_IMAGE:
        file = temp_folder.manage_addImage( id=id, title=filename, file=value)
      else:
        file = temp_folder.manage_addFile( id=id, title=filename, file=value)
      
      if dataRequestKey:
        message['filename'] = blob.getFilename()
        message['size_str'] = self.getDataSizeStr(blob.get_size())
        message['content_type'] = blob.getContentType()
        message['temp_url'] = '%s/%s'%(temp_folder.absolute_url(),id)
        message = self.str_json(message)
      
      if REQUEST.get('set'):
        self.setReqProperty(key,REQUEST)
        message = self.getZMILangStr( 'MSG_UPLOADED')+'('+self.getLangFmtDate(time.time())+')'
      
      # Return with success.
      RESPONSE.setHeader('Content-Type',content_type)
      return message


    def manage_changeTempBlobjProperty(self, lang, key, form_id, action, REQUEST, RESPONSE=None):
      """ ObjAttrs.manage_changeTempBlobjProperty """
      rtn = {}
      # Mandatory parameters.
      SESSION = REQUEST.get('SESSION',None)
      if SESSION is not None:
        session_id = SESSION.getId()
        temp_folder = self.temp_folder
        id = session_id + '_' + form_id + '_' + key
        src = self.getTempBlobjPropertyUrl( format=None, REQUEST=REQUEST, RESPONSE=RESPONSE)['src']
        file = getattr( temp_folder, id)
        orig = self.ImageFromData(file.data,file.title)
        orig.lang = lang
        if action == 'preview':
          maxdim = self.getConfProperty('InstalledProducts.pil.thumbnail.max',100)
          blob = self.pilutil().thumbnail( orig, maxdim)
          thumbkey = key
          for suffix in ['hires','superres']:
            if thumbkey.endswith(suffix):
              thumbkey = thumbkey[:-len(suffix)]
              break
          thumbid = session_id + '_' + form_id + '_' + thumbkey
          if thumbid in temp_folder.objectIds():
            temp_folder.manage_delObjects([thumbid])
          temp_folder.manage_addImage( id=thumbid, title=blob.getFilename(), file=blob.getData())
          file = getattr( temp_folder, thumbid)
          meta_id = REQUEST.get('meta_id',self.meta_id)
          obj_attr = self.getObjAttr(thumbkey,meta_id)
          elName = self.getObjAttrName(obj_attr,lang)
          rtn['elName'] = elName
          rtn['height'] = int(file.getProperty('height'))
          rtn['width'] = int(file.getProperty('width'))
          rtn['filename'] = blob.getFilename()
          rtn['src'] = self.url_append_params(file.absolute_url(),{'ts':time.time()})
          # extra
          rtn['lang'] = thumbkey
          rtn['key'] = thumbkey
          rtn['form_id'] = form_id
        else:
          blob = orig
          if 'resize' in action.split(','):
            width = REQUEST['width']
            height = REQUEST['height']
            size = (width,height)
            blob = self.pilutil().resize( blob, size)
            rtn['height'] = height
            rtn['width'] = width
          if 'crop' in action.split(','):
            x0 = REQUEST['x0']
            y0 = REQUEST['y0']
            x1 = REQUEST['x1']
            y2 = REQUEST['y2']
            box = (x0, y0, x1, y2)
            blob = self.pilutil().crop( blob, box)
            rtn['height'] = y2-y0
            rtn['width'] = x1-x0
          file.manage_upload(blob.getData())
          rtn['filename'] = blob.getFilename()
          rtn['src'] = src
      # Return JSON.
      return self.str_json(rtn)


    def getTempBlobjPropertyUrl(self, format='json', REQUEST=None, RESPONSE=None):
      """ ObjAttrs.getTempBlobjPropertyUrl """
      rtn = {}
      # Mandatory parameters.
      lang = REQUEST['lang']
      key = REQUEST['key']
      SESSION = REQUEST.get('SESSION',None)
      form_id = REQUEST.get('form_id',None)
      if SESSION is not None and form_id is not None:
        session_id = SESSION.getId()
        temp_folder = self.temp_folder
        id = session_id + '_' + form_id + '_' + key
        if id not in temp_folder.objectIds():
          obj_attr = self.getObjAttr(key)
          datatype = obj_attr['datatype_key']
          blob = self.getObjProperty(key,REQUEST)
          filename = blob.getFilename()
          value = blob.getData()
          if datatype == _globals.DT_IMAGE:
            file = temp_folder.manage_addImage( id=id, title=filename, file=value)
          else:
            file = temp_folder.manage_addFile( id=id, title=filename, file=value)
        file = getattr( temp_folder, id)
        if file.meta_type == 'Image':
          rtn['height'] = int(file.getProperty('height'))
          rtn['width'] = int(file.getProperty('width'))
        rtn['content_type'] = file.content_type
        rtn['filename'] = file.title
        rtn['src'] = self.url_append_params(file.absolute_url(),{'ts':time.time()})
      # Return JSON.
      if format == 'json':
        rtn = self.str_json(rtn)
      return rtn


    def clearTempBlobjProperty(self, format='json', REQUEST=None, RESPONSE=None):
      """ ObjAttrs.clearTempBlobjProperty """
      rtn = {}
      # Mandatory parameters.
      lang = REQUEST['lang']
      key = REQUEST['key']
      SESSION = REQUEST.get('SESSION',None)
      form_id = REQUEST.get('form_id',None)
      if SESSION is not None and form_id is not None:
        session_id = SESSION.getId()
        temp_folder = self.temp_folder
        id = session_id + '_' + form_id + '_' + key
        if id in temp_folder.objectIds():
          temp_folder.manage_delObjects([id])
      # Return JSON.
      if format == 'json':
        rtn = self.str_json(rtn)
      return rtn


    # --------------------------------------------------------------------------
    #  ObjAttrs.convertObjPropertyUtf8
    # --------------------------------------------------------------------------
    def convertObjPropertyUtf8(self, key):
      obj_attr = self.getObjAttr(key)
      for obj_vers in self.getObjVersions():
        if obj_attr['multilang']:
          for langId in self.getLangIds():
            setutf8attr(self, obj_vers, obj_attr, langId)
        else:
          langId = self.getPrimaryLanguage()
          setutf8attr(self, obj_vers, obj_attr, langId)


    # --------------------------------------------------------------------------
    #  ObjAttrs.utf8
    # --------------------------------------------------------------------------
    def utf8(self, s, encoding='latin-1'):
      return utf8(s, encoding)


    """
    ############################################################################
    #
    #  C L O N E
    #
    ############################################################################
    """
    
    # --------------------------------------------------------------------------
    #  ObjAttrs.cloneObjAttrs:
    #
    #  Clone object-attributes.
    # --------------------------------------------------------------------------
    def cloneObjAttrs(self, src, dst, REQUEST={}):
      _globals.writeBlock( self, "[cloneObjAttrs]: Clone object-attributes from '%s' to '%s'"%(str(src),str(dst)))
    
      #-- REQUEST
      prim_lang = self.getPrimaryLanguage()
      lang = REQUEST.get('lang',prim_lang)
      
      #-- Clone
      keys = self.getObjAttrs().keys()
      if self.getType()=='ZMSRecordSet':
        keys = self.difference_list( keys, self.getMetaobjAttrIds(self.meta_id)[1:])
      for key in keys:
        obj_attr = self.getObjAttr(key)
        # Multi-Language Attributes.
        if obj_attr['multilang']:
          for s_lang in self.getLangIds():
            if lang in ['*',prim_lang,s_lang]:
              cloneobjattr(self,src,dst,obj_attr,s_lang)
        # Others.
        else:
          coverage = getattr(src,'attr_dc_coverage','')
          if coverage is None or \
             coverage == '' or \
             type(coverage) is not str:
            coverage = 'global.%s'%prim_lang
          s_lang = coverage[coverage.find('.')+1:]
          if lang in ['*',prim_lang,s_lang]:
            cloneobjattr(self,src,dst,obj_attr,lang)


################################################################################
################################################################################
###
###   Object Attributes Manager
###
################################################################################
################################################################################
class ObjAttrsManager:

    # --------------------------------------------------------------------------
    #  ObjAttrsManager.synchronizeObjAttr:
    #
    #  Synchronizes object-attribute.
    # --------------------------------------------------------------------------
    def synchronizeObjAttr(self, attr):
      try:
        if attr['type'] in ZMSMetaobjManager.ZMSMetaobjManager.valid_types:
          dct = {}
          dct['id'] = attr['id']
          dct['name'] = attr.get('name','?')
          dct['type'] = attr['type']
          dct['key'] = attr['id']
          dct['xml'] = attr['id'] not in ['created_uid','created_dt','change_uid','change_dt','work_uid','work_dt','internal_dict','change_history','master_version','major_version','minor_version']
          dct['lang_inherit'] = attr['id'] not in ['change_uid','change_dt','work_uid','work_dt','internal_dict']
          dct['datatype'] = attr['type']
          if attr['type'] in ['autocomplete','password','select']:
            dct['type'] = attr['type']
            dct['datatype'] = 'string'
          elif attr['type'] in ['richtext']:
            dct['type'] = attr['type']
            dct['datatype'] = 'text'
          elif attr['type'] in ['multiautocomplete','multiselect']:
            dct['type'] = attr['type']
            dct['datatype'] = 'list'
          elif attr.get('default','') != '':
            dct['default'] = attr['default']
          elif attr.get('repetitive',0):
            dct['datatype'] = 'list'
          dct['mandatory'] = attr.get('mandatory',0)
          dct['multilang'] = attr.get('multilang',0)
          dct['repetitive'] = attr.get('repetitive',0)
          if len(attr.get('keys',[]))>0:
            options = []
            for option in attr['keys']:
              options.append(option)
              options.append(option)
            dct['options'] = options
          dct['datatype_key'] = _globals.datatype_key(dct['datatype'])
          return dct
      except:
        _globals.writeError( self, '[synchronizeObjAttr]')
      return None

    def synchronizeObjAttrs(self, sync_id=None):
      """
      Synchronizes dictionary of object-attributes.
      @param sync_id: meta-id of content-object, if None synchronize all.
      """
      rtn = []
      rtn.append('[%s.synchronizeObjAttrs]: %s'%(self.absolute_url(),str(sync_id)))
      _globals.writeLog( self, '[synchronizeObjAttrs]')
      
      # Prepare defaults.
      defaults_obj_attrs = {}
      defaults = [
        # Coverage
        { 'id':'attr_dc_coverage', 'type':'string'},
        # Changed by
        { 'id':'created_uid', 'type':'string'},
        { 'id':'created_dt', 'type':'datetime'},
        { 'id':'change_uid','type':'string', 'multilang':1},
        { 'id':'change_dt','type':'datetime', 'multilang':1},
        # Version info
        { 'id':'change_history', 'type':'list', 'default':[]},
        { 'id':'master_version', 'type':'int', 'default':0},
        { 'id':'major_version', 'type':'int', 'default':0},
        { 'id':'minor_version', 'type':'int', 'default':0},
        # Active
        { 'id':'active', 'type':'boolean', 'multilang':1, 'default':1},
        { 'id':'attr_active_start', 'type':'datetime', 'multilang':1},
        { 'id':'attr_active_end','type':'datetime', 'multilang':1},
        # Workflow
        { 'id':'work_uid','type':'string', 'multilang':1},
        { 'id':'work_dt','type':'datetime', 'multilang':1},
        # Internal dictionary
        { 'id':'internal_dict', 'type':'dictionary', 'default':{}},
      ]
      for attr in defaults:
        dct = self.synchronizeObjAttr( attr)
        if type( dct) is dict:
          defaults_obj_attrs[dct['id']] = dct
      
      # Process meta-model.
      if sync_id is None or sync_id == [ None]:
        self.dObjAttrs = {}
        meta_ids = self.dGlobalAttrs.keys()
        for meta_id in self.getMetaobjIds( sort=0):
          if meta_id not in meta_ids:
            meta_ids.append( meta_id)
      else:
        if not type(sync_id) is list:
          sync_id = [sync_id]
        meta_ids = sync_id
      for meta_id in meta_ids:
        if meta_id in self.dGlobalAttrs.keys():
          obj_attrs = {}
          for key in defaults_obj_attrs.keys():
            obj_attr = defaults_obj_attrs[key]
            if obj_attr['id'].find('work_') < 0 or meta_id in ['ZMSCustom','ZMSLinkElement'] or self.getMetaobj(meta_id).get('type') == 'ZMSDocument':
              obj_attrs[key] = obj_attr.copy()
        else:
          obj_attrs = self.dObjAttrs['ZMSCustom'].copy()
        for key in self.getMetaobjAttrIds( meta_id):
          attr = self.getMetaobjAttr( meta_id, key)
          dct = self.synchronizeObjAttr( attr)
          if type( dct) is dict:
            obj_attrs[key] = dct
          elif obj_attrs.has_key(key):
            del obj_attrs[key]
        self.dObjAttrs[meta_id] = obj_attrs
      
      # Make persistent.
      self.dObjAttrs = self.dObjAttrs.copy()
      
      # Process clients.
      for portalClient in self.getPortalClients():
        try:
          b = False
          if not b:
            b = sync_id is None
          if not b:
            metaObjIds = portalClient.getMetaobjIds(sort=0)
            for id in sync_id:
              if not b:
                b = id in metaObjIds and portalClient.getMetaobj(id).get('acquired',0)==1
          if b:
            rtn.append(portalClient.synchronizeObjAttrs(sync_id))
        except:
          _globals.writeError( self, '[synchronizeObjAttrs]: Can\'t process %s'%portalClient.absolute_url())
      
      return '\n'.join(rtn)

################################################################################
