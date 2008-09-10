################################################################################
# ZMSMetadictManager.py
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
import copy
import sys
import time
# Product Imports.
import _globals


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSMetadictManager:


    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.importMetadictXml
    # --------------------------------------------------------------------------

    def _importMetadictXml(self, item, zms_system=0, createIfNotExists=1):
      id = item['id']
      metaDicts = self.dict_list(self.metas)
      ids = metaDicts.keys()
      ids = filter(lambda x: metaDicts[x].get('zms_system',0)==1,metaDicts.keys())
      if createIfNotExists == 1 or id in ids:
        newId = id
        newAcquired = 0
        newName = item['name']
        newType = item['type']
        newMandatory = item.get('mandatory',0)
        newMultilang = item.get('multilang',1)
        newRepetitive = item.get('repetitive',0)
        newKeys = item.get('keys',[])
        newCustom = item.get('custom','')
        self.setMetadictAttr( None, newId, newAcquired, newName, newType, \
          newMandatory, newMultilang, newRepetitive, newCustom, newKeys, \
          zms_system)
        for meta_id in item.get('dst_meta_types',[]):
          metaObj = self.getMetaobj( meta_id)
          if metaObj is not None  and id not in self.getMetadictAttrs(meta_id):
            self.setMetaobjAttr(meta_id,None,newId=id,newType=id)

    def importMetadictXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
      v = self.parseXmlString(xml)
      if type(v) is list:
        for item in v:
          self._importMetadictXml(item,zms_system,createIfNotExists)
      else:
        self._importMetadictXml(v,zms_system,createIfNotExists)


    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.getMetadictAttrs:
    #
    #  Returns list of attributes of DC.Metadictionaries.
    # --------------------------------------------------------------------------
    def getMetadictAttrs(self, meta_type=None):
      obs = self.metas
      if meta_type is not None:
        attrs = []
        metaObj = self.getMetaobj( meta_type)
        for attr in metaObj['attrs']:
          if attr['type'] in obs:
            attrs.append(attr['type'])
      else:
       attrs = map( lambda x: obs[x*2], range(len(obs)/2))
      # Return attributes.
      return attrs


    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.getMetadictAttr:
    #
    #  Get Attribute for Meta-Dictionary specified by key.
    # --------------------------------------------------------------------------
    def getMetadictAttr(self, key):
      obs = self.metas
      if key in obs:
        ob = obs[obs.index(key)+1].copy()
      # Not found!
      else:
        return None
      # Acquire from parent.
      if ob.get('acquired',0)==1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          ob = portalMaster.metaobj_manager.getMetadictAttr(key)
          if ob is None:
            return None
          ob = ob.copy()
          ob['acquired'] = 1
      ob['mandatory'] = ob.get('mandatory',0)
      ob['multilang'] = ob.get('multilang',1)
      ob['repetitive'] = ob.get('repetitive',0)
      ob['keys'] = ob.get('keys',[])
      ob['custom'] = ob.get('custom','')
      ob['errors'] = ob.get('errors','')
      return ob


    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.delMetadictAttr:
    #
    #  Delete Meta-Attribute specified by ID.
    # --------------------------------------------------------------------------
    def delMetadictAttr(self, id):
      # Delete.
      obs = self.metas
      i = obs.index(id)
      # Update attribute.
      del obs[i]
      del obs[i]
      # Make persistent.
      self.metas = copy.deepcopy(self.metas)
      # Return with empty ID.
      return ''


    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.setMetadictAttr:
    # --------------------------------------------------------------------------
    def setMetadictAttr(self, oldId, newId, newAcquired, newName='', newType='', \
          newMandatory=0, newMultilang=1, newRepetitive=0, newCustom='', \
          newKeys=[], zms_system=0):
      """
      Set/add meta-attribute with specified values.
      @param oldId: Old id
      @type oldId: C{string}
      @param newId: New id
      @type newId: C{string}
      @param newAcquired: Acquired
      @type newAcquired: C{int}: 0 or 1
      @param newName: (Display-)Name
      @type newName: C{string}
      @param newType: Type
      @type newType: C{string}
      @return: New id
      @rtype: C{string}
      """
      obs = self.metas
      # Remove exisiting entry.
      if oldId is None:
        oldId = newId
      if oldId in obs:
        i = obs.index(oldId)
        del obs[i]
        del obs[i]
      else: 
        i = len(obs)
      # Values.
      newValues = {}
      newValues['id'] = newId
      newValues['acquired'] = newAcquired
      newValues['name'] = newName
      newValues['type'] = newType
      newValues['mandatory'] = newMandatory
      newValues['multilang'] = newMultilang
      newValues['repetitive'] = newRepetitive
      newValues['keys'] = newKeys
      newValues['custom'] = newCustom
      newValues['zms_system'] = zms_system
      # Update attribute.
      obs.insert(i,newValues)
      obs.insert(i,newId)
      # Make persistent.
      self.metas = copy.deepcopy(self.metas)
      # Return with new attr.
      return newId


    # --------------------------------------------------------------------------
    #  ZMSMetadictManager.moveMetadictAttr:
    #
    #  Moves Meta-Attribute specified by given attr to specified position.
    # --------------------------------------------------------------------------
    def moveMetadictAttr(self, attr, pos):
      # Move.
      obs = self.metas
      i = obs.index(attr)
      attr = obs[i]
      values = obs[i+1]
      del obs[i] 
      del obs[i] 
      obs.insert(pos*2, values)
      obs.insert(pos*2, attr)
      # Make persistent.
      self.metas = copy.deepcopy(self.metas)
      # Return with empty attr.
      return ''


    ############################################################################
    #  ZMSMetadictManager.manage_changeMetaProperties:
    #
    #  Change Meta-Attributes.
    ############################################################################
    def manage_changeMetaProperties(self, btn, lang, REQUEST, RESPONSE=None):
        """ MetadictManager.manage_changeMetaProperties """
        message = ''
        t0 = time.time()
        id = REQUEST.get('id','')
        target = 'manage_metas'
        
        try:
          
          # Acquire.
          # --------
          if btn == self.getZMILangStr('BTN_ACQUIRE'):
            newId = REQUEST['aq_id']
            newAcquired = 1
            id = self.setMetadictAttr( None, newId, newAcquired)
            message = self.getZMILangStr('MSG_INSERTED')%id
          
          # Change.
          # -------
          elif btn == self.getZMILangStr('BTN_CHANGE'): 
            for oldId in REQUEST.get('old_ids',[]):
              if REQUEST.has_key('attr_id_%s'%oldId):
                newId = REQUEST['attr_id_%s'%oldId].strip()
                newAcquired = 0
                newName = REQUEST['attr_name_%s'%oldId].strip()
                newType = REQUEST['attr_type_%s'%oldId].strip()
                newMandatory = REQUEST.get('attr_mandatory_%s'%oldId, 0)
                newMultilang = REQUEST.get('attr_multilang_%s'%oldId, 0)
                newRepetitive = REQUEST.get('attr_repetitive_%s'%oldId, 0)
                newKeys = self.string_list(REQUEST.get('attr_keys_%s'%oldId,''), '\n')
                newCustom = REQUEST.get('attr_custom_%s'%oldId, '')
                self.setMetadictAttr( oldId, newId, newAcquired, newName, newType, newMandatory, newMultilang, newRepetitive, newCustom, newKeys)
            message = self.getZMILangStr('MSG_CHANGED')
          
          # Copy.
          # -----
          elif btn == self.getZMILangStr('BTN_COPY'):
            metaOb = self.getMetadictAttr(id)
            if metaOb.get('acquired',0) == 1:
              masterRoot = getattr(self,self.getConfProperty('Portal.Master'))
              masterDocElmnt = masterRoot.content
              REQUEST.set('ids',[id])
              xml =  masterDocElmnt.manage_changeMetaProperties(self.getZMILangStr('BTN_EXPORT'), lang, REQUEST, RESPONSE)
              self.importMetadictXml(xml=xml)
              message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
          
          # Delete.
          # -------
          elif btn in ['delete',self.getZMILangStr('BTN_DELETE')]:
            oldId = id
            self.delMetadictAttr( oldId)
            message = self.getZMILangStr('MSG_DELETED')%int(1)
          
          # Export.
          # -------
          elif btn == self.getZMILangStr('BTN_EXPORT'):
            value = []
            ids = REQUEST.get('ids',[])
            metadicts = self.metas
            for i in range(len(metadicts)/2):
              id = metadicts[i*2]
              dict = metadicts[i*2+1].copy()
              if id in ids or len(ids) == 0:
                if dict.has_key('zms_system'):
                    del dict['zms_system']
                dst_meta_types = []
                for meta_id in self.getMetaobjIds():
                  if id in self.getMetadictAttrs( meta_id):
                    dst_meta_types.append( meta_id)
                dict['dst_meta_types'] = dst_meta_types
                value.append(dict)
            if len(value) == 1:
              value = value[0]
            content_type = 'text/xml; charset=utf-8'
            filename = 'export.metadict.xml'
            export = self.getXmlHeader() + self.toXmlString(value,1)
            RESPONSE.setHeader('Content-Type',content_type)
            RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
            return export
          
          # Import.
          # -------
          elif btn == self.getZMILangStr('BTN_IMPORT'):
            f = REQUEST['file']
            if f:
              filename = f.filename
              self.importMetadictXml(xml=f)
            else:
              filename = REQUEST['init']
              createIfNotExists = 1
              self.importConf(filename, REQUEST, createIfNotExists)
            message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
          
          # Insert.
          # -------
          elif btn == self.getZMILangStr('BTN_INSERT'):
            newId = REQUEST['_id'].strip()
            newAcquired = 0
            newName = REQUEST['_name'].strip()
            newType = REQUEST['_type'].strip()
            newMandatory = REQUEST.get('_mandatory',0)
            newMultilang = REQUEST.get('_multilang',0)
            newRepetitive = REQUEST.get('_repetitive',0)
            newCustom = ''
            if newType == 'method':
              newCustom += '<dtml-comment>--// BO '+ newId + ' //--</dtml-comment>\n'
              newCustom += '\n'
              newCustom += '<dtml-comment>--// EO '+ newId + ' //--</dtml-comment>\n'
            id = self.setMetadictAttr( None, newId, newAcquired, newName, newType, newMandatory, newMultilang, newRepetitive, newCustom)
            message = self.getZMILangStr('MSG_INSERTED')%id
          
          # Move to.
          # --------
          elif btn == 'move_to':
            pos = REQUEST['pos']
            oldId = id
            id = self.moveMetadictAttr( oldId, pos)
            message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%oldId),(pos+1))
          
          ##### Page-Extension ####
          if id == 'attr_pageext':
            for langId in self.getLangIds():
              self.setLangMethods( langId)
            
          ##### SYNCHRONIZE ####
          self.synchronizeObjAttrs()
        
        # Handle exception.
        except:
          _globals.writeException(self,"[manage_changeMetaProperties]")
          error = str( sys.exc_type)
          if sys.exc_value:
            error += ': ' + str( sys.exc_value)
          target = self.url_append_params( target, { 'manage_tabs_error_message':error})
        
        # Return with message.
        target = self.url_append_params( target, { 'lang':lang, 'id':id})
        if len( message) > 0:
          message = message + ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
          target = self.url_append_params( target, { 'manage_tabs_message':message})
        return RESPONSE.redirect( target)

################################################################################
