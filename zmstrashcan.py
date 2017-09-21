# -*- coding: utf-8 -*- 
################################################################################
# zmstrashcan.py
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
import string
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _confmanager
import standard


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSTrashcan(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSTrashcan"

    # Management Options.
    # -------------------
    manage_options = ( 
    {'label': 'TYPE_ZMSTRASHCAN', 'action': 'manage_main'},
    {'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
    ) 

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
        'manage','manage_main','manage_container','manage_workspace',
        'manage_eraseObjs','manage_moveObjUp','manage_moveObjDown','manage_cutObjects',
        'manage_ajaxDragDrop','manage_ajaxZMIActions',
        'manage_userForm','manage_user',
        )
    __viewPermissions__ = (
        'manage_ajaxGetChildNodes',
        )
    __ac_permissions__=(
        ('ZMS Author', __authorPermissions__),
        ('View', __viewPermissions__),
        )

    # Management Interface.
    # ---------------------
    manage_properties = PageTemplateFile('zpt/ZMSTrashcan/manage_properties', globals())


    """
    ############################################################################
    ###
    ###   Constructor
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSTrashcan.__init__: 
    #
    #  Constructor (initialise a new instance of ZMSTrashcan).
    ############################################################################
    def __init__(self):
      """ ZMSTrashcan.__init__ """
      id = 'trashcan'
      sort_id = 0
      ZMSContainerObject.__init__(self,id,sort_id)


    # --------------------------------------------------------------------------
    #  ZMSTrashcan.display_icon:
    #
    #  @param REQUEST
    # --------------------------------------------------------------------------
    def display_icon(self, REQUEST, meta_type=None, key='icon', zpt=True):
      icon_title = self.display_type(REQUEST,meta_type)
      icon_clazz = 'icon-trash'
      return self.zmi_icon(self,name=icon_clazz,extra='title="%s"'%icon_title)


    """
    ############################################################################
    ###
    ###   Properties
    ###
    ############################################################################
    """

    ############################################################################
    #  ZMSTrashcan.manage_changeProperties: 
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST=None): 
      """ ZMSTrashcan.manage_changeProperties """
      
      if REQUEST.get('btn','') in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        return REQUEST.RESPONSE.redirect('manage_main?lang=%s'%lang)
        
      ##### Garbage Collection #####
      setattr(self,'garbage_collection',REQUEST.get('garbage_collection',''))
      self.run_garbage_collection(forced=1)
      
      # Return with message.
      message = self.getZMILangStr('MSG_CHANGED')
      if REQUEST and hasattr(REQUEST,'RESPONSE'):
        if REQUEST.RESPONSE:
          return REQUEST.RESPONSE.redirect('manage_properties?lang=%s&manage_tabs_message=%s'%(lang,urllib.quote(message)))


    # --------------------------------------------------------------------------
    #  ZMSTrashcan.run_garbage_collection:
    #
    #  Runs garbage collection.
    # --------------------------------------------------------------------------
    def run_garbage_collection(self, forced=0):
      now = time.time()
      last_run = getattr(self,'last_garbage_collection',None)
      if forced or \
         last_run is None or \
         standard.daysBetween(last_run,now)>1:
        # Get days.
        days = int(getattr(self,'garbage_collection','2'))
        # Get IDs.
        ids = []
        for context in self.objectValues(self.dGlobalAttrs.keys()):
          delete = True
          try:
            delete = delete and standard.daysBetween(context.del_dt,now)>=days
          except:
            pass
          if delete:
            ids.append(context.id)
        # Delete objects.
        self.manage_delObjects(ids=ids)
        # Update time-stamp.
        setattr(self,'last_garbage_collection',now)

    # --------------------------------------------------------------------------
    #  ZMSTrashcan._verifyObjectPaste:
    #
    #  Overrides _verifyObjectPaste of OFS.CopySupport.
    # --------------------------------------------------------------------------
    def _verifyObjectPaste(self, object, validate_src=1): 
      return

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getDCCoverage:
    #
    #  Overrides getDCCoverage of ZMSObject.
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      return 'global.'+self.getPrimaryLanguage()

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.isActive
    # --------------------------------------------------------------------------
    def isActive(self, REQUEST):
      return len(self.getChildNodes(REQUEST))>0

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.isPage
    # --------------------------------------------------------------------------
    def isPage(self):
      return False

    # --------------------------------------------------------------------------
    #  ZMSObject.isPageContainer:
    # --------------------------------------------------------------------------
    def isPageContainer(self):
      return True

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getObjProperty
    # --------------------------------------------------------------------------
    def getObjProperty(self, key, REQUEST={}, par=None):
      return ''

    # --------------------------------------------------------------------------
    #  ZMSTrashcan.getTitle
    # --------------------------------------------------------------------------
    def getTitle(self, REQUEST):
      return self.display_type(REQUEST) + " (" + str(len(self.getChildNodes(REQUEST))) + " " + self.getLangStr('ATTR_OBJECTS',REQUEST['lang']) + ")"

################################################################################