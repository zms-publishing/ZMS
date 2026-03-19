"""
_sequence.py

This module provides the Sequence class for generating unique,
auto-incrementing IDs for ZMS objects (e.g. for new content nodes).

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""

# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Product Imports.
from Products.zms import standard
from Products.zms import ZMSItem


################################################################################
# CLASS Sequence
################################################################################
class Sequence(ZMSItem.ZMSItem):
    """
    Auto-incrementing integer sequence used to generate unique IDs
    for ZMS content objects (stored as 'acl_sequence' in the ZODB).
    """

    # Properties.
    # -----------
    meta_type = 'Sequence'
    zmi_icon = "fas fa-sort-numeric-down"
    icon_clazz = zmi_icon

    # Management Options.
    # -------------------
    manage_options = (
      {'label': 'TAB_CONFIGURATION','action': '../manage_customize'},
    ) 

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
      'manage_changeProperties', 'manage_main',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
    )

    # Management Interface.
    # ---------------------
    manage_main = PageTemplateFile('zpt/Sequence/manage_main', globals())


    #--------------------------------------------------------------------------
    # Constructor
    #--------------------------------------------------------------------------

    def __init__(self, startvalue=0):
      """
      Initialise a new Sequence instance.

      @param startvalue: Initial counter value
      @type startvalue: C{int}
      """
      self.id = 'acl_sequence'
      self.value = startvalue


    #--------------------------------------------------------------------------
    # Functions
    #--------------------------------------------------------------------------

    def nextVal(self):
      """
      Increment the sequence counter and return the new value.

      @return: Next sequence value
      @rtype: C{int}
      """
      self.value = self.value + 1
      return self.currVal()


    def currVal(self):
      """
      Return the current sequence value without incrementing.

      @return: Current sequence value
      @rtype: C{int}
      """
      return self.value

    #--------------------------------------------------------------------------
    #  Change Sequence properties.
    #--------------------------------------------------------------------------
    def manage_changeProperties(self, submit, currentvalue, REQUEST, RESPONSE): 
      """ Sequence.manage_changeProperties """
      
      message = ''

      # Set current value.
      if submit == 'Change':
        if currentvalue >= self.value:
          self.value = currentvalue
        
      # Fetch next value.
      if submit == 'Next':
        self.nextVal()

      # Return.
      if RESPONSE is not None:
        RESPONSE.redirect('%s?manage_tabs_message=%s'%(REQUEST[ 'HTTP_REFERER'], standard.url_quote(message)))

