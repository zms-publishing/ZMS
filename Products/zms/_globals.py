#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# _globals.py
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


def create_headless_http_request():
    """
    Returns a ZPublisher.HTTPRequest object to be used in headless mode.
    """
    # Measure time for exection.
    import logging
    LOGGER = logging.getLogger('create_headless_http_request')
    start_time = time.time()
    # Imports.  
    from io import BytesIO
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse

    env = {}
    env.setdefault('SERVER_NAME', 'nohost')
    env.setdefault('SERVER_PORT', '80')
    resp = HTTPResponse(stdout=BytesIO)

    # Print execution time.
    LOGGER.log(logging.INFO, 'Execution time create_headless_http_request(): %s' % (time.time() - start_time))

    return HTTPRequest(stdin=BytesIO, environ=env, response=resp)

# Set gobal variable headless_http_request.
headless_http_request = create_headless_http_request()

################################################################################
# Define StaticPageTemplateFile.
################################################################################
class StaticPageTemplateFile(PageTemplateFile):
  def setEnv(self, context, options):
    self.context = context
    self.options = options
  def pt_getContext(self):
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
# Define MyClass.
################################################################################
class MyClass(object):
  
    # ----------------------------------------------------------------------------
    #  MyClass.keys:
    # ----------------------------------------------------------------------------
    def keys(self):
      return self.__dict__.keys()


################################################################################
# Define MySectionizer.
################################################################################
class MySectionizer(object):

    # --------------------------------------------------------------------------
    #  MySectionizer.__init__:
    #
    #  Constructor.
    # --------------------------------------------------------------------------
    def __init__(self, levelnfc='0'):
      self.levelnfc = levelnfc
      self.sections = []

    # --------------------------------------------------------------------------
    #  MySectionizer.__str__:
    #
    #  Returns a string representation of the object.
    # --------------------------------------------------------------------------
    def __str__(self):
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
      ob = MySectionizer(self.levelnfc)
      ob.sections = copy.deepcopy(self.sections)
      return ob

    # --------------------------------------------------------------------------
    #  MySectionizer.getLevel:
    # --------------------------------------------------------------------------
    def getLevel(self):
      return len(self.sections)

    # --------------------------------------------------------------------------
    #  MySectionizer.processLevel:
    # --------------------------------------------------------------------------
    def processLevel(self, level):
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

################################################################################
