################################################################################
# _deprecated.py
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
import warnings
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Product Imports.
import _globals
import _zreferableitem


# ------------------------------------------------------------------------------
#  getLinkList_ZMSLinkElement:
#
#  Returns list of URLs of links.
# ------------------------------------------------------------------------------
def getLinkList_ZMSLinkElement(self, REQUEST=None, allow_none=0):
  value = []
  ref = self.getObjAttrValue(self.getObjAttr('attr_ref'),REQUEST)
  dct = {}
  dct['dst'] = self.getLinkObj(ref,REQUEST)
  dct['url'] = self.getLinkUrl(ref,REQUEST)
  dct['title'] = self.getObjProperty('title',REQUEST)
  dct['description'] = self.getObjProperty('attr_dc_description',REQUEST)
  dct['internal'] = _zreferableitem.isInternalLink(ref)
  if dct['url'] is not None or allow_none:
    value.append(dct)
  return value


################################################################################
################################################################################
###
###   class DeprecatedAPI:
###
################################################################################
################################################################################
class DeprecatedAPI:

  f_bo_area = '' 
  f_eo_area = '' 
  f_submitBtn = '' 
  def f_bodyContent(self, *args, **kwargs):
    request = self.REQUEST 
    response = request.RESPONSE
    return self.getBodyContent(request)
  def zmi_form_section_begin(self, *args, **kwargs):
    return ''
  def zmi_form_section_end(self, *args, **kwargs):
    return ''
  def f_selectInput(self, *args, **kwargs):
    return here.getSelect(fmName=kwargs['fmName'],elName=kwargs['elName'],value=kwargs['value'],inputtype=kwargs['inputtype'],lang_str=kwargs['lang_str'],required=kwargs['required'],optpl=kwargs['optpl'],enabled=kwargs['enabled'],REQUEST=self.REQUEST)

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.f_headline
  # ----------------------------------------------------------------------------
  def f_headline(self, *args, **kwargs):
    warnings.warn('Using <%s @ %s>.f_headline is deprecated.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return '<h2>%s</h2><div>%s</div>'%(kwargs.get('headline',''),kwargs.get('extra','')) 

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getTitleimage
  # ----------------------------------------------------------------------------
  def getTitleimage( self, REQUEST): 
    warnings.warn('Using <%s @ %s>.getTitleimage(REQUEST) is deprecated.'
                 ' Use getObjProperty(\'titleimage\',REQUEST) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.getObjProperty('titleimage',REQUEST) 

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getImage
  # ----------------------------------------------------------------------------
  def getImage(self,REQUEST):
    warnings.warn('Using <%s @ %s>.getImage(REQUEST) is deprecated.'
                 ' Use getObjProperty(\'img\',REQUEST) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.getObjProperty('img',REQUEST)

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getFile
  # ----------------------------------------------------------------------------
  def getFile(self,REQUEST):
    warnings.warn('Using <%s @ %s>.getFile(REQUEST) is deprecated.'
                 ' Use getObjProperty(\'file\',REQUEST) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.getObjProperty('file',REQUEST)

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getFormat
  # ----------------------------------------------------------------------------
  def getFormat(self,REQUEST):
    print "[getFormat]: @deprecated: returns \"getObjProperty('format',REQUEST)\" for compatibility reasons!"
    return self.getObjProperty('format',REQUEST)

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getLinkList: 
  #
  #  Returns list of URLs of links.
  # ----------------------------------------------------------------------------
  def getLinkList(self, REQUEST=None, allow_none=0):
      value = []
      if self.meta_id == 'ZMSLinkElement' and self.getObjProperty('align',REQUEST) in ['','NONE']:
        if self.isEmbedded(REQUEST):
          if self.isPage():
            ref_obj = self.getRefObj()
            if ref_obj is not None:
              value.extend( ref_obj.getLinkList( REQUEST, allow_none))
        else:
          value.extend( getLinkList_ZMSLinkElement( self, REQUEST, allow_none))
      else:
        for ob in self.filteredChildNodes(REQUEST,['ZMSFile','ZMSLinkContainer','ZMSLinkElement']):
          if ob.meta_id == 'ZMSLinkContainer':
            for sub_ob in ob.filteredChildNodes(REQUEST,['ZMSLinkElement']):
              value.extend( getLinkList_ZMSLinkElement( sub_ob, REQUEST, allow_none))
          elif ob.meta_id == 'ZMSFile' and ob.getObjProperty('align',REQUEST) in ['','NONE']:
            f = ob.getFile(REQUEST)
            if f:
              dct = {}
              dct['dst'] = ob
              dct['url'] = f.getHref(REQUEST)
              dct['title'] = ob.getTitle(REQUEST)
              dct['description'] = _globals.nvl(ob.getObjProperty('attr_dc_description',REQUEST),'')
              dct['internal'] = 1
              value.append(dct)
          elif ob.meta_id == 'ZMSLinkElement' and ob.getObjProperty('align',REQUEST) in ['','NONE']:
            if not ob.isEmbedded(REQUEST):
              value.extend( getLinkList_ZMSLinkElement( ob, REQUEST, allow_none))
      return value

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.getLinkHtml:
  #
  #  Resolves internal/external links and returns Html.
  # ----------------------------------------------------------------------------
  def getLinkHtml( self, url, html='<a href="%s">&raquo;</a>', REQUEST=None):
    print "[getLinkHtml]: @deprecated: use own implementation!"
    REQUEST = _globals.nvl( REQUEST, self.REQUEST)
    s = ''
    ob = self
    while ob is not None:
      if html in ob.getMetaobjIds( sort=0):
        metaObj = ob.getMetaobj( html)
        metaObjAttr = ob.getMetaobjAttr( metaObj['id'], 'getLinkHtml',syncTypes=['*'])
        if type(metaObjAttr) is dict:
          REQUEST.set( 'ref_id', url)
          return self.dt_exec( metaObjAttr['custom'])
      ob = self.getPortalMaster()
    ob = self.getLinkObj(url,REQUEST)
    if ob is not None:
      if ob.isActive(REQUEST) and \
         ob.isVisible(REQUEST):
        url = ob.getHref2IndexHtml(REQUEST)
        s = html%url
    return s

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.meta_id_or_type:
  # ----------------------------------------------------------------------------
  def meta_id_or_type(self):
    print "[meta_id_or_type]: @deprecated: use meta_id!"
    return self.meta_id

  # ----------------------------------------------------------------------------
  #  DeprecatedAPI.absolute_obj_path:
  # ----------------------------------------------------------------------------
  def absolute_obj_path(self):
    print "[absolute_obj_path]: @deprecated!"
    ob = self.getDocumentElement()
    return '%s/%s/'%(ob.aq_parent.id,self.absolute_url()[len(ob.aq_parent.absolute_url())+1:])

  # --------------------------------------------------------------------------
  #  DeprecatedAPI.pil_img_*:
  # --------------------------------------------------------------------------
  def createThumbnail( self, img, maxdim=100, qual=75):
    """
    Creates thumbnail of given image.
    @param img: Image
    @type img: C{MyImage}
    @param qual: JPEG quality (default: 75)
    @type qual: C{int}
    @return: Thumbnail
    @rtype: C{MyImage}
    """
    warnings.warn('Using <%s @ %s>.createThumbnail(...) is deprecated.'
                 ' Use pilutil().thumbnail(...) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.pilutil().thumbnail( img, maxdim, qual)

  def pil_img_resize( self, img, size, mode='resize', sffx='_thumbnail', qual=75):
    """
    Returns a resized copy of an image. The size argument gives the requested
    size in pixels, as a 2-tuple: (width, height).
    @param img: Image
    @type img: C{MyImage}
    @param size: Size 2-tuple: (width, height)
    @type size: C{tuple}
    @param mode: Mode
    @type mode: C{string}
    @param qual: JPEG quality (default: 75)
    @type qual: C{int}
    @return: Resized image
    @rtype: C{MyImage}
    """
    warnings.warn('Using <%s @ %s>.pil_img_resize(...) is deprecated.'
                 ' Use pilutil().resize(...) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.pilutil().resize( img, size, mode, sffx, qual)

  def pil_img_crop( self, img, box, qual=75):
    """
    Returns a rectangular region from the current image. The box is a 4-tuple 
    defining the left, upper, right, and lower pixel coordinate.
    @param img: Image
    @type img: C{MyImage}
    @param box Box 4-tuple: (left, upper, right, bottom)
    @param qual: JPEG quality (default: 75)      
    @type box: C{tuple}
    @return: Cropped image
    @rtype: C{MyImage}
    """
    warnings.warn('Using <%s @ %s>.pil_img_crop(...) is deprecated.'
                 ' Use pilutil().crop(...) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.pilutil().crop( img, box, qual)

  def pil_img_rotate( self, img, direction, qual=75):
    """
    Returns rotated version of the current image. Direction is a simple string 
    defining either left (=90 degree rotation clockwise), right (-90 degree) or 180.
    @param img: Image
    @type img: C{MyImage}
    @param direction string: left, right, 180
    @param qual: JPEG quality (default: 75)
    @type box: C{string}
    @return: Rotated image
    @rtype: C{MyImage}
    """
    warnings.warn('Using <%s @ %s>.pil_img_rotate(...) is deprecated.'
                 ' Use pilutil().rotate(...) instead.'%(self.meta_id,self.absolute_url()),
                   DeprecationWarning, 
                   stacklevel=2)
    return self.pilutil().rotate( img, direction, qual)

################################################################################
