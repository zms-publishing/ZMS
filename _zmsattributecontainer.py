################################################################################
# _zmsattributecontainer.py
#
# $Id: _zmsattributecontainer.py,v 1.2 2003/10/10 18:33:26 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.2 $
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

# Documentation string.
__doc__ = """ZMS product module."""
# Version string. 
__version__ = '0.1' 

# Imports.
from Globals import HTMLFile
from OFS.Folder import Folder
from webdav.Resource import Resource
from webdav.Lockable import ResourceLockedError
from webdav.WriteLockInterface import WriteLockInterface
import urllib
import time
import string
# Product Imports.
import _objattrs
import _pathhandler


################################################################################
################################################################################
###   
###   C o n s t r u c t o r ( s )
###   
################################################################################
################################################################################
def manage_addZMSAttributeContainer(self):
  """ manage_addZMSAttributeContainer """
  id = str(time.time())
  while id in self.objectIds():
    id = str(time.time())
  obj = ZMSAttributeContainer(id)
  self._setObject(id,obj)
  obj = getattr(self,id)
  return obj


################################################################################
################################################################################
###
###   C l a s s
###
################################################################################
################################################################################
class ZMSAttributeContainer(
        Folder,					# Folder.
	_objattrs.ObjAttrs,			# Object-Attributes.
	_pathhandler.PathHandler		# Path-Handler
	): 
	
  # Properties.
  # -----------
  meta_type = 'ZMSAttributeContainer'

  # Management Options.
  # -------------------
  manage_options = (  
	{'label': 'Contents', 'action': 'manage_main'},
	{'label': 'Properties', 'action': 'manage_propertiesForm'},
	) 

  # Management Interface.
  # ---------------------
  manage_propertiesForm = HTMLFile('dtml/objattrs/manage_propertiesform', globals())
  

  # ----------------------------------------------------------------------------
  #  ZMSAttributeContainer.getObjAttrs:
  #
  #  Delegates getObjAttrs to parent.
  # ----------------------------------------------------------------------------
  def getObjAttrs(self, meta_type=None):
    return self.aq_parent.getObjAttrs(meta_type)


  # ----------------------------------------------------------------------------
  #  ZMSAttributeContainer.getObjVersion:
  #
  #  Overrides method from _versionmanager.VersionManager.
  # ----------------------------------------------------------------------------
  def getObjVersion(self, REQUEST={}):
    return self


  # ----------------------------------------------------------------------------
  #  ZMSAttributeContainer.getParentNode:
  #
  #  Delegates getParentNode to parent.
  # ----------------------------------------------------------------------------
  getParentNode__roles__ = None
  def getParentNode(self):
    """
    Delegates getParentNode to parent.
    """
    return self.aq_parent.getParentNode()


  # ----------------------------------------------------------------------------
  #  ZMSAttributeContainer.getChildNodes:
  # ----------------------------------------------------------------------------
  def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
    return []


  ##############################################################################
  #  ZMSAttributeContainer.__init__: 
  #
  #  Constructor (initialise a new instance of ZMSAttributeContainer).
  ##############################################################################
  def __init__(self, id): 
    """ ZMSAttributeContainer.__init__ """
    self.id = id

  
  ##############################################################################
  #  ZMSAttributeContainer.manage_changeProperties: 
  #
  #  Change properties.
  ##############################################################################
  def manage_changeProperties(self, REQUEST, RESPONSE): 
    """ ZMSAttributeContainer.manage_changeProperties """
    message = ''
    for key in self.getObjAttrs().keys():
      obj_attr=self.getObjAttr(key)
      if obj_attr['multilang']:
        for lang in self.getLangIds():
          REQUEST.set('lang',lang)
          self.setReqProperty(key,REQUEST,1)
      else:
        REQUEST.set('lang',self.getPrimaryLanguage())
        self.setReqProperty(key,REQUEST,1)
    # Return with message.
    return RESPONSE.redirect('manage_propertiesForm?manage_tabs_message=%s'%(urllib.quote(message)))


  """
  ##############################################################################
  #
  #   WebDAV
  #
  ##############################################################################
  """

  # WebDAV Interface.
  # -----------------
  __implements__ = (WriteLockInterface,)

  # ----------------------------------------------------------------------------
  #  ZMSObject._checkWebDAVLock
  # ----------------------------------------------------------------------------
  def _checkWebDAVLock(self):
    if self.wl_isLocked():
      raise ResourceLockedError, 'This %s Object is locked via WebDAV' % self.meta_type

  # ----------------------------------------------------------------------------
  #  ZMSObject.document_src
  # ----------------------------------------------------------------------------
  def document_src(self, REQUEST={}):
    """ document_src returns ZMSAttributes as XML """
    return self.toXml(REQUEST, incl_embedded=False, deep=False)

  manage_DAVget = manage_FTPget = document_src

################################################################################
