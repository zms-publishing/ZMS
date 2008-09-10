################################################################################
# ZMSItem.py
#
# $Id: $
# $Name: $
# $Author: $
# $Revision: $
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
from DateTime.DateTime import DateTime
from Globals import HTMLFile, Persistent
from Acquisition import Implicit
from OFS.PropertySheets import PropertySheets, vps
from webdav.Lockable import ResourceLockedError
import OFS.SimpleItem, OFS.ObjectManager, webdav.Collection
import string
import _webdav


################################################################################
################################################################################
###
###   Abstract Class ZMSItem
###
################################################################################
################################################################################
class ZMSItem(
	OFS.ObjectManager.ObjectManager,
	webdav.Collection.Collection,
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
		'manage_dtpref', 'manage_page_header', 'manage_page_footer', 'manage_tabs', 'manage_tabs_sub', 'manage_bodyTop', 
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
    manage_menu = HTMLFile('dtml/object/manage_menu', globals()) # ZMI Menu
    manage_tabs = HTMLFile('dtml/object/manage_tabs', globals()) # ZMI Tabulators
    manage_tabs_sub = HTMLFile('dtml/object/manage_tabs_sub', globals()) # ZMI Tabulators (Sub)
    manage_bodyTop = HTMLFile('dtml/object/manage_bodytop', globals()) # ZMI bodyTop
    manage_page_header = HTMLFile('dtml/object/manage_page_header', globals()) # ZMI Page Header
    manage_page_footer = HTMLFile('dtml/object/manage_page_footer', globals()) # ZMI Page Footer


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


    ############################################################################
    ###
    ###  Sitemap
    ###
    ############################################################################

    ############################################################################
    #  ZMSObject.manage_dtpref: 
    #
    #  De-/Activate Document-Template preference.
    ############################################################################
    def manage_dtpref(self, key, lang, REQUEST, RESPONSE):
      """ ZMSObject.manage_dtpref """
      v = 1
      if REQUEST.has_key(key):
        v = int(not string.atoi(REQUEST[key]))
      e=(DateTime('GMT')+365).rfc822()
      RESPONSE.setCookie(key,str(v),path='/',expires=e)
      return RESPONSE.redirect('manage?lang=%s'%lang)


    ############################################################################
    ###
    ###  WebDAV
    ###
    ############################################################################

    # Standard DAVProperties + ZMSProperties.
    # ---------------------------------------
    propertysheets=vps(_webdav.ZMSPropertySheets)


    # --------------------------------------------------------------------------
    #  ZMSItem._checkWebDAVLock
    # --------------------------------------------------------------------------
    def _checkWebDAVLock(self):
      if self.wl_isLocked():
        raise ResourceLockedError, 'This %s Object is locked via WebDAV' % self.meta_type


    # --------------------------------------------------------------------------
    #  ZMSItem.document_src
    # --------------------------------------------------------------------------
    def document_src(self, REQUEST={}):
      """ document_src returns ZMSAttributes as XML """
      return self.toXml(REQUEST, incl_embedded=False, deep=False, data2hex=True)


    manage_FTPget = manage_DAVget = document_src

    # --------------------------------------------------------------------------
    #  ZMSItem.PUT
    # --------------------------------------------------------------------------
    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        
        file=REQUEST['BODYFILE']
        
        builder = _webdav.XmlWebDAVBuilder()
        
        v = builder.parse(file)
        
        lang = REQUEST.get('lang', None)
        
        if lang is None:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang', lang)
        
        if _globals.debug( self):
          for key in v.keys():
            _globals.writeLog( self, '%s: %s' %(key, v.get(key, lang)))
        
        attrs = self.getObjAttrs()
        
        if _globals.debug( self):
          _globals.writeLog( 'Updating %s via WebDAV' % self.absolute_url())
        
        self.setObjStateModified(REQUEST)
        
        for attr in attrs.keys():
          if attr in v.keys():
            # get new value
            value_new = v.get(attr, lang)
            
            # if value is used as datetime, convert to correct form
            datatype = attrs[attr].get('datatype', 'string')
            if datatype == 'datetime':
                if value_new[0] == '(':
                    value_new = value_new[1:-1].split(',')
                    value_new = map(int, value_new)
                    value_new = _globals.getDateTime(tuple(value_new))
            
            # if value is used as boolea, convert to correct form
            if datatype == 'boolean':
                value_new = bool(value_new)
            
            # get old value
            value_old = self.getObjProperty(attr, REQUEST)
            
            # if value has changed
            if value_new != value_old:
              if _globals.debug( self):
                _globals.writeLog( 'Updating property %s: %s' % (attr, value_new))
              self.setObjProperty(attr, value_new, forced=1)
        
        self.onChangeObj(REQUEST)
        
        RESPONSE.setStatus(204)
        return RESPONSE


    # --------------------------------------------------------------------------
    #  ZMSItem.listDAVObjects
    # --------------------------------------------------------------------------
    def listDAVObjects(self):
      objectValues = getattr(self, 'objectValues', None)
      if objectValues is not None:
        spec = [ 'BTreeFolder2',
                 'DTML Document',
                 'DTML Method',
                 'File',
                 'Folder',
                 'Folder (Ordered)',
                 'Image',
                 'Script (Python)']
        spec.extend( self.dGlobalAttrs.keys())
        return objectValues(spec = spec)
      return []

################################################################################
