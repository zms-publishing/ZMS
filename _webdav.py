################################################################################
# _webdav.py
#
# $Id$
# $Name$
# $Author$
# $Revision$
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
import Globals
from OFS.PropertySheets import PropertySheets, Virtual, PropertySheet, View, DAVProperties, xml_escape
from cgi import escape
# Product Imports.
import _xmllib
import _globals


class ZMSPropertySheet(PropertySheet):

    def formatDateTime(self, dt):
        return self.p_self().getLangFmtDate(dt, fmt_str='ISO-8601')

    def _propertyMap(self):
        return self.p_self().getObjAttrs()

    def hasProperty(self, id, REQUEST={}):
        return self.p_self().hasObjProperty(id, REQUEST)

    def getProperty(self, id):
	return self.p_self().getObjProperty(id)

    def setProperty(self, id, value, REQUEST={}):
        self.p_self().setObjProperty(id, value)
        self.p_self().onChangeObj(REQUEST, forced=1)
 
    def propertyIds(self):
        return self._propertyMap().keys()

    def _propdict(self):
	return self._propertyMap()

    def _setProperty(self, id, value, type='string', meta=None):
       # Set a new property with the given id, value and optional type.
        # Note that different property sets may support different typing
        # systems.
        if not self.hasProperty(id):
            raise BadRequest, 'Invalid property id, %s.' % escape(id)
        self.setProperty(id, value)

 
    def _updateProperty(self, id, value, meta=None):
        # Update the value of an existing property. If value is a string,
        # an attempt will be made to convert the value to the type of the
        # existing property. If a mapping containing meta-data is passed,
        # it will used to _replace_ the properties meta data.
        if not self.hasProperty(id):
            raise BadRequest, 'The property %s does not exist.' % escape(id)
        self.setProperty(id, value)
 

    propstat='<d:propstat xmlns:n="%s">\n' \
             '  <d:prop>\n' \
             '%s\n' \
             '  </d:prop>\n' \
             '  <d:status>HTTP/1.1 %s</d:status>\n%s' \
             '</d:propstat>\n'

    propdesc='  <d:responsedescription>\n' \
             '  %s\n' \
             '  </d:responsedescription>\n'

    def dav__allprop(self, propstat=propstat ):
        # DAV helper method - return one or more propstat elements
        # indicating property names and values for all properties.
        #import pdb; pdb.set_trace()
        result=[]
        propdict = self._propdict()
        for name in propdict.keys():
            type= propdict[name].get('datatype','string')
            value=self.getProperty(name)
            attrs = ''
            if value is not None:
                if type == 'datetime':
                    value = self.formatDateTime(value)
                else:
                    value = xml_escape(value)
            else:
                value = ''
            prop='  <n:%s%s>%s</n:%s>' % (name, attrs, value, name)

            result.append(prop)

        if not result: return ''
        result='\n'.join(result)

        return propstat % (self.xml_namespace(), result, '200 OK', '')


    def dav__propnames(self, propstat=propstat):
        # DAV helper method - return a propstat element indicating
        # property names for all properties in this PropertySheet.
        #import pdb; pdb.set_trace()
        result=[]
        for name in self.propertyIds():
            result.append('  <n:%s/>' % name)
        if not result: return ''
        result='\n'.join(result)
        return propstat % (self.xml_namespace(), result, '200 OK', '')


    def dav__propstat(self, name, result,
                      propstat=propstat, propdesc=propdesc):
        # DAV helper method - return a propstat element indicating
        # property name and value for the requested property.
        #import pdb; pdb.set_trace()
        xml_id=self.xml_namespace()
        propdict=self._propdict()
        if not propdict.has_key(name):
            prop='<n:%s xmlns:n="%s"/>\n' % (name, xml_id)
            code='404 Not Found'
            if not result.has_key(code):
                result[code]=[prop]
            else: result[code].append(prop)
            return
        else:
            type=propdict[name].get('datatype','string')
            value=self.getProperty(name)
            attrs = ''
            if value is not None:
                if type == 'datetime':
                    value = self.formatDateTime(value)
                else:
                    value = xml_escape(value)
            else:
                value = ''
            prop='<n:%s%s xmlns:n="%s">%s</n:%s>\n' % (
                name, attrs, xml_id, value, name)
            code='200 OK'
            if not result.has_key(code):
                result[code]=[prop]
            else: result[code].append(prop)
            return


    del propstat
    del propdesc


Globals.default__class_init__(ZMSPropertySheet)


class ZMSProperties(Virtual, ZMSPropertySheet, View):
    """The default property set mimics the behavior of old-style Zope
       properties -- it stores its property values in the instance of
       its owner."""

    id='default'
    _md={'xmlns': 'ZMS:' }

Globals.default__class_init__(ZMSProperties)


class ZMSPropertySheets(PropertySheets):
    """A PropertySheets container that contains a default property
       sheet for compatibility with the arbitrary property mgmt
       design of Zope PropertyManagers."""
    default=ZMSProperties()
    webdav =DAVProperties()
    def _get_defaults(self):
        return (self.default, self.webdav)

Globals.default__class_init__(ZMSPropertySheets)


class XmlWebDAVBuilder(_xmllib.XmlBuilder):

    def parse(self, input):
        v = _xmllib.XmlBuilder.parse(self, input)
        self._xml = {}

        tags = v.pop().get('tags')

        for tag in tags:
            if type(tag) is dict:
                name = tag.get('name')
                self._xml[name] = tag
        return self


    def keys(self):
        return self._xml.keys()


    def get(self, name, lang=None, _marker=None):
        tag = self._xml[name]
        if tag.has_key('tags'):
            return self._getLangValue(tag.get('tags'), lang, _marker)
        if tag.has_key('cdata'):
            return tag.get('cdata')
        return _marker


    def _getLangValue(self, tags, lang=None, _marker=None):
        for tag in tags:
            if type(tag) is dict:
                name = tag.get('name')
                if name == 'lang' and tag.get('attrs',{}).get('id', None) == lang:
                    if tag.has_key('tags'):
                        return self._getDataValue(tag.get('tags'), _marker)
                    if tag.has_key('cdata'): 
                        return tag.get('cdata')
        return _marker
       
 
    def _getDataValue(self, tags, _marker=None):
        for tag in tags:
            if type(tag) is dict:
                name = tag.get('name')
                if name == 'data':
                    dict = {}
                    attrs = tag.get('attrs', [])
                    for attr in attrs.keys():
                        dict[attr] = attrs[attr]
                    if dict['type'] in ['image','file'] and tag.has_key('cdata'):
                        dict['data'] = _globals.hex2bin(tag.get('cdata'))
                    return dict
        return _marker

################################################################################
