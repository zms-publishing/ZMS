"""
IZMSMetamodelProvider.py

Interface definitions for ZMS metamodel providers.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSMetamodelProvider(Interface):

  def getMetaobjId(self, name):
    """
    Returns id of meta-object specified by name.
    @returns: the meta-object id
    @rtype: C{str}
    """

  def getMetaobjIds(self, sort=None, excl_ids=[]):
    """ 
    Returns list of all meta-ids in model.
    @param sort: if True sort by display_type, if False sort by name, else no sort.
    @type sort: C{Boolean}
    @param excl_ids: the list of ids to exclude
    @type excl_ids: C{list}
    @returns: list of meta-ids
    @rtype: C{list}
    """

  def getMetaobj(self, id):
    """
    Returns meta-object specified by meta-id.
    @rtype: C{dict}
    """

  def getMetaobjAttrIds(self, meta_id, types=[]):
    """
    Returns list of attribute-ids for meta-object specified by meta-id.
    @rtype: C{list}
    """

  def getMetaobjAttrs(self, meta_id, types=[]):
    """
    Get all attributes for meta-object specified by meta-id.
    @rtype: C{list}
    """

  def getMetaobjAttr(self, meta_id, key, sync=True):
    """
    Get attribute for meta-object specified by attribute-id.
    @rtype: C{dict}
    """

  def getMetaobjAttrIdentifierId(self, meta_id):
    """
    Get attribute-id of identifier for datatable specified by meta-id.
    @rtype: C{dict}
    """

  def notifyMetaobjAttrAboutValue(self, meta_id, key, value):
    """
    Notify attribute for meta-object specified by attribute-id about value.
    @rtype: C{dict}
    """
