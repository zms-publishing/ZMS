################################################################################
# _objtypes.py
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
from App.special_dtml import HTMLFile
# Product Imports.
import _confmanager
import _fileutil
import _globals
import _zreferableitem


# ------------------------------------------------------------------------------
#  _objtypes.getHref2Zoom:
# ------------------------------------------------------------------------------
def getHref2Zoom(self, img, REQUEST):
  m = getattr( self, 'getCustomHref2Zoom', None)
  if m is not None:
    href = m( self, img=img, REQUEST=REQUEST)
  else:
    href = img.getHref(REQUEST)
  return href


class ObjTypes:

    # Repetitive (Files/Images).
    # --------------------------
    f_selectRepetitive = HTMLFile('dtml/objattrs/f_select_repetitive', globals())

    # Autocomplete.
    # -------------
    f_selectAutocomplete = HTMLFile('dtml/objattrs/f_select_autocomplete', globals())

    # String, Text, Select, Multiple-Select.
    # --------------------------------------
    f_selectInput = HTMLFile('dtml/objattrs/f_select_input', globals())

    # Textformat.
    # -----------
    f_selectTextformat = HTMLFile('dtml/objattrs/f_select_textformat', globals())

    # Richtext.
    # ---------
    f_selectRichtext = HTMLFile('dtml/objattrs/f_select_richtext', globals())
    f_xstandard_styles = HTMLFile('dtml/objattrs/f_xstandard_styles', globals())
    f_xstandard_css = HTMLFile('dtml/objattrs/f_xstandard_css', globals())

    # Object.
    # -------
    f_selectObject = HTMLFile('dtml/objattrs/f_select_object', globals()) 

    # File.
    # -----
    f_selectFile = _confmanager.ConfDict.template('objattrs/f_select_file') 

    # Image.
    # ------
    f_selectImage = _confmanager.ConfDict.template('objattrs/f_select_image') 

    # Alignment.
    # ----------
    f_selectAlign = HTMLFile('dtml/objattrs/f_select_align', globals())

    # Colors.
    # -------
    f_selectColor = HTMLFile('dtml/objattrs/f_select_color', globals())

    # Character-Format.
    # -----------------
    f_selectCharformat = HTMLFile('dtml/objattrs/f_select_charformat', globals())

    # Displaytype.
    # ------------
    f_selectDisplaytype = HTMLFile('dtml/objattrs/f_select_displaytype', globals())

    ############################################################################
    #  dctDisplaytype :
    #         
    #  Dictionary of display-types. 
    ############################################################################
    dctDisplaytype = {
	'1':'left',
	'2':'top',
	'3':'bottom',
	'4':'right',
	'5':'left',		# 'floatbefore'
	'6':'right',		# 'floatafter'
	'7':'left',		# 'behindtext'
	}


    ############################################################################
    #  ObjTypes.renderDisplaytype:
    #
    #  HTML presentation of Image and Text.
    #
    #  Parameters:
    #    IN:  @self          <Object>
    #         @displaytype   <String>
    #         @imgattr       Object-Attribute <String>
    #         @imghiresattr  Object-Attribute (High-Resolution) <String> 
    #         @imgurl        URL for Image
    #         @imgthumb      Display image as thumbnail (width limited to 365 pixel)
    #         @imgspecial    Special Attributes (for <img>-Tag, e.g. usemap)
    #         @imgclass      CSS Image-Class
    #         @text          String-Object
    #         @textalign     Text-Alignment (Left, Right, Center)
    #         @textclass     CSS Text-Class
    #         @REQUEST       Request-Object
    #    OUT: <html>         String-Object
    ############################################################################
    def renderDisplaytype(self, displaytype, \
      imgattr, imghiresattr, imgurl, imgthumb, imgspecial, imgclass, \
      text, textalign, textclass, REQUEST):
      
      align = self.getObjProperty('align',REQUEST)
      
      # Export-Format.
      if REQUEST.has_key('export_format'):
        try:
          export_format = int( REQUEST.get('export_format'))
        except:
          displaytype = 'export_format'
      
      # Image.
      # ------
      img = self.getObjProperty(imgattr,REQUEST)
      imghires = None
      if imghiresattr is not None:
        imghires = self.getObjProperty(imghiresattr,REQUEST)
        if imghires is not None and displaytype == 'export_format':
          img = imghires
          imgattr = imghiresattr
          imghires = None
          imghiresattr = None
      
      imgtag = ''
      imgzoom = ''
      
      #-- IMAGE-PROPERTIES 
      if img is None or img.get_real_size() == 0:
        width = ''
        height = ''
        
        # Image (HiRes).
        # --------------
        if imghires is not None and imghires.get_real_size() != 0:
          s_url = getHref2Zoom(self,imghires,REQUEST)
          imgtag = ''
          imgtag += '<div class="caption">'
          imgtag += '<a href="%s"><img src="%smime_type.image_basic.gif" title="%s" border="0" align="middle" /></a>&nbsp;'%(s_url,self.MISC_ZMS,imghires.getContentType())
          imgtag += '<a href="%s">%s</a>&nbsp;'%(s_url,imghires.filename)
          imgtag += '<b>(%s)</b>'%self.getDataSizeStr(imghires.get_size())
          imgtag += '</div>'
          
      else:
        imgzoomattr = ''
        
        # Dimensions.
        # -----------
        width = ''
        height = ''
        try:
          max_width = self.getConfProperty('ZMSGraphic.zmi_max_width',480)
          i_height = int(img.height)
          i_width = int(img.width)
          if imgthumb and i_width > max_width:
            i_height = int(max_width*i_height/i_width)
            i_width = max_width
            imgzoomobj = img
            imgzoomattr = imgattr
          height = str(i_height)+'px'
          width = str(i_width)+'px'
          try:
            px2em = float(self.getConfProperty('ZMSGraphic.px2em',''))
            height = str(i_height/px2em)+'em'
            width = str(i_width/px2em)+'em'
          except:
            pass
        except:
          pass
        
        # Image (HiRes).
        # --------------
        if not (imghires is None or imghires.get_real_size() == 0):
          imgzoomobj = imghires
          imgzoomattr = imghiresattr 
        
        # Assemble img-tag.
        imgsrc = img.getHref(REQUEST)
        imgtag = '<img'
        imgtag += ' src="%s"'%imgsrc
        imgtag += ' style="'
        if displaytype != 'export_format':
          if width != '': 
            imgtag += 'width:%s;'%width
          if height != '': 
            imgtag += 'height:%s;'%height
        imgtag += 'display:block;'
        imgtag += '"'
        if imgclass is not None and len(imgclass) > 0:
          imgtag += ' class="%s"'%imgclass
        if imgspecial is not None and len(imgspecial) > 0: 
          imgtag += ' %s'%imgspecial
        imgtag += ' />'
        
        # Image-Url.
        # ----------
        if imgurl is not None and len(imgurl) > 0:
          imgtarget = ''
          if not (imgurl.startswith('/') or imgurl.startswith('.') or imgurl.startswith( REQUEST[ 'BASE0'])):
            imgtarget = ' target="_blank"'
          imgtag = '<a href="%s"%s>%s</a>'%( imgurl, imgtarget, imgtag)
        
        # Zoom (HiRes).
        # -------------
        elif len(imgzoomattr) > 0:
          
          # Zoom (SuperRes).
          # ----------------
          key = 'imgsuperres'
          if key in self.getObjAttrs().keys() and self.getConfProperty('ZMSGraphic.superres',0)==1:
            imgsuperzoomobj = self.getObjProperty(key,REQUEST)
            if imgsuperzoomobj is not None:
              s_url = getHref2Zoom(self,imgzoomobj,REQUEST)
              imgzoomclazz = 'zoom'
              imgzoomalt = '%s (%s)'%(self.getZMILangStr('BTN_ZOOM'),self.getDataSizeStr(imgzoomobj.get_size()))
              imgzoom += '<a href="%s" class="%s fancybox" target="_blank"><img class="%s" src="%s" title="%s" border="0" /></a>'%( s_url, imgzoomclazz, imgzoomclazz, self.spacer_gif, imgzoomalt)
              s_url = getHref2Zoom(self,imgsuperzoomobj,REQUEST)
              imgzoomclazz = 'superzoom'
              imgzoomalt = '%s (%s)'%(self.getZMILangStr('ATTR_SUPERRES'),imgsuperzoomobj.getDataSizeStr())
              imgzoom += '<a href="%s" class="%s" target="_blank"><img class="%s" src="%s" title="%s" border="0" /></a>'%( s_url, imgzoomclazz, imgzoomclazz, self.spacer_gif, imgzoomalt)
          
          # Image-Zoom.
          if imgzoom is not None and len(imgzoom) > 0:
            imgtag += imgzoom
          else:
            imgtag = '<a href="%s" class="fancybox">%s</a>'%(imgzoomobj.getHref(REQUEST),imgtag)
      
      # Build <html>-presentation.
      dtml = HTMLFile('dtml/objattrs/displaytype/displaytype_%s'%displaytype, globals())
      html = dtml(self 
          ,ob=self 
          ,img=imgtag 
          ,text=text 
          ,textalign=textalign
          ,textclass=textclass
          ,height=height
          ,width=width
          ,align=align
          ,float=align.find( '_FLOAT') >= 0
          ,REQUEST=REQUEST)
      
      # Return <html>-presentation.
      return html

################################################################################
