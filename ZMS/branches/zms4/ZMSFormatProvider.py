################################################################################
# ZMSFormatProvider.py
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
import IZMSConfigurationProvider
import IZMSFormatProvider, ZMSTextformatManager, ZMSCharformatManager
import ZMSItem


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSFormatProvider(
        ZMSItem.ZMSItem,
        ZMSTextformatManager.ZMSTextformatManager,
        ZMSCharformatManager.ZMSCharformatManager):
    zope.interface.implements(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSFormatProvider.IZMSFormatProvider)

    # Properties.
    # -----------
    meta_type = 'ZMSFormatProvider'
    icon = "++resource++zms_/img/ZMSFormatProvider.png"
    icon_clazz = "icon-font"

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options()))

    def manage_sub_options(self):
      return (
        {'label': 'TAB_TEXTFORMATS','action': 'manage_textformats'},
        {'label': 'TAB_CHARFORMATS','action': 'manage_charformats'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats',globals())
    manage_main = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats',globals())
    manage_textformats = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats',globals())
    manage_charformats = PageTemplateFile('zpt/ZMSFormatProvider/manage_charformats',globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_changeTextformat', 'manage_textformats',
		'manage_changeCharformat', 'manage_charformats',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		)

    """
    ############################################################################
    #
    #   Constructor
    #
    ############################################################################
    """

    ############################################################################
    #  ZMSFormatProvider.__init__: 
    #
    #  Initialise a new instance.
    ############################################################################
    def __init__(self, textformats=[], charformats=[]):
      self.id = 'format_manager'
      self.textformats = copy.deepcopy(textformats)
      self.charformats = copy.deepcopy(charformats)

################################################################################
