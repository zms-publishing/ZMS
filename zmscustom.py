################################################################################
# zmscustom.py
#
# $Id: zmscustom.py,v 1.9 2004/11/30 20:04:16 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.9 $
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
from Globals import HTMLFile
from types import StringTypes
import sys
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _fileutil
import _globals
import _importable


# ------------------------------------------------------------------------------
#  zmscustom.parseXmlString
# ------------------------------------------------------------------------------
def parseXmlString(self, file):
  _globals.writeBlock( self, '[parseXmlString]')
  message = ''
  REQUEST = self.REQUEST
  lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
  v = self.parseXmlString(file)
  metaObj = self.getMetaobj(self.meta_id)
  res_id = metaObj['attrs'][0]['id']
  res_abs = self.getObjProperty(res_id,REQUEST)
  res_abs.extend(v)
  self.setObjStateModified(REQUEST)
  self.setObjProperty(res_id,res_abs,lang)
  self.onChangeObj(REQUEST)
  return message


################################################################################
################################################################################
###
###  Constructor
###
################################################################################
################################################################################
manage_addZMSCustomForm = HTMLFile('manage_addzmscustomform', globals()) 
def manage_addZMSCustom(self, meta_id, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSCustom """
  
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id','e'))
    obj = ZMSCustom(self.getNewId(id_prefix),_sort_id+1,meta_id)
    self._setObject(obj.id, obj)
    
    metaObj = self.getMetaobj( meta_id)
    redirect_self = bool( REQUEST.get( 'redirect_self', 0)) or REQUEST.get( 'btn', '') == '' or metaObj['type'] == 'ZMSRecordSet'
    for attr in metaObj['attrs']:
      attr_type = attr['type']
      redirect_self = redirect_self or attr_type in self.getMetaobjIds()+['*']
    redirect_self = redirect_self and not REQUEST.get('btn','') in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]
    
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
    obj.manage_changeProperties(lang,REQUEST,RESPONSE)
    
    ##### Normalize Sort-IDs ####
    self.normalizeSortIds(id_prefix)
    
    # Return with message.
    message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    if redirect_self:
      RESPONSE.redirect('%s/%s/manage_main?lang=%s&manage_tabs_message=%s'%(self.absolute_url(),obj.id,lang,urllib.quote(message)))
    else:
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#_%s'%(self.absolute_url(),lang,urllib.quote(message),obj.id))
  
  else:
    RESPONSE.redirect('%s/manage_main?lang=%s'%(self.absolute_url(),lang))


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMSCustom(ZMSContainerObject):

    # Properties.
    # -----------
    meta_type = "ZMSCustom"

    # Management Options.
    # -------------------
    def manage_options(self):
      opts = []
      opts.append({'label': 'TAB_EDIT',         'action': 'manage_main'})
      if self.isPageContainer():
        opts.append({'label': 'TAB_PROPERTIES', 'action': 'manage_properties'})
      opts.append({'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'})
      opts.append({'label': 'TAB_TASKS',        'action': 'manage_tasks'})
      opts.append({'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'})
      opts.append({'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'})
      opts.append({'label': 'TAB_PREVIEW',      'action': 'preview_html'}) # empty string defaults to index_html
      return tuple(opts)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
		'manage','manage_main','manage_container','manage_workspace','manage_checkout',
		'manage_addZMSModule',
		'manage_properties','manage_changeProperties',
		'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs','manage_ajaxDragDrop',
		'manage_search','manage_search_attrs','manage_tasks',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		)
    __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)


    # Templates.
    # ----------
    manage_container = HTMLFile('dtml/ZMSContainerObject/manage_main', globals())
    manage_main = manage_properties = HTMLFile('dtml/ZMSObject/manage_main', globals())
    metaobj_record_select = HTMLFile('dtml/ZMSRecordSet/record_select', globals())
    metaobj_record_update = HTMLFile('dtml/ZMSRecordSet/record_update', globals())
    metaobj_record_insert = HTMLFile('dtml/ZMSRecordSet/record_insert', globals())
    metaobj_record_summary = HTMLFile('dtml/ZMSRecordSet/record_summary', globals())
    metaobj_recordset_details_grid = HTMLFile('dtml/ZMSRecordSet/details_grid', globals())
    metaobj_recordset_details = HTMLFile('dtml/ZMSRecordSet/details', globals())
    metaobj_recordset_main_grid = HTMLFile('dtml/ZMSRecordSet/main_grid', globals())
    metaobj_recordset_main = HTMLFile('dtml/ZMSRecordSet/main', globals())
    metaobj_recordset_actions = HTMLFile('dtml/ZMSRecordSet/actions', globals())
    metaobj_recordset_input_fields = HTMLFile('dtml/ZMSRecordSet/input_fields', globals())
    metaobj_recordset_input_js = HTMLFile('dtml/ZMSRecordSet/input_js', globals())


    """
    ############################################################################
    ###
    ###   Constructor
    ###
    ############################################################################
    """

    ############################################################################
    # ZMSCustom.__init__: 
    #
    # Constructor (initialise a new instance of ZMSCustom).
    ############################################################################
    def __init__(self, id='', sort_id=0, meta_id=''):
      """ ZMSCustom.__init__ """
      ZMSContainerObject.__init__(self,id,sort_id)
      self.meta_id = meta_id


    """
    ############################################################################
    ###
    ###   Http
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSCustom.GET: 
    #
    #  Handle HTTP GET requests.
    # --------------------------------------------------------------------------
    def GET(self, REQUEST, RESPONSE):
      """Handle HTTP GET requests."""
      metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
      i = 0
      while 1:
        if i >= len(metaObjAttrs): break
        objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
        if objAttr['type'] in ['string','text']:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang',lang)
          REQUEST.set('preview','preview')
          return self.getObjProperty(objAttr['id'],REQUEST)
        i = i + 1
      return ''


    # --------------------------------------------------------------------------
    #  ZMSCustom.PUT: 
    #
    #  Handle HTTP PUT requests.
    # --------------------------------------------------------------------------
    def PUT(self, REQUEST, RESPONSE):
      """Handle HTTP PUT requests."""
      metaObjAttrs = self.getMetaobj(self.meta_id)['attrs']
      i = 0
      while 1:
        if i >= len(metaObjAttrs): break
        objAttr = self.getMetaobjAttr(self.meta_id,metaObjAttrs[i]['id'])
        if objAttr['type'] in ['string','text']:
          lang = self.getPrimaryLanguage()
          REQUEST.set('lang',lang)
          self.setObjStateModified(REQUEST)
          self.setObjProperty(objAttr['id'],REQUEST.get('BODY', ''),lang)
          self.onChangeObj(REQUEST)
          break
        i = i + 1
      RESPONSE.setStatus(204)
      return RESPONSE


    ############################################################################
    ###
    ###   ZMSRecordSet
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Init:
    # --------------------------------------------------------------------------
    def recordSet_Init(self, REQUEST):
      """
      Initialize record-set.
      """
      metaObj = self.getMetaobj(self.meta_id)
      res_id = metaObj['attrs'][0]['id']
      res = self.getObjProperty(res_id,REQUEST)
      REQUEST.set('res_id',res_id)
      REQUEST.set('res_abs',res)
      REQUEST.set('res',res)
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Filter:
    # --------------------------------------------------------------------------
    def recordSet_Filter(self, REQUEST):
      """
      Filter record-set.
      """
      metaObj = self.getMetaobj(self.meta_id)
      res_id = REQUEST['res_id']
      res_abs = REQUEST['res_abs']
      res = REQUEST['res']
      SESSION = REQUEST.SESSION
      
      # Filter (FK).
      filterattr='fk_key'
      filtervalue='fk_val'
      sessionattr='%s_%s'%(filterattr,self.id)
      sessionvalue='%s_%s'%(filtervalue,self.id)
      SESSION.set(sessionattr,REQUEST.form.get(filterattr,SESSION.get(sessionattr,'')))
      SESSION.set(sessionvalue,REQUEST.form.get(filtervalue,SESSION.get(sessionvalue,'')))
      if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
        SESSION.set(sessionattr,'')
        SESSION.set(sessionvalue,'')
      if SESSION.get(sessionattr,'') != '' and \
         SESSION.get(sessionvalue,''):
        res = self.filter_list(res,SESSION.get(sessionattr),SESSION.get(sessionvalue),'==')
        masterType = filter(lambda x: x['id']==SESSION.get(sessionattr),metaObj['attrs'][1:])[0]['type']
        master = filter(lambda x: x.meta_id==masterType,self.getParentNode().objectValues(['ZMSCustom']))[0]
        masterMetaObj = self.getMetaobj(masterType)
        masterAttrs = masterMetaObj['attrs']
        masterRows = master.getObjProperty(masterAttrs[0]['id'],REQUEST)
        masterRows = self.filter_list(masterRows,masterAttrs[1]['id'],SESSION.get(sessionvalue),'==')
        REQUEST.set('masterMetaObj',masterMetaObj)
        REQUEST.set('masterRow',masterRows[0])
      
      # Filter (Custom).
      SESSION.set('qfilters',REQUEST.form.get('qfilters',SESSION.get('qfilters',1)))
      for i in range(SESSION['qfilters']):
        filterattr='filterattr%i'%i
        filtervalue='filtervalue%i'%i
        sessionattr='%s_%s'%(filterattr,self.id)
        sessionvalue='%s_%s'%(filtervalue,self.id)
        
        #-- Set filter parameters in Session
        if REQUEST.get('action','')=='':
          if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
            SESSION.set(sessionattr,'')
            SESSION.set(sessionvalue,'')
          elif REQUEST.get('btn','')==self.getZMILangStr('BTN_REFRESH'):
            SESSION.set(sessionattr,REQUEST.form.get(filterattr,''))
            SESSION.set(sessionvalue,REQUEST.form.get(filtervalue,''))
        
        #-- Apply filter parameters 
        for attr in metaObj['attrs'][1:]:
          if attr.get('name','')!='':
            if SESSION.get(sessionattr,'') == attr['id'] and \
               SESSION.get(sessionvalue,'') != '':
              attr['datatype_key'] = _globals.datatype_key(attr['type'])
              if attr['datatype_key'] in _globals.DT_NUMBERS:
                res = self.filter_list(res,attr['id'],self.formatObjAttrValue(attr,SESSION.get(sessionvalue,''),REQUEST['lang']))
              else:
                res = self.filter_list(res,attr['id'],SESSION.get(sessionvalue,''))
      
      REQUEST.set('res_id',res_id)
      REQUEST.set('res_abs',res_abs)
      REQUEST.set('res',res)
      
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Sort:
    # --------------------------------------------------------------------------
    def recordSet_Sort(self, REQUEST):
      """
      Sort record-set.
      """
      metaObj = self.getMetaobj(self.meta_id)
      
      res = REQUEST['res']
      qorder = REQUEST.get('qorder','')
      qorderdir = REQUEST.get('qorderdir','asc')
      for attr in metaObj['attrs'][1:]:
        if attr['id'] == 'sort_id':
          qorder = attr['id']
        if qorder=='':
          if attr.get('type','') not in [ 'constant', 'file', 'image', 'resource'] and \
             attr.get('type','') not in self.getMetaobjIds() and \
             attr.get('name','') != '' and \
             attr.get('custom','') != '':
            qorder = attr['id']
            if attr.get('type','') in ['date','datetime','time']:
              qorderdir = 'desc'
      res = self.sort_list(res,qorder,qorderdir)
      
      REQUEST.set('res',res)
      REQUEST.set('qorder',qorder)
      REQUEST.set('qorderdir',qorderdir)
      
      return res


    # --------------------------------------------------------------------------
    #  ZMSCustom.recordSet_Export:
    # --------------------------------------------------------------------------
    def recordSet_Export(self, lang, qorder, qorderdir, qindex=[], REQUEST=None, RESPONSE=None):
      """
      Export record-set to XML.
      """
      self.recordSet_Init(REQUEST)
      self.recordSet_Filter(REQUEST)
      self.recordSet_Sort(REQUEST)
      res=REQUEST['res']
      value = []
      for i in range(len(res)):
        if len(qindex)==0 or str(i) in qindex:
          value.append(res[i])
      RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
      RESPONSE.setHeader('Content-Disposition','inline;filename=recordSet_Export.xml')
      export = self.getXmlHeader() + self.toXmlString(value,True)
      return export


    ############################################################################
    #  ZMSCustom.manage_import:
    #
    #  Import XML-file.
    ############################################################################
    def manage_import(self, file, lang, REQUEST, RESPONSE):
      """ ZMSCustom.manage_import """
      message = ''
      
      if self.meta_id=='ZMSSysFolder':
        import os, tempfile
        # Create temporary folder.
        folder = tempfile.mktemp()
        os.mkdir(folder)
        # Save to temporary file.
        filename = _fileutil.getOSPath('%s/%s'%(folder,_fileutil.extractFilename(file.filename)))
        _fileutil.exportObj(file,filename)
        if _fileutil.extractFileExt(filename) == 'zip':
          _fileutil.extractZipArchive(filename)
          _fileutil.remove(filename)
        # Import temporary file.
        _fileutil.importPath(self,folder)
        # Remove temporary files.
        _fileutil.remove(folder,deep=1)
        # Message.
        message += self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%_fileutil.extractFilename(file.filename))
      elif self.getType()=='ZMSRecordSet':
        message += parseXmlString( self, file)
      # Import XML-file.
      else:
        message += _importable.importFile( self, file, REQUEST, _importable.importContent)
      
      # Return with message.
      message = urllib.quote(message)
      return REQUEST.RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,message))

################################################################################
