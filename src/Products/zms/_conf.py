################################################################################
# _conf.py
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
import copy
from zope.interface import implementer
# Product imports.
from Products.zms import standard
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem


################################################################################
################################################################################
###
###   ZMSSysConf
###
################################################################################
################################################################################
@implementer(
        IZMSRepositoryProvider.IZMSRepositoryProvider)
class ZMSSysConf(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSSysConf'
    zmi_icon = "fas fa-wrench"
    icon_clazz = zmi_icon

    ############################################################################
    #  ZMSMetacmdProvider.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'sys_conf'


    ############################################################################
    #  Initialize 
    ############################################################################
    def initialize(self):
      pass


    ############################################################################
    #  Properties 
    ############################################################################
    def get_properties(self):
      id = '__attr_conf_dict__'
      container = self.aq_parent
      return getattr( container, id, {})

    def set_properties(self, properties):
      id = '__attr_conf_dict__'
      container = self.aq_parent
      setattr( container, id, properties.copy())

    def get_property(self, key, default=None):
      properties = self.get_properties()
      return properties.get(key, default)

    def set_property(self, key, value):
      if key.startswith("Portal"):
        self.clearReqBuff()
      properties = self.get_properties()
      if value is None:
        self.del_property(key)
      else:
        properties[key] = value
      self.set_properties(properties)

    def del_property(self, key):
      properties = self.get_properties()
      if key in properties:
        del properties[key]


    ############################################################################
    #
    #  IRepositoryProvider
    #
    ############################################################################

    """
    @see IRepositoryProvider
    """
    def provideRepository(self, ids=None):
      r = {}
      valid_ids = ['sys_conf']
      if ids is None:
        ids = valid_ids
      for id in [x for x in ids if x in valid_ids]:
        properties = copy.deepcopy(self.get_properties())
        d = {'id':id,'__filename__':['__init__.py'],'Properties':properties}
        r[id] = d
      return r


    """
    @see IRepositoryProvider
    """
    def updateRepository(self, r):
      self.set_properties(r['properties'])