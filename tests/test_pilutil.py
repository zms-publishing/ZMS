from Products.zms import pilutil
from Products.zms import standard
import test_util

def read_image(zmscontext):
  import os
  filename = 'zope_logo.png'
  filepath = os.path.join(standard.getPRODUCT_HOME(),'www',filename)
  file = open(filepath,'rb')
  data = file.read()
  file.close()
  return standard.ImageFromData(zmscontext,data,filename)

class PilUtilTest(test_util.BaseTest):

  def test_resize(self):
    img = read_image(self.context)
    size = (img.getWidth()/2,img.getHeight()/2)
    img2 = pilutil.resize(img,size)

  def test_optimize(self):
    img = read_image(self.context)
    img2 = pilutil.optimize(img)