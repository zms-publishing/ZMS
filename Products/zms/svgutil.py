################################################################################
# svglutil.py
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
from AccessControl.SecurityInfo import ModuleSecurityInfo
import xml.dom.minidom

security = ModuleSecurityInfo('Products.zms.zmsutil')

security.declarePublic('get_svg_dimensions')
def get_dimensions(image):
    size = None
    if image.filename.endswith('.svg'):
        data = bytes(image.getData())
        xmldoc = xml.dom.minidom.parseString(data)
        for svg in xmldoc.getElementsByTagName('svg'):
            if 'height' in svg.attributes and 'width' in svg.attributes:
              height = float(svg.attributes['height'].value)
              width = float(svg.attributes['width'].value)
            elif 'viewBox' in svg.attributes:
              viewBox = svg.attributes['svg'].value
              viewBox = [int(x) for x in d['viewBox'].split(' ')]
              w = viewBox[2] - viewBox[0]
              h = viewBox[3] - viewBox[1]
              size = (w,h)
    return size

security.declarePublic('set_svg_dimensions')
def set_dimensions(image, size):
    svg_dim = get_dimensions(image)
    if svg_dim is not None:
        data = bytes(image.getData())
        data = data.replace('width="%s"'%str(svg_dim[0]),'width="%s"'%str(size[0]))
        data = data.replace('height="%s"'%str(svg_dim[1]),'height="%s"'%str(size[1]))
        data = data.replace('viewBox="0 0 %s %s"'%(str(svg_dim[0]),str(svg_dim[1])),'height="0 0 %s %s"'%(str(size[0]),str(size[1])))
        #image.data = data
        image.width = size[0]
        image.height = size[1]
    return image

security.apply(globals())

################################################################################
