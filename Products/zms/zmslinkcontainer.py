"""
zmslinkcontainer.py

Container implementation for managing ZMS link references.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Product Imports.
from Products.zms import zmscustom


class ZMSLinkContainer(zmscustom.ZMSCustom):
    """
    Represent a lightweight container for link reference objects.
    The container provides a dedicated meta-type and rendering context for link
    references, but otherwise inherits all behavior from C{ZMSCustom}.
    """

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSLinkContainer"
