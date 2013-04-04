################################################################################
# ZMSItem.py
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
from DateTime.DateTime import DateTime
from App.special_dtml import HTMLFile
from Persistence import Persistent
from Acquisition import Implicit
import OFS.SimpleItem, OFS.ObjectManager
import string


################################################################################
################################################################################
###
###   Abstract Class ZMSItem
###
################################################################################
################################################################################
class ZMSItem(
	OFS.ObjectManager.ObjectManager,
	OFS.SimpleItem.Item,
	Persistent,				# Persistent. 
	Implicit,				# Acquisition. 
	):

    # Documentation string.
    __doc__ = """ZMS product module."""
    # Version string. 
    __version__ = '0.1' 
    
    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage_page_request', 'manage_page_header', 'manage_page_footer', 'manage_tabs', 'manage_tabs_sub', 'manage_bodyTop', 'manage_main_iframe' 
		)
    __viewPermissions__ = (
		'manage_menu',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		('View', __viewPermissions__),
		)

    # Templates.
    # ----------
    f_bodyContent = HTMLFile('dtml/object/f_bodycontent', globals()) # Template: Body-Content / Element
    manage = HTMLFile('dtml/object/manage', globals())
    manage_workspace = HTMLFile('dtml/object/manage', globals()) # ZMI Manage
    manage_main = HTMLFile('dtml/ZMSObject/manage_main', globals())
    manage_tabs = HTMLFile('dtml/object/manage_tabs', globals()) # ZMI Tabulators
    manage_tabs_sub = HTMLFile('dtml/object/manage_tabs_sub', globals()) # ZMI Tabulators (Sub)
    manage_bodyTop = HTMLFile('dtml/object/manage_bodytop', globals()) # ZMI bodyTop
    manage_page_request = HTMLFile('dtml/object/manage_page_request', globals()) # ZMI Page Request
    manage_page_header = HTMLFile('dtml/object/manage_page_header', globals()) # ZMI Page Header
    manage_page_footer = HTMLFile('dtml/object/manage_page_footer', globals()) # ZMI Page Footer
    manage_main_iframe = HTMLFile('dtml/ZMSObject/manage_main_iframe', globals()) # ZMI Iframe

    # --------------------------------------------------------------------------
    #  ZMSItem.display_icon:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_icon(self, REQUEST, meta_type=None, key='icon'):
      if meta_type is None:
        return self.icon
      else:
        return self.aq_parent.display_icon( REQUEST, meta_type, key)


    # --------------------------------------------------------------------------
    #  ZMSItem.getTitlealt
    # --------------------------------------------------------------------------
    def getTitlealt( self, REQUEST):
      return self.getZMILangStr( self.meta_type)


    # --------------------------------------------------------------------------
    #  ZMSItem.breadcrumbs_obj_path:
    # --------------------------------------------------------------------------
    def breadcrumbs_obj_path(self, portalMaster=True):
      return self.aq_parent.breadcrumbs_obj_path(portalMaster)

################################################################################