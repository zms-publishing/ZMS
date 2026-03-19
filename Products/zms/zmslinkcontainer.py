"""
zmslinkcontainer.py

Container implementation for managing ZMS link references.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Product Imports.
from Products.zms import zmscustom


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMSLinkContainer(zmscustom.ZMSCustom): 

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSLinkContainer"

################################################################################