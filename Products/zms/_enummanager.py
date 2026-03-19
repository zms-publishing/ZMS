"""
_enummanager.py

Internal helpers for enummanager in ZMS.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
from App.Common import package_home
# Product Imports.
from Products.zms import _xmllib


class EnumManager(object):

  """Load enumeration values from XML files in the product import folder."""

  def __init__(self):
    """Initialize the enum manager mixin."""
    pass
    
  getValues__roles__ = None
  def getValues(self, id, path=None):
    """Return values for the named enumeration.

    @param id: Enumeration identifier.
    @type id: C{str}
    @param path: Optional base directory for enum XML files.
    @type path: C{str}
    @return: Enumeration entries as a list of key/value pairs.
    @rtype: C{list}
    """
    if path is None:
      path = package_home(globals())+'/import/'
    filename = path + 'enum.%s.xml'%id
    xml = open(filename)
    builder = _xmllib.XmlAttrBuilder()
    v = builder.parse(xml)
    xml.close()
    if isinstance(v, dict):
      l = sorted([(v[x], x) for x in v])
      v = []
      for i in l:
        v.append([i[1], i[0]])
    return v

