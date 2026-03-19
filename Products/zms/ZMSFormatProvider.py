"""
ZMSFormatProvider.py

ZMS support for zmsformat provider.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSConfigurationProvider
from Products.zms import IZMSFormatProvider, ZMSTextformatManager, ZMSCharformatManager
from Products.zms import ZMSItem


@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSFormatProvider.IZMSFormatProvider)
class ZMSFormatProvider(
        ZMSItem.ZMSItem,
        ZMSTextformatManager.ZMSTextformatManager,
        ZMSCharformatManager.ZMSCharformatManager):

    """Provide editable text and character formats for the local portal."""

    # Properties.
    # -----------
    meta_type = 'ZMSFormatProvider'
    zmi_icon = "fas fa-font"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      """Return parent management tabs with local relative actions."""
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      """Return the text and character format tabs shown in the ZMI."""
      return (
        {'label': 'TAB_TEXTFORMATS','action': 'manage_textformats'},
        {'label': 'TAB_CHARFORMATS','action': 'manage_charformats'},
        )

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats', globals())
    manage_main = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats', globals())
    manage_textformats = PageTemplateFile('zpt/ZMSFormatProvider/manage_textformats', globals())
    manage_charformats = PageTemplateFile('zpt/ZMSFormatProvider/manage_charformats', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
      'manage_changeTextformat', 'manage_textformats',
      'manage_changeCharformat', 'manage_charformats',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
    )

    def __init__(self, textformats=[], charformats=[]):
      """Initialize the format manager with persisted format definitions.

      @param textformats: Stored text format definitions.
      @type textformats: C{list}
      @param charformats: Stored character format definitions.
      @type charformats: C{list}
      """
      self.id = 'format_manager'
      self.textformats = copy.deepcopy(textformats)
      self.charformats = copy.deepcopy(charformats)

