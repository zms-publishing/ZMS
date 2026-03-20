"""
_conf.py

This module implements the ZMSSysConf class, which manages system-level
configuration properties for a ZMS instance. It also implements the
IZMSRepositoryProvider interface for persisting configuration to the
file-system repository.

The class acts as a thin adapter around the parent container attribute
C{__attr_conf_dict__}, exposing helper methods for reading/writing single
properties and for serializing/deserializing settings during repository sync.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
import copy
from zope.interface import implementer
# Product imports.
from Products.zms import standard
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem


@implementer(
        IZMSRepositoryProvider.IZMSRepositoryProvider)
class ZMSSysConf(
        ZMSItem.ZMSItem):
    """
    System configuration container for a ZMS instance.
    Stores key/value configuration properties in __attr_conf_dict__
    and implements IZMSRepositoryProvider for repository persistence.
    """

    meta_type = 'ZMSSysConf'
    zmi_icon = "fas fa-wrench"
    icon_clazz = zmi_icon


    def __init__(self):
      """
      Initialise a new ZMSSysConf instance with id 'sys_conf'.

      @return: C{None}
      @rtype: C{None}
      """
      self.id = 'sys_conf'


    def initialize(self):
      """
      Hook for post-creation initialization (currently a no-op).

      @return: C{None}
      @rtype: C{None}
      """
      pass


    def get_properties(self):
      """
      Return the full configuration properties dictionary.

      @return: Configuration properties
      @rtype: C{dict}
      """
      id = '__attr_conf_dict__'
      container = self.aq_parent
      return getattr( container, id, {})

    def set_properties(self, properties):
      """
      Replace the full configuration properties dictionary.

      @param properties: New configuration properties mapping.
        Expected value is a plain C{dict} with string keys.
      @type properties: C{dict}
      @return: C{None}
      @rtype: C{None}
      """
      id = '__attr_conf_dict__'
      container = self.aq_parent
      setattr( container, id, properties.copy())


    def get_property(self, key, default=None):
      """
      Return a single configuration property value.

      @param key: Property key.
      @type key: C{str}
      @param default: Default value returned when C{key} does not exist.
      @type default: C{any}
      @return: Property value or C{default}.
      @rtype: C{any}
      """
      properties = self.get_properties()
      return properties.get(key, default)


    def set_property(self, key, value):
      """
      Set a single configuration property. If value is None, the
      property is deleted. Clears the request buffer for Portal keys.

      @param key: Property key.
      @type key: C{str}
      @param value: Property value. Use C{None} to delete the key.
      @type value: C{any} | C{None}
      @return: C{None}
      @rtype: C{None}
      """
      if key.startswith("Portal"):
        self.clearReqBuff()
      properties = self.get_properties()
      if value is None:
        self.del_property(key)
      else:
        properties[key] = value
      self.set_properties(properties)


    def del_property(self, key):
      """
      Delete a configuration property by key.

      @param key: Property key to delete.
      @type key: C{str}
      @return: C{None}
      @rtype: C{None}
      """
      properties = self.get_properties()
      if key in properties:
        del properties[key]


    def provideRepository(self, ids=None):
      """
      Provide configuration data for the repository export.

      @see: IZMSRepositoryProvider
      @param ids: List of IDs to export. Expected values include C{'sys_conf'};
        C{None} exports all valid ids.
      @type ids: C{list} or C{None}
      @return: Dictionary of repository data keyed by id
      @rtype: C{dict}
      """
      r = {}
      valid_ids = ['sys_conf'] if not bool(self.getConfProperty('ZMS.conf.ignore.sys_conf', False)) else []
      if ids is None:
        ids = valid_ids
      for id in [x for x in ids if x in valid_ids]:
        properties = copy.deepcopy(self.get_properties())
        d = {'id':id,'__filename__':['__init__.py'],'Properties':properties}
        r[id] = d
      return r


    def updateRepository(self, r):
      """
      Update configuration from repository import data.

      @see: IZMSRepositoryProvider
      @param r: Repository data dictionary containing C{'Properties'}
        (or legacy C{'properties'}).
      @type r: C{dict}
      @return: C{None}
      @rtype: C{None}
      """
      self.set_properties(r.get('Properties',r.get('properties',{})))