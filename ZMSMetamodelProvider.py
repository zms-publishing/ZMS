################################################################################
# ZMSMetamodelProvider.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import zope.interface
# Product Imports.
import _confmanager
import _globals
import IZMSConfigurationProvider
import IZMSMetamodelProvider, ZMSMetaobjManager, ZMSMetadictManager
import ZMSItem


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSMetamodelProvider(
        ZMSItem.ZMSItem,
        ZMSMetaobjManager.ZMSMetaobjManager,
        ZMSMetadictManager.ZMSMetadictManager):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSMetamodelProvider.IZMSMetamodelProvider)

    # Properties.
    # -----------
    meta_type = 'ZMSMetamodelProvider'
    icon = "misc_/zms/ZMSMetamodelProvider.gif"

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'TAB_METADATA','action': 'manage_metas'},
        {'label': 'TAB_METAOBJ','action': 'manage_main'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main',globals())
    manage_main = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main',globals())
    manage_main_import = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main_import',globals())
    manage_main_acquire = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main_acquire',globals())
    manage_bigpicture = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_bigpicture', globals())
    manage_analyze = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_analyze', globals())
    manage_metas = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_metas',globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_changeProperties', 'manage_ajaxChangeProperties', 'manage_main', 'manage_main_import', 'manage_bigpicture',
		'manage_changeMetaProperties', 'manage_metas',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    ############################################################################
    #  ZMSMetamodelProvider.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self, model={}, metas=[]):
      self.id = 'metaobj_manager'
      self.model = model.copy()
      self.metas = copy.deepcopy(metas)

    # @see _confmanager:TemplateWrapper.__get__
    def getConfProperty(self, key, default=None):
      v = default
      try:
        if self.content is not None:
          v = self.content.getConfProperty(key,default)
      except:
        pass
      return v

    # --------------------------------------------------------------------------
    #  ZMSMetamodelProvider.__bobo_traverse__
    # --------------------------------------------------------------------------
    def __bobo_traverse__(self, TraversalRequest, name):
      
      # If the name is in the list of attributes, call it.
      attr = getattr( self, name, None)
      if attr is not None:
        return attr
      
      # otherwise do some 'magic'
      else:
        _globals.writeLog(self, "[ZMSMetamodelProvider.__bobo_traverse__]: otherwise do some 'magic'")
        ob = self.getHome().aq_parent
        while ob is not None:
          content = getattr( ob, 'content', None)
          if content is not None:
            metaobj_manager = getattr( content, self.id, None)
            if metaobj_manager is not None:
              # If the name is in the list of attributes, call it.
              attr = getattr( metaobj_manager, name, None)
              if attr is not None:
                return attr
          ob = getattr( ob, 'aq_parent', None)
        return None

################################################################################
