################################################################################
# zmslinkcontainer.py
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
from AccessControl import ClassSecurityInfo
import Globals
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import zmslinkelement
import _confmanager
import _globals
import _zreferableitem


################################################################################
################################################################################
###   
###   Constructor
###   
################################################################################
################################################################################
def manage_addZMSLinkContainer(self, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSLinkContainer """
  
  ##### Create ####
  id_prefix = _globals.id_prefix(REQUEST.get('id_prefix','e'))
  new_id = self.getNewId(id_prefix)
  obj = ZMSLinkContainer(new_id,_sort_id+1)
  self._setObject(obj.id, obj)
  
  obj = getattr(self,obj.id)
  ##### Object State ####
  obj.setObjStateNew(REQUEST)
  ##### Init Coverage ####
  coverage = self.getDCCoverage(REQUEST)
  if coverage.find('local.')==0:
    obj.setObjProperty('attr_dc_coverage',coverage)
  else:
    obj.setObjProperty('attr_dc_coverage','global.'+lang)
  ##### Init Properties ####
  obj.setObjProperty('active',1,lang)
  ##### VersionManager ####
  obj.onChangeObj(REQUEST)
  
  ##### Normalize Sort-IDs ####
  self.normalizeSortIds(id_prefix)
  
  # Return with message.
  message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
  RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMSLinkContainer(ZMSContainerObject): 

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Properties.
    # -----------
    meta_type = meta_id = "ZMSLinkContainer"

    # Management Options.
    # -------------------
    manage_options = ( 
	{'label': 'TAB_EDIT',       'action': 'manage_main'},
	{'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'},
	)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_main_iframe','manage_workspace',
		'manage_deleteObjs','manage_undoObjs',
		'manage_properties','manage_changeProperties','manage_changeTempBlobjProperty',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_ajaxZMIActions',
		'manage_userForm','manage_user',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)


    ############################################################################
    ###
    ###  Properties
    ###
    ############################################################################

    ############################################################################
    #  ZMSLinkContainer.manage_changeProperties: 
    #
    #  Change LinkContainer properties.
    ############################################################################
    def manage_changeProperties(self, lang, REQUEST, RESPONSE): 
      """ ZMSLinkContainer.manage_changeProperties """
        
      message = ''
      
      # Change.
      # -------
      if REQUEST.get('btn','') not in  [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        
        ##### Object State #####
        self.setObjStateModified(REQUEST)
        
        ##### Properties ####
        # Attributes.
        self.setReqProperty('active',REQUEST)
        self.setReqProperty('attr_active_start',REQUEST)
        self.setReqProperty('attr_active_end',REQUEST)
        self.setReqProperty('align',REQUEST)
        
        ##### Change #####
        if REQUEST['btn'] == self.getZMILangStr('BTN_SAVE'):
          for ob in self.getChildNodes(REQUEST,['ZMSLinkElement']):
            id = ob.id
            url = REQUEST['url%s'%id]
            title = REQUEST['title%s'%id]
            description = REQUEST['description%s'%id]
            zmslinkelement.setZMSLinkElement(ob,title,url,description,REQUEST)
        
        ##### Add #####
        elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
          title = REQUEST['_title']
          url = REQUEST['_url']
          description = REQUEST['_description']
          zmslinkelement.addZMSLinkElement(self,title,url,description,REQUEST)
        
        ##### VersionManager ####
        self.onChangeObj(REQUEST)
        
        # Return with message.
        message = self.getZMILangStr('MSG_CHANGED')
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,urllib.quote(message)))
      
      else:
        # Return to parent.
        return RESPONSE.redirect('%s/manage_main?lang=%s#zmi_item_%s'%(self.getParentNode().absolute_url(),lang,self.id))


    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.isPageElement
    # --------------------------------------------------------------------------
    def isPageElement( self): 
      return self.getObjProperty('align',self.REQUEST) != 'NONE'


    ############################################################################
    ###
    ###  HTML-Presentation
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer._getBodyContent:
    # --------------------------------------------------------------------------
    def _getBodyContent(self, REQUEST):
      # @see ZMSObject.getBodyContent
      v = self.metaobj_manager.renderTemplate( self)
      if v:
        return v
      # @deprecated after ZMS2 2.13.4.1569
      align = self.getObjProperty('align',REQUEST)
      css = []
      if align in [ 'LEFT', 'RIGHT']:
        css.append(align.lower())
      elif align in [ 'LEFT_FLOAT']:
        css.append('floatleft')
      elif align in [ 'RIGHT_FLOAT']:
        css.append('floatright')
      if css:
        bodyContent = self.renderShort(REQUEST)
        return '<div class="%s" id="%s">%s</div>'%(' '.join(css), self.id, bodyContent)
      return ''


    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.renderShort:
    # 
    # Renders short presentation of link-container.
    # --------------------------------------------------------------------------
    def renderShort(self, REQUEST):
      html = ''
      try:
        html = ''.join(
          map(lambda x: x.renderShort(REQUEST), 
            filter(lambda x: x.isCommitted(REQUEST), 
              self.getChildNodes(REQUEST,['ZMSLinkElement']))))
        html = self._getBodyContentContentEditable(html)
        # Process html <form>-tags.
        html = _globals.form_quote(html,REQUEST)
      except:
        html = _globals.writeError(self,"[renderShort]")
        html = '<br/>'.join(html.split('\n'))
      # Return <html>.
      return html


    ############################################################################
    ###
    ###  DOM-Methods
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSLinkContainer.getChildNodes:
    #
    #  Returns a NodeList that contains all children of this node in correct 
    #  sort-order. If none, this is a empty NodeList. 
    # --------------------------------------------------------------------------
    def getChildNodes(self, REQUEST={}, meta_types=None, reid=None):
      lang = REQUEST.get('lang',None)
      nodelist = ZMSContainerObject.getChildNodes(self,REQUEST,meta_types,reid)
      if lang is None:
        return nodelist
      else:
        return filter(lambda ob: ob.getDCCoverage(REQUEST).find("."+lang)>0,nodelist)


# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ZMSLinkContainer)

################################################################################
