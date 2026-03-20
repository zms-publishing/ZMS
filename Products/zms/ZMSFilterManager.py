"""
ZMSFilterManager.py

ZMS support for zmsfilter manager.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import ZPublisher.HTTPRequest
import copy
from zope.interface import implementer
# Product Imports.
from Products.zms import _blobfields
from Products.zms import IZMSConfigurationProvider, IZMSRepositoryProvider
from Products.zms import ZMSItem
from Products.zms import standard
from Products.zms import zopeutil


@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSRepositoryProvider.IZMSRepositoryProvider,)
class ZMSFilterManager(
        ZMSItem.ZMSItem):

    """Manage reusable content filters and their executable process chains.

    The filter manager persists local filter definitions, optional uploaded
    process assets, and repository import/export payloads used for sync.
    """
    meta_type = 'ZMSFilterManager'
    zmi_icon = "fas fa-filter"
    icon_clazz = zmi_icon

    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      """Return parent management tabs with local relative actions."""
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      """Return the filter manager sub tabs shown in the ZMI."""
      return (
        {'label': 'TAB_FILTER','action': 'manage_main'},
        )

    manage = PageTemplateFile('zpt/ZMSFilterManager/manage_main', globals())
    manage_main = PageTemplateFile('zpt/ZMSFilterManager/manage_main', globals())

    __administratorPermissions__ = (
        'manage_main',
        'manage_changeFilter',
        'manage_changeProcess',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )


    def __init__(self, filters={}, processes={}):
      """Initialize the manager from serialized filters and processes.

      @param filters: Persisted filter definitions.
      @type filters: C{list}
      @param processes: Persisted process definitions.
      @type processes: C{list}
      """
      self.id = 'filter_manager'
      self.filters = {}
      for x in filters:
        try:
          self.setFilter(None, x['id'], x['acquired'], x['name'], x['format'], x['content_type'], x['description'], x['roles'], x['meta_types'])
          index = 0
          for p in x.get('processes', []):
            self.setFilterProcess(x['id'], index, p['id'], p['file'])
            index += 1
        except:
          standard.writeError(self,'can\'t __init__ filter: %s'%str(x))
      self.processes = {}
      for x in processes:
        try:
          self.setProcess(None, x['id'], x['acquired'], x['name'], x['type'], x['command'])
        except:
          standard.writeError(self,'can\'t __init__ process: %s'%str(x))


    def provideRepository(self, r, ids=None):
      """Build a repository export mapping for filters and processes.

      @param r: Repository accumulator passed by the caller.
      @type r: C{dict}
      @param ids: Optional subset of ids to export.
      @type ids: C{list}
      @return: Repository data keyed by object id.
      @rtype: C{dict}
      """
      r = {}
      for id in self.getFilterIds():
        d = self.getFilter(id)
        d['meta_type'] = 'filter'
        d['__icon__'] = 'fas fa-filter'
        d['__description__'] = self.getZMILangStr('ATTR_FILTER')
        d['__filename__'] = ['filters',id,'__init__.py']
        if 'processes' in d:
          del d['processes']
        d['Processes'] = []
        for fp in self.getFilterProcesses(id):
          p = {}
          p['id'] = fp['id']
          if 'file' in fp:
            p['id'] = '%s/%i.%s'%(fp['id'],len(d['Processes']),fp['file_filename'])
            p['ob'] = fp['file']
          d['Processes'].append(p)
        r[id] = d
      for id in self.getProcessIds():
        d = self.getProcess(id)
        d['meta_type'] = 'process'
        d['__icon__'] = 'fas fa-cog'
        d['__description__'] = self.getZMILangStr('ATTR_PROCESS')
        d['__filename__'] = ['processes',id,'__init__.py']
        ob = zopeutil.getObject(self,id)
        if ob:
          command = {}
          command['id'] = id
          command['ob'] = ob
          command['type'] = ob.meta_type
          if 'command' in d:
            del d['command']
          d['Command'] = [command]
        r[id] = d
      return r

    def updateRepository(self, r):
      """Apply one repository item to the local filter manager state.

      @param r: Repository item describing a filter or process.
      @type r: C{dict}
      @return: The imported id.
      @rtype: C{str}
      """
      id = r['id']
      if not id.startswith('__') and not id.endswith('__'):
        standard.writeBlock(self,"[updateRepository]: id=%s"%id)
        oldId = id
        newId = id
        if r.get('meta_type') == 'filter':
          newName = r['name']
          newFormat = r['format']
          newContentType = r['content_type']
          newDescription = r.get('description','')
          newRoles = r.get('roles',[])
          newMetaTypes = r.get('meta_types',[])
          self.setFilter(oldId, newId, newAcquired=0, newName=newName, newFormat=newFormat, newContentType=newContentType, newDescription=newDescription, newRoles=newRoles, newMetaTypes=newMetaTypes)
          index = 0
          for process in r.get('Processes', []):
            newProcessId = process.get('id')
            newProcessFile = None
            if newProcessId.find('/') >= 0:
              data = process.get('data')
              filename = process.get('id')
              filename = filename[filename.find('/')+1:]
              filename = filename[filename.find('.')+1:]
              newProcessId = newProcessId[:newProcessId.find('/')]
              newProcessFile = standard.FileFromData(self,data,filename)
            self.setFilterProcess(newId, index, newProcessId, newProcessFile)
            index += 1
        elif r.get('meta_type') == 'process':
          newName = r['name']
          newType = r['type']
          newCommand = r.get('command',None)
          for command in r.get('Command',[]):
            newCommand = command['data']
            break
          self.setProcess(oldId, newId, newName=newName, newType=newType, newCommand=newCommand)
      return id


    def _importXml(self, item):
      """Import a single parsed XML item.

      @param item: Parsed filter or process description.
      @type item: C{dict}
      """
      itemType = item.get('type')
      itemOb = item.get('value')
      if itemType == 'filter':
        newId = itemOb.get('id')
        newAcquired = 0
        newName = itemOb.get('name')
        newFormat = itemOb.get('format')
        newContentType = itemOb.get('content_type')
        newDescription = itemOb.get('description', '')
        newRoles = itemOb.get('roles', [])
        newMetaTypes = itemOb.get('meta_types', [])
        self.setFilter(None, newId, newAcquired, newName, newFormat, newContentType, newDescription, newRoles, newMetaTypes)
        index = 0
        for process in itemOb.get('processes', []):
            newProcessId = process.get('id')
            newProcessFile = process.get('file')
            self.setFilterProcess(newId, index, newProcessId, newProcessFile)
            index += 1
      elif itemType == 'process':
        newId = itemOb.get('id')
        newAcquired = 0
        newName = itemOb.get('name')
        newType = itemOb.get('type', 'process')
        newCommand = itemOb.get('command')
        self.setProcess(None, newId, newAcquired, newName, newType, newCommand)
      else:
        standard.writeError(self, "[_importXml]: Unknown type >%s<"%itemType)
    
    def importXml(self, xml):
      """Import one or more filter manager entries from XML data.

      @param xml: XML string or uploaded file-like object.
      @type xml: C{str}
      """
      v = standard.parseXmlString(xml)
      if isinstance(v, list):
        for item in v:
          id = self._importXml(item)
      else:
        id = self._importXml(v)
    
    def exportXml(self, REQUEST, RESPONSE):
      """Export selected filters and processes as an XML download.

      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: The active HTTP response.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Serialized XML export data.
      @rtype: C{str}
      """
      value = []
      ids = REQUEST.get('ids', [])
      filterIds = []
      for id in self.getFilterIds():
        if id in ids or len(ids) == 0:
          ob = self.getFilter(id).copy()
          ob['processes'] = []
          for fp in self.getFilterProcesses(id):
            p = {}
            p['id'] = fp['id']
            if 'file'in fp:
              p['file'] = fp['file']
            ob['processes'].append(fp)
          value.append({'type':'filter','value':ob})
          filterIds.append(id)
      for id in self.getProcessIds():
        if id in ids or len(ids) == 0:
          ob = self.getProcess(id).copy()
          value.append({'type':'process','value':ob})
      # Filename.
      filename = 'export'
      if len(filterIds)==1:
        filename = filterIds[0]
      elif len(ids)==1:
        filename = ids[0]
      # XML.
      if len(value)==1:
        value = value[0]
      content_type = 'text/xml; charset=utf-8'
      filename = '%s.filter.xml'%filename
      export = self.getXmlHeader() + self.toXmlString(value, 1)
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Content-Disposition', 'attachment;filename="%s"'%filename)
      return export
    
    
    def getProcessIds(self, sort=True):
      """Return the available process ids, including acquired ones.

      @param sort: Sort by display name when true.
      @type sort: C{bool}
      @return: Process ids.
      @rtype: C{list}
      """
      obs = self.processes
      ids = list(obs)
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        ids = list(set(ids+portalMaster.getFilterManager().getProcessIds()))
      if sort:
        ids = sorted(ids,key=lambda x:self.getProcess(x)['name'])
      return ids

    def getProcess(self, id):
      """Return a process definition, falling back to the portal master.

      @param id: Process identifier.
      @type id: C{str}
      @return: Process metadata and synchronized command data.
      @rtype: C{dict}
      """
      processes = self.processes
      process = {}
      if id in processes:
        process = processes.get( id).copy()
      else:
        # Acquire from parent.
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          if id in portalMaster.getFilterManager().getProcessIds():
            process = portalMaster.getFilterManager().getProcess(id)
            process['acquired'] = 1
            return process
      process['id'] = id
      process['name'] = process.get('name',process['id'])
      # Synchronize type.
      ob = zopeutil.getObject( self, process['id'])
      if ob is not None:
        process['ob'] = ob
        process['command'] = zopeutil.readData( ob)
      return process


    def getFilterIds(self, sort=True):
      """Return the available filter ids, including acquired ones.

      @param sort: Sort by display name when true.
      @type sort: C{bool}
      @return: Filter ids.
      @rtype: C{list}
      """
      obs = self.filters
      ids = list(obs)
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        ids = list(set(ids+portalMaster.getFilterManager().getFilterIds()))
      if sort:
        ids = sorted(ids,key=lambda x:self.getFilter(x)['name'])
      return ids


    def getFilter(self, id):
      """Return a filter definition, falling back to the portal master.

      @param id: Filter identifier.
      @type id: C{str}
      @return: Filter metadata.
      @rtype: C{dict}
      """
      obs = self.filters
      ob = {}
      if id in obs:
        ob = obs.get( id).copy()
      else:
        # Acquire from parent.
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          ob = portalMaster.getFilterManager().getFilter(id)
          ob['acquired'] = 1
          return ob
      ob['id'] = id
      return ob


    def setFilter(self, oldId, newId, newAcquired=0, newName='', newFormat='', newContentType='', newDescription='', newRoles=[], newMetaTypes=[]):
      """Create or update a filter definition.

      @param oldId: Existing filter id to replace.
      @type oldId: C{str}
      @param newId: Target filter id.
      @type newId: C{str}
      @param newAcquired: Whether the filter is acquired from a master portal.
      @type newAcquired: C{int}
      @param newName: Display name.
      @type newName: C{str}
      @param newFormat: Filter input format.
      @type newFormat: C{str}
      @param newContentType: Filter output content type.
      @type newContentType: C{str}
      @param newDescription: Descriptive help text.
      @type newDescription: C{str}
      @param newRoles: Allowed roles.
      @type newRoles: C{list}
      @param newMetaTypes: Supported content meta types.
      @type newMetaTypes: C{list}
      @return: The persisted filter id.
      @rtype: C{str}
      """
      # Set.
      obs = self.filters
      ob = {}
      ob['acquired'] = newAcquired
      ob['name'] = newName
      ob['format'] = newFormat
      ob['content_type'] = newContentType
      ob['description'] = newDescription
      ob['roles'] = newRoles
      ob['meta_types'] = newMetaTypes
      obs[newId] = ob
      # Rename assets.
      if oldId != newId:
        oldprefix = '%s.'%(oldId)
        ids = [x for x in self.objectIds('File') if x.startswith(oldprefix)]
        for id in ids:
          suffix = '.'.join(id.split('.')[1:])
          self.manage_renameObject(id=id, new_id='%s%s'%('%s.'%newId,suffix))
      # Set attribute.
      self.filters = obs.copy()
      # Return with new id.
      return newId
    def delFilter(self, id):
      """Delete a filter definition and its uploaded assets.

      @param id: Filter identifier.
      @type id: C{str}
      @return: Empty string for legacy callers.
      @rtype: C{str}
      """
      # Delete.
      cp = self.filters
      obs = {}
      for key in cp:
        if key != id:
          obs[key] = cp[key]
      # Delete assets.
      prefix = '%s.'%(id)
      ids = [x for x in self.objectIds('File') if x.startswith(prefix)]
      if ids:
        self.manage_delObjects(ids=ids)
      # Set attribute.
      self.filters = obs.copy()
      # Return with empty id.
      return ''



    def getFilterProcesses(self, id):
      """Return process definitions attached to a filter.

      @param id: Filter identifier.
      @type id: C{str}
      @return: Filter process descriptors with optional uploaded files.
      @rtype: C{list}
      """
      obs = []
      index = 0
      for process in self.getFilter( id).get( 'processes', []):
        ob = process.copy()
        ob[ 'type'] = ob.get( 'type', 'process')
        prefix = '%s.%i.'%(id,index)
        ids = [x for x in self.objectIds('File') if x.startswith(prefix)]
        if ids:
          f = zopeutil.getObject(self,ids[0])
          ob['file'] = f
          ob['file_href'] = f.absolute_url()
          ob['file_filename'] = '.'.join(f.getId().split('.')[2:])
          ob['file_content_type'] = f.getContentType()
          ob['file_size'] = f.get_size()
        if ob['id']:
          p = self.getProcess(ob['id'])
          if p is not None:
            obs.append( ob)
        index += 1
      return obs

    def setFilterProcess(self, id, index, newProcessId, newProcessFile=None):
      """Append a process to a filter and persist its optional file asset.

      @param id: Filter identifier.
      @type id: C{str}
      @param index: Process position inside the filter pipeline.
      @type index: C{int}
      @param newProcessId: Linked process id.
      @type newProcessId: C{str}
      @param newProcessFile: Optional uploaded process file.
      @type newProcessFile: C{_blobfields.MyBlob}
      @return: The appended process index.
      @rtype: C{int}
      """
      # Set.
      obs = self.filters
      ob = {}
      ob['id'] = newProcessId
      pobs = obs[id].get('processes', [])
      pobs.append(ob)
      obs[id]['processes'] = pobs
      # Asset.
      if isinstance(newProcessFile, _blobfields.MyBlob):
        prefix = '%s.%i.'%(id,index)
        # Delete asset with prefix.
        ids = [x for x in self.objectIds('File') if x.startswith(prefix)]
        if ids:
          self.manage_delObjects(ids=ids)
        # Add asset with prefix.
        fn = newProcessFile.getFilename()
        data = newProcessFile.getData()
        zopeutil.addFile(self, '%s%s'%(prefix,fn), fn, data)
      # Set attribute.
      self.filters = obs.copy()
      # Return with new id.
      return len(pobs)-1

    # ------------------------------------------------------------------------------
    def delFilterProcess(self, id, index):
      """Remove a process from a filter and renumber stored assets.

      @param id: Filter identifier.
      @type id: C{str}
      @param index: Process position to remove.
      @type index: C{int}
      @return: Legacy sentinel value.
      @rtype: C{int}
      """
      # Delete.
      obs = self.filters
      p = obs[ id].get('processes', [])
      p.remove( p[index])
      obs[id]['processes'] = p
      # Asset.
      prefix = '%s.%i.'%(id,index)
      # Delete asset with prefix.
      ids = [x for x in self.objectIds('File') if x.startswith(prefix)]
      if ids:
        self.manage_delObjects(ids=ids)
      # Rename assets.
      for i in range(len(p)-index):
        oldprefix = '%s.%i.'%(id,i+index+1)
        newprefix = '%s.%i.'%(id,i+index)
        old = [x for x in self.objectIds('File') if x.startswith(oldprefix)]
        if old:
          old_id = old[0]
          fn = '.'.join(old_id.split('.')[2:])
          new_id = '%s%s'%(newprefix,fn)
          self.manage_renameObject(id=old_id, new_id=new_id)
      # Set attribute.
      self.filters = obs.copy()
      # Return with empty id.
      return -1

    # ------------------------------------------------------------------------------
    def moveFilterProcess(self, id, index, pos):
      """Move a filter process to a new position in the pipeline.

      @param id: Filter identifier.
      @type id: C{str}
      @param index: Current process position.
      @type index: C{int}
      @param pos: Target process position.
      @type pos: C{int}
      @return: The new position.
      @rtype: C{int}
      """
      # Set.
      obs = self.filters
      p = obs[id].get('processes', [])
      ob = p[index]
      p.remove(ob)
      p.insert(pos, ob)
      obs[id]['processes'] = p
      # Asset.
      prefix = '%s.%i.'%(id,index)
      # Rename asset with prefix.
      ids = [x for x in self.objectIds('File') if x.startswith(prefix)]
      if ids:
        old_id = ids[0]
        fn = '.'.join(old_id.split('.')[2:])
        new_id='%s.%i.%s'%(id,pos,fn)
        self.manage_renameObject(id=old_id,new_id=new_id)
      # Rename assets after move.
      for i in range(abs(index-pos)):
        oldprefix = '%s.%i.'%(id,i+min(index,pos)+1)
        newprefix = '%s.%i.'%(id,i+min(index,pos))
        old = [x for x in self.objectIds('File') if x.startswith(oldprefix)]
        if old:
          old_id = old[0]
          fn = '.'.join(old_id.split('.')[2:])
          new_id='%s%s'%(newprefix,fn)
          self.manage_renameObject(id=old_id, new_id=new_id)
      # Set attribute.
      self.filters = obs.copy()
      # Return with new id.
      return pos


    def manage_changeFilter(self, lang, btn='', key='', REQUEST=None, RESPONSE=None):
      """Handle ZMI actions for filters and filter-process assignments.

      @param lang: Active UI language.
      @type lang: C{str}
      @param btn: Submitted button id.
      @type btn: C{str}
      @param key: Secondary action key.
      @type key: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: The active HTTP response.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Redirect response or export payload.
      @rtype: C{object}
      """
      message = ''
      id = REQUEST.get('id', '')
      index = REQUEST.get('index', -1)
      
      # Change.
      # -------
      if btn == 'BTN_SAVE':
        cp = self.getFilter(id)
        # Filter.
        newId = REQUEST.get('inpId').strip()
        newAcquired = 0
        newName = REQUEST.get('inpName').strip()
        newFormat = REQUEST.get('inpFormat').strip()
        newContentType = REQUEST.get('inpContentType').strip()
        newDescription = REQUEST.get('inpDescription').strip()
        newRoles = REQUEST.get('inpRoles', [])
        newMetaTypes = REQUEST.get('inpMetaTypes', [])
        id = self.setFilter(id, newId, newAcquired, newName, newFormat, newContentType, newDescription, newRoles, newMetaTypes)
        # Filter Processes.
        index = 0
        for filterProcess in cp.get('processes', []):
          processId = REQUEST.get('filterProcessId_%i'%index, '').strip()
          processFile = REQUEST.get('filterProcessFile_%i'%index)
          if isinstance(processFile, ZPublisher.HTTPRequest.FileUpload):
            if len(getattr(processFile, 'filename', ''))==0:
              processFile = filterProcess.get('file', None)
            else:
              processFile = _blobfields.createBlobField(self, _blobfields.MyFile, processFile)
          self.setFilterProcess(id, index, processId, processFile)
          index += 1
       # New Filter Process?
        for k in [k for k in REQUEST.keys() if k.startswith('filterProcessId')]:
          if k[-1].isdigit() and int(k[-1]) > index:
            processId = REQUEST.get(k, '').strip()
            processFile = REQUEST.get(k.replace('Id','File'), None)
            if isinstance(processFile, ZPublisher.HTTPRequest.FileUpload):
              processFile = _blobfields.createBlobField(self, _blobfields.MyFile, processFile)
            self.setFilterProcess(id, index, processId, processFile)
            index += 1
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn == 'BTN_DELETE':
        if key == 'obj':
          ids = REQUEST.get('ids', [])
          for id in ids:
            self.delFilter(id)
          message = self.getZMILangStr('MSG_DELETED')%len(ids)
        elif key == 'attr':
          ids = [REQUEST.get('id')]
          for id in ids:
            if id is not None:
              self.delFilterProcess(id, index)
          message = self.getZMILangStr('MSG_DELETED')%len(ids)
      
      # Export.
      # -------
      elif btn == 'BTN_EXPORT':
        return self.exportXml(REQUEST, RESPONSE)
      
      # Import.
      # -------
      elif btn == 'BTN_IMPORT':
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importXml(xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename)
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%filename)
      
      # Insert.
      # -------
      elif btn == 'BTN_INSERT':
        newId = REQUEST.get('newId').strip()
        newAcquired = 0
        newName = REQUEST.get('newName').strip()
        newFormat = REQUEST.get('newFormat').strip()
        newContentType = REQUEST.get('newContentType').strip()
        id = self.setFilter(None, newId, newAcquired, newName, newFormat, newContentType)
        message = self.getZMILangStr('MSG_INSERTED')%id
      
      # Move to.
      # --------
      elif btn == 'move_to':
        pos = REQUEST['pos']
        self.moveFilterProcess(id, index, pos)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<em>%s</em>"%index), (pos+1))
      
      # Return with message.
      message = standard.url_quote(message)
      return RESPONSE.redirect('manage_main?id=%s&index:int=%i&lang=%s&manage_tabs_message=%s'%(id, index, lang, message))


    def setProcess(self, oldId, newId, newAcquired=0, newName='', newType='process', newCommand=None):
      """Create or update an executable process definition.

      @param oldId: Existing process id to replace.
      @type oldId: C{str}
      @param newId: Target process id.
      @type newId: C{str}
      @param newAcquired: Whether the process is acquired from a master portal.
      @type newAcquired: C{int}
      @param newName: Display name.
      @type newName: C{str}
      @param newType: Backing Zope object type.
      @type newType: C{str}
      @param newCommand: Source text or uploaded blob for the process.
      @type newCommand: C{object}
      @return: The persisted process id.
      @rtype: C{str}
      """
      if newCommand is None:
        newCommand = ''
        if newType in [ 'Script (Python)']:
          newCommand += '# --// BO '+ newId + ' //--\n'
          newCommand += '# Example code:\n'
          newCommand += '\n'
          newCommand += '# Import a standard function, and get the HTML request and response objects.\n'
          newCommand += 'from Products.PythonScripts.standard import html_quote\n'
          newCommand += 'request = container.REQUEST\n'
          newCommand += 'RESPONSE =  request.RESPONSE\n'
          newCommand += '\n'
          newCommand += '# Return a string identifying this script.\n'
          newCommand += 'p = []\n'
          newCommand += 'p.append("This is the Python Script %s" % script.getId())\n'
          newCommand += 'p.append("in %s" % container.absolute_url())\n'
          newCommand += 'return "\\n".join(p)\n'
          newCommand += '\n'
          newCommand += '# --// EO '+ newId + ' //--\n'
        elif newType in [ 'External Method']:
          newCommand = ''
          newCommand += '# Example code:\n'
          newCommand += '\n'
          newCommand += 'def ' + newId + '( self, request):\n'
          newCommand += '  return "This is the external method ' + newId + '"\n'
      # Remove Zope-Object (if exists)
      zopeutil.removeObject(self, oldId)
      zopeutil.removeObject(self, newId)
      # Insert Zope-Object.
      if isinstance(newCommand,_blobfields.MyBlob): newCommand = newCommand.getData()
      if isinstance(newCommand, str): newCommand = newCommand.replace('\r', '')
      zopeutil.addObject(self, newType, newId, newName, newCommand)
      # Set.
      obs = self.processes
      ob = {}
      ob['acquired'] = newAcquired
      ob['name'] = newName
      ob['type'] = newType
      ob['command'] = newCommand
      obs[newId] = ob
      # Set attribute.
      self.processes = obs.copy()
      # Return with new id.
      return newId


    def delProcess(self, id):
      """Delete a process definition and its backing Zope object.

      @param id: Process identifier.
      @type id: C{str}
      @return: Empty string for legacy callers.
      @rtype: C{str}
      """
      # Delete.
      obs = self.processes
      del obs[id]
      zopeutil.removeObject(self, id)
      # Set attribute.
      self.processes = obs.copy()
      # Return with empty id.
      return ''


    def manage_changeProcess(self, lang, btn='', key='', REQUEST=None, RESPONSE=None):
      """Handle ZMI actions for creating, editing, and deleting processes.

      @param lang: Active UI language.
      @type lang: C{str}
      @param btn: Submitted button id.
      @type btn: C{str}
      @param key: Secondary action key.
      @type key: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: The active HTTP response.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Redirect response or export payload.
      @rtype: C{object}
      """
      message = ''
      id = REQUEST.get('id', '')

      # Change.
      # -------
      if btn == 'BTN_SAVE':
        newId = REQUEST.get('inpId').strip()
        newAcquired = 0
        newName = REQUEST.get('inpName').strip()
        newType = REQUEST.get('inpType').strip()
        newCommand = REQUEST.get('inpCommand').strip()
        id = self.setProcess(id, newId, newAcquired, newName, newType, newCommand)
        message = self.getZMILangStr('MSG_CHANGED')

      # Delete.
      # -------
      elif btn == 'BTN_DELETE':
        ids = REQUEST.get('ids', [])
        for id in ids:
          self.delProcess(id)
        message = self.getZMILangStr('MSG_DELETED')%len(ids)

      # Export.
      # -------
      elif btn == 'BTN_EXPORT':
        return self.exportXml(REQUEST, RESPONSE)

      # Import.
      # -------
      elif btn == 'BTN_IMPORT':
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importXml(xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename)
        message = self.getZMILangStr('MSG_IMPORTED')%('<em>%s</em>'%filename)

      # Insert.
      # -------
      elif btn == 'BTN_INSERT':
        newId = REQUEST.get('newId').strip()
        newAcquired = 0
        newName = REQUEST.get('newName').strip()
        newType = REQUEST.get('newType').strip()
        id = self.setProcess(None, newId, newAcquired, newName, newType)
        message = self.getZMILangStr('MSG_INSERTED')%id

      # Return with message.
      message = standard.url_quote(message)
      return RESPONSE.redirect('manage_main?id=%s&lang=%s&manage_tabs_message=%s'%(id, lang, message))

