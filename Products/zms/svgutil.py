################################################################################
# svgutil.py
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

security = ModuleSecurityInfo('Products.zms.svgutil')

security.declarePublic('get_svg_dimensions')
def get_dimensions(image):
    size = None
    if image.filename.endswith('.svg'):
        data = bytes(image.getData())
        xmldoc = xml.dom.minidom.parseString(data)
        for svg in xmldoc.getElementsByTagName('svg'):
            if 'height' in svg.attributes and 'width' in svg.attributes:
              w = svg.attributes['width'].value
              h = svg.attributes['height'].value
              try:
                w = int(float(w))
                h = int(float(h))
              except:
                if str(w).endswith('px'):
                  w = int(float(w[:-2]))
                  h = int(float(h[:-2]))
                elif str(w).endswith('mm'):
                  w = int(float(w[:-2]) * 3.7795)
                  h = int(float(h[:-2]) * 3.7795)
                elif str(w).endswith('cm'):
                  w = int(float(w[:-2]) * 37.795)
                  h = int(float(h[:-2]) * 37.795)
              size = (w,h)
              break
            elif 'viewBox' in svg.attributes:
              viewBox = svg.attributes['viewBox'].value
              viewBox = [int(float(x)) for x in viewBox.split(' ')]
              w = viewBox[2] - viewBox[0]
              h = viewBox[3] - viewBox[1]
              size = (w,h)
    return size

security.declarePublic('set_svg_dimensions')
def set_dimensions(image, size):
    svg_dim = get_dimensions(image)
    if svg_dim is not None:
        w = int(float(size[0]))
        h = int(float(size[1]))
        data = bytes(image.getData())
        xmldoc = xml.dom.minidom.parseString(data)
        for svg in xmldoc.getElementsByTagName('svg'):
            oldwidth = '<svg '
            newwidth = '<svg '
            oldheight = '<svg '
            newheight = '<svg '
            if 'width' in svg.attributes:
              oldwidth = 'width="%s"'%svg.attributes['width'].value
              newwidth = ''
            if 'height' in svg.attributes:
              oldheight = 'height="%s"'%svg.attributes['height'].value
              newheight = ''
            data = data.replace(bytes(oldwidth, 'utf-8'), bytes('%s width="%i" '%(newwidth, w), 'utf-8'))
            data = data.replace(bytes(oldwidth, 'utf-8'), bytes('%s height="%i" '%(newheight, h), 'utf-8'))
        image.data = data
    return image

security.apply(globals())

################################################################################
