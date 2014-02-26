################################################################################
# _objinputs.py
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

# Product Imports.
import _globals
import _zreferableitem


class ObjInputs:

  # ----------------------------------------------------------------------------
  #  ObjInputs.getUrlInput:
  #
  #	@param fmName
  #	@param elName
  #	@param elTextName
  #	@param size
  #	@param value
  #	@param enabled
  #	@param REQUEST
  #	@param css	CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getUrlInput(self, fmName, elName, elTextName, size, value, enabled, REQUEST, css='form-control'):
    lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
    html = []
    html.append(self.getTextInput(fmName,elName,size,value,'text',enabled,REQUEST,css+' url-input'))
    ref_obj = self.getLinkObj(value,REQUEST)
    if ref_obj is not None:
      html.append(ref_obj.zmi_breadcrumbs_obj_path(ref_obj,REQUEST))
    return ''.join(html)


  # ----------------------------------------------------------------------------
  #  getHiddenInput:
  #
  #	@param fmName
  #	@param elName
  #	@param value
  # ----------------------------------------------------------------------------
  def getHiddenInput(self, fmName, elName, value, onchange=''):
    html = []
    html.append('<input ')
    html.append(' type="hidden"')
    html.append(' name="%s"'%elName)
    html.append(' value="%s"'%str(value))
    if onchange:
      html.append(' onchange="%s"'%onchange)
    html.append('/>')
    return ''.join(html)


  # ----------------------------------------------------------------------------
  #  getDateTimeInput:
  #
  #	@param fmName
  #	@param elName
  #	@param size
  #	@param value
  #	@param enabled
  #	@param REQUEST
  #	@param css	CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getDateTimeInput(self, fmName, elName, size=8, value=None, enabled=True, fmt_str='DATETIME_FMT', REQUEST=None, css='form-control', extra=''):
    manage_lang = self.get_manage_lang()
    html = []
    if not type(value) is str:
      value = self.getLangFmtDate(value,manage_lang,fmt_str)
    if value is not None and self.parseLangFmtDate(value) is None:
      value = ''
    extra += ' title="%s"'%self.getZMILangStr(fmt_str)
    if enabled:
      if fmt_str == 'DATE_FMT':
        css += ' datepicker'
      elif fmt_str == 'DATETIME_FMT':
        css += ' datetimepicker'
    html.append(self.getTextInput(fmName,elName,size,value,'text',enabled,REQUEST,css,extra))
    return ''.join(html)


  # ----------------------------------------------------------------------------
  #  getDateInput:
  #
  #	@param fmName
  #	@param elName
  #	@param value
  #	@param enabled
  #	@param REQUEST
  #	@param css	CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getDateInput(self, fmName, elName, value, enabled, REQUEST, css='form-control', extra=''):
    return self.getDateTimeInput(fmName=fmName,elName=elName,size=8,value=value,enabled=enabled,fmt_str='DATE_FMT',REQUEST=REQUEST,css=css, extra=extra)


  # ----------------------------------------------------------------------------
  #  getPasswordInput:
  #
  #	@param fmName
  #	@param elName
  #	@param size
  #	@param value
  #	@param enabled
  #	@param css	CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getPasswordInput(self, fmName, elName, size=15, value='', enabled=True, REQUEST=None, css='form-control', extra=''):
    return self.getTextInput(fmName,elName,size,value,'password',enabled,REQUEST,css,extra)


  # ----------------------------------------------------------------------------
  # 	getTextInput:
  #
  #	@param fmName
  #	@param elName
  #	@param size
  #	@param value (optional)
  #	@param type (optional: "text" or "password")
  #	@param css	CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getTextInput(self, fmName, elName, size=None, value='', type='text', enabled=True, REQUEST=None, css='form-control', extra=''):
    lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
    elId = elName
    if elId.endswith('_%s'%lang):
      elId = elId[:-len('_%s'%lang)]
    html = []
    html.append('<input ')
    html.append(' class="%s"'%' '.join([css,elId,lang]))
    html.append(' type="%s"'%type)
    html.append(' id="%s"'%elName.replace(':int',''))
    html.append(' name="%s"'%elName)
    if size:
      html.append(' size="%i"'%size)
    if value is not None:
      html.append(' value="%s"'%_globals.html_quote(value))
    if not enabled:
      html.append(' disabled="disabled"')
    html.append(' %s/>'%extra)
    return ''.join(html)


  # ----------------------------------------------------------------------------
  # 	getSelect:
  #
  #	@param fmName
  #	@param elName
  #	@param value
  #	@param inputtype
  #	@param lang_str
  #	@param required
  #	@param optpl
  #	@param enabled
  #	@param REQUEST  	Http-Request
  #	@param css		CSS-Class
  #	@return String
  # ----------------------------------------------------------------------------
  def getSelect(self, fmName, elName, value, inputtype, lang_str, required, optpl, enabled, REQUEST, css='form-control', maxlen=30):
    if inputtype in ['select','multiline']:
      return self.zmi_input_select(self,name=elName,value=value,lang_str=lang_str,mandatory=required,options=optpl,enabled=enabled)
    elif inputtype in ['multiselect']:
      return self.zmi_input_multiselect(self,name=elName,value=value,lang_str=lang_str,mandatory=required,options=optpl,enabled=enabled)
    elif type in ['text']:
      return self.getTextArea(fmName,elName,35,4,value=value,enabled=enabled,REQUEST=REQUEST)
    else:
      return self.getTextInput(fmName=fmName,elName=elName,size=35,value=value,type='text',enabled=enabled,REQUEST=REQUEST)


  # ----------------------------------------------------------------------------
  # 	getCheckbox:
  #
  #	@param fmName
  #	@param elName
  #	@param elId
  #	@param value
  #	@param enabled
  #	@param hidden           Add hidden Input-Field if not enabled
  #	@param REQUEST  	Http-Request
  #	@param css		CSS-Class
  #	@param extra		Extra-Parameters
  #	@return String
  # ----------------------------------------------------------------------------
  def getCheckbox(self, fmName, elName, elId=None, value=None, enabled=True, hidden=True, REQUEST=None, css='', extra=''):
    lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
    elId = elName
    if elId.endswith('_%s'%lang):
      elId = elId[:-len('_%s'%lang)]
    html = []
    checked = str(value) == '1'
    if elName.find(':int') > 0 and value in [True, False]:
      value = int(value)
    html.append('<input ')
    html.append(' type="hidden"')
    html.append(' name="%s"'%elName)
    html.append(' value="%s"'%str(_globals.nvl(value,0)))
    html.append(' />')
    html.append('<input ')
    if type(elId) is str:
      html.append(' id="%s"'%elId)
    html.append(' class="%s"'%' '.join([css,elId,lang]))
    html.append(' type="checkbox"')
    if not enabled:
      html.append(' disabled="disabled"')
    if checked: 
      html.append(' checked="checked"')
    html.append(' onclick="if (this.checked){$(\'input[name=\\x22%s\\x22]\',this.form).val(1)}else{$(\'input[name=\\x22%s\\x22]\',this.form).val(0)}"'%(elName,elName))
    html.append(' />')
    return ''.join(html)


  # ----------------------------------------------------------------------------
  # 	getTextArea:
  #
  #	@param fmName
  #	@param elName
  #	@param cols
  #	@param rows
  #	@param value
  #	@param enabled
  #	@param REQUEST  	Http-Request
  #	@param css		CSS-Class
  #	@param wrap		Word-Wrap (on|off)
  #	@param extra		Extra-Parameters
  #	@return String
  # ----------------------------------------------------------------------------
  def getTextArea(self, fmName, elName, cols, rows, value, enabled, REQUEST, css='form-control', wrap='virtual', extra=''):
    lang = self.REQUEST.get('lang',self.getPrimaryLanguage())
    elId = elName
    if elId.endswith('_%s'%lang):
      elId = elId[:-len('_%s'%lang)]
    html = []
    html.append('<textarea ')
    html.append(' class="%s"'%' '.join([css,elId,lang]))
    html.append(' id="%s"'%elName)
    html.append(' name="%s"'%elName)
    if cols:
      html.append(' cols="%i"'%cols)
    if rows:
      html.append(' rows="%i"'%rows)
    html.append(' wrap="%s"'%wrap)
    if not enabled:
      html.append(' disabled="disabled"')
    html.append('%s>'%extra)
    if value is not None:
      if type(value) is list:
        for item in value:
          html.append('%s\n'%_globals.html_quote(item))
      else:
        html.append('%s'%_globals.html_quote(value))
    html.append('</textarea>')
    if type(value) is str and not REQUEST.get('URL','').find('manage_customize') >= 0:
      inline_links = []
      # Inline-links: getLinkUrl (deprecated!)
      i = -1
      start = '{$'
      end = '}'
      while True:
        i = value.find( start, i + 1)
        j = value.find( end, i + len( start))
        if i < 0 or j < 0:
          break
        inline_links.append( value[i:j+1])
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
        ref_obj = self.getSelf( self.PAGES)
        for el in href.split( '/'):
          if ref_obj is not None:
            if el == '..':
              ref_obj = ref_obj.aq_parent
            elif len( el) > 0:
              ref_obj = getattr( ref_obj, el, None)
        if ref_obj is None:
          ref_url = '{$__' + href.split( '/')[ -1] + '__}'
          inline_links.append( ref_url)
        elif isinstance( ref_obj, _zreferableitem.ZReferableItem):
          inline_links.append( self.getRefObjPath( ref_obj))
      if len( inline_links) > 0:
        html.append('<table cellspacing="0" cellpadding="1" border="0" align="left">')
        html.append('<tr valign="top">')
        html.append('<td class="form-small" align="left"><b>%s</b>:</td>'%(self.getZMILangStr('ATTR_TARGET')))
        html.append('<td class="form-small" align="left">')
        for c in range( len( inline_links)):
          if c % 2 == 0:
            html.append('<div class="zmiTableRowEven">')
          else:
            html.append('<div class="zmiTableRowOdd">')
          html.append('<div class="form-small">')
          ref_url = inline_links[c]
          ref_obj = self.getLinkObj(ref_url,REQUEST)
          if ref_obj is not None:
            html.append('<i class="icon-link" /> %s'%(ref_obj.zmi_breadcrumbs_obj_path(ref_obj,REQUEST)))
          elif isinstance( ref_obj, _zreferableitem.ZReferableItem):
            html.append('<i class="icon-unlink" />  %s'%(ref_url))
          html.append('</div>')
          html.append('</div>')
        html.append('</td>')
        html.append('</tr>')
        html.append('</table>')
    return ''.join(html)

################################################################################
