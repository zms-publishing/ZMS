"""
_zmsattributecontainer.py - ZMS Attribute Container for Custom Attribute Storage and Management

Defines ZMSAttributeContainer for object persistence, Zope integration, and container protocols.
It implements Zope's ObjectManager interface, handles acquisition, and manages object lifecycle.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import time

from Products.zms import _objattrs
from Products.zms import _pathhandler
from Products.zms import standard


def manage_addZMSAttributeContainer(self):
  """Create and attach a new C{ZMSAttributeContainer} below the current object."""
  id = str(time.time())
  while id in self.objectIds():
    id = str(time.time())
  obj = ZMSAttributeContainer(id)
  self._setObject(id, obj)
  obj = getattr(self, id)
  return obj


def containerFilter(container):
  """Return C{True} when C{container} can be listed as a ZMS child container."""
  return container.meta_type.startswith('ZMS')


class ZMSAttributeContainer(
      Folder,
      _objattrs.ObjAttrs,
      _pathhandler.PathHandler):
  """Container object that stores and edits custom attribute values."""

  meta_type = 'ZMSAttributeContainer'

  manage_options = (
    {'label': 'Contents', 'action': 'manage_main'},
    {'label': 'Properties', 'action': 'manage_propertiesForm'},
  )

  manage_propertiesForm = PageTemplateFile('zpt/objattrs/manage_propertiesform', globals())


  def __init__(self, id):
    """Initialize the container with a generated object id."""
    self.id = id


  def getObjAttrs(self, meta_type=None):
    """Delegate attribute schema lookup to the parent ZMS object."""
    return self.aq_parent.getObjAttrs(meta_type)


  def getObjVersion(self, REQUEST={}):
    """Return self as version object because containers are not versioned."""
    return self


  getParentNode__roles__ = None


  def getParentNode(self):
    """Delegate parent node lookup to the acquisition parent."""
    return self.aq_parent.getParentNode()


  def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
    """Return an empty list because attribute containers have no children."""
    return []


  def manage_changeProperties(self, REQUEST, RESPONSE):
    """
    Persist submitted attribute values for all configured object attributes.

    Multilingual attributes are written for every language, while single-language
    attributes are written for the primary language only.
    """
    message = ''
    for key in self.getObjAttrs():
      obj_attr = self.getObjAttr(key)
      if obj_attr['multilang']:
        for lang in self.getLangIds():
          REQUEST.set('lang', lang)
          self.setReqProperty(key, REQUEST, 1)
      else:
        REQUEST.set('lang', self.getPrimaryLanguage())
        self.setReqProperty(key, REQUEST, 1)
    return RESPONSE.redirect(
      'manage_propertiesForm?manage_tabs_message=%s' % (standard.url_quote(message))
    )
