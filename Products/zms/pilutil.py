"""
pilutil.py

Provides enabled, generate_preview, thumbnail helper functions for image processing and PIL/Pillow operations.
It resizes images, applies filters, generates thumbnails, and manipulates image metadata.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
import tempfile
# Product Imports.
from Products.zms import _fileutil
from Products.zms import standard
from Products.zms import svgutil

security = ModuleSecurityInfo('Products.zms.pilutil')

security.declarePublic('enabled')
def enabled():
  """Return whether Pillow is available in the current runtime."""
  try:
    from PIL import Image
    return True
  except:
    return False

security.declarePublic('generate_preview')
def generate_preview(self, hiresKey, loresKey, maxdim):
  """
  Generate and persist a low-resolution preview image from a hi-res source.

  The method reads object properties, derives a thumbnail via L{thumbnail}, and
  stores both low-res and hi-res values back into object properties.
  """
  request = self.REQUEST
  lang = request['lang']
  hires = self.attr(hiresKey)
  lores = self.attr(loresKey)
  if hires is None and lores is not None:
    if lores.getWidth() > int(maxdim):
      hires = lores
  if hires is not None:
    thumb = thumbnail( hires, int(maxdim))
    self.setObjProperty(loresKey,thumb,lang)
    self.setObjProperty(hiresKey,hires,lang)


security.declarePublic('thumbnail')
def thumbnail(img, maxdim, qual=75):
  """
  Tumbnail image.
  @rtype: C{MyImage}
  """
  # Resize image
  context = img.aq_parent
  size = (maxdim, maxdim)
  thumb = resize( img, size, mode='thumbnail', qual=qual)
  
  # Returns resulting image
  image = standard.ImageFromData(context, thumb.getData(), thumb.getFilename())
  return image


security.declarePublic('resize')
def resize(img, size, mode='resize', sffx='_thumbnail', qual=75):
  """
  Resize image.
  @rtype: C{MyImage}
  """
  from PIL import Image, ImageFile
  ImageFile.LOAD_TRUNCATED_IMAGES = True
  
  # Save image in temp-folder
  context = img.aq_parent
  tempfolder = tempfile.mkdtemp()
  filepath = _fileutil.getOSPath('%s/%s'%(tempfolder, img.filename))
  _fileutil.exportObj(img, filepath)
  
  # Resize SVG
  svg_dim = svgutil.get_dimensions(img)
  if svg_dim is not None:
    img = svgutil.set_dimensions(img,size)
    f = open(filepath, 'wb')
    f.write(img.getData())
    f.close()
  
  # Resize image
  else:
    im = Image.open(filepath)
    im = im.convert('RGB')
    maxdim = max(list(size))
    if mode == 'thumbnail':
      try:
        im.thumbnail((maxdim, maxdim), Image.ANTIALIAS)
      except:
        im.thumbnail((maxdim, maxdim))
    elif mode == 'resize':
      try:
        im = im.resize(size, Image.ANTIALIAS)
      except:
        im = im.resize(size)
    elif mode == 'square':
      try:
        width, height = im.size
        dst_width, dst_height = maxdim, maxdim
        if width > height:
          delta = width - height
          left = int(delta/2)
          upper = 0
          right = height + left
          lower = height
        else:
          delta = height - width
          left = 0
          upper = int(delta/2)
          right = width
          lower = width + upper
        im = im.crop(( left, upper, right, lower))
        im = im.resize((dst_width, dst_height), Image.ANTIALIAS)
      except:
        im.resize(size)
    im.convert('RGB').save(filepath, "JPEG", quality=qual, optimize=True)
  
  # Read resized image from file-system
  f = open(filepath, 'rb')
  result_data = f.read()
  f.close()
  
  # Remove temp-folder and images
  _fileutil.remove(tempfolder, deep=1)
  
  thumb_sffx = str(sffx)
  getfilename = _fileutil.extractFilename(filepath).split('.')
  filename = getfilename[0:-1]
  filename = ".".join(filename)
  filename = filename.replace('.', '_')
  extension = _fileutil.extractFileExt(filepath)
  result_filename = filename + thumb_sffx + '.' + extension
  result = {'data':result_data,'filename':result_filename}
  
  # Returns resulting image
  image = standard.ImageFromData(context, result['data'], result['filename'])
  return image


security.declarePublic('crop')
def crop(img, box, qual=75):
  """
  Crop image.
  @rtype: C{MyImage}
  """
  from PIL import Image, ImageFile
  ImageFile.LOAD_TRUNCATED_IMAGES = True
  
  # Save image in temp-folder
  context = img.aq_parent
  tempfolder = tempfile.mkdtemp()
  filepath = _fileutil.getOSPath('%s/%s'%(tempfolder, img.filename))
  _fileutil.exportObj(img, filepath)
  
  # Crop image
  im = Image.open(filepath)
  im = im.crop(box)
  im.convert('RGB').save(filepath, "JPEG", quality=qual)
  
  # Read resized image from file-system
  f = open(filepath, 'rb')
  result_data = f.read()
  result_filename = _fileutil.extractFilename(filepath)
  result = {'data':result_data,'filename':result_filename}
  f.close()
  
  # Remove temp-folder and images
  _fileutil.remove(tempfolder, deep=1)
  
  # Returns resulting image
  image = standard.ImageFromData(context, result['data'], result['filename'])
  return image


security.declarePublic('rotate')
def rotate(img, direction, qual=75):
  """
  Rotate image.
  """
  from PIL import Image, ImageFile
  ImageFile.LOAD_TRUNCATED_IMAGES = True
  
  # Save image in temp-folder
  context = img.aq_parent
  tempfolder = tempfile.mkdtemp()
  filepath = _fileutil.getOSPath('%s/%s'%(tempfolder, img.filename))
  _fileutil.exportObj(img, filepath)
  
  # Rotate image
  im = Image.open(filepath)
  im = im.rotate(direction)
  im.convert('RGB').save(filepath, "JPEG", quality=qual, optimize=True)
  
  # Read rotated image from file-system
  f = open(filepath, 'rb')
  data = f.read()
  result_filename = _fileutil.extractFilename(filepath)
  result = {'data':data,'filename':img.filename}
  f.close()
  
  # Remove temp-folder and images
  _fileutil.remove(tempfolder, deep=1)
  
  # Returns resulting image
  image = standard.ImageFromData(context, result['data'], result['filename'])
  return image


security.declarePublic('optimize')
def optimize(img, qual=75):
  """
  Optimize image.
  @rtype: C{MyImage}
  """
  from PIL import Image, ImageFile
  ImageFile.LOAD_TRUNCATED_IMAGES = True
  
  # Save image in temp-folder
  context = img.aq_parent
  tempfolder = tempfile.mkdtemp()
  filepath = _fileutil.getOSPath('%s/%s'%(tempfolder, img.filename))
  _fileutil.exportObj(img, filepath)
  
  # Resize image
  im = Image.open(filepath)
  im = im.convert('RGB')
  im.convert('RGB').save(filepath, "JPEG", quality=qual, optimize=True)
  
  # Read optimized image from file-system
  f = open(filepath, 'rb')
  data = f.read()
  result = {'data':data,'filename':img.filename}
  f.close()
  
  # Remove temp-folder and images
  _fileutil.remove(tempfolder, deep=1)
  
  # Returns resulting image
  image = standard.ImageFromData(context, result['data'], result['filename'])
  return image


security.apply(globals())

