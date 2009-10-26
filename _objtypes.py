################################################################################
# _objtypes.py
#
# $Id: _objtypes.py,v 1.4 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.4 $
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
import _fileutil
import _globals
import  _zreferableitem


# ------------------------------------------------------------------------------
#  _objtypes.getHref2Zoom:
# ------------------------------------------------------------------------------
def getHref2Zoom(self, img, REQUEST):
  m = getattr( self, 'getCustomHref2Zoom', None)
  if m is not None:
    href = m( self, img=img, REQUEST=REQUEST)
  else:
    href = img.getHref(REQUEST)
    try:
      width = int(img.width)
      height = int(img.height)
      href = "javascript:open_function('%s',%i,%i,'')"%(href,width,height)
    except:
      pass
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

    # Object.
    # -------
    f_selectObject = HTMLFile('dtml/objattrs/f_select_object', globals()) 

    # File.
    # -----
    f_selectFile = HTMLFile('dtml/objattrs/f_select_file', globals()) 

    # Image.
    # ------
    f_selectImage = HTMLFile('dtml/objattrs/f_select_image', globals()) 

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
      
      #-- IMAGE-OBJECT  
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
      if img is None or img.get_size() == 0:
        width = ''
        height = ''
        
        # Image (HighRes).
        # ----------------
        if imghires is not None and imghires.get_size() != 0:
          s_url = getHref2Zoom(self,imghires,REQUEST)
          imgtag = ''
          imgtag += '<div class="caption">'
          imgtag += '<a href="%s"><img src="%smime_type.image_basic.gif" title="%s" border="0" align="middle" /></a>&nbsp;'%(s_url,self.MISC_ZMS,imghires.getContentType())
          imgtag += '<a href="%s">%s</a>&nbsp;'%(s_url,imghires.filename)
          imgtag += '<b>(%s)</b>'%imghires.getDataSizeStr()
          imgtag += '</div>'
          
      else:
        imgzoomattr = ''
        
        # Dimensions.
        # -----------
        width = ''
        height = ''
        try:
          max_width = self.getConfProperty('ZMSGraphic.zmi_max_width',360)
          i_width = int(img.width)
          i_height = int(img.height)
          if imgthumb and i_width > max_width:
            width = max_width
            height = int(max_width*i_height/i_width)
            imgzoomobj = img
            imgzoomattr = imgattr
          width = str(i_width)+'px'
          height = str(i_height)+'px'
          px2em = float(self.getConfProperty('ZMSGraphic.px2em',''))
          width = str(i_width/px2em)+'em'
          height = str(i_height/px2em)+'em'
        except:
          pass
        
        # Image (HighRes).
        # ----------------
        if not (imghires is None or imghires.get_size() == 0):
          imgzoomobj = imghires
          imgzoomattr = imghiresattr 
        
        # Zoom (Lupe).
        # ------------
        if len(imgzoomattr) > 0:
          s_url = getHref2Zoom(self,imgzoomobj,REQUEST)
          s_content_type = getattr(imgzoomobj,'content_type','')
          try:
            if int(imgzoomobj.width) or int(imgzoomobj.height): pass
            imgzoomclazz = 'zoom'
          except:
            imgzoomclazz = 'download'
          imgzoomalt = '%s (%s)'%(self.getZMILangStr('BTN_ZOOM'),imgzoomobj.getDataSizeStr())
          imgzoom += '<a href="%s" class="%s"><img class="%s" src="%s" title="%s" alt="%s" border="0" /></a>'%( s_url, imgzoomclazz, imgzoomclazz, self.spacer_gif, imgzoomalt, imgzoomalt)
          
          # Zoom (SuperRes).
          # ----------------
          key = 'imgsuperres'
          if key in self.getObjAttrs().keys() and self.getConfProperty('ZMSGraphic.superres',0)==1:
            imgzoomobj = self.getObjProperty(key,REQUEST)
            if imgzoomobj is not None:
              s_url = getHref2Zoom(self,imgzoomobj,REQUEST)
              imgzoomclazz = 'superzoom'
              imgzoomalt = '%s (%s)'%(self.getZMILangStr('ATTR_SUPERRES'),imgzoomobj.getDataSizeStr())
              imgzoom += '<a href="%s" class="%s"><img class="%s" src="%s" title="%s" alt="%s" border="0" /></a>'%( s_url, imgzoomclazz, imgzoomclazz, self.spacer_gif, imgzoomalt, imgzoomalt)
        
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
        
        # Image-URL.
        if imgurl is not None and len(imgurl) > 0:
          target = ''
          if imgurl is not None and not imgurl.find( REQUEST[ 'BASE0']) == 0:
            target = ' target="_blank"'
          imgtag = '<a href="%s"%s>%s</a>'%(imgurl,target,imgtag)
        
        # Image-Zoom.
        if imgzoom is not None and len(imgzoom) > 0:
          imgtag += imgzoom
      
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
