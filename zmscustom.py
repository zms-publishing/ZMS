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
  message = ''
  messagekey = 'manage_tabs_message'
  t0 = time.time()
  target = self.absolute_url()
  
  if REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
    
    # Create
    id_prefix = _globals.id_prefix(REQUEST.get('id_prefix','e'))
    new_id = self.getNewId(id_prefix)
    globalAttr = self.dGlobalAttrs.get(meta_id,self.dGlobalAttrs['ZMSCustom'])
    constructor = globalAttr.get('obj_class',self.dGlobalAttrs['ZMSCustom']['obj_class'])
    obj = constructor(new_id,_sort_id+1,meta_id)
    self._setObject(obj.id, obj)
    
    metaObj = self.getMetaobj( meta_id)
    redirect_self = bool( REQUEST.get( 'redirect_self', 0)) or REQUEST.get( 'btn', '') == '' or metaObj['type'] == 'ZMSRecordSet'
    for attr in metaObj['attrs']:
      attr_type = attr['type']
      redirect_self = redirect_self or attr_type in self.getMetaobjIds()+['*']
    redirect_self = redirect_self and not REQUEST.get('btn','') in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]
    
    obj = getattr(self,obj.id)
    try:
      # Object State
      obj.setObjStateNew(REQUEST)
      # Init Coverage
      coverage = self.getDCCoverage(REQUEST)
      if coverage.find('local.')==0:
        obj.setObjProperty('attr_dc_coverage',coverage)
      else:
        obj.setObjProperty('attr_dc_coverage','global.'+lang)
      # Change Properties
      obj.changeProperties(lang)
      # Normalize Sort-Ids
      self.normalizeSortIds(id_prefix)
      # Message
      message = self.getZMILangStr('MSG_INSERTED')%obj.display_type(REQUEST)
    except:
      message = _globals.writeError(self,"[manage_addZMSCustom]")
      messagekey = 'manage_tabs_error_message'
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    
    # Return with message.
    if redirect_self:
      target = '%s/%s'%(target,obj.id)
    target = REQUEST.get( 'manage_target', '%s/manage_main'%target)
    target = self.url_append_params( target, { 'lang': lang, messagekey: message})
    target = '%s#zmi_item_%s'%( target, obj.id)
    RESPONSE.redirect(target)
  
  else:
    RESPONSE.redirect('%s/manage_main?lang=%s'%(target,lang))


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
      pc = 'e' in map(lambda x:x['id'],self.getMetaobjAttrs(self.meta_id,types=['*']))
      opts = []
      opts.append({'label': 'TAB_EDIT',         'action': 'manage_main'})
      if pc:
        opts.append({'label': 'TAB_PROPERTIES', 'action': 'manage_properties'})
      opts.append({'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'})
      opts.append({'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'})
      if not self.getAutocommit() or self.getHistory():
        opts.append({'label': 'TAB_HISTORY',    'action': 'manage_UndoVersionForm'})
      for metaObjAttr in filter(lambda x:x['id'].startswith('manage_tab'),self.getMetaobjAttrs(self.meta_id)):
        opt = {'label': metaObjAttr['name'],    'action': 'manage_executeMetacmd', 'alias':metaObjAttr['id'], 'params':{'id':metaObjAttr['id']}}
        opts.append(opt)
      for metaCmd in self.getMetaCmds(self,'tab'):
        opt = {'label': metaCmd['name'],        'action': 'manage_executeMetacmd', 'alias':metaCmd['id'], 'params':{'id':metaCmd['id']}}
        opts.append(opt)
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
        'manage_UndoVersionForm','manage_UndoVersion',
        'manage_wfTransition', 'manage_wfTransitionFinalize',
        'manage_userForm', 'manage_user',
        'manage_importexport', 'manage_import', 'manage_export',
        'manage_executeMetacmd',
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
    def __init__(self, id='', sort_id=0, meta_id=None):
      """ ZMSCustom.__init__ """
      ZMSContainerObject.__init__(self,id,sort_id)
      self.meta_id = _globals.nvl(meta_id,self.meta_type)


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
      request = self.REQUEST
      metaObj = self.getMetaobj(self.meta_id)
      res_id = metaObj['attrs'][0]['id']
      res = self.getObjProperty(res_id,REQUEST)
      REQUEST.set('res_abs',res)
      REQUEST.set('res',res)
      return res


    """
    Filter record-set.
    @return: filtered list of records
    @rtype: C{list}
    """
    def recordSet_Filter(self, REQUEST):
      SESSION = REQUEST.SESSION
      metaObj = self.getMetaobj(self.meta_id)
      res = REQUEST['res']
      # foreign key
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
      # init filter from request.
      for filterIndex in range(100):
        for filterStereotype in ['attr','op','value']:
          requestkey = 'filter%s%i'%(filterStereotype,filterIndex)
          sessionkey = '%s_%s'%(requestkey,self.id)
          requestvalue = REQUEST.form.get(requestkey,SESSION.get(sessionkey,''))
          if REQUEST.get('btn','')==self.getZMILangStr('BTN_RESET'):
            requestvalue = ''
          REQUEST.set(requestkey,requestvalue)
          SESSION.set(sessionkey,requestvalue)
      SESSION.set('qfilters_%s'%self.id,REQUEST.form.get('qfilters',SESSION.get('qfilters_%s'%self.id,1)))
      # apply filter
      for filterIndex in range(100):
        suffix = '%i_%s'%(filterIndex,self.id)
        sessionattr = SESSION.get('filterattr%s'%suffix,'')
        sessionop = SESSION.get('filterop%s'%suffix,'%')
        sessionvalue = SESSION.get('filtervalue%s'%suffix,'')
        if sessionattr and sessionvalue:
          metaObjAttr = self.getMetaobjAttr(self.meta_id,sessionattr)
          sessionvalue = self.formatObjAttrValue(metaObjAttr,sessionvalue,REQUEST['lang'])
          res = self.filter_list(res,sessionattr,sessionvalue,sessionop)
      REQUEST.set('res',res)
      return res


    """
    Sort record-set.
    @return: sorted list of records
    @rtype: C{list}
    """
    def recordSet_Sort(self, REQUEST=None):
      request = self.REQUEST
      metaObj = self.getMetaobj(self.meta_id)
      res = request['res']
      
      if 'sort_id' in map(lambda x:x['id'],metaObj['attrs']):
        l = map(lambda x:(x.get('sort_id',1),x),res)
        # Sort (FK).
        for metaObjAttr in metaObj['attrs'][1:]:
          if metaObjAttr.get('type','') in self.getMetaobjIds():
            d = {}
            # FK-id for primary-sort.
            map(lambda x:self.operator_setitem(d,x.get(metaObjAttr['id']),x.get(metaObjAttr['id'])),res)
            for fkContainer in self.getParentNode().getChildNodes(request,metaObjAttr['type']):
              fkMetaObj = self.getMetaobj(fkContainer.meta_id)
              fkMetaObjAttrIdRecordSet = fkMetaObj['attrs'][0]['id']
              if 'sort_id' in map(lambda x:x['id'],metaObj['attrs']):
                fkMetaObjRecordSet = fkContainer.attr(fkMetaObjAttrIdRecordSet)
                fkMetaObjIdId = self.getMetaobjAttrIdentifierId(fkContainer.meta_id)
                # FK-sort_id for primary-sort.
                map(lambda x:self.operator_setitem(d,x.get(fkMetaObjIdId),x.get('sort_id')),fkMetaObjRecordSet)
            # Add primary-sort.
            l = map(lambda x:((d.get(x[1].get(metaObjAttr['id'])),x[0]),x[1]),l)
            break
        l.sort()
        res = map(lambda x:x[1],l)
      else:
        qorder = request.get('qorder','')
        qorderdir = 'asc'
        if qorder == '':
          skiptypes = [ 'file', 'image']+self.getMetaobjManager().valid_xtypes+self.getMetaobjIds()
          for attr in metaObj['attrs'][1:]:
            if attr.get('type','') not in skiptypes and \
               attr.get('name','') != '' and \
               attr.get('custom','') != '':
              qorder = attr['id']
              if attr.get('type','') in ['date','datetime','time']:
                qorderdir = 'desc'
              break
        if qorder:
          qorderdir = request.get('qorderdir',qorderdir)
          res = self.sort_list(res,qorder,qorderdir)
          request.set('qorder',qorder)
          request.set('qorderdir',qorderdir)
        
      request.set('res',res)
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


    # --------------------------------------------------------------------------
    #  ZMSCustom.getEntityRecordHandler
    # --------------------------------------------------------------------------
    def getEntityRecordHandler(self, id):
      class EntityRecordHandler:
        def __init__(self, parent, id):
          self.parent = parent 
          self.id = id
          self.fk = {}
          metaObjIds = parent.getMetaobjIds()
          for k in parent.getMetaobjAttrIds(id):
            metaObjAttr = parent.getMetaobjAttr(id,k)
            if metaObjAttr['type'] in metaObjIds:
              fkMetaObj = parent.getMetaobj(metaObjAttr['type'])
              fkMetaObjIdId = fkMetaObj['attrs'][0]['id']
              for fkContainer in parent.getParentNode().getChildNodes(self.parent.REQUEST,metaObjAttr['type']):
                fkMetaObj = parent.getMetaobj(fkContainer.meta_id);
                fkMetaObjAttrIdRecordSet = fkMetaObj['attrs'][0]['id'];
                fkMetaObjRecordSet = fkContainer.attr(fkMetaObjAttrIdRecordSet);
                fkMetaObjIdId = parent.getMetaobjAttrIdentifierId(fkContainer.meta_id)
                self.fk[k] = {'fkMetaObj':fkMetaObj,'fkMetaObjRecordSet':fkMetaObjRecordSet,'fkMetaObjIdId':fkMetaObjIdId}
        __call____roles__ = None
        def __call__(self, r):
          d = {}
          for k in r.keys():
            v = r[k]
            if k in self.fk.keys():
              fk = self.fk[k]
              fkMetaObj = fk['fkMetaObj']
              fkMetaObjRecordSet = fk['fkMetaObjRecordSet']
              fkMetaObjIdId = fk['fkMetaObjIdId']
              for fkMetaObjRecord in filter(lambda x:x.get(fkMetaObjIdId)==v,fkMetaObjRecordSet):
                fkMetaObjAttrs = filter(lambda x:x['type']=='string' and fkMetaObjRecord.get(x['id'],'')!='',fkMetaObj['attrs'])
                v = ', '.join(map(lambda x:str(fkMetaObjRecord.get(x['id'])),fkMetaObjAttrs))
            d[k] =  v
          return d
      return EntityRecordHandler(self,id)


    ############################################################################
    #  ZMSCustom.manage_changeRecordSet:
    #
    #  Change record-set.
    ############################################################################
    def manage_changeRecordSet(self, lang, btn, action, REQUEST, RESPONSE):
      """ ZMSCustom.manage_changeRecordSet """
      message = ''
      messagekey = 'manage_tabs_message'
      target = REQUEST.get('target','manage_main')
      params = {'lang':lang}
      t0 = time.time()
      
      if btn not in [ self.getZMILangStr('BTN_CANCEL'), self.getZMILangStr('BTN_BACK')]:
        try:
          ##### Object State #####
          self.setObjStateModified(REQUEST)
          
          metaObj = self.getMetaobj(self.meta_id)
          metaObjAttrIds = self.getMetaobjAttrIds(self.meta_id)
          res_abs = self.recordSet_Init(REQUEST)
          if action == 'insert':
            row = {}
            row['_created_uid'] = REQUEST['AUTHENTICATED_USER'].getUserName()
            row['_created_dt'] = _globals.getDateTime( time.time())
            row['_change_uid'] = REQUEST['AUTHENTICATED_USER'].getUserName()
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
            params['qindex'] = len(res_abs)-1
            message = self.getZMILangStr('MSG_INSERTED')%self.getZMILangStr('ATTR_RECORD')
          elif action == 'update':
            row = res_abs[REQUEST['qindex']]
            row['_change_uid'] = REQUEST['AUTHENTICATED_USER'].getUserName()
            row['_change_dt'] = _globals.getDateTime( time.time())
            for metaObjAttr in metaObj['attrs'][1:]:
              objAttr = self.getObjAttr(metaObjAttr['id'])
              objAttrName = self.getObjAttrName(objAttr,lang)
              if metaObjAttr['type'] in self.metaobj_manager.valid_types or \
                 metaObjAttr['type'] not in self.metaobj_manager.valid_xtypes+self.metaobj_manager.valid_zopetypes:
                set,value = True,self.formatObjAttrValue(objAttr,REQUEST.get(objAttrName),lang)
                try: del value['aq_parent']
                except: pass
                if value is None and metaObjAttr['id'] == 'sort_id':
                  value = len(res_abs)
                if value is None and metaObjAttr['type'] in ['file','image'] and int(REQUEST.get('del_%s'%objAttrName,0)) == 0:
                  set = False
                if set:
                  row[metaObjAttr['id']] = value
            res_abs[REQUEST['qindex']] = row
            params['qindex'] = REQUEST['qindex']
            message = self.getZMILangStr('MSG_CHANGED')
          elif action == 'delete':
            rows = map(lambda x: res_abs[int(x)], REQUEST.get('qindices',[]))
            for row in rows:
              del res_abs[res_abs.index(row)]
            message = self.getZMILangStr('MSG_DELETED')%len(rows)
          elif action == 'move':
            for row in res_abs:
              row['sort_id'] = row.get('sort_id',1)*10
            pos = REQUEST['pos']
            newpos = REQUEST['newpos']
            row = res_abs[REQUEST['qindex']]
            row['sort_id'] = row['sort_id']+(newpos-pos)*15
            params['qindex'] = REQUEST['qindex']+(newpos-pos)
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%('%s %i'%(self.getZMILangStr('ATTR_RECORD'),pos),newpos)
          # Normalize sort-ids.
          if 'sort_id' in metaObjAttrIds:
            res_abs = self.sort_list(res_abs,'sort_id')
            for i in range(len(res_abs)):
              row = res_abs[i]
              row['sort_id'] = i+1
          self.setObjProperty(metaObj['attrs'][0]['id'],res_abs,lang)
          
          ##### VersionManager ####
          self.onChangeObj(REQUEST)
        except:
          message = _globals.writeError(self,"[manage_changeProperties]")
          messagekey = 'manage_tabs_error_message'
        
        message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      
      # Return with message.
      params[messagekey] = message
      target = self.url_append_params( target, params)
      return REQUEST.RESPONSE.redirect(target)


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
