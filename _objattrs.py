################################################################################
# _objattrs.py
#
# $Id: _objattrs.py,v 1.11 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.11 $
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
from DateTime.DateTime import DateTime
from types import StringTypes
import ZPublisher.HTTPRequest
import time
import urllib
# Product Imports.
import _blobfields
import _globals


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
  key = self.getObjAttrName(obj_attr,langId)
  v = getattr(obj_vers,key,None)
  v = utf8(v,charset)
  setattr(obj_vers,key,v)


# ------------------------------------------------------------------------------
#  _objattrs.hasobjattr:
# ------------------------------------------------------------------------------
def hasobjattr(obj, key):
  try:
    id = obj.id
    keys = obj.__dict__.keys() 
    return key in keys
  except:
    return hasattr( obj, key)

# ------------------------------------------------------------------------------
#  _objattrs.getobjattr:
# ------------------------------------------------------------------------------
def getobjattr(self, obj, obj_attr, lang):
  key = self.getObjAttrName(obj_attr,lang)
  v = None
  if hasobjattr(obj,key):
    v = getattr(obj,key)
  # Default value.
  if v is None:
    datatype = obj_attr['datatype_key']
    default = obj_attr.get('default',_globals.dtMapping[datatype][1])
    if default is not None:
      if datatype in _globals.DT_DATETIMES and default == '{now}':
        default = time.time()
      elif type(default) is list or type(default) is tuple:
        v = self.copy_list(default)
      elif type(default) is dict:
        v = default.copy()
      else:
        if type( default) is str and len( default) > 0:
          default = _globals.dt_html( self, str( default), self.REQUEST)
        v = default
  return v

# ------------------------------------------------------------------------------
#  _objattrs.setobjattr:
# ------------------------------------------------------------------------------
def setobjattr(self, obj, obj_attr, value, lang):
  key = self.getObjAttrName(obj_attr,lang)
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
        raise e
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
    def ajaxGetObjOptions(self, key, meta_id, REQUEST):
      """ ObjAttrs.ajaxGetObjOptions """
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/plain; charset=utf-8'
      filename = 'ajaxGetObjOptions.txt'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      l = map( lambda x: x[1], self.getObjOptions( self.getObjAttr( key, meta_id), REQUEST))
      q = REQUEST.get( 'q', '').upper()
      if q:
        l = filter( lambda x: x.upper().find( q) >= 0, l)
      if REQUEST.has_key( 'limit'):
        limit = int(REQUEST.get( 'limit'))
        l = l[:limit]
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
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
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
      return obj_attrs.get(key,{'id':key,'key':key,'xml':False,'multilang':False,'lang_inherit':False,'name':'UNKOWN','datatype':'string','datatype_key':_globals.DT_UNKNOWN})


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
          dtml = ''.join(map(lambda x: str(obj_attropts[x*2]),range(len(obj_attropts)/2)))
          if len(obj_attropts)==2 and self.getLinkObj(obj_attropts[0],REQUEST):
            ob = self.getLinkObj(obj_attropts[0],REQUEST)
            metaObj = self.getMetaobj(ob.meta_id)
            res = ob.getObjProperty(metaObj['attrs'][0]['id'],REQUEST)
            res = map(lambda x: {'key':x['key'],'value':x.get('value',x.get('value_%s'%REQUEST['lang']))},res)
            res = self.sort_list(res,'value','asc')
            opts = map(lambda x: [x['key'],x['value']],res)
          elif dtml.find('<dtml')>=0:
            try:
              opts = _globals.dt_html(self,dtml,REQUEST)
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
          else:
            display = self.string_maxlen(display,30)
          optpl.append([value,display])
      return optpl

    # --------------------------------------------------------------------------
    #  ObjAttrs.getObjAttrName:
    # --------------------------------------------------------------------------
    def getObjAttrName(self, obj_attr, lang=None):
      attr = obj_attr['id']
      if obj_attr['multilang']:
        if lang is None: 
          lang = self.getPrimaryLanguage()
        attr = '%s_%s'%(attr,lang)
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
      
      #-- Repetitive-Fields.
      if obj_attr.get('repetitive',0):
        return self.f_selectRepetitive(self,ob=self,fmName=fmName,elName=elName,value=value,obj_attr=obj_attr,REQUEST=REQUEST) 
      
      #-- ID-Fields.
      if inputtype == 'identifier':
        if value == '': value = 'e%i'%self.getSequence().nextVal()
        return '<div class="form-element"><code><input type="hidden" name="%s" value="%s">%s</code></div>'%(elName,value,value)
      
      #-- Richtext-Fields.
      elif inputtype == 'richtext':
        REQUEST.set('data',value)
        form_fixed = False
        css = 'form-element'
        wrap = 'virtual'
        if len(filter( lambda x: x['id']=='format', metaObj['attrs'])) > 0:
          if REQUEST.get('ZMS_INSERT'):
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
          css = 'form-fixed'
          wrap = 'off'
        if disabled: 
          css += '-disabled'
        return self.f_selectRichtext(self,ob=self,fmName=fmName,elName=elName,cols=50,rows=15,value=value,key=obj_attr['id'],metaObj=metaObj,enabled=enabled,lang=lang,lang_str=lang_str,REQUEST=REQUEST,css=css,wrap=wrap)
      
      #-- Color-Fields.
      elif inputtype == 'color':
        return self.f_selectColor(self,ob=self,fmName=fmName,elName=elName,value=value,key=obj_attr['id'],lang_str=lang_str,mandatory=mandatory,REQUEST=REQUEST)
      
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
        css = 'form-fixed'
        wrap = 'virtual'
        if disabled: 
          css += '-disabled'
        cols = 35
        rows = 1
        inp = []
        inp.append(self.getTextArea(fmName,elName,cols,rows,self.toXmlString(value),enabled,REQUEST,css,wrap))
        inp.append('<a href="javascript:f_open_input(\'%s\',\'%s\',\'form-fixed\',\'off\')">'%(fmName,elName))
        inp.append('<img src="%stable_cell_edit.gif" border="0" title="%s" align="bottom"/>'%(self.MISC_ZMS,self.getZMILangStr('BTN_SAVE')))
        inp.append('</a>')
        return ''.join(inp)
      
      #-- Text-Fields.
      elif inputtype in [ 'text', 'xml', 'dialog']:
        css = 'form-element'
        wrap = 'virtual'
        if inputtype in ['xml']:
          css = 'form-fixed'
          wrap = 'off'
        if disabled: 
          css += '-disabled'
        cols = 35
        rows = 5
        extra = ' onselect="storeCaret(this)"'
        inp = []
        inp.append(self.getTextArea(fmName,elName,cols,rows,value,enabled,REQUEST,css,wrap,extra))
        if inputtype == 'dialog':
          try:
            title = self.getZMILangStr('CAPTION_CHOOSEOBJ')
            url = '%s/%s'%(self.absolute_url(),obj_attr[inputtype]['url'])
            params = ''
            params += 'lang=' + lang
            params += '&fmName=' + fmName
            params += '&elName=' + elName
            width = 420
            height = 360
            extra = ',resizable=yes,scrollbars=yes'
            inp.append('<input class="form-element" type="submit" name="btn" value="..." onclick="open_frame(\'%s\',\'%s\',\'%s\',%i,%i,\'%s\'); return false;" style="vertical-align:top"/>'%(title,url,params,width,height,extra))
          except:
            inp = []
            inp.append('<div class="form-element"><i>%s</i></div>'%(self.getZMILangStr('MSG_AFTER_INSERT')%self.display_type(REQUEST,meta_id)))
        return ''.join(inp)
      
      #-- Boolean-Fields.
      elif inputtype == 'boolean':
        return self.getCheckbox(fmName=fmName,elName=elName,value=value,enabled=enabled,hidden=False,REQUEST=REQUEST)
      
      #-- Autocomplete-Fields.
      elif inputtype == 'autocomplete':
        css = 'form-element'
        if disabled: css += '-disabled'
        return self.f_selectAutocomplete(self,fmName=fmName,elName=elName,value=value,key=obj_attr['id'],lang_str=lang_str,enabled=enabled,css=css,REQUEST=REQUEST)
      
      #-- Select-Fields.
      elif inputtype in ['multiselect','select']:
        css = 'form-element'
        if disabled: css += '-disabled'
        optpl = self.getObjOptions(obj_attr,REQUEST)
        return self.getSelect(fmName,elName,value,inputtype,lang_str,mandatory,optpl,enabled,REQUEST,css)
      
      #-- Input-Fields.
      else: 
        css = 'form-element'
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
          size = 20
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
      fmName = REQUEST.get( 'fmName' ,'form0_%s'%id)
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
      attr = self.getObjAttrName(obj_attr,lang)
      
      #-- Return true if object has specified property, false else.
      return hasobjattr(ob,attr) and getattr(ob,attr,None) is not None


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
            if _globals.debug( self):
              _globals.writeLog( self, "[_getObjAttrValue]: type(value) is type(string) - parseLangFmtDate(%s)"%(str(value)))
            set, value = True, self.parseLangFmtDate(value)
          elif type(value) is not time.struct_time:
            if _globals.debug( self):
              _globals.writeLog( self, "[_getObjAttrValue]: type(value) is not time.struct_time - getDateTime(%s)"%(str(value)))
            set, value = True, _globals.getDateTime(value)
      
      #-- List-Fields.
      elif datatype == _globals.DT_LIST:
        if not type(value) is type(obj_default):
          set, value = True, [value]
      
      #-- Integer-Fields.
      elif datatype in _globals.DT_INTS and not type(value) is type(obj_default):
        try:
          set, value = True, int(value)
        except:
          set, value = True, obj_default
      
      #-- Float-Fields.
      elif datatype == _globals.DT_FLOAT and not type(value) is type(obj_default):
        try:
          set, value = True, float(value)
        except:
          set, value = True, obj_default
      
      #-- Url-Fields
      elif datatype == _globals.DT_URL and value.find('{$') == 0:
        try:
          old = value
          ref_obj = self.getLinkObj(value)
          if ref_obj is not None:
            # Repair link.
            value = self.getRefObjPath( ref_obj)
          elif value.find('{$__') < 0:
            # Broken link.
            value = '{$__' + value[2:-1] + '__}'
          set = old != value
        except:
          _globals.writeError(self,'[_getObjAttrValue]: Unexpected Exception when processing Url-Fields: value=%s!'%str(value))
      
      #-- SET?
      if set: 
        attr = self.getObjAttrName( obj_attr, lang)
        if _globals.debug( self):
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
      while 1:
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
    # --------------------------------------------------------------------------
    def getObjProperty(self, key, REQUEST={}, par=None):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = '%s_%s'%('getObjProperty',key)
      try:
        if ( type( par) is dict and par.get( 'fetchReqBuff') in [ 0, False]) or \
           ( REQUEST.get( 'ZMS_VERSION_%s'%self.id) is not None):
          raise 'ReqBuff set inactive!'
        forced = type( par) is dict and par.get( 'fetchReqBuff') in [ 1, True]
        value = self.fetchReqBuff( reqBuffId, REQUEST, forced)
        return value
      except:
        objAttrs = self.getObjAttrs()
        metaObjAttr = None
        try:
          if key not in objAttrs.keys():
            metaObjAttr = self.getMetaobjAttr( self.meta_id, key)
        except:
          _globals.writeError( self, "[getObjProperty]: Can't get attribute from meta-objects: %s.%s"%(self.meta_id,key))
          
        #-- Special attributes.
        if metaObjAttr is not None and metaObjAttr['type'] == 'method':
          try:
            value = _globals.dt_html(self,metaObjAttr.get('custom',''),REQUEST)
          except:
            value = _globals.writeError(self,'[getObjProperty]: key=%s'%key)
        elif metaObjAttr is not None and metaObjAttr['type'] == 'constant':
          value = metaObjAttr.get('custom','')
        elif metaObjAttr is not None and metaObjAttr['type'] == 'resource':
          value = _blobfields.MyBlobWrapper(metaObjAttr.get('custom',None))
        
        #-- Standard attributes.
        elif key in objAttrs.keys():
          objAttr = objAttrs[key]
          datatype = objAttr['datatype_key']
          value = self.getObjAttrValue( objAttr, REQUEST)
          if datatype == _globals.DT_TEXT and  type(value) in StringTypes:
            try:
              value = _globals.dt_html(self,value,REQUEST)
            except:
              value = _globals.writeError(self,'[getObjProperty]: key=%s'%key)
        
        #-- Undefined attributes.
        else:
          value = ''
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, value, REQUEST)


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
      v = self.getObjProperty('active',REQUEST)
      if type(v) is bool:
        return v
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
            if not empty: break
          # Toggle.
          if key == 'active':
            b = b and value
          # Start time.
          elif key == 'attr_active_start':
            if value is not None:
              dt = DateTime(time.mktime(value))
              b = b and dt.isPast()
          # End time.
          elif key == 'attr_active_end':
            if value is not None:
              dt = DateTime(time.mktime(value))
              b = b and (dt.isFuture() or (dt.equalTo(dt.earliestTime()) and dt.latestTime().isFuture()))
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
      datatype = obj_attr['datatype_key']
      
      #-- VALUE
      if type(v) in StringTypes:
        v = v.strip()
        while len(v) > 0 and v[-1] == '\n':
          v = v[:-1]
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
        else:
          if type(v) in StringTypes:
            v = v.strip()
      
      #-- Text-Fields
      if datatype == _globals.DT_TEXT:
        # Inline-links: getLinkUrl (deprecated!)
        i = -1
        start = '{$'
        end = '}'
        while True:
          i = v.find( start, i + 1)
          j = v.find( end, i + 1)
          if i < 0 or j < 0:
            break
          ref_url = v[i:j+1]
          ref_obj = self.getLinkObj(ref_url)
          if ref_obj is not None:
            # Repair link.
            ref_url = self.getRefObjPath(ref_obj)
            v = v[:i] + ref_url + v[j+1:]
          elif ref_url.find('{$') == 0 and ref_url.find('{$__') < 0:
            # Broken link.
            ref_url = '{$__' + ref_url[2:-1] + '__}'
            v = v[:i] + ref_url + v[j+1:]
        # Inline-links: relative
        i = -1
        start = 'href="./'
        end = '"'
        while True:
          i = v.find( start, i + 1)
          j = v.find( end, i + len( start))
          if i < 0 or j < 0:
            break
          href = v[ i + len( start) :j]
          if href.rfind( '#') > 0:
            if href.rfind( '/') > 0:
              href = href[ :href.rfind( '/')] + '/' + href[ href.rfind( '#') + 1:]
            else:
              href = href[ href.rfind( '#') + 1:]
          else:
            if href.rfind( '/') > 0:
              href = href[ :href.rfind( '/')]
            else:
              href = ''
          ob = self
          for el in href.split( '/'):
            if ob is not None:
              if el == '..':
                ob = ob.aq_parent
              elif len( el) > 0:
                ob = getattr( ob, el, None)
          if ob is None:
            _globals.writeBlock( self, '[formatObjAttrValue]: invalid href=%s'%href)
      
      #-- Url-Fields
      if datatype == _globals.DT_URL:
        ref_obj = self.getLinkObj(v)
        if ref_obj is not None:
          # Repair link.
          v = self.getRefObjPath(ref_obj)
        elif v.find('{$') == 0 and v.find('{$__') < 0:
          # Broken link.
          v = '{$__' + v[2:-1] + '__}'
      
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
      
      #-- ENABLED
      enabled = not self.isDisabledAttr(obj_attr,REQUEST)
      
      #-- DATATYPE
      datatype = obj_attr['datatype_key']
      
      #-- RETURN
      if ( not enabled) or \
         ( not obj_attr['xml']) or \
         ( obj_attr['id'].find('_') == 0 and not REQUEST.form.has_key( self.getObjAttrName( obj_attr, lang))) or \
         ( datatype == _globals.DT_UNKNOWN): 
        if not forced: 
          return
      
      #-- ATTR
      attr = self.getObjAttrName(obj_attr,lang)
      
      #-- VALUE
      set, value =False, REQUEST.get(attr,None)
      
      #-- Blob-Fields
      if datatype in _globals.DT_BLOBS:
      
        # Delete
        if REQUEST.has_key('del_%s'%attr) and int(REQUEST['del_%s'%attr]) == 1:
          set, value = True, None
        
        # Upload
        elif isinstance(value,ZPublisher.HTTPRequest.FileUpload) and len(value.filename) > 0:
          set, value = True, value
        
        # Insert
        elif REQUEST.get('ZMS_INSERT',None) is not None:
          # Reset
          set, value = True, None
          # Preload
          SESSION = REQUEST.get('SESSION',None)
          form_id = REQUEST.get('form_id',None)
          if SESSION is not None and form_id is not None:
            session_id = SESSION.getId()
            temp_folder = self.temp_folder
            id = session_id + '_' + form_id + '_' + key
            if id in temp_folder.objectIds():
              f = getattr( temp_folder, id).data
              filename = getattr( temp_folder, id).title
              value = {'data':f,'filename':filename}
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
        if _globals.debug( self):
          _globals.writeLog( self, "[setReqProperty] %s=%s"%(key,str(value)))
        self.setObjProperty(key,value,lang)


    # --------------------------------------------------------------------------
    #  ObjAttrs.setObjProperty:
    #
    #  Assigns value to specified property.
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
      
      #-- Text-Fields
      if datatype == _globals.DT_TEXT:
        # Inline-links: relative
        i = -1
        start = 'href="./'
        end = '"'
        while True:
          i = value.find( start, i + 1)
          j = value.find( end, i + len( start))
          if i < 0 or j < 0:
            break
          href = value[ i + len( start) :j]
          if href.rfind( '#') > 0:
            if href.rfind( '/') > 0:
              href = href[ :href.rfind( '/')] + '/' + href[ href.rfind( '#') + 1:]
            else:
              href = href[ href.rfind( '#') + 1:]
          else:
            if href.rfind( '/') > 0:
              href = href[ :href.rfind( '/')]
            else:
              href = ''
          ref_obj = self
          for el in href.split( '/'):
            if ref_obj is not None:
              if el == '..':
                ref_obj = ref_obj.aq_parent
              elif len( el) > 0:
                ref_obj = getattr( ref_obj, el, None)
          if ref_obj is None:
            ref_url = '{$' + href.split( '/')[ -1] + '}'
            ref_obj = self.getLinkObj( ref_url)
          if ref_obj is not None:
            rel_url = self.getRelObjPath( ref_obj)
            if './' + href != rel_url:
              if ref_obj.isPage():
                rel_url = rel_url + '/index_%s.html'%lang
              else:
                rel_url = rel_url[ : rel_url.rfind( '/')] + '/index_%s.html'%lang + '#' + rel_url[ rel_url.rfind( '/') + 1: ]
	      value = value[: i + 6] + rel_url + value[ j :]
      
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
          # Repair link.
          value = self.getRefObjPath(ref_obj)
        elif value.find('{$') == 0 and value.find('{$__') < 0:
          # Broken link.
          value = '{$__' + value[2:-1] + '__}'
      
      #-- SET!
      if _globals.debug( self):
        _globals.writeLog( self, "[setObjProperty]: %s(%s)=%s"%(key,str(datatype),str(value)))
      ob = self.getObjVersion({'preview':'preview'})
      setobjattr(self,ob,obj_attr,value,lang)
      if forced:
        ob = self.getObjVersion()
        setobjattr(self,ob,obj_attr,value,lang)


    ############################################################################
    #  ObjAttrs.uploadObjProperty:
    #
    #  Upload property.
    ############################################################################
    def uploadObjProperty(self, REQUEST, RESPONSE=None):
      """ ObjAttrs.uploadObjProperty """
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
      value = REQUEST['userfile[0]']
      # Handle request.
      if REQUEST.get('ZMS_INSERT'):
        #-- INSERT: Add to temp-folder.
        session_id = REQUEST['session_id']
        form_id = REQUEST['form_id']
        temp_folder = self.temp_folder
        id = session_id + '_' + form_id + '_' + key
        if id in temp_folder.objectIds():
          temp_folder.manage_delObjects([id])
        file = temp_folder.manage_addFile( id=id, title=value.filename, file=value)
      else:
        #-- SAVE: Set property.
        self.setObjProperty( key, value, lang)
      # Return with message.
      message = self.getZMILangStr( 'MSG_UPLOADED')+'('+self.getLangFmtDate(time.time())+')'
      return message


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
        if attr['type'] in self.metaobj_manager.valid_types:
          dct = {}
          dct['id'] = attr['id']
          dct['name'] = attr.get('name','?')
          dct['type'] = attr['type']
          dct['key'] = attr['id']
          dct['xml'] = attr['id'] not in ['created_uid','created_dt','change_uid','change_dt','work_uid','work_dt','change_history','master_version','major_version','minor_version']
          dct['lang_inherit'] = attr['id'] not in ['change_uid','change_dt','work_uid','work_dt']
          dct['datatype'] = attr['type']
          if attr['type'] in ['autocomplete','password','select']:
            dct['type'] = attr['type']
            dct['datatype'] = 'string'
          elif attr['type'] in ['richtext']:
            dct['type'] = attr['type']
            dct['datatype'] = 'text'
          elif attr['type'] in ['multiselect']:
            dct['type'] = attr['type']
            dct['datatype'] = 'list'
          elif attr['type'] in ['dialog']:
            if type( attr['keys']) is list and len( attr['keys']) == 1:
              url = attr['keys'][0]
            else:
              url = attr['custom']
            dct['type'] = attr['type']
            dct['datatype'] = 'text'
            dct['size'] = 25
            dct[attr['type']] = {}
            dct[attr['type']]['url'] = url
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

    # --------------------------------------------------------------------------
    #  ObjAttrsManager.synchronizeObjAttrs:
    #
    #  Synchronizes object-attributes.
    # --------------------------------------------------------------------------
    def synchronizeObjAttrs(self, id=None):
      if _globals.debug( self):
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
      ]
      for attr in defaults:
        dct = self.synchronizeObjAttr( attr)
        if type( dct) is dict:
          defaults_obj_attrs[dct['id']] = dct
      
      # Process meta-model.
      if (id is None):
        self.dObjAttrs = {}
        meta_ids = self.dGlobalAttrs.keys()
        for meta_id in self.getMetaobjIds( sort=0):
          if meta_id not in meta_ids:
            meta_ids.append( meta_id)
      else:
        meta_ids = [id]
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
          if (id is None) or \
             (id in portalClient.getMetaobjIds(sort=0) and portalClient.getMetaobj(id).get('acquired',0)==1):
            portalClient.synchronizeObjAttrs(id)
        except:
          _globals.writeError( self, '[synchronizeObjAttrs]: Can\'t process %s'%portalClient.absolute_url())
      
      return ''

################################################################################
