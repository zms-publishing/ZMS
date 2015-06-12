################################################################################
# _pilutil.py
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
import tempfile
# Product Imports.
import _fileutil


class pilutil:

  def __init__(self, context):
    self.context = context


  enabled__roles__ = None
  def enabled(self):
    try:
      from PIL import Image
      return True
    except:
      try:
        import Image
        return True
      except:
        return False


  thumbnail__roles__ = None
  def thumbnail(self, img, maxdim, qual=75):
    # Resize image
    size = (maxdim, maxdim)
    thumb = self.resize( img, size, mode='thumbnail', qual=qual)
    
    # Returns resulting image
    image = self.context.ImageFromData(thumb.getData(),thumb.getFilename())
    return image


  resize__roles__ = None
  def resize(self, img, size, mode='resize', sffx='_thumbnail', qual=75):
    """
    Resize image.
    """
    try:
      from PIL import Image
    except:
      import Image
    
    # Save image in temp-folder
    tempfolder = tempfile.mktemp()
    filepath = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
    _fileutil.exportObj(img,filepath)
    
    # Resize image
    im = Image.open(filepath)
    im = im.convert('RGB')
    maxdim = max(list(size))
    if mode == 'thumbnail':
      try:
        im.thumbnail((maxdim,maxdim),Image.ANTIALIAS)
      except:
        im.thumbnail((maxdim,maxdim))
        im.convert('RGB').save(infile,"JPEG", quality=qual)
    elif mode == 'resize':
      try:
        im = im.resize(size,Image.ANTIALIAS)
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
    im.convert('RGB').save(filepath,"JPEG", quality=qual)
    
    # Read resized image from file-system
    f = open(filepath,'rb')
    result_data = f.read()
    thumb_sffx = str(sffx)
    getfilename = _fileutil.extractFilename(filepath).split('.')
    filename = getfilename[0:-1]
    filename = ".".join(filename)
    filename = filename.replace('.','_')
    extension = _fileutil.extractFileExt(filepath)
    result_filename = filename + thumb_sffx + '.' + extension
    result = {'data':result_data,'filename':result_filename}
    f.close()
    
    # Remove temp-folder and images
    _fileutil.remove(tempfolder,deep=1)
    
    # Returns resulting image
    image = self.context.ImageFromData(result['data'],result['filename'])
    return image


  crop__roles__ = None
  def crop(self, img, box, qual=75):
    """
    Crop image.
    """
    try:
      from PIL import Image
    except:
      import Image
    
    # Save image in temp-folder
    tempfolder = tempfile.mktemp()
    filepath = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
    _fileutil.exportObj(img,filepath)
    
    # Crop image
    im = Image.open(filepath)
    im = im.crop(box)
    im.convert('RGB').save(filepath,"JPEG", quality=qual)
    
    # Read resized image from file-system
    f = open(filepath,'rb')
    result_data = f.read()
    result_filename = _fileutil.extractFilename(filepath)
    result = {'data':result_data,'filename':result_filename}
    f.close()
    
    # Remove temp-folder and images
    _fileutil.remove(tempfolder,deep=1)
    
    # Returns resulting image
    image = self.context.ImageFromData(result['data'],result['filename'])
    return image


  rotate__roles__ = None
  def rotate( self, img, direction, qual=75):
    """
    Rotate image.
    """
    try:
      from PIL import Image
    except:
      import Image
    
    # Save image in temp-folder
    tempfolder = tempfile.mktemp()
    filepath = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
    _fileutil.exportObj(img,filepath)
    
    # Rotate image
    im = Image.open(filepath)
    im = im.rotate(direction)
    im.convert('RGB').save(filepath,"JPEG", quality=qual)
    
    # Read resized image from file-system
    f = open(filepath,'rb')
    result_data = f.read()
    result_filename = _fileutil.extractFilename(filepath)
    result = {'data':result_data,'filename':result_filename}
    f.close()
    
    # Remove temp-folder and images
    _fileutil.remove(tempfolder,deep=1)
    
    # Returns resulting image
    image = self.context.ImageFromData(result['data'],result['filename'])
    return image

################################################################################