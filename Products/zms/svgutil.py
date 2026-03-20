"""
svgutil.py

SVG parsing and dimension helpers for ZMS image handling.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
import xml.dom.minidom

security = ModuleSecurityInfo('Products.zms.svgutil')

security.declarePublic('get_svg_dimensions')


def get_dimensions(image):
    """
    Return intrinsic SVG dimensions as C{(width, height)} in pixel units.

    Width/height attributes are preferred; C{viewBox} is used as fallback.
    """
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
    """
    Update width/height attributes in SVG data and return the image object.

    If the object is not an SVG or has no detectable dimensions, the image is
    returned unchanged.
    """
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

