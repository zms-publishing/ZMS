################################################################################
# _objinputs.py
#
# $Id: _objinputs.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.7 $
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
from Globals import HTMLFile
# Product Imports.
import _globals


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
  def getUrlInput(self, fmName, elName, elTextName, size, value, enabled, REQUEST, css='form-element', extra=''):
    html = []
    html.append('<div class="%s">'%css)
    html.append(self.getTextInput(fmName,elName,size,value,'text',enabled,REQUEST,css))
    if enabled:
      html.append('<input ')
      html.append(' class="%s"'%css)
      html.append(' type="submit"')
      html.append(' name="btn"')
      html.append(' value="..."')
      if extra.find('onclick') < 0:
        html.append(' onclick="return browseObjsBtnClick(\'%s\',\'%s\',\'%s\',\'%s\')"'%(fmName,elName,elTextName,self.REQUEST.get('lang',self.getPrimaryLanguage())))
      html.append(' %s/>'%extra)
    html.append('</div>')
    ref_obj = self.getLinkObj(value,REQUEST)
    if ref_obj is not None:
      html.append('<div class="form-small">')
      html.append('<b>%s</b>: %s'%(self.getZMILangStr('ATTR_TARGET'),ref_obj.f_breadcrumbs(objectPathElements=ref_obj.breadcrumbs_obj_path(),no_icon=1,lang=REQUEST['lang'],REQUEST=REQUEST)))
      html.append('</div>')
    return ''.join(html)


  # ----------------------------------------------------------------------------
  #  ObjInputs.getEnumInput:
  #
  #	@param fmName
  #	@param elName
  # ----------------------------------------------------------------------------
  def getEnumInput(self, fmName, elName, size, value, enum, enabled=True, REQUEST=None, css='form-element'):
    html = []
    html.append('<span class="%s">'%css)
    if size > 0:
      html.append(self.getTextInput(fmName,elName,size,value,'text',enabled,REQUEST,css))
    else:
      html.append(self.getHiddenInput(fmName,elName,value,'%sChange(this);'%elName))
    if enabled:
      html.append('<input ')
      html.append(' class="%s"'%css)
      html.append(' type="submit"')
      html.append(' name="btn"')
      html.append(' value="..."')
      html.append(' onclick="return browseEnumBtnClick(\'%s\',\'%s\',\'%s\')"'%(fmName,elName,enum))
      html.append('/>')
    html.append('</span>')
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
  def getDateTimeInput(self, fmName, elName, size, value, enabled, fmt_str, REQUEST, css='form-element', extra=''):
    html = []
    lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
    manage_lang = REQUEST.get( 'manage_lang', self.getManageLanguage(lang))
    if not type(value) is str:
      value = self.getLangFmtDate(value,manage_lang,fmt_str)
    if value is not None and self.parseLangFmtDate(value) is None:
      value = ''
    html.append('<span class="%s" title="%s">'%(css,self.getZMILangStr(fmt_str)))
    html.append(self.getTextInput(fmName,elName,size,value,'text',enabled,REQUEST,css,extra))
    if enabled and fmt_str != 'TIME_FMT':
      html.append('<a href="javascript:calendarBtnClick(\'%s\',\'%s\')" class="button">'%(fmName,elName))
      html.append('<img src="%sbtn_calendar.gif" title="%s..." border="0" align="middle"/>'%(self.MISC_ZMS,self.getZMILangStr('ATTR_CALENDAR')))
      html.append('</a>')
    html.append('</span>')
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
  def getDateInput(self, fmName, elName, value, enabled, REQUEST, css='form-element', extra=''):
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
  def getPasswordInput(self, fmName, elName, size=15, value='', enabled=True, REQUEST=None, css='form-element'):
    return self.getTextInput(fmName,elName,size,value,'password',enabled,REQUEST,css)


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
  def getTextInput(self, fmName, elName, size=15, value='', type='text', enabled=True, REQUEST=None, css='form-element', extra=''):
    html = []
    html.append('<span class="%s">'%css)
    html.append('<input ')
    html.append(' class="%s"'%css)
    html.append(' type="%s"'%type)
    html.append(' id="%s"'%elName)
    html.append(' name="%s"'%elName)
    html.append(' size="%i"'%size)
    if value is not None:
      html.append(' value="%s"'%_globals.html_quote(value))
    if extra.find('style=') < 0:
      styles = []
      styles.append( 'width:%iem;'%size)
      if elName.endswith(':int'):
        styles.append( 'text-align:right')
      html.append(' style="%s"'%(';'.join(styles)))
    if not enabled:
      html.append(' disabled="disabled"')
    html.append(' %s/>'%extra)
    html.append('</span>')
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
  def getSelect(self, fmName, elName, value, inputtype, lang_str, required, optpl, enabled, REQUEST, css='form-element'):
    return self.f_selectInput(self,fmName=fmName,elName=elName,value=value,type=inputtype,lang_str=lang_str,required=required,optpl=optpl,enabled=enabled,css=css,REQUEST=REQUEST)


  # ----------------------------------------------------------------------------
  # 	getCheckbox:
  #
  #	@param fmName
  #	@param elName
  #	@param value
  #	@param enabled
  #	@param hidden           Add hidden Input-Field if not enabled
  #	@param REQUEST  	Http-Request
  #	@param css		CSS-Class
  #	@param extra		Extra-Parameters
  #	@return String
  # ----------------------------------------------------------------------------
  def getCheckbox(self, fmName, elName, value, enabled=True, hidden=True, REQUEST=None, css='form-checkbox', extra=''):
    html = []
    checked = str(value) == '1'
    if elName.find(':int') > 0 and value in [True, False]:
      value = int(value)
    html.append('<input ')
    html.append(' type="hidden"')
    html.append(' id="%s"'%elName)
    html.append(' name="%s"'%elName)
    html.append(' value="%s"'%str(value))
    html.append(' />')
    html.append('<input ')
    html.append(' class="%s"'%css)
    html.append(' type="checkbox"')
    if not enabled:
      html.append(' disabled="disabled"')
    if checked: 
      html.append(' checked="checked"')
    html.append(' onclick="if (this.checked) { this.form.elements[\'%s\'].value=1; } else {this.form.elements[\'%s\'].value=0;};"'%(elName,elName))
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
  def getTextArea(self, fmName, elName, cols, rows, value, enabled, REQUEST, css='form-element', wrap='virtual', extra=''):
    html = []
    html.append('<textarea ')
    html.append(' class="%s"'%css)
    html.append(' id="%s"'%elName)
    html.append(' name="%s"'%elName)
    html.append(' cols="%i"'%cols)
    html.append(' rows="%i"'%rows)
    html.append(' wrap="%s"'%wrap)
    if extra.find('style=') < 0:
      styles = []
      styles.append( 'width:%iem;'%cols)
      html.append(' style="%s"'%(';'.join(styles)))
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
        ref_obj = self
        for el in href.split( '/'):
          if ref_obj is not None:
            if el == '..':
              ref_obj = ref_obj.aq_parent
            elif len( el) > 0:
              ref_obj = getattr( ref_obj, el, None)
        if ref_obj is None:
          ref_url = '{$__' + href.split( '/')[ -1] + '__}'
          inline_links.append( ref_url)
        else:
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
            html.append('<img src="%sinternal_link.gif" title="" border="0" align="absmiddle"/> %s'%(self.MISC_ZMS,ref_obj.f_breadcrumbs(objectPathElements=ref_obj.breadcrumbs_obj_path(),no_icon=1,lang=REQUEST['lang'],REQUEST=REQUEST)))
          else:
            html.append('<img src="%sinternal_link_broken.gif" title="" border="0" align="absmiddle"/> %s'%(self.MISC_ZMS,ref_url))
          html.append('</div>')
          html.append('</div>')
        html.append('</td>')
        html.append('</tr>')
        html.append('</table>')
    return ''.join(html)

################################################################################
