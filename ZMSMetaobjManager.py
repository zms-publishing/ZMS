################################################################################
# ZMSMetaobjManager.py
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
from zope.interface import implements
from Products.ExternalMethod import ExternalMethod
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
from cStringIO import StringIO
import ZPublisher.HTTPRequest
import copy
import os
import sys
import time
import zExceptions
# Product Imports.
import _blobfields
import _fileutil
import _globals
import _ziputil


# ------------------------------------------------------------------------------
#  Synchronize type.
# ------------------------------------------------------------------------------
syncTypes = ['method','py','zpt','interface','resource']
def syncType( self, id, attr, forced=False):
  try:
    if attr['type'] not in self.valid_zopetypes+syncTypes:
      return
    attr_id = attr['id']
    if attr['type'] in self.valid_zopetypes:
      container = self.getHome()
      for ob_id in attr_id.split('/')[:-1]:
         container = getattr( container, ob_id)
      ob_id = attr['id'].split('/')[-1]
      ob = getattr( container, ob_id)
      attr['ob'] = ob
      if ob.meta_type in [ 'DTML Method', 'DTML Document']:
        attr['custom'] = ob.raw
      elif ob.meta_type in [ 'Folder']:
        zip = _ziputil.exportZodb2Zip(ob)
        blob = _blobfields.createBlobField( self,_globals.DT_FILE, zip, mediadbStorable=False)
        attr['custom'] = blob
      elif ob.meta_type in [ 'Page Template']:
        attr['custom'] = unicode(ob.read()).encode('utf-8')
      elif ob.meta_type in [ 'Script (Python)']:
        attr['custom'] = ob.read()
      elif ob.meta_type in [ 'Z SQL Method']:
        connection = ob.connection_id
        params = ob.arguments_src
        attr['custom'] = '<connection>%s</connection>\n<params>%s</params>\n%s'%(connection,params,ob.src)
    else:
      ob = getattr(self,id+'.'+attr_id,None)
      if ob is not None:
        attr['ob'] = ob
        if attr['type'] == 'method':
          attr['custom'] = ob.raw
        elif attr['type'] == 'py':
          attr['py'] = ob
          attr['custom'] = ob.read()
        elif attr['type'] == 'zpt':
          attr['zpt'] = ob
          attr['custom'] = unicode(ob.read()).encode('utf-8')
        elif attr['type'] == 'interface':
          if ob.meta_type in ['Page Template']:
            attr['zpt'] = ob
            attr['name'] = unicode(ob.read()).encode('utf-8')
          elif ob.meta_type in [ 'Script (Python)']:
            attr['py'] = ob
            attr['name'] = ob.read()
          else:
            attr['name'] = ob.raw
        elif attr['type'] == 'resource':
          attr['custom'] = ob
  except:
    value = _globals.writeError(self,'[syncType]')


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSMetaobjManager:

    # Globals.
    # --------
    valid_types =     ['amount','autocomplete','boolean','color','date','datetime','dictionary','file','float','identifier','image','int','list','multiautocomplete','multiselect','password','richtext','select','string','text','time','url','xml']
    valid_xtypes =    ['constant','delimiter','hint','interface','method','py','zpt','resource']
    valid_datatypes = valid_types+valid_xtypes
    valid_datatypes.sort()
    valid_objtypes =  [ 'ZMSDocument', 'ZMSObject', 'ZMSTeaserElement', 'ZMSRecordSet', 'ZMSResource', 'ZMSReference', 'ZMSLibrary', 'ZMSPackage', 'ZMSModule']
    valid_zopetypes = [ 'DTML Method', 'DTML Document', 'External Method', 'Folder', 'Page Template', 'Script (Python)', 'Z SQL Method']
    deprecated_types = [ 'DTML Method', 'DTML Document', 'method']


    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.importMetaobjXml
    # --------------------------------------------------------------------------

    def _importMetaobjXml(self, item, createIfNotExists=1, createIdsFilter=None):
      ids = []
      id = item['key']
      meta_types = self.model.keys()
      if (createIfNotExists == 1) and \
         (createIdsFilter is None or (id in createIdsFilter)):
        # Register Meta Attributes.
        metadictAttrs = []
        if id in meta_types:
          valid_types = self.valid_datatypes+self.valid_zopetypes+meta_types+['*']
          metaObj = self.getMetaobj( id)
          for metaObjAttr in metaObj['attrs']:
            if metaObjAttr['type'] not in valid_types+metadictAttrs:
              metadictAttrs.append( metaObjAttr['type'])
        newDtml = item.get('dtml')
        newValue = item.get('value')
        newAttrs = newValue.get('attrs',newValue.get('__obj_attrs__'))
        newValue['attrs'] = []
        newValue['id'] = id
        newValue['enabled'] = newValue.get('enabled',item.get('enabled',1))
        # Delete Object.
        oldAttrs = None
        if id in ids:
          self.delMetaobj( id)
        # Set Object.
        self.setMetaobj( newValue)
        # Set Attributes.
        attr_ids = []
        for attr in newAttrs:
          # Mandatory.
          attr_id = attr.get('id')
          newName = attr.get('name')
          newMandatory = attr.get('mandatory')
          newMultilang = attr.get('multilang')
          newRepetitive = attr.get('repetitive')
          newType = attr.get('type')
          # Optional.
          newKeys = attr.get('keys',[])
          newCustom = attr.get('custom','')
          newDefault = attr.get('default','')
          # Old Attribute.
          if type(oldAttrs) is list and len(oldAttrs) > 0:
            while len(oldAttrs) > 0 and not (attr_id == oldAttrs[0]['id'] and newType == oldAttrs[0]['type']):
              oldAttr = oldAttrs[0]
              # Set Attribute.
              if oldAttr['id'] not in attr_ids:
                self.setMetaobjAttr( id, None, oldAttr['id'], oldAttr['name'], oldAttr['mandatory'], oldAttr['multilang'], oldAttr['repetitive'], oldAttr['type'], oldAttr['keys'], oldAttr['custom'], oldAttr['default'])
                attr_ids.append(oldAttr['id'])
              # Deregister Meta Attribute.
              if oldAttr['id'] in metadictAttrs:
                metadictAttrs.remove(oldAttr['id'])
              oldAttrs.remove( oldAttr)
            if len(oldAttrs) > 0:
              oldAttrs.remove( oldAttrs[0])
          # Set Attribute.
          if attr_id not in attr_ids:
            self.setMetaobjAttr( id, attr_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
            attr_ids.append(attr_id)
          # Deregister Meta Attribute.
          if attr_id in metadictAttrs:
            metadictAttrs.remove(attr_id)
        # Set Meta Attributes.
        for attr_id in metadictAttrs:
          newName = attr_id
          newMandatory = 0
          newMultilang = 0
          newRepetitive = 0
          newType = attr_id
          newKeys = []
          newCustom = ''
          newDefault = ''
          # Set Attribute.
          if attr_id not in attr_ids:
            self.setMetaobjAttr( id, None, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
            attr_ids.append(attr_id)
        # Set Template (backwards compatibility).
        if newValue['type'] not in [ 'ZMSLibrary', 'ZMSModule', 'ZMSPackage'] and newDtml is not None:
          tmpltId = 'standard_html'
          tmpltName = 'Template: %s'%newValue['name']
          tmpltCustom = newDtml
          newType = 'DTML Method'
          newKeys = []
          newDefault = ''
          self.setMetaobjAttr(id,tmpltId,tmpltId,tmpltName,0,0,0, newType, newKeys, tmpltCustom, newDefault)
      _globals.writeBlock( self, '[ZMSMetaobjManager._importMetaobjXml]: id=%s'%str(id))
      return id

    def importMetaobjXml(self, xml, createIfNotExists=1, createIdsFilter=None):
      self.REQUEST.set( '__get_metaobjs__', True)
      ids = []
      v = self.parseXmlString( xml, mediadbStorable=False)
      if not type(v) is list:
        v = [v]
      for item in v:
        id = self._importMetaobjXml(item,createIfNotExists,createIdsFilter)
        ids.append( id)
      if len( ids) == 1:
        ids = ids[ 0]
      _globals.writeBlock( self, '[ZMSMetaobjManager.importMetaobjXml]: ids=%s'%str(ids))
      return ids

    def exportMetaobjXml(self, ids, REQUEST=None, RESPONSE=None):
      value = []
      export_ids = []
      for id in ids:
        metaObj = self.getMetaobj( id)
        export_ids.append(id)
        if metaObj['type'] == 'ZMSPackage':
          for pkgMetaObjId in self.getMetaobjIds():
              pkgMetaObj = self.getMetaobj( pkgMetaObjId)
              if pkgMetaObj[ 'package'] == metaObj[ 'id']:
                export_ids.append( pkgMetaObjId)
      keys = self.model.keys()
      keys.sort()
      revision = '0.0.0'
      for id in keys:
        if id in export_ids or len(export_ids) == 0:
          ob = copy.deepcopy(self.__get_metaobj__(id))
          revision = self.getMetaobjRevision(id)
          attrs = []
          for attr in ob['attrs']:
            attr_id = attr['id']
            syncType( self, id, attr)
            for key in ['keys','custom','default']:
              if attr.has_key(key) and not attr[key]:
                del attr[key]
            for key in ['sync','ob','py','zpt']:
              if attr.has_key(key):
                del attr[key]
            attrs.append( attr)
          ob['__obj_attrs__'] = attrs
          for key in ['attrs','acquired']:
            if ob.has_key(key):
              del ob[key]
          # Value.
          value.append({'key':id,'value':ob})
      if len(value)==1:
        value = value[0]
      # XML.
      if len(ids)==1:
        filename = '%s-%s.metaobj.xml'%(ids[0],revision)
      else:
        filename = 'export.metaobj.xml'
      content_type = 'text/xml; charset=utf-8'
      export = self.getXmlHeader() + self.toXmlString(value,1)
      
      if RESPONSE:
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
      return export


    ############################################################################
    #
    #   OBJECTS
    #
    ############################################################################

    # -------------------------------------------------------------------------- 
    #  ZMSMetaobjManager.getTemplateId 
    # 
    #  Returns template-id for meta-object specified by given Id. 
    #  @deprecated
    # -------------------------------------------------------------------------- 
    def getTemplateId(self, id): 
      return "bodyContentZMSCustom_%s"%id 

    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.renderTemplate
    #
    #  Renders template for meta-object.
    # --------------------------------------------------------------------------
    def renderTemplate(self, obj):
      v = ""
      id = obj.meta_id
      tmpltIds = []
      if obj.REQUEST.get("ZMS_SKIN") is not None and  obj.REQUEST.get("ZMS_EXT") is not None:
        tmpltIds.append("%s_%s"%(obj.REQUEST.get("ZMS_SKIN"),obj.REQUEST.get("ZMS_EXT")))
      tmpltIds.append("standard_html")
      tmpltIds.append("bodyContentZMSCustom_%s"%id)
      for tmpltId in tmpltIds:
        if tmpltId in obj.getMetaobjAttrIds(id):
          if obj.getMetaobjAttr(id,tmpltId)['type'] in ['method','py','zpt']:
            v = obj.attr(tmpltId)
            break
          elif tmpltId not in ["standard_html"]:
            tmpltDtml = getattr(obj,tmpltId,None)
            if tmpltDtml is not None:
              v = tmpltDtml(obj,obj.REQUEST)
              try:
                v = v.encode('utf-8')
              except UnicodeDecodeError:
                v = str(v)
              break
      return v


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.__get_metaobjs__:
    #
    #  Returns all meta-objects (including acquisitions).
    # --------------------------------------------------------------------------
    def __get_metaobjs__(self):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = '__get_metaobjs__'
      try:
        forced = \
          not self.REQUEST.get( '__get_metaobjs__', False) and \
          not self.REQUEST.get( 'recurse_updateVersionBuild', False)
        obs = self.fetchReqBuff( reqBuffId, self.REQUEST, forced)
        return obs
      except:
        obs = {}
        raw = self.model
        master_obs = None
        for ob_id in raw.keys():
          ob = raw.get(ob_id)
          # Acquire from parent.
          if ob.get('acquired',0) == 1:
            acquired = 1
            subobjects = ob.get('subobjects',1)
            if master_obs is None:
              portalMaster = self.getPortalMaster()
              if portalMaster is not None:
                master_obs = portalMaster.metaobj_manager.__get_metaobjs__()
            if master_obs is not None:
              if master_obs.has_key(ob_id):
                ob = master_obs[ob_id].copy()
              else:
                ob = {'id':ob_id,'type':'ZMSUnknown'}
              ob['acquired'] = acquired
              ob['subobjects'] = subobjects
              obs[ob_id] =  ob
              if ob['type'] == 'ZMSPackage' and ob['subobjects'] == 1:
                package = ob_id
                for ob_id in master_obs.keys():
                  ob = master_obs[ob_id].copy()
                  if ob.get( 'package') == package:
                    ob['acquired'] = 1
                    obs[ob_id] =  ob
          else:
            obs[ob_id] = ob
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, obs, self.REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.__get_metaobj__:
    #
    #  Returns meta-object identified by id.
    # --------------------------------------------------------------------------
    def __get_metaobj__(self, id):
      obs = self.__get_metaobjs__()
      ob = obs.get( id)
      return ob


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.__is_page_container__:
    # --------------------------------------------------------------------------
    def __is_page_container__(self, id):
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = '__%s_is_page_container__'%id
      try:
        forced = True
        return self.fetchReqBuff( reqBuffId, self.REQUEST, forced)
      except:
        rtnVal = False
        ob = self.__get_metaobj__( id)
        if type( ob) is dict and (ob.get('type') == 'ZMSDocument' or ob.get('id') == 'ZMSTeaserContainer'):
          ids = map( lambda x: x['id'], filter( lambda x: x['type']=='*', ob['attrs']))
          rtnVal = 'e' in ids
        
        #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
        return self.storeReqBuff( reqBuffId, rtnVal, self.REQUEST)


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjIds:
    #
    #  Returns list of all meta-ids in model.
    # --------------------------------------------------------------------------
    def getMetaobjIds(self, sort=1, excl_ids=[]):
      obs = self.__get_metaobjs__()
      ids = obs.keys()
      if len( excl_ids) > 0:
        excl_types = [ 'ZMSPackage']
        ids = filter( lambda x: x not in excl_ids and obs[x]['type'] not in excl_types, ids)
      if sort:
        mapping = map(lambda x: (self.display_type(self.REQUEST,x),x),ids)
        mapping.sort()
        ids = map(lambda x: x[1],mapping)
      return ids


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobj:
    #
    #  Returns meta-object specified by id.
    # --------------------------------------------------------------------------
    def getMetaobj(self, id):
      ob = _globals.nvl( self.__get_metaobj__(id), {'id':id, 'attrs':[], })
      if ob is not None and ob.get('acquired',0) == 1:
        for k in ob.keys():
          v = self.getConfProperty('%s.%s'%(id,k),None)
          if v is not None:
            ob[k] = v
      return ob


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjRevision:
    #
    #  Returns meta-object-revision specified by id.
    # --------------------------------------------------------------------------
    def getMetaobjRevision(self, id):
      ob = self.getMetaobj(id)
      if ob is not None and ob.get('type') == 'ZMSPackage':
        metaobjs = filter(lambda x:x.get('package')==ob['id'],self.__get_metaobjs__().values())
        revision = max(['0.0.0']+map(lambda x:_globals.nvl(x.get('revision'),'0.0.0'),metaobjs))
        if revision > ob.get('revision','0.0.0'):
          ob['revision'] = revision
      return ob.get('revision','0.0.0')


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjId:
    #
    #  Returns id of meta-object specified by name.
    # --------------------------------------------------------------------------
    def getMetaobjId(self, name):
      for id in self.getMetaobjIds():
        if name == self.display_type(meta_type=id):
          return id
      return None


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.setMetaobj:
    #
    #  Sets meta-object with specified values.
    # --------------------------------------------------------------------------
    def setMetaobj(self, ob):
      obs = self.model
      ob = ob.copy()
      ob[ 'name'] = ob.get( 'name', '')
      ob[ 'revision'] = ob.get( 'revision', '0.0.0')
      ob[ 'type'] = ob.get( 'type', '')
      ob[ 'package'] = ob.get( 'package', '')
      ob[ 'attrs'] = ob.get( 'attrs', ob.get( '__obj_attrs__', []))
      ob[ 'acquired'] = ob.get( 'acquired' ,0)
      ob[ 'enabled'] = ob.get( 'enabled', 1)
      if ob.has_key('__obj_attrs__'):
        del ob['__obj_attrs__']
      obs[ob['id']] = ob
      # Make persistent.
      self.model = self.model.copy()


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.acquireMetaobj:
    #
    #  Acquires meta-object specified by id.
    # --------------------------------------------------------------------------
    def acquireMetaobj(self, id, subobjects=1):
      obs = self.model
      ob = self.getMetaobj( id)
      if ob is not None and len( ob.keys()) > 0 and subobjects == 1:
        if ob.get('type','') == 'ZMSPackage':
          pk_obs = filter( lambda x: x.get('package') == id, obs.values())
          pk_ids = map( lambda x: x['id'], pk_obs)
          for pk_id in pk_ids:
            self.delMetaobj( pk_id)
        self.delMetaobj( id)
      ob = {}
      ob['id'] = id
      ob['acquired'] = 1
      ob['subobjects'] = subobjects
      self.setMetaobj( ob)
      # Make persistent.
      self.model = self.model.copy()


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.delMetaobj:
    #
    #  Delete meta-object specified by id.
    # --------------------------------------------------------------------------
    def delMetaobj(self, id):
      # Handle type.
      ids = filter( lambda x: x.startswith(id+'.'), self.objectIds())
      if ids:
        self.manage_delObjects( ids)
      # Delete object.
      cp = self.model
      obs = {}
      for key in cp.keys():
        if key == id:
          # Delete attributes.
          attr_ids = map( lambda x: x['id'], cp[key]['attrs'] )
          for attr_id in attr_ids:
            self.delMetaobjAttr( id, attr_id)
        else:
          obs[key] = cp[key]
      # Make persistent.
      self.model = obs.copy()


    ############################################################################
    #
    #   ATTRIBUTES
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.notifyMetaobjAttrAboutValue:
    #
    #  Notify attribute for meta-object specified by attribute-id about value.
    # --------------------------------------------------------------------------
    def notifyMetaobjAttrAboutValue(self, meta_id, key, value):
      sync_id = False
      
      attr = self.getMetaobjAttr( meta_id, key)
      if attr is not None:
        # Self-learning auto-complete attributes.
        if attr.get('type') in ['autocomplete','multiautocomplete']:
          keys = attr['keys']
          if ''.join(keys).find('<dtml') < 0:
            if type(value) is not list:
              value = [value]
            for v in value:
              if v not in keys:
                keys.append(v)
                sync_id = meta_id
            if sync_id:
              self.setMetaobjAttr( meta_id, key, key, attr['name'], attr['mandatory'], attr['multilang'], attr['repetitive'], attr['type'], keys, attr['custom'], attr['default'])
      
      ##### SYNCHRONIZE ####
      if sync_id:
        self.synchronizeObjAttrs( sync_id)


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjAttrIdentifierId:
    #
    #  Get attribute-id of identifier for datatable specified by meta-id.
    # --------------------------------------------------------------------------
    def getMetaobjAttrIdentifierId(self, meta_id):
      for attr_id in self.getMetaobjAttrIds( meta_id, types=[ 'identifier', 'string', 'int']):
        return attr_id
      return None


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjAttrIds:
    #
    #  Returns list of attribute-ids for meta-object specified by meta-id.
    # --------------------------------------------------------------------------
    def getMetaobjAttrIds(self, id, types=[]):
      return map(lambda x: x['id'], self.getMetaobjAttrs( id, types))


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjAttrs:
    #
    #  Returns list of attribute-ids for meta-object specified by meta-id.
    # --------------------------------------------------------------------------
    def getMetaobjAttrs(self, id, types=[]):
      attrs = []
      ob = self.__get_metaobj__(id)
      if ob is not None:
        attrs = ob.get('attrs',ob.get('__obj_attrs__',[]))
        if len( types) > 0:
          attrs = filter( lambda x: x['type'] in types, attrs)
      return attrs


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.evalMetaobjAttr
    # --------------------------------------------------------------------------
    def evalMetaobjAttr(self, id, attr_id, zmscontext=None, options={}):
      def call(fn):
        if options:
          return fn(zmscontext=zmscontext,options=options)
        else:
          return fn(zmscontext=zmscontext)
      value = None
      metaObjAttr = self.getMetaobjAttr( id, attr_id, syncTypes=['*'])
      if metaObjAttr is not None:
        if metaObjAttr['type'] == 'interface':
          if metaObjAttr.get('py') is not None:
            value = call(metaObjAttr['py'])
          elif metaObjAttr.get('zpt') is not None:
            value = call(metaObjAttr['zpt'])
            value = unicode(value).encode('utf-8')
          else:
            value = zmscontext.dt_exec(metaObjAttr.get('name',''))
        elif metaObjAttr['type'] == 'method':
          value = zmscontext.dt_exec(metaObjAttr.get('custom',''))
        elif metaObjAttr['type'] == 'py':
          value = call(metaObjAttr['py'])
        elif metaObjAttr['type'] == 'zpt':
          value = call(metaObjAttr['zpt'])
          value = unicode(value).encode('utf-8')
        elif metaObjAttr['type'] == 'constant':
          value = metaObjAttr.get('custom','')
        elif metaObjAttr['type'] == 'resource':
          value = metaObjAttr.get('custom',None)
      return value


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjAttr:
    # 
    #  Get attribute for meta-object specified by attribute-id.
    # --------------------------------------------------------------------------
    def getMetaobjAttr(self, id, attr_id, syncTypes=['resource']):
      meta_objs = self.__get_metaobjs__()
      if meta_objs.get(id,{}).get('acquired',0) == 1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          attr = portalMaster.getMetaobjAttr( id, attr_id, syncTypes)
          return attr
      meta_obj = meta_objs.get(id,{})
      attrs = meta_obj.get('attrs',meta_obj.get('__obj_attrs__',[]))
      for attr in attrs:
        valid_datatype = attr['type'] in self.valid_datatypes
        if attr_id == attr['type'] and not valid_datatype:
          meta_attrs = self.getMetadictAttrs()
          if attr['type'] in meta_attrs:
            attr_type = attr['type']
            attr = self.getMetadictAttr(attr['type'])
            attr = attr.copy()
            attr['meta_type'] = attr_type
            return attr
        if attr_id == attr['id']:
          attr = attr.copy()
          attr['datatype_key'] = _globals.datatype_key(attr['type'])
          attr['mandatory'] = attr.get('mandatory',0)
          attr['multilang'] = attr.get('multilang',1)
          attr['errors'] = attr.get('errors','')
          attr['meta_type'] = ['','?'][int(attr['type']==attr['id'] and not valid_datatype)]
          if '*' in syncTypes or attr['type'] in syncTypes: syncType( self, id, attr)
          return attr
      return None


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.setMetaobjAttr:
    #
    #  Set/add meta-object attribute with specified values.
    # --------------------------------------------------------------------------
    def setMetaobjAttr(self, id, oldId, newId, newName='', newMandatory=0, newMultilang=1, newRepetitive=0, newType='string', newKeys=[], newCustom='', newDefault=''):
      ob = self.__get_metaobj__(id)
      if ob is None: return
      attrs = copy.copy(ob['attrs'])
      
      # Set Attributes.
      if newType in ['delimiter','hint','interface']:
        newCustom = ''
      if newType in ['resource'] and (type(newCustom) is str or type(newCustom) is int):
        newCustom = None
      if newType not in ['*','autocomplete','multiautocomplete','multiselect','recordset','select']:
        newKeys = []
      if newType in self.getMetadictAttrs():
        newId = newType
      if newType in self.getMetaobjIds(sort=0)+['*']:
        newMultilang = 0
      
      # Defaults for Insert
      method_types = [ 'method','py','zpt'] + self.valid_zopetypes
      if oldId is None and \
         newType in method_types and \
         (newCustom == '' or type(newCustom) is not str):
        if newType in [ 'method', 'DTML Method', 'DTML Document']:
          newCustom = ''
          newCustom += '<!-- '+ newId + ' -->\n'
          newCustom += '\n'
          newCustom += '<!-- /'+ newId + ' -->\n'
        elif newType in [ 'External Method']:
          newCustom = ''
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += 'def ' + newId + '( self):\n'
          newCustom += '  return "This is the external method ' + newId + '"\n'
        elif newType in [ 'zpt', 'Page Template']:
          newCustom = ''
          newCustom += '<span tal:replace="here/title_or_id">content title or id</span>'
          newCustom += '<span tal:condition="template/title" tal:replace="template/title">optional template title</span>'
        elif newType in [ 'py', 'Script (Python)']:
          newCustom = '## Script (Python) ""\n'
          newCustom += '##bind container=container\n'
          newCustom += '##bind context=context\n'
          newCustom += '##bind namespace=\n'
          newCustom += '##bind script=script\n'
          newCustom += '##bind subpath=traverse_subpath\n'
          newCustom += '##parameters='
          if newType in ['py']: newCustom += 'zmscontext=None'
          newCustom += '\n'
          newCustom += '##title='
          if newType in ['py']: newCustom += newType+': '
          newCustom += newName
          newCustom += '\n'
          newCustom += '##\n'
          newCustom += '# --// '+ newId + ' //--\n'
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += '# Import a standard function, and get the HTML request and response objects.\n'
          newCustom += 'from Products.PythonScripts.standard import html_quote\n'
          newCustom += 'request = container.REQUEST\n'
          newCustom += 'RESPONSE =  request.RESPONSE\n'
          newCustom += '\n'
          newCustom += '# Return a string identifying this script.\n'
          newCustom += 'print "This is the Python Script %s" % script.getId(),\n'
          newCustom += 'print "in", container.absolute_url()\n'
          newCustom += 'return printed\n'
          newCustom += '\n'
          newCustom += '# --// /'+ newId + ' //--\n'
        elif newType in [ 'Z SQL Method']:
          newCustom = ''
          newCustom += '<connection>%s</connection>\n'%self.SQLConnectionIDs()[0][0]
          newCustom += '<params></params>\n'
          newCustom += 'SELECT * FROM tablename\n'
      
      # Handle resources.
      if (newType in ['resource']) or \
         (newMandatory and newType in self.getMetaobjIds()) or \
         (newRepetitive and newType in self.getMetaobjIds()):
        if not newCustom:
          if oldId is not None and id+'.'+oldId in self.objectIds():
            self.manage_delObjects(ids=[id+'.'+oldId])
        elif isinstance( newCustom, _blobfields.MyFile):
          if oldId is not None and id+'.'+oldId in self.objectIds():
            self.manage_delObjects(ids=[id+'.'+oldId])
          self.manage_addFile( id=id+'.'+newId, file=newCustom.getData(),title=newCustom.getFilename(),content_type=newCustom.getContentType())
        elif oldId is not None and oldId != newId and id+'.'+oldId in self.objectIds():
          self.manage_renameObject(id=id+'.'+oldId,new_id=id+'.'+newId)
        if not ob['type'] == 'ZMSRecordSet':
          newCustom = ''
      
      attr = {}
      attr['sync'] = False
      attr['id'] = newId
      attr['name'] = newName
      attr['mandatory'] = newMandatory
      attr['multilang'] = newMultilang
      attr['repetitive'] = newRepetitive
      attr['type'] = newType
      attr['keys'] = newKeys
      attr['custom'] = newCustom
      attr['default'] = newDefault
      
      # Parse Dtml for Errors.
      newOb = None
      message = ''
      if newType in [ 'delimiter', 'hint', 'interface']:
        newCustom = newName
        if newCustom.find('<tal:') >= 0:
          newType = 'zpt'
        else:
          newType = 'method'
      if newType in [ 'DTML Method', 'DTML Document', 'method', 'py', 'zpt']:
        newCustom = newCustom.replace('\r','')
      # Handle methods and interfaces.
      if newType in ['method']:
        if oldId is not None and id+'.'+oldId in self.objectIds():
          self.manage_delObjects(ids=[id+'.'+oldId])
        self.manage_addDTMLMethod( id+'.'+newId, newType, newCustom)
        newOb = getattr( self, id+'.'+newId)
        roles=[ 'Manager']
        newOb._proxy_roles=tuple(roles)
      # Handle py.
      if newType in ['py']:
        if oldId is not None and id+'.'+oldId in self.objectIds():
          self.manage_delObjects(ids=[id+'.'+oldId])
        PythonScript.manage_addPythonScript( self, id+'.'+newId)
        newOb = getattr( self, id+'.'+newId)
        newOb.write(newCustom)
        roles=[ 'Manager']
        newOb._proxy_roles=tuple(roles)
      # Handle zpt.
      elif newType in ['zpt']:
        if oldId is not None and id+'.'+oldId in self.objectIds():
          self.manage_delObjects(ids=[id+'.'+oldId])
        ZopePageTemplate.manage_addPageTemplate( self, id+'.'+newId, title=newType, text=newCustom)
        newOb = getattr(self,id+'.'+newId)
        newOb.output_encoding = 'utf-8'
      
      # Restrict access. 
      if newOb is not None:
        newOb.manage_acquiredPermissions([])
        permissions = map(lambda x: x['name'],newOb.permissionsOfRole('Manager'))
        for role_to_manage in [ 'ZMSAuthor', 'ZMSEditor', 'ZMSAdministrator']:
          newOb.manage_role(role_to_manage=role_to_manage,permissions=permissions)
      
      # Replace
      ids = map( lambda x: x['id'], attrs) # self.getMetaobjAttrIds(id)
      if oldId in ids:
        i = ids.index(oldId)
        attrs[i] = attr
      else:
        # Always append new methods at the end.
        if oldId == newId or newType in method_types:
          attrs.append( attr)
        # Insert new attributes before methods
        else:
          i = len( attrs)
          while i > 0 and attrs[ i - 1][ 'type'] in method_types:
            i -= 1
          if i < len(attrs):
            attrs.insert( i, attr)
          else:
            attrs.append( attr)
      ob['attrs'] = attrs
      
      # Handle native Zope-Objects.
      if newType in self.valid_zopetypes:
        # Get container.
        container = self.getHome()
        for ob_id in newId.split('/')[:-1]:
          if ob_id not in container.objectIds():
            container.manage_addFolder(id=ob_id,title='Folder: %s'%id)
          container = getattr( container, ob_id)
        newObId = newId.split('/')[-1]
        # Get container (old).
        if oldId is not None:
          oldContainer = self.getHome()
          for ob_id in oldId.split('/')[:-1]:
            oldContainer = getattr(oldContainer,ob_id,None)
          oldObId = oldId.split('/')[-1]
        # External Method.
        if newType == 'External Method':
          try:
            _fileutil.remove( INSTANCE_HOME+'/Extensions/'+oldObId+'.py')
          except:
            pass
          newExternalMethod = INSTANCE_HOME+'/Extensions/'+newObId+'.py'
          _fileutil.exportObj( newCustom, newExternalMethod)
        # Insert Zope-Object.
        if oldId is None or oldId == newId:
          # Delete existing Zope-Object.
          if newObId in container.objectIds():
            if newType in ['External Method', 'Page Template'] or \
               newType not in self.valid_zopetypes:
              container.manage_delObjects( ids=[ newObId])
            # Delete old Zope-Object if type is incompatible.
            if newObId in container.objectIds() and getattr(container,newObId).meta_type != newType:
              container.manage_delObjects( ids=[ newObId])
          # Add new Zope-Object.
          if newObId not in container.objectIds():
            if newType == 'DTML Method':
              container.manage_addDTMLMethod( newObId, newName, newCustom)
            elif newType == 'DTML Document':
              container.manage_addDTMLDocument( newObId, newName, newCustom)
            elif newType == 'External Method':
              ExternalMethod.manage_addExternalMethod( container, newObId, newName, newId, newId)
            elif newType == 'Folder':
              container.manage_addFolder(id=newObId,title=newName)
            elif newType == 'Page Template':
              ZopePageTemplate.manage_addPageTemplate( container, newObId, title=newName, text=newCustom)
              newOb = getattr( container, newObId)
              newOb.output_encoding = 'utf-8'
            elif newType == 'Script (Python)':
              PythonScript.manage_addPythonScript( container, newObId)
            elif newType == 'Z SQL Method':
              try:
                from Products.ZSQLMethods import SQL
                connection_id = self.SQLConnectionIDs()[0][0]
                arguments = ''
                template = ''
                SQL.manage_addZSQLMethod( container, newObId, newName, connection_id, arguments, template)
              except:
                pass
        # Rename Zope-Object.
        elif oldId != newId:
          if oldContainer != container:
            cb_copy_data = oldContainer.manage_cutObjects( ids=[oldObId])
            container.manage_pasteObjects( cb_copy_data)
          if oldObId != newObId:
            container.manage_renameObject( id=oldObId, new_id=newObId)
        # Change Zope-Object.
        newOb = getattr( container, newObId)
        if newType in [ 'DTML Method', 'DTML Document']:
          newOb.manage_edit( title=newName, data=newCustom)
          roles=[ 'Manager']
          newOb._proxy_roles=tuple(roles)
          if newId.find( 'manage_') >= 0:
            newOb.manage_role(role_to_manage='Authenticated',permissions=['View'])
            newOb.manage_acquiredPermissions([])
        elif newType == 'Folder':
          if isinstance( newCustom, _blobfields.MyFile) and len(newCustom.getData()) > 0:
            newOb.manage_delObjects(ids=newOb.objectIds())
            _ziputil.importZip2Zodb( newOb, newCustom.getData())
          attr['custom'] = ''
        elif newType == 'Script (Python)':
          newOb.write(newCustom)
          roles=[ 'Manager']
          newOb._proxy_roles=tuple(roles)
          if newId.find( 'manage_') >= 0:
            newOb.manage_role(role_to_manage='Authenticated',permissions=['View'])
            newOb.manage_acquiredPermissions([])
        elif newType == 'Z SQL Method':
          connection = newCustom
          connection = connection[connection.find('<connection>'):connection.find('</connection>')]
          connection = connection[connection.find('>')+1:]
          arguments = newCustom
          arguments = arguments[arguments.find('<params>'):arguments.find('</params>')]
          arguments = arguments[arguments.find('>')+1:]
          template = newCustom
          template = template[template.find('</params>'):]
          template = template[template.find('>')+1:]
          template = '\n'.join(filter( lambda x: len(x) > 0, template.split('\n')))
          newOb.manage_edit(title=newName,connection_id=connection,arguments=arguments,template=template)
      
      # Assign Attributes to Meta-Object.
      self.model[id] = ob
      
      # Make persistent.
      self.model = self.model.copy()
      
      # Return with message.
      return message


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.delMetaobjAttr:
    #
    #  Delete attribute from meta-object specified by id.
    # --------------------------------------------------------------------------
    def delMetaobjAttr(self, id, attr_id):
      ob = self.__get_metaobj__(id)
      attrs = copy.copy(ob.get('attrs',[]))
      
      # Delete Attribute.
      cp = []
      for attr in attrs:
        if attr['id'] == attr_id:
          if id+'.'+attr['id'] in self.objectIds():
            self.manage_delObjects(ids=[id+'.'+attr['id']])
          if attr['type'] in self.valid_zopetypes:
            # Get container.
            container = self.getHome()
            for ob_id in attr['id'].split('/')[:-1]:
              container = getattr( container, ob_id)
            ob_id = attr['id'].split('/')[-1]
            if ob_id in container.objectIds([attr['type']]):
              container.manage_delObjects(ids=[ob_id])
            if attr['type'] == 'External Method':
              try:
                _fileutil.remove( INSTANCE_HOME+'/Extensions/'+ob_id+'.py')
              except:
                pass
        else:
          cp.append(attr)
      ob['attrs'] = cp
      
      # Assign Attributes to Meta-Object.
      self.model[id] = ob
      
      # Make persistent.
      self.model = self.model.copy()


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.moveMetaobjAttr:
    #
    #  Move meta-object attribute to specified position.
    # --------------------------------------------------------------------------
    def moveMetaobjAttr(self, id, attr_id, pos):
      ob = self.__get_metaobj__(id)
      attrs = copy.copy(ob['attrs'])
      # Move Attribute.
      ids = self.getMetaobjAttrIds(id)
      i = ids.index(attr_id)
      attr = attrs[i]
      attrs.remove(attr)
      attrs.insert(pos,attr)
      ob['attrs'] = attrs
      # Assign Attributes to Meta-Object.
      self.model[id] = ob
      # Make persistent.
      self.model = self.model.copy()


    ############################################################################
    #  ZMSMetaobjManager.manage_ajaxChangeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_ajaxChangeProperties(self, id, REQUEST, RESPONSE=None):
      """ MetaobjManager.manage_ajaxChangeProperties """
      xml = self.getXmlHeader()
      xml += '<result '
      xml += ' id="%s"'%id
      ob = self.__get_metaobj__(id)
      prefix = 'set'
      for key in REQUEST.form.keys():
        if key.startswith(prefix):
          k = key[len(prefix):].lower()
          v = REQUEST.form.get(key)
          if k in ob.keys():
            if ob.get('acquired'):
              self.setConfProperty('%s.%s'%(id,k),v)
            else:
              ob[k] = v
            xml += ' %s="%s"'%(k,str(v))
      xml += '/>'
      # Assign Attributes to Meta-Object.
      self.model[id] = ob
      # Make persistent.
      self.model = self.model.copy()
      # Return with xml
      if RESPONSE is not None:
        content_type = 'text/xml; charset=utf-8'
        filename = 'manage_ajaxChangeProperties.xml'
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename="%s"'%filename)
        RESPONSE.setHeader('Cache-Control', 'no-cache')
        RESPONSE.setHeader('Pragma', 'no-cache')
        return xml


    ############################################################################
    #  ZMSMetaobjManager.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, btn='', key='all', REQUEST=None, RESPONSE=None):
        """ ZMSMetaobjManager.manage_changeProperties """
        old_model = copy.deepcopy(self.model)
        message = ''
        messagekey = 'manage_tabs_message'
        extra = {}
        t0 = time.time()
        id = REQUEST.get('id','').strip()
        target = REQUEST.get('target','manage_main')
        REQUEST.set( '__get_metaobjs__', True)
        
        try:
          sync_id = []
          
          # Delete.
          # -------
          # Delete Object.
          if key == 'obj' and btn == self.getZMILangStr('BTN_DELETE'):
            if id:
              meta_ids = [id]
            else:
              meta_ids = REQUEST.get('ids',[])
            for meta_id in meta_ids:
              metaObj = self.getMetaobj( meta_id)
              if metaObj['type'] == 'ZMSPackage':
                for pkgMetaObjId in self.getMetaobjIds():
                  pkgMetaObj = self.getMetaobj( pkgMetaObjId)
                  if pkgMetaObj.get('package') == metaObj.get('id'):
                    if pkgMetaObjId not in meta_ids:
                      meta_ids.append( pkgMetaObjId)
            for meta_id in meta_ids:
              self.delMetaobj(meta_id)
            id = ''
            message = self.getZMILangStr('MSG_DELETED')%len(meta_ids)
          # Delete Attribute.
          elif key == 'attr' and btn == 'delete':
            attr_id = REQUEST['attr_id']
            self.delMetaobjAttr( id, attr_id)
          
          # Change.
          # -------
          elif key == 'all' and btn == self.getZMILangStr('BTN_SAVE'):
            savedAttrs = copy.copy(self.getMetaobj(id)['attrs'])
            # Change object.
            newValue = {}
            newValue['id'] = id
            newValue['name'] = REQUEST.get('obj_name').strip()
            newValue['revision'] = REQUEST.get('obj_revision','').strip()
            newValue['type'] = REQUEST.get('obj_type').strip()
            newValue['package'] = REQUEST.get('obj_package','').strip()
            newValue['attrs'] = savedAttrs
            newValue['enabled'] = REQUEST.get('obj_enabled',0)
            newValue['access'] = {
             'insert_deny': REQUEST.get( 'access_insert_deny', []),
             'insert_custom': REQUEST.get( 'access_insert_custom', ''),
             'delete_deny': REQUEST.get( 'access_delete_deny', []),
             'delete_custom': REQUEST.get( 'access_delete_custom', ''),
            }
            self.setMetaobj( newValue)
            # Change attributes.
            for old_id in REQUEST.get('old_ids',[]):
              attr_id = REQUEST['attr_id_%s'%old_id].strip()
              newName = REQUEST['attr_name_%s'%old_id].strip()
              newMandatory = REQUEST.get( 'attr_mandatory_%s'%old_id, 0)
              newMultilang = REQUEST.get( 'attr_multilang_%s'%old_id, 0)
              newRepetitive = REQUEST.get( 'attr_repetitive_%s'%old_id, 0)
              newType = REQUEST.get( 'attr_type_%s'%old_id)
              newKeys = self.string_list(REQUEST.get('attr_keys_%s'%old_id,''),'\n')
              newCustom = REQUEST.get('attr_custom_%s'%old_id,'')
              newDefault = REQUEST.get('attr_default_%s'%old_id,'')
              # Upload resource.
              if isinstance(newCustom,ZPublisher.HTTPRequest.FileUpload):
                  if len(getattr(newCustom,'filename','')) > 0:
                      newCustom = _blobfields.createBlobField( self,_globals.DT_FILE, newCustom, mediadbStorable=False)
                  else:
                      REQUEST.set('attr_custom_%s_modified'%old_id,'0')
              # Restore resource.
              if REQUEST.get('attr_custom_%s_modified'%old_id,'1') == '0' and \
                 REQUEST.get('attr_custom_%s_active'%old_id,'0') == '1':
                  savedAttr = filter(lambda x: x['id']==old_id, savedAttrs)[0]
                  syncType( self, id, savedAttr)
                  newCustom = savedAttr['custom']
              # Change attribute.
              message += self.setMetaobjAttr( id, old_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
            # Return with message.
            message += self.getZMILangStr('MSG_CHANGED')
            # Insert attribute.
            attr_id = REQUEST.get('attr_id','').strip()
            newName = REQUEST.get('attr_name','').strip()
            newMandatory = REQUEST.get('_mandatory',0)
            newMultilang = REQUEST.get('_multilang',0)
            newRepetitive = REQUEST.get('_repetitive',0)
            newType = REQUEST.get('_type','string')
            newKeys = REQUEST.get('_keys',[])
            newCustom = REQUEST.get('_custom','')
            newDefault = REQUEST.get('_default','')
            if (len(attr_id) > 0 and len(newName) > 0 and len(newType) > 0) or newType in self.getMetadictAttrs():
              message += self.setMetaobjAttr( id, None, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
              message += self.getZMILangStr('MSG_INSERTED')%attr_id
          elif key == 'obj' and btn == self.getZMILangStr('BTN_SAVE'):
            # Change Acquired-Object.
            subobjects = REQUEST.get('obj_subobjects',0)
            self.acquireMetaobj( id, subobjects)
            # Return with message.
            message += self.getZMILangStr('MSG_CHANGED')
          
          # Copy.
          # -----
          elif btn == self.getZMILangStr('BTN_COPY'):
            metaOb = self.getMetaobj(id)
            if metaOb.get('acquired',0) == 1:
              xml = self.getPortalMaster().metaobj_manager.exportMetaobjXml([id])
              self.importMetaobjXml(xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%id)
          
          # Export.
          # -------
          elif btn == self.getZMILangStr('BTN_EXPORT'):
            ids = REQUEST.get('ids',[])
            return self.exportMetaobjXml(ids,REQUEST,RESPONSE)
          
          # Insert.
          # -------
          elif btn == self.getZMILangStr('BTN_INSERT'):
            # Insert Object.
            if key == 'obj':
              id = REQUEST['_meta_id'].strip()
              newValue = {}
              newValue['id'] = id
              newValue['name'] = REQUEST.get('_meta_name').strip()
              newValue['type'] = REQUEST.get('_meta_type').strip()
              self.setMetaobj( newValue)
              # Insert Attributes.
              if newValue['type'] == 'ZMSDocument':
                message += self.setMetaobjAttr(id,None,newId='titlealt',newType='titlealt')
                message += self.setMetaobjAttr(id,None,newId='title',newType='title')
              elif newValue['type'] == 'ZMSTeaserElement':
                message += self.setMetaobjAttr(id,None,newId='titlealt',newType='titlealt')
                message += self.setMetaobjAttr(id,None,'attr_penetrance',self.getZMILangStr('ATTR_PENETRANCE'),1,1,0,'select',['this','sub_nav','sub_all'])
              elif newValue['type'] == 'ZMSRecordSet':
                message += self.setMetaobjAttr(id,None,'records',self.getZMILangStr('ATTR_RECORDS'),1,1,0,'list')
                message += self.setMetaobjAttr(id,None,'col_id','COL_ID',1,0,0,'identifier',[],0)
                message += self.setMetaobjAttr(id,None,'col_1','COL_1',0,0,0,'string',[],1)
                message += self.setMetaobjAttr(id,None,'col_2','COL_2',0,0,0,'string',[],1)
              elif newValue['type'] == 'ZMSModule':
                message += self.setMetaobjAttr(id,None,'zexp','ZEXP',0,0,0,'resource')
              # Insert Template.
              if newValue['type'] not in [ 'ZMSModule', 'ZMSPackage']:
                tmpltId = 'standard_html'
                tmpltName = 'Template: %s'%newValue['name']
                tmpltCustom = []
                tmpltCustom.append('<!-- %s.%s -->\n'%(id,tmpltId))
                tmpltCustom.append('\n')
                tmpltCustom.append('<tal:block tal:define="global\n')
                tmpltCustom.append('\t\tzmscontext options/zmscontext">\n')
                if newValue['type'] == 'ZMSRecordSet':
                  tmpltCustom.append('\t<h2 tal:content="python:zmscontext.getTitlealt(request)">The title.alt</h2>\n')
                  tmpltCustom.append('\t<p class="description" tal:content="python:\'%i %s\'%(len(zmscontext.attr(zmscontext.getMetaobj(zmscontext.meta_id)[\'attrs\'][0][\'id\'])),zmscontext.getLangStr(\'ATTR_RECORDS\',request[\'lang\']))">#N records</p>\n')
                tmpltCustom.append('</tal:block>\n')
                tmpltCustom.append('\n')
                tmpltCustom.append('<!-- /%s.%s -->\n'%(id,tmpltId))
                tmpltCustom = ''.join(tmpltCustom)
                message += self.setMetaobjAttr(id,None,tmpltId,tmpltName,0,0,0,'zpt',[],tmpltCustom)
              message += self.getZMILangStr('MSG_INSERTED')%id
          
          # Acquire.
          # --------
          elif btn == self.getZMILangStr('BTN_ACQUIRE'):
            immediately = REQUEST.get('immediately',0)
            overwrite = []
            ids = REQUEST.get('aq_ids',[])
            for id in ids:
              if not immediately and id in self.getMetaobjIds():
                overwrite.append( id)
              else:
                self.acquireMetaobj( id)
            if overwrite:
              id = ''
              extra['section'] = 'acquire'
              extra['temp_ids'] = ','.join(overwrite)
            else:
              # Return with message.
              message = self.getZMILangStr('MSG_INSERTED')%str(len(ids))
          
          # Import.
          # -------
          elif btn == self.getZMILangStr('BTN_IMPORT'):
            immediately = False
            xmlfile = None
            temp_folder = self.temp_folder
            temp_id = self.id + '_' + REQUEST['AUTHENTICATED_USER'].getId() + '.xml'
            if temp_id in temp_folder.objectIds():
              filename = str(getattr( temp_folder, temp_id).title)
              xmlfile = str(getattr( temp_folder, temp_id).data)
              temp_folder.manage_delObjects([temp_id])
              immediately = True
            if REQUEST.get('file'):
              f = REQUEST['file']
              filename = f.filename
              xmlfile = f
            if REQUEST.get('init'):
              file = REQUEST['init']
              filename, xmlfile = self.getConfXmlFile( file)
            if xmlfile is not None:
              if not immediately:
                xml = xmlfile.read()
                xmlfile = StringIO( xml)
                v = self.parseXmlString( xmlfile, mediadbStorable=False)
                xmlfile = StringIO( xml)
                immediately = not type( v) is list
              if not immediately:
                file = temp_folder.manage_addFile(id=temp_id,title=filename,file=xmlfile)
                extra['section'] = 'import'
                extra['temp_import_file_id'] = temp_id
              else:
                createIdsFilter = REQUEST.get('createIdsFilter')
                ids = self.importMetaobjXml(xmlfile,createIdsFilter=createIdsFilter)
                if type(ids) is list:
                  sync_id.extend(ids)
                else:
                  sync_id.append(ids)
                message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%filename)
          
          # Move to.
          # --------
          elif key == 'attr' and btn == 'move_to':
            pos = REQUEST['pos']
            attr_id = REQUEST['attr_id']
            self.moveMetaobjAttr( id, attr_id, pos)
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<em>%s</em>"%attr_id),(pos+1))
          
          ##### SYNCHRONIZE ####
          types = self.valid_types+map(lambda x:self.metas[x*2],range(len(self.metas)/2))
          for k in self.getMetaobjIds():
            if k not in sync_id:
              if old_model.has_key(k):
                d = self.model[k]
                types_attrs = map(lambda x: (x['id'],x), filter(lambda x: x['type'] in types, d.get('attrs',[])))
                d = old_model[k]
                old_types_attrs = map(lambda x: (x['id'],x), filter(lambda x: x['type'] in types, d.get('attrs',[])))
                if types_attrs != old_types_attrs:
                  sync_id.append(k)
              else:
                sync_id.append(k)
          if len(sync_id) > 0:
            _globals.writeBlock( self, '[ZMSMetaobjManager.manage_changeProperties]: sync_id=%s'%str(sync_id))
            self.synchronizeObjAttrs( sync_id)
        
        # Handle exception.
        except:
          message = _globals.writeError(self,"[manage_changeProperties]")
          messagekey = 'manage_tabs_error_message'
        
        # Return with message.
        if RESPONSE:
          if len( message) > 0:
            message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
            target = self.url_append_params( target, { messagekey: message})
          target = self.url_append_params( target, { 'lang': lang, 'id':id, 'attr_id':REQUEST.get('attr_id','')})
          target = self.url_append_params( target, extra)
          if REQUEST.has_key('inp_id_name'):
            target += '&inp_id_name=%s'%REQUEST.get('inp_id_name')
            target += '&inp_name_name=%s'%REQUEST.get('inp_name_name')
            target += '&inp_value_name=%s'%REQUEST.get('inp_value_name')
            target += '#Edit'
          return RESPONSE.redirect( target)
        
        return message

################################################################################
