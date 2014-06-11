################################################################################
# zmscustom.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from types import StringTypes
import Globals
import sys
import time
import urllib
# Product Imports.
from zmscontainerobject import ZMSContainerObject
import _confmanager
import _fileutil
import _globals
import _importable
import _ziputil


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
manage_addZMSCustomForm = PageTemplateFile('manage_addzmscustomform', globals()) 
def manage_addZMSCustom(self, meta_id, lang, _sort_id, REQUEST, RESPONSE):
  """ manage_addZMSCustom """
  
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    ##### Create ####
    id_prefix = _globals.id_prefix(REQUEST.get('id_prefix','e'))
    new_id = self.getNewId(id_prefix)
    obj = ZMSCustom(new_id,_sort_id+1,meta_id)
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
      RESPONSE.redirect('%s/manage_main?lang=%s&manage_tabs_message=%s#zmi_item_%s'%(self.absolute_url(),lang,urllib.quote(message),obj.id))
  
  else:
    RESPONSE.redirect('%s/manage_main?lang=%s'%(self.absolute_url(),lang))


def containerFilter(container):
  return container.meta_type.startswith('ZMS')


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMSCustom(ZMSContainerObject):

    # Create a SecurityInfo for this class. We will use this
    # in the rest of our class definition to make security
    # assertions.
    security = ClassSecurityInfo()

    # Properties.
    # -----------
    meta_type = "ZMSCustom"

    # Management Options.
    # -------------------
    def manage_options(self):
      pc = self.isPageContainer()
      opts = []
      opts.append({'label': 'TAB_EDIT',         'action': 'manage_main'})
      if pc:
        opts.append({'label': 'TAB_PROPERTIES', 'action': 'manage_properties'})
      opts.append({'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'})
      if pc:
        opts.append({'label': 'TAB_TASKS',        'action': 'manage_tasks'})
      opts.append({'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'})
      if not self.getAutocommit() or self.getHistory():
        opts.append({'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'})
      if pc:
        opts.append({'label': 'TAB_SEARCH',       'action': 'manage_search'})
      opts.append({'label': 'TAB_PREVIEW',      'action': 'preview_html'})
      return tuple(opts)

    # Management Permissions.
    # -----------------------
    __authorPermissions__ = (
        'manage','manage_main','manage_main_iframe','manage_container','manage_workspace',
        'manage_menu',
        'manage_addZMSModule',
        'manage_changeRecordSet',
        'manage_properties','manage_changeProperties','manage_changeTempBlobjProperty',
        'manage_deleteObjs','manage_undoObjs','manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
        'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
        'manage_ajaxDragDrop','manage_ajaxZMIActions',
        'manage_search','manage_tasks',
        'manage_UndoVersionForm','manage_UndoVersion',
        'manage_wfTransition', 'manage_wfTransitionFinalize',
        'manage_userForm', 'manage_user',
        'manage_importexport', 'manage_import', 'manage_export',
        'GET', 'PUT',
        )
    __viewPermissions__ = (
        'manage_ajaxGetChildNodes',
        )
    __ac_permissions__=(
        ('ZMS Author', __authorPermissions__),
        ('View', __viewPermissions__),
        )


    # Templates.
    # ----------
    manage_properties = PageTemplateFile('zpt/ZMSObject/manage_main', globals())
    manage_main_iframe = PageTemplateFile('zpt/ZMSObject/manage_main_iframe', globals())
    manage_menu = PageTemplateFile('zpt/object/manage_menu', globals())
    metaobj_recordset_main_grid = PageTemplateFile('zpt/ZMSRecordSet/main_grid', globals())
    metaobj_recordset_main = PageTemplateFile('zpt/ZMSRecordSet/main', globals())
    metaobj_recordset_input_fields = PageTemplateFile('zpt/ZMSRecordSet/input_fields', globals())


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

    """
    Initialize record-set.
    @return: list of records
    @rtype: C{list}
    """
    def recordSet_Init(self, REQUEST):
      metaObj = self.getMetaobj(self.meta_id)
      res_id = metaObj['attrs'][0]['id']
      res = self.getObjProperty(res_id,REQUEST)
      REQUEST.set('res_id',res_id)
      REQUEST.set('res_abs',res)
      REQUEST.set('res',res)
      return res


    """
    Filter record-set.
    @return: filtered list of records
    @rtype: C{list}
    """
    def recordSet_Filter(self, REQUEST):
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
          elif REQUEST.get('btn','') in [self.getZMILangStr('BTN_REFRESH'),self.getZMILangStr('BTN_SEARCH')]:
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


    """
    Sort record-set.
    @return: sorted list of records
    @rtype: C{list}
    """
    def recordSet_Sort(self, REQUEST):
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
    security.declareProtected('View', 'recordSet_Export')
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
      RESPONSE.setHeader('Content-Disposition','attachment;filename="recordSet_Export.xml"')
      export = self.getXmlHeader() + self.toXmlString(value,True)
      return export


    ############################################################################
    #  ZMSCustom.manage_changeRecordSet:
    #
    #  Change record-set.
    ############################################################################
    def manage_changeRecordSet(self, lang, btn, action, REQUEST, RESPONSE):
      """ ZMSCustom.manage_changeRecordSet """
      message = ''
      messagekey = 'manage_tabs_message'
      t0 = time.time()
      
      if btn not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
          ##### Object State #####
          self.setObjStateModified(REQUEST)
          
          metaObj = self.getMetaobj(self.meta_id)
          res_abs = self.recordSet_Init(REQUEST)
          if action == 'insert':
            row = {}
            row['_created_uid'] = REQUEST['AUTHENTICATED_USER'].getId()
            row['_created_dt'] = _globals.getDateTime( time.time())
            row['_change_uid'] = REQUEST['AUTHENTICATED_USER'].getId()
            row['_change_dt'] = _globals.getDateTime( time.time())
            for metaObjAttr in metaObj['attrs'][1:]:
              objAttr = self.getObjAttr(metaObjAttr['id'])
              objAttrName = self.getObjAttrName(objAttr,lang)
              if metaObjAttr['type'] in self.metaobj_manager.valid_types or \
                 metaObjAttr['type'] not in self.metaobj_manager.valid_xtypes+self.metaobj_manager.valid_zopetypes:
                value = self.formatObjAttrValue(objAttr,REQUEST.get(objAttrName),lang)
                try: del value['aq_parent']
                except: pass
                if metaObjAttr['id'] == 'sort_id' and value is None:
                  value = len(res_abs)
                row[metaObjAttr['id']] = value
            res_abs.append(row)
            message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_RECORD')
          elif action == 'update':
            row = res_abs[REQUEST['qindex']]
            row['_change_uid'] = REQUEST['AUTHENTICATED_USER'].getId()
            row['_change_dt'] = _globals.getDateTime( time.time())
            for metaObjAttr in metaObj['attrs'][1:]:
              objAttr = self.getObjAttr(metaObjAttr['id'])
              objAttrName = self.getObjAttrName(objAttr,lang)
              if metaObjAttr['type'] in self.metaobj_manager.valid_types or \
                 metaObjAttr['type'] not in self.metaobj_manager.valid_xtypes+self.metaobj_manager.valid_zopetypes:
                value = self.formatObjAttrValue(objAttr,REQUEST.get(objAttrName),lang)
                try: del value['aq_parent']
                except: pass
                if metaObjAttr['id'] == 'sort_id' and value is None:
                  value = len(res_abs)
                row[metaObjAttr['id']] = value
            res_abs[REQUEST['qindex']] = row
            message = self.getZMILangStr('MSG_CHANGED')
          elif action == 'delete':
            rows = map(lambda x: res_abs[int(x)], REQUEST.get('qindices',[]))
            for row in rows:
              del res_abs[res_abs.index(row)]
            message = self.getZMILangStr('MSG_DELETED')%len(rows)
          elif action == 'move':
            pos = REQUEST['pos']
            newpos = REQUEST['newpos']
            sibling_sort_ids = map(lambda x: (x+1)*10, range(len(res_abs)))
            sibling_sort_ids.remove(pos*10)
            if newpos-1 < len(sibling_sort_ids):
              new_sort_id = sibling_sort_ids[newpos-1]-1
            else:
              new_sort_id = sibling_sort_ids[-1]+1
            res_abs = self.sort_list(res_abs,'sort_id')
            for i in range(len(res_abs)):
              row = res_abs[i]
              if i == pos - 1:
                row['sort_id'] = new_sort_id
              else:
                row['sort_id'] = row['sort_id']*10
            # Normalize sort-ids.
            res_abs = self.sort_list(res_abs,'sort_id')
            for i in range(len(res_abs)):
              row = res_abs[i]
              row['sort_id'] = i+1
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%('%s %i'%(self.getZMILangStr('ATTR_RECORD'),pos),newpos)
          self.setObjProperty(metaObj['attrs'][0]['id'],res_abs,lang)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
        except:
          message = _globals.writeError(self,"[manage_changeProperties]")
          messagekey = 'manage_tabs_error_message'
        
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      message = urllib.quote(message)
      return REQUEST.RESPONSE.redirect('manage_main?lang=%s&%s=%s'%(lang,messagekey,message))


    ############################################################################
    #  ZMSCustom.manage_import:
    #
    #  Import XML-file.
    ############################################################################
    def manage_import(self, file, lang, REQUEST, RESPONSE=None):
      """ ZMSCustom.manage_import """
      ob = self
      message = ''
      
      if self.meta_id=='ZMSSysFolder':
        _ziputil.importZip2Zodb( self, file)
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%_fileutil.extractFilename(file.filename))
      
      elif self.getType()=='ZMSRecordSet':
        message = parseXmlString( self, file)
      
      else:
        ob = _importable.importFile( self, file, REQUEST, _importable.importContent)
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%ob.display_type(REQUEST))
      
      # Return with message.
      if RESPONSE is not None:
        message = urllib.quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s'%(lang,message))
      else:
        return ob


# call this to initialize framework classes, which
# does the right thing with the security assertions.
Globals.InitializeClass(ZMSCustom)

################################################################################
