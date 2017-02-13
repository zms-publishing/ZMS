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

# Product Imports.
import standard

def warn(self,old,new=None):
  import warnings
  warnings.warn('Using <%s@%s>.%s() is deprecated.'
               ' Use %s() instead.'%(self.meta_id,self.absolute_url(),old,[old,new][new is not None]),
                 DeprecationWarning, 
                 stacklevel=2)

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
    warn(self,'f_bodyContent','None')
    request = self.REQUEST 
    response = request.RESPONSE
    return self.getBodyContent(request)

  def zmi_form_section_begin(self, *args, **kwargs):
    warn(self,'zmi_form_section_begin','None')
    return ''

  def zmi_form_section_end(self, *args, **kwargs):
    warn(self,'zmi_form_section_end','None')
    return ''

  def f_selectInput(self, *args, **kwargs):
    warn(self,'f_selectInput','getSelect')
    return here.getSelect(fmName=kwargs['fmName'],elName=kwargs['elName'],value=kwargs['value'],inputtype=kwargs['inputtype'],lang_str=kwargs['lang_str'],required=kwargs['required'],optpl=kwargs['optpl'],enabled=kwargs['enabled'],REQUEST=self.REQUEST)

  def f_headline(self, *args, **kwargs):
    warn(self,'f_headline','None')
    return '<h2>%s</h2><div>%s</div>'%(kwargs.get('headline',''),kwargs.get('extra','')) 

  def getTitleimage( self, REQUEST): 
    warn(self,'getTitleimage(REQUEST)','attr(\'titleimage\')')
    return self.getObjProperty('titleimage',REQUEST) 

  def getImage(self,REQUEST):
    warn(self,'getImage(REQUEST)','attr(\'img\')')
    return self.getObjProperty('img',REQUEST)

  def getFile(self,REQUEST):
    warn(self,'getFile(REQUEST)','attr(\'file\')')
    return self.getObjProperty('file',REQUEST)

  def getFormat(self,REQUEST):
    warnings.warn("[getFormat]: @deprecated: returns \"getObjProperty('format',REQUEST)\" for compatibility reasons!")
    return self.getObjProperty('format',REQUEST)

  def meta_id_or_type(self):
    warn(self,'meta_id_or_type','meta_id')
    return self.meta_id

  def absolute_obj_path(self):
    warn(self,'absolute_obj_path','None')
    ob = self.getDocumentElement()
    return '%s/%s/'%(ob.aq_parent.id,self.absolute_url()[len(ob.aq_parent.absolute_url())+1:])

  """
  Resolves internal/external links and returns Html. 
  """
  def getLinkHtml( self, url, html='<a href="%s">&raquo;</a>', REQUEST=None): 
    warn(self,'getLinkHtml','@deprecated: use own implementation!')
    REQUEST = standard.nvl( REQUEST, self.REQUEST) 
    s = '' 
    ob = self 
    while ob is not None: 
      if html in ob.getMetaobjIds(): 
        metaObj = ob.getMetaobj( html) 
        metaObjAttr = ob.getMetaobjAttr( metaObj['id'], 'getLinkHtml') 
        if type(metaObjAttr) is dict: 
          REQUEST.set( 'ref_id', url) 
          return self.dt_exec( metaObjAttr['custom']) 
      ob = ob.getPortalMaster() 
    ob = self.getLinkObj(url) 
    if ob is not None: 
      if ob.isActive(REQUEST) and \
         ob.isVisible(REQUEST): 
        url = ob.getHref2IndexHtml(REQUEST) 
        s = html%url 
    return s 

  # --------------------------------------------------------------------------
  #  DeprecatedAPI.pil_img_*:
  # --------------------------------------------------------------------------
  """
  Creates thumbnail of given image.
  @param img: Image
  @type img: C{MyImage}
  @param qual: JPEG quality (default: 75)
  @type qual: C{int}
  @return: Thumbnail
  @rtype: C{MyImage}
  """
  def createThumbnail( self, img, maxdim=100, qual=75):
    warn(self,'createThumbnail','pilutil().thumbnail')
    return self.pilutil().thumbnail( img, maxdim, qual)

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
  def pil_img_resize( self, img, size, mode='resize', sffx='_thumbnail', qual=75):
    warn(self,'pil_img_resize','pilutil().resize')
    return self.pilutil().resize( img, size, mode, sffx, qual)

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
  def pil_img_crop( self, img, box, qual=75):
    warn(self,'pil_img_crop','pilutil().crop')
    return self.pilutil().crop( img, box, qual)

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
  def pil_img_rotate( self, img, direction, qual=75):
    warn(self,'pil_img_rotate','pilutil().rotate')
    return self.pilutil().rotate( img, direction, qual)


  # --------------------------------------------------------------------------
  #  DeprecatedAPI.ZCatalogItem:
  # --------------------------------------------------------------------------
  def search_quote(self, s, maxlen=255, tag='&middot;'):
    warn(self,'search_quote','Products.zms.standard.string_maxlen')
    return standard.string_maxlen(s,maxlen,etc=tag*3)

  def search_encode(self, s):
    warn(self,'search_encode','Products.zms.standard.umlaut_quote')
    return standard.umlaut_quote(self, s)

  def getCatalogNavUrl(self, REQUEST):
    warn(self,'getCatalogNavUrl','None')
    return self.url_inherit_params(REQUEST['URL'],REQUEST,['qs'])


  # --------------------------------------------------------------------------
  #  DeprecatedAPI.ZMSGlobals:
  # --------------------------------------------------------------------------
  """
  Replace special characters in string for javascript.
  """
  def js_quote(self, text, charset=None):
    warn(self,'js_quote','None')
    if type(text) is unicode:
      text= text.encode([charset, 'utf-8'][charset==None])
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    text = text.replace('"', '\\"').replace("'", "\\'")
    return text

  """
  Parses default-stylesheet and returns elements.
  @deprecated
  @return: Elements
  @rtype: C{dict}
  """
  def parse_stylesheet(self):
    warn(self,'parse_stylesheet','None')
    stylesheet = self.getStylesheet()
    if stylesheet.meta_type in ['DTML Document','DTML Method']:
      data = stylesheet.raw
    elif stylesheet.meta_type in ['File']:
      data = stylesheet.data
    data = re.sub( '/\*(.*?)\*/', '', data)
    value = {}
    for elmnt in data.split('}'):
      i = elmnt.find('{')
      keys = elmnt[:i].strip()
      v = elmnt[i+1:].strip()
      for key in keys.split(','):
        key = key.strip()
        if len(key) > 0:
          value[key] = value.get(key,'') + v
    colormap = {}
    for key in value.keys():
      if key.startswith('.') and \
         key.find('Color') > 0 and \
         key.find('.cms') < 0 and \
         key.find('.zmi') < 0:
        for elmnt in value[key].split(';'):
          i = elmnt.find(':')
          if i > 0:
            elmntKey = elmnt[:i].strip().lower()
            elmntValue = elmnt[i+1:].strip().lower()
            if elmntKey == 'color' or elmntKey == 'background-color':
              colormap[key[1:]] = elmntValue
    self.setConfProperty('ZMS.colormap',colormap)
    return colormap

  def get_colormap(self):
    warn(self,'get_colormap','None')
    colormap = self.getConfProperty('ZMS.colormap',None)
    if colormap is None:
      try:
        colormap = self.parse_stylesheet()
      except:
        # Destroy Colormap on Error
        colormap = {}
        self.setConfProperty('ZMS.colormap',colormap)
    return colormap

  def string_maxlen(self, s, maxlen=20, etc='...', encoding=None):
    warn(self,'string_maxlen','Products.zms.standard.string_maxlen')
    return standard.string_maxlen(s,maxlen,etc,encoding)

  def http_import(self, url, method='GET', auth=None, parse_qs=0, timeout=10, headers={'Accept':'*/*'}):
    warn(self,'http_import','Products.zms.standard.http_import')
    return standard.http_import( self, url, method=method, auth=auth, parse_qs=parse_qs, timeout=timeout, headers=headers)

  def get_id_prefix(self, s):
    warn(self,'get_id_prefix','Products.zms.standard.id_prefix')
    return standard.id_prefix(s)

  def parseLangFmtDate(self, s, lang=None, fmt_str=None, recflag=None):
    warn(self,'parseLangFmtDate','Products.zms.standard.parseLangFmtDate')
    return standard.parseLangFmtDate(s)

  def compareDate(self, t0, t1):
    warn(self,'compareDate','Products.zms.standard.compareDate')
    return standard.compareDate(t0, t1) 

  def daysBetween(self, t0, t1):
    warn(self,'daysBetween','Products.zms.standard.daysBetween')
    return standard.daysBetween(t0, t1) 

  def re_sub( self, pattern, replacement, subject, ignorecase=False):
    warn(self,'re_sub','Products.zms.standard.re_sub')
    return standard.re_sub(pattern, replacement, subject, ignorecase)

  def re_search( self, pattern, subject, ignorecase=False):
    warn(self,'re_search','Products.zms.standard.re_search')
    return standard.re_search(pattern, subject, ignorecase)

  def re_findall( self, pattern, text, ignorecase=False):
    warn(self,'re_findall','Products.zms.standard.re_findall')
    return standard.re_findall(pattern, text, ignorecase)