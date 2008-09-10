################################################################################
# ZMSFormatProvider.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
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
from __future__ import nested_scopes
from zope.interface import implements
from Globals import HTMLFile
import copy
# Product Imports.
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
    implements(IZMSFormatProvider.IZMSFormatProvider)

    # Properties.
    # -----------
    meta_type = 'ZMSFormatProvider'
    icon = "misc_/zms/ZMSFormatProvider.gif"

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return map( lambda x: self.operator_setitem( x, 'action', '../'+x['action']), copy.deepcopy(self.aq_parent.manage_options))

    manage_sub_options = (
	{'label': 'TAB_TEXTFORMATS','action': 'manage_textformats'},
	{'label': 'TAB_CHARFORMATS','action': 'manage_charformats'},
	)

    # Management Interface.
    # ---------------------
    manage = manage_main = manage_textformats = HTMLFile('dtml/ZMSFormatProvider/manage_textformats', globals())
    manage_charformats = HTMLFile('dtml/ZMSFormatProvider/manage_charformats', globals())

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
