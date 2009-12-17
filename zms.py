################################################################################
# zms.py
#
# $Id: zms.py,v 1.13 2004/03/24 18:05:13 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.13 $
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
from AccessControl.User import UserFolder
from App.Common import package_home
from App.special_dtml import HTMLFile
from OFS.Image import Image
from sys import *
import copy
import os
import shutil
import sys
import time
import urllib
# Product imports.
import _accessmanager
import _builder
import _confmanager
import _enummanager
import _fileutil
import _ftpmanager
import _globals
import _importable
import _language
import _multilangmanager
import _objattrs
import _xmllib
import _zcatalogmanager
import _zmsattributecontainer
import zmscontainerobject
import ZMSMetamodelProvider, ZMSFormatProvider
from _versionmanager import getObjStates
from zmscustom import ZMSCustom
from zmslinkcontainer import ZMSLinkContainer
from zmslinkelement import ZMSLinkElement
from zmslog import ZMSLog
from zmssqldb import ZMSSqlDb
from zmstrashcan import ZMSTrashcan

__all__= ['ZMS']


################################################################################
################################################################################
###
###  Common Function(s)
###
################################################################################
################################################################################

# ------------------------------------------------------------------------------
#  ZMS.recurse_cleanArtefacts:
#
#  Clean artefacts.
# ------------------------------------------------------------------------------
def recurse_cleanArtefacts( self, level=0):
  from OFS.CopySupport import absattr
  # Recursion.
  last_id = None
  for ob in self.objectValues():
    if absattr(self.id) == absattr(ob.id):
      print (" "*level)+"recurse_cleanArtefacts", ob.absolute_url(), ob.meta_type
      raise "InfiniteRecursionError"
    else:
      try:
        recurse_cleanArtefacts( ob, level+1)
      except "InfiniteRecursionError":
        print (" "*level)+"recurse_cleanArtefacts: clean artefact ", ob.absolute_url(), ob.meta_type
        self._delObject(absattr(ob.id), suppress_events=True)


# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionBuild:
#
#  Update version build.
# ------------------------------------------------------------------------------
def recurse_updateVersionBuild(docElmnt, self, REQUEST):
  message = ''

  ##### Build 130a: ZMS Standard-Objects ####
  if getattr( docElmnt, 'build', '000') < '130':
    if self.meta_type == 'ZMS':
      
      ### Managers.
      try:
        self.metaobj_manager
      except:
        model = self.getConfProperty('ZMS.custom.objects',{})
        for meta_id in model.keys():
          metaObj = model[meta_id]
          if metaObj.get('acquired',0) == 0:
            for attr in metaObj.get('__obj_attrs__',metaObj.get('attrs')):
              if attr['type'] in [ 'method']:
                home = self.Special_Objects
                ob = getattr( home, meta_id+'.'+attr['id'], None)
                if ob is not None:
                  attr['custom'] = ob.raw
              elif attr['type'] in [ 'DTML Method', 'DTML Document', 'Script (Python)']:
                home = self.getHome()
                ob = getattr( home, attr['id'], None)
                if ob is not None:
                  if ob.meta_type in [ 'DTML Method', 'DTML Document']:
                    attr['custom'] = ob.raw
                  elif ob.meta_type in [ 'Script (Python)']:
                    attr['custom'] = ob.body()
        metas=self.getConfProperty('ZMS.custom.metas',[])
        manager = ZMSMetamodelProvider.ZMSMetamodelProvider(model,metas)
        self._setObject( manager.id, manager)
        self.delConfProperty('ZMS.custom.objects')
        self.delConfProperty('ZMS.custom.metas')
      try:
        self.format_manager
      except:
        default = self.getConfProperty('ZMS.custom.textformats.default','body')
        textformats = self.getConfProperty('ZMS.custom.textformats',[])
        for x in range(len(textformats)/2):
          i = textformats[x*2]
          d = textformats[x*2+1]
          d['default'] = d.get('default',int(i==default))
        charformats = self.getConfProperty('ZMS.custom.charformats',[])
        for d in charformats:
          id = self.id_quote(d.get('display',''))
          if len(id) == 0:
            id = self.getNewId('fmt')
          d['id'] = d.get('id',id)
        manager = ZMSFormatProvider.ZMSFormatProvider(textformats)
        self._setObject( manager.id, manager)
        manager = getattr( self, manager.id)
        manager.importCharformatXml( self.toXmlString(charformats))
        self.delConfProperty('ZMS.custom.textformats')
        self.delConfProperty('ZMS.custom.textformats.default')
        self.delConfProperty('ZMS.custom.charformats')
      
      # Import / acquire standard-object-model.
      portalMaster = self.getPortalMaster()
      _confmanager.initConf(self, 'zms.metaobj', REQUEST)
      # Refactor API.
      home = self.getHome()
      for dtml_method in home.objectValues( ['DTML Method']):
        modified = False
        data = dtml_method.raw
        if data.find( '"getTeaserElements(REQUEST)"') > 0:
          data = data.replace( '"getTeaserElements(REQUEST)"', 'getTeaserElements')
          modified = True
        if data.find( '"getLinkList(REQUEST)"') > 0:
          data = data.replace( '"getLinkList(REQUEST)"', 'getLinkList')
          modified = True
        if modified:
          dtml_method.manage_edit( title=dtml_method.title, data=data)
      # Refactor metamodel.
      obs = self.metaobj_manager.model
      for id in obs.keys():
        ob = obs[id]
        ob[ 'id'] = id
        ob[ 'enabled'] = ob.get( 'enabled', self.getConfProperty('%s.enabled'%id,1))
        self.metaobj_manager.setMetaobj(ob)
        if ob.get('acquired',0) == 0:
          ob = self.getMetaobj( id)
          # Convert resources to files in metamodel-provider.
          for attr in ob['attrs']:
            if attr['type'] == 'resource':
              self.metaobj_manager.setMetaobjAttr(id,attr['id'],attr['id'],attr['name'],newType=attr['type'],newCustom=attr['custom'],zms_system=ob['zms_system'])
          # Convert metamodel templates to attributes.
          tmpltId = self.metaobj_manager.getTemplateId( id)
          if ob['type'] not in [ 'ZMSLibrary', 'ZMSPackage', 'ZMSModule'] and not tmpltId in self.getMetaobjAttrIds( id):
            tmpltName = 'Template: %s'%ob['name']
            tmplt = getattr( self, tmpltId, None)
            if tmplt:
              tmpltCustom = tmplt.raw
              self.metaobj_manager.setMetaobjAttr(id,tmpltId,tmpltId,tmpltName,newType='DTML Method',newCustom=tmpltCustom,zms_system=ob['zms_system'])
      # Convert meta-data semantics (i).
      metaDictAttrs = self.metaobj_manager.metas
      for i in range( len( metaDictAttrs) / 2):
        key = metaDictAttrs[ i*2]
        metaDictAttr = metaDictAttrs[ i*2+1]
        dst_meta_types = metaDictAttr.get('dst_meta_types',[])
        if metaDictAttr['type'] in self.metaobj_manager.valid_datatypes:
          metaDictId = key
        elif metaDictAttr['type'] == '' and metaDictAttr.get('acquired',0) == 1 and self.metaobj_manager.getMetadictAttr(key) is not None:
          metaDictId = key
          for metaObjId in portalMaster.metaobj_manager.getMetaobjIds():
            if metaDictId in portalMaster.metaobj_manager.getMetadictAttrs( metaObjId):
              dst_meta_types.append( metaObjId)
        else:
          metaDictId = metaDictAttr[ 'id']
        for dst_meta_type in dst_meta_types:
          metaObj = self.getMetaobj( dst_meta_type)
          if metaObj is not None:
            if metaDictId in self.getMetaobjAttrIds( dst_meta_type):
              metaObjAttr = self.getMetaobjAttr( dst_meta_type, metaDictId)
              if metaObjAttr['type'] != metaDictId:
                self.metaobj_manager.delMetaobjAttr( dst_meta_type, metaDictId)
            if metaDictId not in self.getMetaobjAttrIds( dst_meta_type):
              try:
                self.metaobj_manager.setMetaobjAttr(dst_meta_type,None,metaDictId,'',0,0,0,metaDictId,zms_system=int(metaObj.get('zms_system',0) and metaDictAttr.get('zms_system',0)))
              except:
                print "[recurse_updateVersionBuild]: can't setMetaobjAttr",self.getHome().id,dst_meta_type,None,metaDictId
        try:
          del metaDictAttr['dst_meta_types']
        except:
          pass
      # Convert meta-data semantics (ii).
      new_obs = []
      obs = self.metaobj_manager.metas
      if 'titlealt' not in obs:
        key = 'titlealt'
        if portalMaster is None:
          ob = {'id':key,'acquired':0,'name':'DC.Title.Alt','type':'string','mandatory':1,'multilang':1,'repetitive':0,'zms_system':1}
        else:
          ob = {'id':key,'acquired':1,'name':'','type':'','mandatory':1,'multilang':1,'repetitive':0,'zms_system':1}
        new_obs.extend( [key,ob])
      if 'title' not in obs:
        key = 'title'
        if portalMaster is None:
          ob = {'id':key,'acquired':0,'name':'DC.Title','type':'string','mandatory':1,'multilang':1,'repetitive':0,'zms_system':1}
        else:
          ob = {'id':key,'acquired':1,'name':'','type':'','mandatory':1,'multilang':1,'repetitive':0,'zms_system':1}
        new_obs.extend( [key,ob])
      for i in range(len(obs)/2):
        key = obs[i*2]
        ob = obs[i*2+1]
        if (ob['type'] in self.metaobj_manager.valid_datatypes) or \
           (ob['type'] in [''] and ob.get('acquired',0) and portalMaster is not None and \
             portalMaster.metaobj_manager.getMetadictAttr(key) is not None and \
             portalMaster.metaobj_manager.getMetadictAttr(key)['type'] in self.metaobj_manager.valid_datatypes):
          # ob['name'] = ob['id']
          ob['id'] = key
        else:
          key = ob['id']
        new_obs.extend( [key,ob])
      self.metaobj_manager.metas = copy.deepcopy(new_obs)
      # Synchronize.
      self.synchronizeObjAttrs()
      # Acquired standard-objects?
      if portalMaster is not None:
        obs = filter( lambda x: x.get('package') == 'com.zms.foundation', self.metaobj_manager.model.values())
        obsMaster = filter( lambda x: x.get('package') == 'com.zms.foundation', portalMaster.metaobj_manager.model.values())
        ids = map( lambda x: x['id'], obs)
        ids.sort()
        idsMaster = map( lambda x: x['id'], obsMaster)
        idsMaster.sort()
        if ids == idsMaster:
          attrs = map( lambda x: {'id':x, 'attrs': map( lambda y: y['id']+'('+y['type']+')', self.metaobj_manager.model[x]['attrs'])}, ids)
          attrsMaster = map( lambda x: {'id':x, 'attrs': map( lambda y: y['id']+'('+y['type']+')', portalMaster.metaobj_manager.model[x]['attrs'])}, idsMaster)
          if attrs == attrsMaster:
            self.metaobj_manager.acquireMetaobj( 'com.zms.foundation')
          else:
            self.metaobj_manager.acquireMetaobj( 'com.zms.foundation',subobjects=0)
            print "[recurse_updateVersionBuild]: can't acquire standard-objects for",self.getHome().id
            c = 0
            for attr in attrs:
              if attrs[c] != attrsMaster[c]:
                print "[recurse_updateVersionBuild]: diff",attrs[c]['id'],self.difference_list(attrs[c]['attrs'],attrsMaster[c]['attrs']),self.difference_list(attrsMaster[c]['attrs'],attrs[c]['attrs'])
              else:
                self.metaobj_manager.acquireMetaobj( attrs[c]['id'])
              c = c + 1
    # Convert titleshort to titlealt.
    keys = self.getObjAttrs().keys()
    if 'titlealt' in keys and not 'titleshort' in keys:
      from _objattrs import hasobjattr
      mapping = { 
        'titleshort': 'titlealt',
        }
      for ob_ver in self.getObjVersions():
        for key in mapping.keys():
          for lang in self.getLangIds():
            if hasobjattr( ob_ver, key+'_'+lang): #!important: hasobjattr instead of hasattr
              try:
                v = getattr( ob_ver, key+'_'+lang)
                setattr( ob_ver, mapping[ key]+'_'+lang, v)
                delattr( ob_ver, key+'_'+lang)
              except:
                pass
    # Convert ZMSObjects into ZMSCustoms.
    meta_types = [ 'ZMSDocument', 'ZMSFile', 'ZMSFolder', 'ZMSGraphic', 'ZMSNote', 'ZMSSysFolder', 'ZMSTable', 'ZMSTeaserContainer', 'ZMSTeaserElement', 'ZMSTextarea']
    # Rename original-objects.
    for ob in self.objectValues(meta_types):
      old_id = ob.id
      new_id = ob.id+'~'
      try:
        self.manage_renameObject( id=old_id, new_id=new_id)
      except:
        print "[recurse_updateVersionBuild]: can't rename original-object", old_id, new_id
        recurse_cleanArtefacts( self)
        self.manage_renameObject( id=old_id, new_id=new_id)
    # Copy ZMSObjects into ZMSCustoms.
    for ob in self.objectValues( meta_types):
      ob_id = ob.id
      ob_permissions = ob.permission_settings()
      ob_roles = ob.valid_roles()
      new_ob_id = ob.id[:-1]
      new_ob = ZMSCustom( id=new_ob_id, meta_id=ob.meta_type)
      self._setObject( new_ob.id, new_ob)
      # Copy attributes.
      new_ob = getattr( self, new_ob.id)
      for key in ob.__dict__.keys():
        if key != 'id' and hasattr( ob, key):
          v = getattr( ob, key)
          if key == '__work_state__' or v is None or type( v) is str:
            setattr( new_ob, key, v)
      # Move sub-objects.
      try:
        cb_copy_data = ob.manage_cutObjects( ob.objectIds())
        new_ob.manage_pasteObjects( cb_copy_data)
      except:
        for id in ob.objectIds():
          try:
            cb_copy_data = ob.manage_cutObjects( ids=[id])
            new_ob.manage_pasteObjects( cb_copy_data)
          except:
            print "[recurse_updateVersionBuild]: ", new_ob.meta_id, new_ob.absolute_url(), "Can't paste", id
      # Roles.
      role_permissions = {}
      for ob_role in ob_roles:
        role_permissions[ob_role] = []
        if ob_role not in new_ob.valid_roles():
          new_ob._addRole( ob_role)
      # Permissions.
      acquired_permissions = []
      for ob_permission in ob_permissions:
        if ob_permission.get( 'acquire') == 'CHECKED':
          acquired_permissions.append( ob_permission.get( 'name'))
        c = 0
        for ob_role in ob_roles:
          if ob_permission.get( 'roles')[ c].get( 'checked') == 'CHECKED':
            role_permissions[ob_role].append( ob_permission.get( 'name'))
          c = c + 1
      new_ob.manage_acquiredPermissions(permissions=acquired_permissions)
      for ob_role in ob_roles:
        new_ob.manage_role(role_to_manage=ob_role,permissions=role_permissions[ob_role])
      #-- new_ob.synchronizePublicAccess()
      # Delete original-object.
      self._delObject(ob_id, suppress_events=True)
  
  ##### Build 131a: ZMS Teaser-Elements: Penetrance ####
  if getattr( docElmnt, 'build', '000') < '131':
    try:
      if self.getType() == 'ZMSTeaserElement':
        d = { '0': 'this', '1': 'sub_nav', '2': 'sub_all'}
        for ob_ver in self.getObjVersions():
          key = 'attr_penetrance'
          if hasattr( ob_ver, key):
            try:
              v = getattr( ob_ver, key)
              setattr( ob_ver, key, d.get( str( v), v))
            except:
              pass
    except:
      pass

  ##### Build 132a: Rename logo to zmi_logo ####
  if getattr( docElmnt, 'build', '000') < '132':
    try:
      self.zmi_logo = self.logo
      delattr( self, 'logo')
    except:
      pass
  
  # Recursion.
  for ob in self.objectValues( self.dGlobalAttrs.keys()):
    recurse_updateVersionBuild(docElmnt, ob, REQUEST)
  
  ##### Build 130a: ZMS Standard-Objects ####
  if getattr( docElmnt, 'build', '000') < '130':
    if self.meta_type == 'ZMS':
      users = self.getConfProperty('ZMS.security.users',{})
      for user in users.keys():
        nodes = users[user].get('nodes',{})
        try:
          for node_ref in nodes.keys():
            node_ob = self.getLinkObj(node_ref)
            node_dict = nodes[node_ref]
            if node_ob:
              self.setLocalUser( user, node_ref, node_dict['roles'], node_dict['langs'])
        except:
          pass

  # Return with message.
  return message


# ------------------------------------------------------------------------------
#  ZMS.recurse_updateVersionPatch:
#
#  Update version patch.
# ------------------------------------------------------------------------------
def recurse_updateVersionPatch(docElmnt, self, REQUEST):
  message = ''
  _confmanager.updateConf(self,REQUEST)
  _confmanager.initCSS(self)
  self.getSequence()
  self.synchronizeObjAttrs()
  self.initLangStr()
  self.initRoleDefs()
  return message


# ------------------------------------------------------------------------------
#  initTheme:
# ------------------------------------------------------------------------------
def initTheme(self, theme, new_id, REQUEST):
  
  filename = _fileutil.extractFilename(theme)
  id = filename[:filename.rfind('.')]
  
  ### Store copy of ZEXP in INSTANCE_HOME/import-folder.
  filepath = INSTANCE_HOME + '/import/' + filename
  if theme.startswith('http://'):
    initutil = _globals.initutil()
    initutil.setConfProperty('HTTP.proxy',REQUEST.get('http_proxy',''))
    zexp = _globals.http_import( initutil, theme)
    _fileutil.exportObj( zexp, filepath)
  else:
    packagepath = package_home(globals()) + '/import/' + filename
    try: 
      os.stat(_fileutil.getOSPath(filepath))
    except OSError:
      shutil.copy( packagepath, filepath)
  
  ### Import theme from ZEXP.
  _fileutil.importZexp( self, filename)
  
  ### Assign folder-id.
  if id != new_id:
    self.manage_renameObject( id=id, new_id=new_id)
  
  ### Return new ZMS home instance.
  return getattr( self, new_id)


# ------------------------------------------------------------------------------
#  initZMS:
# ------------------------------------------------------------------------------
def initZMS(self, id, titlealt, title, lang, manage_lang, REQUEST):
  
  ### Constructor.
  obj = ZMS()
  obj.id = id
  self._setObject(obj.id, obj)
  obj = getattr(self,obj.id)
  
  ### Trashcan.
  trashcan = ZMSTrashcan()
  obj._setObject(trashcan.id, trashcan)
  
  ### Manager.
  manager = ZMSMetamodelProvider.ZMSMetamodelProvider()
  obj._setObject( manager.id, manager)
  manager = ZMSFormatProvider.ZMSFormatProvider()
  obj._setObject( manager.id, manager)
  
  ### Log.
  if REQUEST.get('zmslog'):
    zmslog = ZMSLog( copy_to_stdout=True, logged_entries=[ 'ERROR', 'INFO'])
    obj._setObject(zmslog.id, zmslog)
  
  ### Init Configuration.
  obj.setConfProperty('HTTP.proxy',REQUEST.get('http_proxy',''))
  obj.setConfProperty('ZMS.autocommit',1)
  obj.setConfProperty('ZMS.Version.autopack',2)
  
  ### Init zcatalog.
  obj.recreateCatalog(lang)
  
  ### Init languages.
  obj.setPrimaryLanguage(lang)
  obj.setLanguage(lang,REQUEST['lang_label'],'',manage_lang)
  
  ### Init ZMS object-model.
  _confmanager.initConf(obj, 'zms', REQUEST)
  
  ### Init default-configuration.
  _confmanager.initConf(obj, 'default', REQUEST)
  
  ### Init Role-Definitions and Permission Settings.
  obj.initRoleDefs()
  
  ### Init Properties: active, titlealt, title.
  obj.setObjStateNew(REQUEST)
  obj.updateVersion(lang,REQUEST)
  obj.setObjProperty('active',1,lang)
  obj.setObjProperty('titlealt',titlealt,lang)
  obj.setObjProperty('title',title,lang)
  obj.onChangeObj(REQUEST,forced=1)
  
  ### Return new ZMS instance.
  return obj


# ------------------------------------------------------------------------------
#  initContent:
# ------------------------------------------------------------------------------
def initContent(self, filename, REQUEST):
  xmlfile = open(_fileutil.getOSPath(package_home(globals())+'/import/'+filename),'rb')
  _importable.importFile( self, xmlfile, REQUEST, _importable.importContent)
  xmlfile.close()


################################################################################
################################################################################
###   
###   Constructor
###   
################################################################################
################################################################################
manage_addZMSForm = HTMLFile('manage_addzmsform', globals()) 
def manage_addZMS(self, lang, manage_lang, REQUEST, RESPONSE):
  """ manage_addZMS """
  message = ''
  t0 = time.time()
  
  if REQUEST['btn'] == 'Add':
  
    ##### Add Theme ####
    homeElmnt = initTheme(self,REQUEST['theme'],REQUEST['folder_id'],REQUEST)
      
    ##### Add ZMS ####
    titlealt = 'ZMS home'
    title = 'ZMS - ZOPE-based contentmanagement system for science, technology and medicine'
    obj = initZMS(homeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
    
    ##### Default content ####
    if REQUEST.get('initialization',0)==1:
      initContent(obj,'content.default.zip',REQUEST)
    
    ##### E-Learning components ####
    if REQUEST.get('initialization',0)==2:
      # Create Home.
      lcmsHomeElmnt = initTheme(homeElmnt,'lcms.zexp','lcms',REQUEST)
      # Create LCMS.
      titlealt = 'LCMS'
      title = 'Learning Content Management System'
      lcms = initZMS(lcmsHomeElmnt,'content',titlealt,title,lang,manage_lang,REQUEST)
      lcms.setLanguage('eng', 'English', 'ger')
      # Init configuration.
      _confmanager.initConf(lcms, 'lcms', REQUEST)
      _confmanager.initConf(obj, 'lms', REQUEST)
      # Register Portal/Client.
      lcms.setConfProperty('Portal.Master',homeElmnt.id)
      obj.setConfProperty('Portal.Clients',[lcmsHomeElmnt.id])
      # Init content.
      initContent(lcms,'lcms.default.xml',REQUEST)
      initContent(obj,'lms.default.zip',REQUEST)
    
    ##### Configuration ####
    
    #-- Example Database
    if REQUEST.get('specobj_exampledb',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'exampledb', REQUEST)
      # Init content.
      initContent(obj,'exampledb.content.xml',REQUEST)
    
    #-- Bulletin Board
    if REQUEST.get('specobj_discussions',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'discussions', REQUEST)
      # Init content.
      initContent(obj,'discussions.content.xml',REQUEST)
    
    #-- Newsletter
    if REQUEST.get('specobj_newsletter',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'newsletter', REQUEST)
    
    #-- Calendar
    if REQUEST.get('specobj_calendar',0) == 1:
      # Init configuration.
      _confmanager.initConf(obj, 'calendar', REQUEST)

    ##### Access ####
    obj.synchronizePublicAccess()
    
    # Return with message.
    message = obj.getLangStr('MSG_INSERTED',manage_lang)%obj.meta_type
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    RESPONSE.redirect('%s/%s/manage?manage_tabs_message=%s'%(homeElmnt.absolute_url(),obj.id,urllib.quote(message)))
  
  else:
    RESPONSE.redirect('%s/manage_main'%self.absolute_url())


################################################################################
################################################################################
###
###  Class
###
################################################################################
################################################################################
class ZMS(
        zmscontainerobject.ZMSContainerObject,
        _accessmanager.AccessManager,
        _builder.Builder,
        _confmanager.ConfManager,
        _ftpmanager.FtpManager,
        _language.Language,
        _objattrs.ObjAttrsManager,
        _zcatalogmanager.ZCatalogManager,
        ):

    # Version-Info.
    # -------------
    zms_build = '132'		# Internal use only, designates object model!
    zms_patch = 'e'		# Internal use only!

    # Properties.
    # -----------
    meta_type = meta_id = "ZMS"

    # Management Options.
    # -------------------
    manage_options = (
	{'label': 'TAB_EDIT',         'action': 'manage_main'},
	{'label': 'TAB_PROPERTIES',   'action': 'manage_properties'},
	{'label': 'TAB_ACCESS',       'action': 'manage_users'},
	{'label': 'TAB_IMPORTEXPORT', 'action': 'manage_importexport'},
	{'label': 'TAB_TASKS',        'action': 'manage_tasks'},
	{'label': 'TAB_REFERENCES',   'action': 'manage_RefForm'},
	{'label': 'TAB_HISTORY',      'action': 'manage_UndoVersionForm'},
	{'label': 'TAB_CONFIGURATION','action': 'manage_customize'},
	{'label': 'TAB_PREVIEW',      'action': 'preview_html'}, # empty string defaults to index_html
	)

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
		'manage_importexportFtp',
		'manage_customize', 'manage_customizeSystem',
		'manage_changeLanguages', 'manage_customizeLanguagesForm',
		'manage_changeMetacmds', 'manage_customizeMetacmdForm',
		'manage_changeWorkflow', 'manage_changeWfTransitions', 'manage_changeWfActivities', 'manage_customizeWorkflowForm',
		'manage_customizeDesign', 'manage_customizeDesignForm',
		)
    __authorPermissions__ = (
		'manage','manage_main','manage_workspace',
		'manage_addZMSModule',
		'manage_deleteObjs','manage_undoObjs',
		'manage_moveObjUp','manage_moveObjDown','manage_moveObjToPos',
		'manage_cutObjects','manage_copyObjects','manage_pasteObjs',
		'manage_properties','manage_changeProperties',
		'manage_search','manage_search_attrs','manage_tasks',
		'manage_wfTransition', 'manage_wfTransitionFinalize',
		'manage_userForm', 'manage_user',
		'manage_importexport', 'manage_import', 'manage_export',
		)
    __userAdministratorPermissions__ = (
		'manage_users', 'manage_userProperties', 'manage_roleProperties',
		)
    __ac_permissions__=(
		('ZMS Administrator', __administratorPermissions__),
		('ZMS Author', __authorPermissions__),
		('ZMS UserAdministrator', __userAdministratorPermissions__),
		)

    # Globals.
    # --------
    dGlobalAttrs = {
	'ZMS':{
				'obj_class':None},
	'ZMSCustom':{
				'obj_class':ZMSCustom},
	'ZMSLinkContainer':{
				'obj_class':ZMSLinkContainer,
				'constructor':'manage_addZMSLinkContainer'},
	'ZMSLinkElement':{
				'obj_class':ZMSLinkElement,
				'constructor':'manage_addzmslinkelementform'},
	'ZMSSqlDb':{
				'obj_class':ZMSSqlDb,
				'constructor':'manage_addzmssqldbform'},
	}

    # Interface.
    # ----------
    index_html = HTMLFile('dtml/ZMS/index', globals()) # index_html
    not_found_html = HTMLFile('dtml/ZMS/not_found', globals()) # index_html
    f_inactive_html = HTMLFile('dtml/ZMS/f_inactive', globals()) # inactive_html
    f_headDoctype = HTMLFile('dtml/ZMS/f_headdoctype', globals()) # Template: DOCTYPE
    f_bodyContent_Sitemap = HTMLFile('dtml/ZMS/f_bodycontent_sitemap', globals()) # Template: Sitemap
    f_bodyContent_Search = HTMLFile('dtml/ZMS/f_bodycontent_search', globals()) # Template: Search
    f_bodyContent_NotFound = HTMLFile('dtml/ZMS/f_bodycontent_notfound', globals()) # Template: Not Found
    f_headTitle = HTMLFile('dtml/ZMS/f_headtitle', globals()) # Head.Title
    f_headMeta_DC = HTMLFile('dtml/ZMS/f_headmeta_dc', globals()) # Head.Meta.DC
    f_headMeta_Locale = HTMLFile('dtml/ZMS/f_headmeta_locale', globals()) # Head.Locale (Content-Type & Charset)
    f_sitemap = HTMLFile('dtml/ZMS/f_sitemap', globals()) # f_sitemap
    f_standard_html_request = HTMLFile('dtml/ZMS/f_standard_html_request', globals()) # f_standard_html_request
    f_standard_html_header = HTMLFile('dtml/ZMS/f_standard_html_header', globals()) # f_standard_html_header
    f_standard_html_footer = HTMLFile('dtml/ZMS/f_standard_html_footer', globals()) # f_standard_html_footer
    headScript = HTMLFile('dtml/ZMS/headscript', globals()) # Head.Script
    headMeta = HTMLFile('dtml/ZMS/headmeta', globals()) # Head.Meta
    headCStyleSheet = HTMLFile('dtml/ZMS/headcstylesheet', globals()) # Template_L1: CSS-Reference
    headCSS = HTMLFile('dtml/ZMS/headcstylesheet', globals()) # Template_L1: CSS-Referenz
    search_nav_html = HTMLFile('dtml/ZMS/search_nav', globals()) # search_nav_html
    manage_editorForm = HTMLFile('dtml/ZMS/manage_editorform', globals()) # Editor (Frameset)

    # Enumerations.
    # -------------
    browse_enum = HTMLFile('dtml/ZMS/browse_enum', globals()) 
    enumManager = _enummanager.EnumManager()


    """
    ############################################################################
    ###
    ###   Constructor
    ###
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMS.__init__: 
    # --------------------------------------------------------------------------
    def __init__(self):
      """
      Constructor.
      """
      self.id = 'content'
      file = open(_fileutil.getOSPath(package_home(globals())+'/www/spacer.gif'),'rb')
      self.zmi_logo = Image(id='logo', title='', file=file.read())
      file.close()

    # --------------------------------------------------------------------------
    #  ZMS.zms_version:
    #
    #  Get version.
    # --------------------------------------------------------------------------
    def zms_version(self):
      file = open(_fileutil.getOSPath(package_home(globals())+'/version.txt'),'r')
      rtn = file.read()
      file.close()
      return rtn

    # --------------------------------------------------------------------------
    #  ZMS.getDocumentElement
    # --------------------------------------------------------------------------
    def getDocumentElement(self):
      """
      The root element of the site.
      """
      return self

    # --------------------------------------------------------------------------
    #  ZMS.getHome
    # --------------------------------------------------------------------------
    def getHome(self):
      """
      Returns the home-folder of the site.
      """
      docElmnt = self.getDocumentElement()
      ob = docElmnt
      try:
        depth = 0
        while ob.meta_type != 'Folder': 
          if depth > sys.getrecursionlimit():
            raise "Maximum recursion depth exceeded"
          depth = depth + 1
          ob = ob.aq_parent
      except:
        ob = getattr( docElmnt, docElmnt.absolute_url().split( '/')[-2])
      return ob

    # --------------------------------------------------------------------------
    #  ZMS.getTrashcan
    # --------------------------------------------------------------------------
    def getTrashcan(self):
      return self.objectValues(['ZMSTrashcan'])[0]

    # --------------------------------------------------------------------------
    #  ZMS.getNewId
    # --------------------------------------------------------------------------
    def getNewId(self, id_prefix='e'):
      """
      Returns new (unique) Object-ID.
      """
      return '%s%i'%(id_prefix,self.getSequence().nextVal())

    # --------------------------------------------------------------------------
    #  ZMS.getDCCoverage
    # --------------------------------------------------------------------------
    def getDCCoverage(self, REQUEST={}):
      """
      Returns Dublin-Core Meta-Attribute Coverage.
      """
      return 'global.'+self.getPrimaryLanguage()

    # --------------------------------------------------------------------------
    #  ZMS.sendMail
    # --------------------------------------------------------------------------
    def sendMail(self, mto, msubject, mbody, REQUEST):
      """
      Sends Mail via MailHost.
      """
      
      ##### Get Sender ####
      auth_user = REQUEST['AUTHENTICATED_USER']
      mfrom = self.getUserAttr(auth_user,'email',self.getConfProperty('ZMSAdministrator.email',''))
      
      ##### Get MailHost ####
      mailhost = None
      homeElmnt = self.getHome()
      if len(homeElmnt.objectValues(['Mail Host'])) == 1:
        mailhost = homeElmnt.objectValues(['Mail Host'])[0]
      elif getattr(homeElmnt,'MailHost',None) is not None:
        mailhost = getattr(homeElmnt,'MailHost',None)
      
      ##### Get MessageText ####
      messageText = ''
      messageText += 'Content-Type: text/plain; charset=unicode-1-1-utf-8\n'
      if type(mto) is dict and mto.has_key( 'From'):
        messageText += 'From: %s\n'%mto['From']
      else:
        messageText += 'From: %s\n'%mfrom
      if type(mto) is dict:
        for key in ['To','Cc','Bcc']:
          if mto.has_key( key):
            messageText += '%s: %s\n'%(key,mto[key])
      else:
        messageText += 'To: %s\n'%mto
      messageText += 'Subject: %s\n\n'%msubject
      messageText += '%s\n'%mbody
      
      ##### Send mail ####
      try:
        _globals.writeBlock( self, "[sendMail]: %s"%messageText)
        mailhost.send(messageText)
        return 0
      except:
        return -1


    ############################################################################
    #
    #   ZMS - Portals
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.getPortalMaster
    # --------------------------------------------------------------------------
    def getPortalMaster(self):
      """
      Returns portal-master, none if it does not exist.
      """
      v = self.getConfProperty('Portal.Master','')
      if len(v) > 0:
        try:
          return getattr( self, v).content
        except:
          _globals.writeError(self, '[getPortalMaster]: %s not found!'%str(v))
      return None

    # --------------------------------------------------------------------------
    #  ZMS.getPortalClients
    # --------------------------------------------------------------------------
    def getPortalClients(self):
      """
      Returns portal-clients, empty list if none exist.
      """
      docElmnts = []
      v = self.getConfProperty('Portal.Clients',[])
      if len(v) > 0:
        thisHome = self.getHome()
        for id in v:
          try:
            docElmnts.append(getattr(thisHome,id).content)
          except:
            _globals.writeError(self, '[getPortalClients]: %s not found!'%str(id))
      return docElmnts


    ############################################################################
    #
    #   ZMS - Versions
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.updateVersion:
    #
    #  Update version.
    # --------------------------------------------------------------------------
    def updateVersion(self, lang, REQUEST, maintenance=True):
      message = ''
      build = getattr( self, 'build', '000')
      patch = getattr( self, 'patch', '000')
      if build != self.zms_build:
        REQUEST.set('recurse_updateVersionBuild',True)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from build #%s%s to #%s%s...'%(build,patch,self.zms_build,self.zms_patch))
        message += recurse_updateVersionBuild( self, self, REQUEST)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from build #%s%s to #%s%s - Finished!'%(build,patch,self.zms_build,self.zms_patch))
        setattr( self, 'build', self.zms_build)
        message += 'Synchronized object-model from build #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if build != self.zms_build or patch != self.zms_patch:
        REQUEST.set('recurse_updateVersionPatch',True)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from patch #%s%s to #%s%s...'%(build,patch,self.zms_build,self.zms_patch))
        message += recurse_updateVersionPatch( self, self, REQUEST)
        _globals.writeBlock(self,'[ZMS.updateVersion]: Synchronize object-model from patch #%s%s to #%s%s - Finished!'%(build,patch,self.zms_build,self.zms_patch))
        setattr( self, 'patch', self.zms_patch)
        message += 'Synchronized object-model from patch #%s%s to #%s%s!<br/>'%(build,patch,self.zms_build,self.zms_patch)
      if maintenance:
        try:
          self.getTrashcan().run_garbage_collection()
        except:
          _globals.writeError( self, '[updateVersion]: can\'t run garbage collection')
      
      # Process clients.
      if message:
        for portalClient in self.getPortalClients():
          message += portalClient.updateVersion( lang, REQUEST, False)
      
      return message


    ############################################################################
    ###  
    ###   DOM-Methods
    ### 
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.getParentNode
    # --------------------------------------------------------------------------
    getParentNode__roles__ = None
    def getParentNode(self): 
      """
      The parent of this node. 
      All nodes except root may have a parent.
      """
      return None


    ############################################################################
    ###
    ###   XML-Builder
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMS.xmlOnStartElement
    # --------------------------------------------------------------------------
    def xmlOnStartElement(self, sTagName, dTagAttrs, oParentNode, oRoot):
      """
      Handler for XML-Builder (_builder.py)
      """
      if _globals.debug( self):
        _globals.writeLog( self, "[xmlOnStartElement]: sTagName=%s"%sTagName)
      
      # remove all ZMS-objects.
      self.manage_delObjects(self.objectIds(self.dGlobalAttrs.keys()))
      # remove all languages.
      for s_lang in self.getLangIds():
        self.delLanguage(s_lang)
      
      self.dTagStack = _globals.MyStack()
      self.dValueStack  = _globals.MyStack()
      
      # WORKAROUND! The member variable "aq_parent" does not contain the right 
      # parent object at this stage of the creation process (it will later on!). 
      # Therefore, we introduce a special attribute containing the parent 
      # object, which will be used by xmlGetParent() (see below).
      self.oParent = None

################################################################################
