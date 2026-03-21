"""
ZMSMetadictManager.py - ZMS Meta-Dictionary Manager

Defines ZMSMetadictManager for metadata dictionary storage and lookup.
It caches and retrieves metamodel definitions, providing fast access to schema and constraint data.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
import copy
import sys
import time
# Product Imports.
from Products.zms import standard


class ZMSMetadictManager(object):
    """Manage Dublin-Core meta-dictionary attributes and their repository persistence."""


    def provideRepositoryMetas(self, r, ids=None):
      """
      Write configured meta-dictionary records into the repository export payload.

      @param r: Repository export accumulator.
      @type r: C{dict}
      @param ids: Optional subset of repository keys to export.
      @type ids: C{list} | C{None}
      """
      standard.writeBlock(self, "[provideRepositoryMetas]: ids=%s"%str(ids))
      valid_ids = ['__metas__']
      if ids is None:
        ids = valid_ids
      for id in [x for x in ids if x in valid_ids]:
        metas = copy.deepcopy(self.metas)
        metas = [metas[x*2+1] for x in range(len(metas)//2)]
        l = []
        for meta in metas:
          if meta.get('acquired'):
            meta = {'id': meta['id'], 'acquired': 1}
          l.append(meta)
        metas = l  
        d = {'id':id,'__filename__':['__metas__.py'],'Metas':metas}
        r[id] = d

    def updateRepositoryMetas(self, r):
      """
      Replace local meta-dictionary records from a repository import payload.

      @param r: Imported repository payload.
      @type r: C{dict}
      @return: Imported record id.
      @rtype: C{str}
      """
      id = r['id']
      if id == '__metas__':
        standard.writeBlock(self, "[updateRepositoryMetas]: id=%s"%id)
        self.metas = []
        for attr in r.get('Metas', []):
          self.metas.extend([attr['id'], attr])
        # Make persistent.
        self.metas = copy.deepcopy(self.metas)
      return id


    def _importMetadictXml(self, item):
      """Import a single serialized meta-dictionary attribute record."""
      id = item['id']
      newId = id
      newAcquired = 0
      newName = item['name']
      newType = item['type']
      newMandatory = item.get('mandatory', 0)
      newMultilang = item.get('multilang', 1)
      newRepetitive = item.get('repetitive', 0)
      newKeys = item.get('keys', [])
      newCustom = item.get('custom', '')
      newDefault = item.get('default', '')
      self.setMetadictAttr( None, newId, newAcquired, newName, newType, \
        newMandatory, newMultilang, newRepetitive, newCustom, newKeys, newDefault)
      for meta_id in item.get('dst_meta_types', []):
        metaObj = self.getMetaobj( meta_id)
        if metaObj is not None  and id not in self.getMetadictAttrs(meta_id):
          self.setMetaobjAttr(meta_id, None, newId=id, newType=id)

    def importMetadictXml(self, xml):
      """Import one or many meta-dictionary attribute records from XML content."""
      v = standard.parseXmlString(xml)
      if isinstance(v, list):
        for item in v:
          self._importMetadictXml(item)
      else:
        self._importMetadictXml(v)


    def getMetadictAttrs(self, meta_type=None):
      """
      Return a list of meta-dictionary attribute ids.

      When C{meta_type} is given, only ids shared with that meta type are returned.

      @param meta_type: Limit results to attributes used by this meta type.
      @type meta_type: C{str} | C{None}
      @return: List of attribute ids.
      @rtype: C{list}
      """
      obs = self.metas
      if meta_type is not None:
        attrs = []
        metaObj = self.getMetaobj( meta_type)
        for attr in metaObj.get('attrs', []):
          if attr['type'] in obs:
            attrs.append(attr['type'])
      else:
       attrs = [obs[x*2] for x in range(len(obs)//2)]
      # Return attributes.
      return attrs


    def getMetadictAttr(self, key):
      """
      Return one meta-dictionary attribute dict by id.

      Attributes configured as C{acquired} are resolved transparently from the portal master.
      Returns C{None} when the key is not found.

      @param key: Attribute id.
      @type key: C{str}
      @return: Attribute mapping or C{None}.
      @rtype: C{dict} | C{None}
      """
      obs = self.metas
      if key in obs:
        ob = obs[obs.index(key)+1].copy()
      # Not found!
      else:
        return None
      # Acquire from parent.
      if ob.get('acquired', 0)==1:
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          portalMasterOb = portalMaster.metaobj_manager.getMetadictAttr(key)
          if portalMasterOb is not None:
            ob = portalMasterOb
            ob = ob.copy()
            ob['acquired'] = 1
          else:
            ob = ob.copy()
            ob['errors'] = 'Not found in master!'
      ob['mandatory'] = ob.get('mandatory', 0)
      ob['multilang'] = ob.get('multilang', 1)
      ob['repetitive'] = ob.get('repetitive', 0)
      ob['keys'] = ob.get('keys', [])
      ob['custom'] = ob.get('custom', '')
      ob['default'] = ob.get('default', '')
      ob['errors'] = ob.get('errors', '')
      return ob


    def delMetadictAttr(self, id):
      """Remove a meta-dictionary attribute by id and persist the updated list."""
      obs = self.metas
      i = obs.index(id)
      # Update attribute.
      del obs[i]
      del obs[i]
      # Make persistent.
      self.metas = copy.deepcopy(self.metas)
      # Return with empty ID.
      return ''


    def setMetadictAttr(self, oldId, newId, newAcquired, newName='', newType='', \
          newMandatory=0, newMultilang=1, newRepetitive=0, newCustom='', \
          newKeys=[], newDefault=''):
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
      newValues['default'] = newDefault
      # Update attribute.
      obs.insert(i, newValues)
      obs.insert(i, newId)
      # Make persistent.
      self.metas = copy.deepcopy(self.metas)
      # Return with new attr.
      return newId


    def moveMetadictAttr(self, attr, pos):
      """Move the meta-dictionary attribute with the given id to the given list position."""
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


    def manage_changeMetaProperties(self, btn, lang, REQUEST, RESPONSE=None):
      """Handle add/edit/delete/copy/import/export/reorder actions for meta-dictionary attributes."""
      message = ''
      extra = {}
      t0 = time.time()
      id = REQUEST.get('id', '')
      target = 'manage_metas'
      if btn == 'BTN_SAVE' or btn == 'BTN_DELETE':
        target = REQUEST.get('target', target)
      
      try:
        
        # Acquire.
        # --------
        if btn == 'BTN_ACQUIRE':
          ids = REQUEST.get('aq_ids', [])
          for newId in ids:
            newAcquired = 1
            id = self.setMetadictAttr( None, newId, newAcquired)
          message = self.getZMILangStr('MSG_INSERTED')%str(len(ids))
        
        # Change.
        # -------
        elif btn == 'BTN_SAVE': 
          for oldId in REQUEST.get('old_ids', []):
            if 'attr_id_%s'%oldId in REQUEST:
              newId = REQUEST['attr_id_%s'%oldId].strip()
              newAcquired = 0
              newName = REQUEST['attr_name_%s'%oldId].strip()
              newType = REQUEST['attr_type_%s'%oldId].strip()
              newMandatory = REQUEST.get('attr_mandatory_%s'%oldId, 0)
              newMultilang = REQUEST.get('attr_multilang_%s'%oldId, 0)
              newRepetitive = REQUEST.get('attr_repetitive_%s'%oldId, 0)
              newKeys = standard.string_list(REQUEST.get('attr_keys_%s'%oldId, ''), '\n')
              newCustom = REQUEST.get('attr_custom_%s'%oldId, '')
              newDefault = REQUEST.get('attr_default_%s'%oldId, '')
              self.setMetadictAttr( oldId, newId, newAcquired, newName, newType, newMandatory, newMultilang, newRepetitive, newCustom, newKeys, newDefault)
          message += self.getZMILangStr('MSG_CHANGED')
        
        # Copy.
        # -----
        elif btn == 'BTN_COPY':
          metaOb = self.getMetadictAttr(id)
          if metaOb.get('acquired', 0) == 1:
            masterRoot = getattr(self, self.getConfProperty('Portal.Master'))
            masterDocElmnt = masterRoot.content
            REQUEST.set('ids', [id])
            xml =  masterDocElmnt.manage_changeMetaProperties('BTN_EXPORT', lang, REQUEST, RESPONSE)
            self.importMetadictXml(xml=xml)
            message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%id)
        
        # Delete.
        # -------
        elif btn == 'BTN_DELETE':
          oldId = id
          self.delMetadictAttr( oldId)
          for portalClient in self.getPortalClients():
            pcmm = portalClient.metaobj_manager
            if oldId in pcmm.getMetadictAttrs() and pcmm.getMetadictAttr(oldId).get('acquired', 0)==1:
              pcmm.delMetadictAttr( oldId)
          message = self.getZMILangStr('MSG_DELETED')%int(1)
        
        # Export.
        # -------
        elif btn == 'BTN_EXPORT':
          value = []
          ids = REQUEST.get('ids', [])
          metadicts = self.metas
          for i in range(len(metadicts)//2):
            id = metadicts[i*2]
            dict = metadicts[i*2+1].copy()
            if id in ids or len(ids) == 0:
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
          export = self.getXmlHeader() + self.toXmlString(value, 1)
          RESPONSE.setHeader('Content-Type', content_type)
          RESPONSE.setHeader('Content-Disposition', 'attachment;filename="%s"'%filename)
          return export
        
        # Import.
        # -------
        elif btn == 'BTN_IMPORT':
          f = REQUEST['file']
          if f:
            filename = f.filename
            self.importMetadictXml(xml=f)
          else:
            filename = REQUEST['init']
            self.importConf(filename)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
        
        # Move to.
        # --------
        elif btn == 'move_to':
          pos = REQUEST['pos']
          oldId = id
          id = self.moveMetadictAttr( oldId, pos)
          message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%oldId), (pos+1))
        
        ##### SYNCHRONIZE ####
        self.synchronizeObjAttrs()
      
      # Handle exception.
      except:
        standard.writeError(self, "[manage_changeMetaProperties]")
        error = str( sys.exc_info()[0])
        if sys.exc_info()[1]:
          error += ': ' + str( sys.exc_info()[1])
        if target=='zmi_manage_tabs_message':
          REQUEST.set('manage_tabs_error_message', error)
          return self.zmi_manage_tabs_message(lang=lang, id=id, extra=extra)
        else:
          target = standard.url_append_params( target, { 'manage_tabs_error_message':error})
      
      # Return with message.
      if target=='zmi_manage_tabs_message':
        REQUEST.set('manage_tabs_message', message)
        return self.zmi_manage_tabs_message(lang=lang, id=id, extra=extra)
      else:
        target = standard.url_append_params( target, { 'lang':lang, 'id':id})
        target = standard.url_append_params( target, extra)
        if len( message) > 0:
          message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
          target = standard.url_append_params( target, { 'manage_tabs_message':message})
        return RESPONSE.redirect( target)

