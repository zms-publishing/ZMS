################################################################################
# _pilutil.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
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
from App.Common import package_home
import os
import tempfile
# Product Imports.
import _fileutil


# ------------------------------------------------------------------------------
#  pil_command:
# ------------------------------------------------------------------------------
def pil_command( self, f):
  pythonpath = self.getConfProperty('InstalledProducts.pil.pythonpath','python')
  command = pythonpath+' '+_fileutil.getOSPath(package_home(globals())+'/conf/pil/%s'%f)
  return command


################################################################################
###
###  PIL (Python Imaging Library)
###
################################################################################

# ------------------------------------------------------------------------------
#  pil_img_conv:
#
#  Creates thumbnail of given image.
#  @param img
#  @return thumb
# ------------------------------------------------------------------------------
def pil_img_conv(self, img, maxdim=100, qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
  _fileutil.exportObj(img,filename)
  
  # Call PIL to generate thumbnail.
  command = pil_command(self,'img_conv.py')+' '+str(maxdim)+' '+filename+' '+str(qual)
  os.system(command)
  
  # Read thumbnail from file-system.
  lang_sffx = '_' + img.lang
  thumb_sffx = '_thumbnail'
  filename = filename[:-(len(_fileutil.extractFileExt(filename))+1)]
  f = open(filename + thumb_sffx + '.jpg','rb')
  thumb_data = f.read()
  thumb_filename = filename
  if len(thumb_filename)>len(lang_sffx) and \
     thumb_filename[-len(lang_sffx):]==lang_sffx:
    thumb_filename = thumb_filename[:-len(lang_sffx)]
  thumb_filename = _fileutil.extractFilename(thumb_filename + thumb_sffx + lang_sffx + '.jpg')
  thumb = {'data':thumb_data,'filename':thumb_filename}
  f.close()
    
  # Remove temp-folder and images.
  _fileutil.remove(tempfolder,deep=1)
  
  # Returns thumbnail.
  return thumb


# ------------------------------------------------------------------------------
#  pil_img_resize:
# ------------------------------------------------------------------------------
def pil_img_resize( self, img, size, mode='resize', sffx='_thumbnail', qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
  _fileutil.exportObj(img,filename)
  
  # Call PIL to generate resized image.
  command = pil_command(self,'img_resize.py')+' ' + str(size[0])+' '+str(size[1])+' '+filename+' '+mode+' '+str(qual)
  os.system(command)
  
  # Read resized image from file-system.
  
  if sffx == 'none':
    f = open(filename,'rb')
    resized_data = f.read()
    resized_filename = _fileutil.extractFilename(filename)
    resized = {'data':resized_data,'filename':resized_filename}
    f.close()
  else:
    # Read thumbnail from file-system.
    lang_sffx = '_' + img.lang
    thumb_sffx = str(sffx)
    newfilename = filename[:-(len(_fileutil.extractFileExt(filename))+1)]
    f = open(filename,'rb')
    thumb_data = f.read()
    thumb_filename = filename
    if len(thumb_filename)>len(lang_sffx) and \
       thumb_filename[-len(lang_sffx):]==lang_sffx:
      thumb_filename = thumb_filename[:-len(lang_sffx)]
    thumb_filename = _fileutil.extractFilename(newfilename + thumb_sffx + lang_sffx + '.jpg')
    resized = {'data':thumb_data,'filename':thumb_filename}
    f.close()
  
  # Remove temp-folder and images.
  _fileutil.remove(tempfolder,deep=1)
  
  # Returns resized image.
  return resized


# ------------------------------------------------------------------------------
#  pil_img_crop:
# ------------------------------------------------------------------------------
def pil_img_crop( self, img, box, qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
  _fileutil.exportObj(img,filename)
  
  # Call PIL to generate resized image.
  command = pil_command(self,'img_crop.py')+' '+str(box[0])+' '+str(box[1])+' '+str(box[2])+' '+str(box[3])+' '+filename+' '+str(qual)
  os.system(command)
  
  # Read resized image from file-system.
  f = open(filename,'rb')
  cropped_data = f.read()
  cropped_filename = _fileutil.extractFilename(filename)
  cropped = {'data':cropped_data,'filename':cropped_filename}
  f.close()
  
  # Remove temp-folder and images.
  _fileutil.remove(tempfolder,deep=1)
  
  # Returns cropped image.
  return cropped


# ------------------------------------------------------------------------------
#  pil_img_rotate:
# ------------------------------------------------------------------------------
def pil_img_rotate( self, img, direction, qual=75):
  
  # Save image in temp-folder.
  tempfolder = tempfile.mktemp()
  filename = _fileutil.getOSPath('%s/%s'%(tempfolder,img.filename))
  _fileutil.exportObj(img,filename)
  
  # Call PIL to generate resized image.
  command = pil_command(self,'img_rotate.py')+' '+str(direction)+' '+filename+' '+str(qual)
  os.system(command)
  
  # Read resized image from file-system.
  f = open(filename,'rb')
  rot_data = f.read()
  rot_filename = _fileutil.extractFilename(filename)
  rotated = {'data':rot_data,'filename':rot_filename}
  f.close()
  
  # Remove temp-folder and images.
  _fileutil.remove(tempfolder,deep=1)
  
  # Returns cropped image.
  return rotated

################################################################################