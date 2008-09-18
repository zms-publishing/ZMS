################################################################################
# ZMSMetaobjManager.py
#
# $Id:$
# $Name:$
# $Author:$
# $Revision:$
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
from Products.ExternalMethod import ExternalMethod
from Products.PythonScripts import PythonScript
from Products.ZSQLMethods import SQL
import ZPublisher.HTTPRequest
import copy
import sys
import time
# Product Imports.
import _blobfields
import _fileutil
import _globals


# ------------------------------------------------------------------------------
#  Synchronize type.
# ------------------------------------------------------------------------------
def syncType( self, meta_id, attr):
  try:
    if attr['type'] == 'resource':
      ob = getattr( self, meta_id+'.'+attr['id'], None)
      if ob is not None:
        attr['custom'] = ob
    elif attr['type'] == 'method':
      ob = getattr( self, meta_id+'.'+attr['id'], None)
      if ob is not None:
        attr['custom'] = ob.raw
    elif attr['type'] == 'interface':
      ob = getattr( self, meta_id+'.'+attr['id'], None)
      if ob is not None:
        attr['name'] = ob.raw
    elif attr['type'] in self.valid_zopetypes:
      home = self.getHome()
      ob = getattr( home, attr['id'])
      if ob.meta_type in [ 'DTML Method', 'DTML Document']:
        attr['custom'] = ob.raw
      elif ob.meta_type in [ 'Script (Python)']:
        attr['custom'] = ob.body()
      elif ob.meta_type in [ 'Z SQL Method']:
        connection = ob.connection_id
        params = ob.arguments_src
        attr['custom'] = '<connection>%s</connection>\n<params>%s</params>\n%s'%(connection,params,ob.src)
  except:
    value = _globals.writeException(self,'[getMetaobjAttr]')


# ------------------------------------------------------------------------------
#  Search tree for instance of object with given meta-ids.
# ------------------------------------------------------------------------------
def findMetaobj(self, ids):
  if self.meta_id in ids:
    return self
  for child in self.getChildNodes():
    ob = findMetaobj(child, ids)
    if ob is not None:
      return ob
  return None


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
    valid_types = ['amount','autocomplete','boolean','color','date','datetime','dialog','dictionary','file','float','identifier','image','int','list','multiselect','password','richtext','select','string','text','time','url','xml']
    valid_xtypes = ['constant','delimiter','hint','interface','method','resource']
    valid_datatypes = ['amount','autocomplete','boolean','color','constant','date','datetime','delimiter','dialog','dictionary','file','float','hint','identifier','image','int','interface','list','method','multiselect','password','resource','richtext','select','string','text','time','url','xml']
    valid_objtypes = [ 'ZMSDocument', 'ZMSObject', 'ZMSTeaserElement', 'ZMSRecordSet', 'ZMSResource', 'ZMSReference', 'ZMSLibrary', 'ZMSPackage', 'ZMSModule']
    valid_zopetypes = [ 'DTML Method', 'DTML Document', 'External Method', 'Script (Python)', 'Z SQL Method']


    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.importMetaobjXml
    # --------------------------------------------------------------------------

    def _importMetaobjXml(self, item, zms_system=0, createIfNotExists=1):
      id = item['key']
      ids = filter( lambda x: self.model[x].get('zms_system',0)==1, self.model.keys())
      if createIfNotExists == 1 or id in ids:
        newDtml = item.get('dtml')
        newValue = item.get('value')
        newAttrs = newValue.get('attrs',newValue.get('__obj_attrs__'))
        newValue['attrs'] = []
        newValue['id'] = id
        newValue['enabled'] = newValue.get('enabled',item.get('enabled',1))
        newValue['zms_system'] = zms_system
        # Delete Object.
        oldAttrs = None
        if id in ids:
          if zms_system == 1:
            oldAttrs = self.getMetaobj( id)['attrs']
          self.delMetaobj( id)
        # Set Object.
        self.setMetaobj( newValue)
        # Set Attributes.
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
              self.setMetaobjAttr( id, None, oldAttr['id'], oldAttr['name'], oldAttr['mandatory'], oldAttr['multilang'], oldAttr['repetitive'], oldAttr['type'], oldAttr['keys'], oldAttr['custom'], oldAttr['default'], zms_system)
              oldAttrs.remove( oldAttr)
            if len(oldAttrs) > 0:
              oldAttrs.remove( oldAttrs[0])
          # Set Attribute.
          self.setMetaobjAttr( id, attr_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault, zms_system)
        # Set Template (backwards compatibility).
        if newValue['type'] not in [ 'ZMSLibrary', 'ZMSModule', 'ZMSPackage'] and newDtml is not None:
          tmpltId = self.getTemplateId( id)
          tmpltName = 'Template: %s'%newValue['name']
          tmpltCustom = newDtml
          newType = 'DTML Method'
          newKeys = []
          newDefault = ''
          self.setMetaobjAttr(id,tmpltId,tmpltId,tmpltName,0,0,0, newType, newKeys, tmpltCustom, newDefault, zms_system)

    def importMetaobjXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
      self.REQUEST.set( '__get_metaobjs__', True)
      v = self.parseXmlString( xml, mediadbStorable=False)
      if type(v) is list:
        for item in v:
          id = self._importMetaobjXml(item,zms_system,createIfNotExists)
      else:
        id = self._importMetaobjXml(v,zms_system,createIfNotExists)


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getTemplateId
    #
    #  Returns template-id for meta-object specified by given Id.
    # --------------------------------------------------------------------------
    def getTemplateId(self, id):
      return "bodyContentZMSCustom_%s"%id


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
              ob = master_obs[ob_id].copy()
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
        if ob['type'] == 'ZMSDocument' or ob['id'] == 'ZMSTeaserContainer':
          ids = map( lambda x: x['id'], filter( lambda x: x['type']=='*', ob['attrs']))
          rtnVal = ids == ['e']
        
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
      return _globals.nvl( self.__get_metaobj__(id), {})


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
      ob[ 'type'] = ob.get( 'type', '')
      ob[ 'package'] = ob.get( 'package', '')
      ob[ 'attrs'] = ob.get( 'attrs', ob.get( '__obj_attrs__', []))
      ob[ 'acquired'] = ob.get( 'acquired' ,0)
      ob[ 'enabled'] = ob.get( 'enabled', 1)
      ob[ 'zms_system'] = ob.get( 'zms_system', 0)
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
        if ob['type'] == 'ZMSPackage':
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
    #  ZMSMetaobjManager.getMetaobjAttrIdentifierId:
    # 
    #  Returns attribute-id of datatable-identifier for meta-object specified by id.
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
    def getMetaobjAttrIds(self, meta_id, types=[]):
      ids = []
      ob = self.__get_metaobj__(meta_id)
      if ob is not None:
        attrs = ob.get('attrs',ob.get('__obj_attrs__'))
        if attrs is None:
          raise 'Can\'t getMetaobjAttrIds: %s'%(str(meta_id))
        if len( types) > 0:
          attrs = filter( lambda x: x['type'] in types, attrs)
        ids = map(lambda x: x['id'], attrs)
      return ids


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.getMetaobjAttr:
    # 
    #  Get attribute for meta-object specified by attribute-id.
    # --------------------------------------------------------------------------
    def getMetaobjAttr(self, meta_id, key):
      meta_objs = self.__get_metaobjs__()
      if meta_objs.get(meta_id,{}).get('acquired',0) == 1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          attr = portalMaster.getMetaobjAttr( meta_id, key)
          return attr
      meta_obj = meta_objs.get(meta_id)
      attrs = meta_obj.get('attrs',meta_obj.get('__obj_attrs__'))
      if attrs is None:
        raise 'Can\'t getMetaobjAttr %s.%s'%(str(meta_id),str(key))
      for attr in attrs:
        if key == attr['type']:
          meta_attrs = self.getMetadictAttrs()
          if key in meta_attrs:
            attr_meta_type = attr['type']
            attr = self.getMetadictAttr( attr_meta_type).copy()
            attr['meta_type'] = attr_meta_type
            return attr
        if key == attr['id']:
          attr = attr.copy()
          attr['mandatory'] = attr.get('mandatory',0)
          attr['multilang'] = attr.get('multilang',1)
          attr['errors'] = attr.get('errors','')
          meta_types = meta_objs.keys()
          valid_types = self.valid_datatypes+self.valid_zopetypes+meta_types+['*']
          # type is valid: sync type (copy can be edited directly in ZODB via FTP!)
          if attr['type'] in valid_types:
            attr['meta_type'] = ''
            syncType( self, meta_id, attr)
          # type not found: may be meta-attribute (must be '?' to display error on customize-form!)
          else:
            attr['meta_type'] = '?'
          return attr
      return None


    # --------------------------------------------------------------------------
    #  ZMSMetaobjManager.setMetaobjAttr:
    # 
    #  Set/add meta-object attribute with specified values.
    # --------------------------------------------------------------------------
    def setMetaobjAttr(self, id, oldId, newId, newName='', newMandatory=0, newMultilang=1, newRepetitive=0, newType='string', newKeys=[], newCustom='', newDefault='', zms_system=0):
      ob = self.__get_metaobj__(id)
      attrs = copy.copy(ob['attrs'])
      
      # Set Attributes.
      if newType in ['delimiter','hint','interface']:
        newCustom = ''
      if newType in ['resource'] and (type(newCustom) is str or type(newCustom) is int):
        newCustom = None
      if newType not in ['*','autocomplete','dialog','multiselect','recordset','select']:
        newKeys = []
      if newType in self.getMetaobjIds(sort=0)+['*']:
        newMultilang = 0
      
      # Defaults for Insert
      method_types = [ 'method'] + self.valid_zopetypes
      if oldId is None and \
         newType in method_types and \
         (newCustom == '' or type(newCustom) is not str):
        if newType in [ 'method', 'DTML Method', 'DTML Document']:
          newCustom = ''
          newCustom += '<dtml-comment>--// BO '+ newId + ' //--</dtml-comment>\n'
          newCustom += '\n'
          newCustom += '<dtml-comment>--// EO '+ newId + ' //--</dtml-comment>\n'
        elif newType in [ 'External Method']:
          newCustom = ''
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += 'def ' + newId + '():\n'
          newCustom += '  return "This is the external method ' + newId + '"\n'
        elif newType in [ 'Script (Python)']:
          newCustom = ''
          newCustom += '# --// BO '+ newId + ' //--\n'
          newCustom += '# Example code:\n'
          newCustom += '\n'
          newCustom += '# Import a standard function, and get the HTML request and response objects.\n'
          newCustom += 'from Products.PythonScripts.standard import html_quote\n'
          newCustom += 'request = container.REQUEST\n'
          newCustom += 'RESPONSE =  request.RESPONSE\n'
          newCustom += '\n'
          newCustom += '# Return a string identifying this script.\n'
          newCustom += 'print "This is the", script.meta_type, \'"%s"\' % script.getId(),\n'
          newCustom += 'if script.title:\n'
          newCustom += '    print "(%s)" % html_quote(script.title),\n'
          newCustom += 'print "in", container.absolute_url()\n'
          newCustom += 'return printed\n'
          newCustom += '\n'
          newCustom += '# --// EO '+ newId + ' //--\n'
        elif newType in [ 'Z SQL Method']:
          newCustom = ''
          newCustom += '<connection>%s</connection>\n'%self.SQLConnectionIDs()[0][0]
          newCustom += '<params></params>\n'
          newCustom += 'SELECT * FROM tablename\n'
      
      # Handle resources.
      if newType == 'resource':
        if isinstance( newCustom, _blobfields.MyFile):
          if oldId is not None and id+'.'+oldId in self.objectIds():
            self.manage_delObjects(ids=[id+'.'+oldId])
          self.manage_addFile( id=id+'.'+newId, file=newCustom.getData(),title=newCustom.getFilename(),content_type=newCustom.getContentType())
        elif oldId is not None and oldId != newId and id+'.'+oldId in self.objectIds(['File']):
          self.manage_renameObject(id=id+'.'+oldId,new_id=id+'.'+newId)
        newCustom = ''
      
      attr = {}
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
      message = ''
      dtml = ''
      if newType in [ 'delimiter', 'hint', 'interface']:
        dtml = newName
      elif newType in [ 'method', 'DTML Method', 'DTML Document']:
        dtml = newCustom
      if len(dtml) > 0:
        message = _globals.dt_parse( self, dtml)
        if len( message) > 0:
          attr['errors'] = message
          message = '<div class="form-label">' + newId + '</div><div style="color:red; background-color:yellow; ">%s</div>'%message
        else:
          # Handle methods.
          if newType == 'method':
            if oldId is not None and id+'.'+oldId in self.objectIds():
              self.manage_delObjects(ids=[id+'.'+oldId])
            self.manage_addDTMLMethod( id+'.'+newId, newType+': '+newName, newCustom)
          # Handle interfaces.
          elif newType == 'interface':
            if oldId is not None and id+'.'+oldId in self.objectIds():
              self.manage_delObjects(ids=[id+'.'+oldId])
            self.manage_addDTMLMethod( id+'.'+newId, newType, newName)
      
      # Replace
      ids = self.getMetaobjAttrIds(id)
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
      
      # Handle Zope-Objects.
      if newType in self.valid_zopetypes:
        # Remove Zope-Object (deprecated use in document-element).
        container = self.getDocumentElement()
        if oldId in container.objectIds():
          container.manage_delObjects( ids=[ oldId])
          oldId = None
        # External Method.
        if newType == 'External Method':
          try:
            _fileutil.remove( INSTANCE_HOME+'/Extensions/'+oldId+'.py')
          except:
            pass
          newExternalMethod = INSTANCE_HOME+'/Extensions/'+newId+'.py'
          _fileutil.exportObj( newCustom, newExternalMethod)
        # Insert Zope-Object.
        container = self.getHome()
        if oldId is None or oldId == newId:
          if newId in container.objectIds():
            container.manage_delObjects( ids=[ newId])
          if newType == 'DTML Method':
            container.manage_addDTMLMethod( newId, newName, newCustom)
          elif newType == 'DTML Document':
            container.manage_addDTMLDocument( newId, newName, newCustom)
          elif newType == 'External Method':
            ExternalMethod.manage_addExternalMethod( container, newId, newName, newId, newId)
          elif newType == 'Script (Python)':
            PythonScript.manage_addPythonScript( container, newId)
          elif newType == 'Z SQL Method':
            connection_id = self.SQLConnectionIDs()[0][0]
            arguments = ''
            template = ''
            SQL.manage_addZSQLMethod( container, newId, newName, connection_id, arguments, template)
        # Rename Zope-Object.
        elif oldId != newId:
          container.manage_renameObject( id=oldId, new_id=newId)
        # Change Zope-Object.
        obElmnt = getattr( container, newId)
        if newType in [ 'DTML Method', 'DTML Document' ]:
          obElmnt.manage_edit( title=newName, data=newCustom)
          roles=[ 'Manager']
          obElmnt._proxy_roles=tuple(roles)
          if newId.find( 'manage_') == 0:
            obElmnt.manage_role(role_to_manage='Authenticated',permissions=['View'])
            obElmnt.manage_acquiredPermissions([])
        elif newType == 'Script (Python)':
          params = obElmnt._params
          body = ''
          count = 0
          for s in newCustom.split( '\n'):
            if count == 0 and \
               s.find( '# --// BO %s('%newId) == 0 and \
               s.find( ') //--') > 0:
              params = s[s.find('(')+1:s.rfind(')')]
            while len(s) > 0 and ord(s[-1]) == 13:
              s = s[:-1]
            body += s + '\n'
            count += 1
          obElmnt.ZPythonScript_setTitle( newName)
          obElmnt.ZPythonScript_edit( params=params, body=body)
          roles=[ 'Manager']
          obElmnt._proxy_roles=tuple(roles)
          if newId.find( 'manage_') == 0:
            obElmnt.manage_role(role_to_manage='Authenticated',permissions=['View'])
            obElmnt.manage_acquiredPermissions([])
        elif newType == 'Z SQL Method':
          valid_connection_ids = map( lambda x: x[0], self.SQLConnectionIDs())
          connection = newCustom
          connection = connection[connection.find('<connection>'):connection.find('</connection>')]
          connection = connection[connection.find('>')+1:]
          if connection not in valid_connection_ids:
            connection = valid_connection_ids[0]
          arguments = newCustom
          arguments = arguments[arguments.find('<params>'):arguments.find('</params>')]
          arguments = arguments[arguments.find('>')+1:]
          template = newCustom
          template = template[template.find('</params>'):]
          template = template[template.find('>')+1:]
          template = '\n'.join(filter( lambda x: len(x) > 0, template.split('\n')))
          obElmnt.manage_edit(title=newName,connection_id=connection,arguments=arguments,template=template)
      
      # Assign Attributes to Meta-Object.
      ob['zms_system'] = int( ob['zms_system'] and (oldId is None or zms_system))
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
      attrs = copy.copy(ob['attrs'])
      
      # Delete Attribute.
      cp = []
      for attr in attrs:
        if attr['id'] == attr_id:
          if id+'.'+attr['id'] in self.objectIds():
            self.manage_delObjects(ids=[id+'.'+attr['id']])
          if attr['type'] in self.valid_zopetypes:
            home = self.getHome()
            if attr['id'] in home.objectIds([attr['type']]):
              home.manage_delObjects(ids=[attr['id']])
            if attr['type'] == 'External Method':
              try:
                _fileutil.remove( INSTANCE_HOME+'/Extensions/'+attr['id']+'.py')
              except:
                pass
        else:
          cp.append(attr)
      ob['attrs'] = cp
      
      # Assign Attributes to Meta-Object.
      ob['zms_system'] = 0
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
    def manage_ajaxChangeProperties(self, id, REQUEST=None, RESPONSE=None):
      """ MetaobjManager.manage_ajaxChangeProperties """
      ob = self.__get_metaobj__(id)
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      filename = 'manage_ajaxChangeProperties.xml'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      xml = self.getXmlHeader()
      xml += '<result '
      xml += ' id="%s"'%id
      for key in REQUEST.form.keys():
        if key.find('set') == 0:
          k = key[3:].lower()
          v = REQUEST.form.get(key)
          if k in ob.keys():
            ob[k] = v
            xml += ' %s="%s"'%(k,str(v))
      xml += '/>'
      # Assign Attributes to Meta-Object.
      self.model[id] = ob
      # Make persistent.
      self.model = self.model.copy()
      return xml


    ############################################################################
    #  ZMSMetaobjManager.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, lang, btn='', key='all', REQUEST=None, RESPONSE=None):
        """ ZMSMetaobjManager.manage_changeProperties """
        message = ''
        t0 = time.time()
        id = REQUEST.get('id','')
        sync_id = None
        target = 'manage_main'
        REQUEST.set( '__get_metaobjs__', True)
        
        try:
          
          # Delete.
          # -------
          # Delete Object.
          if key == 'obj' and btn == self.getZMILangStr('BTN_DELETE'):
            ids = [id]
            metaObj = self.getMetaobj( id)
            if metaObj['type'] == 'ZMSPackage':
              for pkgMetaObjId in self.getMetaobjIds():
                pkgMetaObj = self.getMetaobj( pkgMetaObjId)
                if pkgMetaObj[ 'package'] == metaObj[ 'id']:
                    ids.insert( 0, pkgMetaObjId)
            metaobj = findMetaobj( self, ids)
            if metaobj is None:
              for id in ids:
                self.delMetaobj( id)
              id = ''
              message = self.getZMILangStr('MSG_CHANGED')
            else:
              raise 'All instances of "%s" must be deleted before definition can be deleted: <a href="%s/manage_main#_%s">%s</a>!'%(id,metaobj.getParentNode().absolute_url(),metaobj.id,metaobj.absolute_url())
          # Delete Attribute.
          elif key == 'attr' and btn == 'delete':
            attr_id = REQUEST['attr_id']
            self.delMetaobjAttr( id, attr_id)
          
          # Change.
          # -------
          elif key == 'all' and btn == self.getZMILangStr('BTN_CHANGE'):
            sync_id = id
            savedAttrs = copy.copy(self.getMetaobj(id)['attrs'])
            # Change Object.
            id = REQUEST['id'].strip()
            newValue = {}
            newValue['id'] = id
            newValue['name'] = REQUEST.get('obj_name').strip()
            newValue['type'] = REQUEST.get('obj_type').strip()
            newValue['package'] = REQUEST.get('obj_package').strip()
            newValue['attrs'] = savedAttrs
            newValue['enabled'] = REQUEST.get('obj_enabled',0)
            newValue['access'] = {
             'insert': REQUEST.get( 'access_insert', []),
             'insert_custom': REQUEST.get( 'access_insert_custom', ''),
             'edit': REQUEST.get( 'access_edit', []),
             'edit_custom': REQUEST.get( 'access_edit_custom', ''),
             'delete': REQUEST.get( 'access_delete', []),
             'delete_custom': REQUEST.get( 'access_delete_custom', ''),
            }
            self.setMetaobj( newValue)
            # Change Attributes.
            for old_id in REQUEST.get('old_ids',[]):
              attr_id = REQUEST['attr_id_%s'%old_id].strip()
              newName = REQUEST['attr_name_%s'%old_id].strip()
              newMandatory = REQUEST.get( 'attr_mandatory_%s'%old_id, 0)
              newMultilang = REQUEST.get( 'attr_multilang_%s'%old_id, 0)
              newRepetitive = REQUEST.get( 'attr_repetitive_%s'%old_id, 0)
              newType = REQUEST.get( 'attr_type_%s'%old_id)
              newMetaType = REQUEST.get( 'attr_meta_type_%s'%old_id, '')
              newKeys = self.string_list(REQUEST.get('attr_keys_%s'%old_id,''),'\n')
              newCustom = REQUEST.get('attr_custom_%s'%old_id,'')
              newDefault = REQUEST.get('attr_default_%s'%old_id,'')
              if len( newMetaType) > 0:
                attr_id = old_id
                newType = newMetaType
              if isinstance(newCustom,ZPublisher.HTTPRequest.FileUpload):
                if len(getattr(newCustom,'filename','')) > 0:
                    newCustom = _blobfields.createBlobField( self,_globals.DT_FILE, newCustom, mediadbStorable=False)
              message += self.setMetaobjAttr( id, old_id, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault )
            # Return with message.
            message += self.getZMILangStr('MSG_CHANGED')
          elif key == 'obj' and btn == self.getZMILangStr('BTN_CHANGE'):
            sync_id = id
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
              masterRoot = getattr(self,self.getConfProperty('Portal.Master'))
              masterDocElmnt = masterRoot.content
              REQUEST.set('ids',[id])
              xml =  masterDocElmnt.metaobj_manager.manage_changeProperties(lang, self.getZMILangStr('BTN_EXPORT'), key, REQUEST, RESPONSE)
              self.importMetaobjXml(xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
          
          # Export.
          # -------
          elif btn == self.getZMILangStr('BTN_EXPORT'):
            sync_id = False
            value = []
            ids = REQUEST.get('ids',[])
            for id in ids:
              metaObj = self.getMetaobj( id)
              if metaObj['type'] == 'ZMSPackage':
                for pkgMetaObjId in self.getMetaobjIds():
                    pkgMetaObj = self.getMetaobj( pkgMetaObjId)
                    if pkgMetaObj[ 'package'] == metaObj[ 'id']:
                      ids.append( pkgMetaObjId)
            keys = self.model.keys()
            keys.sort()
            for id in keys:
              if id in ids or len(ids) == 0:
                ob = copy.deepcopy(self.__get_metaobj__(id))
                attrs = []
                for attr in ob['attrs']:
                  attr_id = attr['id']
                  syncType( self, id, attr)
                  for key in ['keys','custom','default']:
                    if not attr[key]:
                      del attr[key]
                  attrs.append( attr)
                ob['__obj_attrs__'] = attrs
                del ob['attrs']
                if ob.has_key('zms_system'):
                  del ob['zms_system']
                # Value.
                value.append({'key':id,'value':ob})
            # XML.
            if len(value)==1:
              value = value[0]
              filename = '%s.metaobj.xml'%ids[0]
            else:
              filename = 'export.metaobj.xml'
            content_type = 'text/xml; charset=utf-8'
            export = self.getXmlHeader() + self.toXmlString(value,1)
            
            RESPONSE.setHeader('Content-Type',content_type)
            RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
            return export
          
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
                tmpltId = self.getTemplateId(id)
                tmpltName = 'Template: %s'%newValue['name']
                tmpltCustom = []
                tmpltCustom.append('<dtml-comment>--// BO %s //--</dtml-comment>\n'%tmpltId)
                tmpltCustom.append('\n')
                if newValue['type'] == 'ZMSRecordSet':
                  tmpltCustom.append('  <h2><dtml-var "getTitlealt(REQUEST)"></h2>\n')
                  tmpltCustom.append('  <p class="description"><dtml-var "_.len(getObjProperty(getMetaobj(meta_id)[\'attrs\'][0][\'id\'],REQUEST))"> <dtml-var "getLangStr(\'ATTR_RECORDS\',lang)"></p>\n')
                tmpltCustom.append('\n')
                tmpltCustom.append('<dtml-comment>--// EO %s //--</dtml-comment>\n'%tmpltId)
                tmpltCustom = ''.join(tmpltCustom)
                message += self.setMetaobjAttr(id,None,tmpltId,tmpltName,0,0,0,'DTML Method',[],tmpltCustom)
              message += self.getZMILangStr('MSG_INSERTED')%id
            # Insert Attribute.
            if key == 'attr':
              attr_id = REQUEST['attr_id'].strip()
              newName = REQUEST['attr_name'].strip()
              newMandatory = REQUEST.get('_mandatory',0)
              newMultilang = REQUEST.get('_multilang',0)
              newRepetitive = REQUEST.get('_repetitive',0)
              newType = REQUEST.get('_type','string')
              newKeys = REQUEST.get('_keys',[])
              newCustom = REQUEST.get('_custom','')
              newDefault = REQUEST.get('_default','')
              message += self.setMetaobjAttr( id, None, attr_id, newName, newMandatory, newMultilang, newRepetitive, newType, newKeys, newCustom, newDefault)
              message += self.getZMILangStr('MSG_INSERTED')%attr_id
          
          # Acquire.
          # --------
          elif btn == self.getZMILangStr('BTN_ACQUIRE'):
            ids = REQUEST.get('aq_ids',[])
            for id in ids:
              self.acquireMetaobj( id)
            # Return with message.
            message = self.getZMILangStr('MSG_INSERTED')%str(len(ids))
          
          # Import.
          # -------
          elif btn == self.getZMILangStr('BTN_IMPORT'):
            f = REQUEST['file']
            if f:
              filename = f.filename
              self.importMetaobjXml(xml=f)
            else:
              filename = REQUEST['init']
              createIfNotExists = 1
              self.importConf(filename, REQUEST, createIfNotExists)
            message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
          
          # Move to.
          # --------
          elif key == 'attr' and btn == 'move_to':
            sync_id = False
            pos = REQUEST['pos']
            attr_id = REQUEST['attr_id']
            self.moveMetaobjAttr( id, attr_id, pos)
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%attr_id),(pos+1))
          
          ##### SYNCHRONIZE ####
          if sync_id != False:
            self.synchronizeObjAttrs( sync_id)
        
        # Handle exception.
        except:
          _globals.writeException(self,"[manage_changeProperties]")
          error = str( sys.exc_type)
          if sys.exc_value:
            error += ': ' + str( sys.exc_value)
          target = self.url_append_params( target, { 'manage_tabs_error_message':error})
        
        # Return with message.
        target = self.url_append_params( target, { 'lang':lang, 'id':id, 'attr_id':REQUEST.get('attr_id','')})
        if len( message) > 0:
          message = message + ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
          target = self.url_append_params( target, { 'manage_tabs_message':message})
        if REQUEST.has_key('inp_id_name'):
          target += '&inp_id_name=%s'%REQUEST.get('inp_id_name')
          target += '&inp_name_name=%s'%REQUEST.get('inp_name_name')
          target += '&inp_value_name=%s'%REQUEST.get('inp_value_name')
          target += '#Edit'
        return RESPONSE.redirect( target)

################################################################################
