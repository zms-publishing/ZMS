"""
_globals.py

This module defines global constants and utility classes used throughout
the ZMS product, including datatype constants (DT_*), a static page
template wrapper, a generic attribute container (MyClass), and a
section-numbering helper (MySectionizer).

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
import sys
import time
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Datatypes.
DT_UNKNOWN = 0
DT_BOOLEAN = 1
DT_DATE = 2
DT_DATETIME = 3
DT_DICT = 4
DT_FILE = 5
DT_FLOAT = 6
DT_IMAGE = 7
DT_INT = 8
DT_LIST = 9
DT_PASSWORD = 10
DT_STRING = 11
DT_TEXT = 12
DT_TIME = 13
DT_URL = 14
DT_ID = 15
DT_XML = 16
DT_AMOUNT = 17
DT_TEXTS = [ DT_STRING, DT_TEXT ]
DT_STRINGS = [ DT_STRING, DT_TEXT, DT_URL, DT_PASSWORD, DT_XML ]
DT_BLOBS = [ DT_IMAGE, DT_FILE ]
DT_INTS = [ DT_INT, DT_BOOLEAN ]
DT_NUMBERS = [ DT_INT, DT_FLOAT, DT_AMOUNT ]
DT_DATETIMES = [ DT_DATE, DT_TIME, DT_DATETIME ]

datatype_map = [
  [ 'unknown', ''],
  [ 'boolean', 0],
  [ 'date', None],
  [ 'datetime', None],
  [ 'dictionary', {}],
  [ 'file', None],
  [ 'float', 0.0],
  [ 'image', None],
  [ 'int', 0],
  [ 'list', []],
  [ 'password', ''],
  [ 'string', ''],
  [ 'text', ''],
  [ 'time', None],
  [ 'url', ''],
  [ 'identifier', ''],
  [ 'xml', ''],
  [ 'amount', 0.0],
]

def datatype_key(datatype):
  """
  Return the integer key for a given datatype name.

  @param datatype: Datatype name (e.g. 'string', 'int', 'image')
  @type datatype: C{str}
  @return: Integer datatype key, or DT_UNKNOWN if not found
  @rtype: C{int}
  """
  for dt_index in range(len(datatype_map)):
    if datatype_map[dt_index][0] == datatype:
      return dt_index
  else:
    return DT_UNKNOWN


def get_size(v):
  """
  Returns size of given object v in bytes.
  @return: Size in bytes
  @rtype: C{int}
  """
  if hasattr(v, 'get_real_size') and callable(getattr(v, 'get_real_size')):
      return v.get_real_size()
  elif hasattr(v, 'get_size') and callable(getattr(v, 'get_size')):
      return v.get_size()
  return sys.getsizeof(v)


################################################################################
# CLASS StaticPageTemplateFile.
################################################################################
class StaticPageTemplateFile(PageTemplateFile):
    """
    A PageTemplateFile subclass that allows injecting a custom context
    and options dictionary into the template rendering environment.
    """

    def setEnv(self, context, options):
        """
        Set the rendering context and options for this template.

        @param context: The ZMS object used as rendering context
        @type context: C{ZMSObject}
        @param options: Additional template options
        @type options: C{dict}
        """
        self.context = context
        self.options = options

    def pt_getContext(self):
      """
      Build and return the namespace dictionary for page template rendering.

      @return: Template namespace with 'template', 'here', 'context', etc.
      @rtype: C{dict}
      """
      root = self.context.getPhysicalRoot()
      context = self.context
      options = self.options
      c = {'template': self,
          'here': context,
          'context': context,
          'options': options,
          'root': root,
          'request': getattr(root, 'REQUEST', None),
          'modules': SecureModuleImporter,
          }
      return c


################################################################################
# CLASS MyClass
################################################################################
class MyClass(object):
    """
    Generic attribute container that exposes its instance attributes
    via a keys() method, similar to a dictionary.
    """
  
    # ----------------------------------------------------------------------------
    #  MyClass.keys:
    # ----------------------------------------------------------------------------
    def keys(self):
      """
      Return the names of all instance attributes.

      @return: Attribute names
      @rtype: C{dict_keys}
      """
      return self.__dict__.keys()


################################################################################
# CLASS MySectionizer
################################################################################
class MySectionizer(object):
    """
    Helper class for generating hierarchical section numbers
    (e.g. '1.2.3.') with support for different numbering formats
    (numeric, uppercase, lowercase).
    """

    # --------------------------------------------------------------------------
    #  MySectionizer.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self, levelnfc='0'):
      """
      Initialise a new MySectionizer.

      @param levelnfc: Numbering format code: '0'=numeric, '1'=uppercase, '2'=lowercase
      @type levelnfc: C{str}
      """
      self.levelnfc = levelnfc
      self.sections = []

    # --------------------------------------------------------------------------
    #  MySectionizer.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
      """
      Return a string representation of the current section number.

      @return: Section string (e.g. '1.2.3.')
      @rtype: C{str}
      """
      s = ''
      for i in range(len(self.sections)):
        if self.levelnfc == '0':
          s += str(self.sections[i]) + '.'
        elif self.levelnfc == '1':
          s += chr(self.sections[i] - 1 + ord('A')) + '.'
        elif self.levelnfc == '2':
          s += chr(self.sections[i] - 1 + ord('a')) + '.'
      return s

    # --------------------------------------------------------------------------
    #  MySectionizer.clone:
    #
    #  Creates and returns a copy of this object.
    # --------------------------------------------------------------------------
    def clone(self):
      """
      Create and return a deep copy of this sectionizer.

      @return: Cloned MySectionizer instance
      @rtype: C{MySectionizer}
      """
      ob = MySectionizer(self.levelnfc)
      ob.sections = copy.deepcopy(self.sections)
      return ob

    # --------------------------------------------------------------------------
    #  MySectionizer.getLevel:
    # --------------------------------------------------------------------------
    def getLevel(self):
      """
      Return the current nesting depth.

      @return: Current level (number of sections)
      @rtype: C{int}
      """
      return len(self.sections)

    # --------------------------------------------------------------------------
    #  MySectionizer.processLevel:
    # --------------------------------------------------------------------------
    def processLevel(self, level):
      """
      Update the section counter for the given nesting level.

      @param level: The heading level to process
      @type level: C{int}
      """
      # Increase section counter on this level.
      if level > 0:
        if level == len(self.sections):
          self.sections[level-1] = self.sections[level-1] + 1
        elif level > len(self.sections):
          for i in range(len(self.sections), level):
            self.sections.append(1)
        elif level < len(self.sections):
          for i in range(level, len(self.sections)):
            del self.sections[len(self.sections)-1]
          self.sections[level-1] = self.sections[level-1] + 1
