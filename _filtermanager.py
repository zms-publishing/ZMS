################################################################################
# _filtermanager.py
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
from App.Common import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ExternalMethod import ExternalMethod
from Products.PageTemplates import ZopePageTemplate
from Products.PythonScripts import PythonScript
import ZPublisher.HTTPRequest
import copy
import os
import tempfile
import time
import urllib
import zExceptions
# Product Imports.
import _blobfields
import _fileutil
import _globals


################################################################################
#
#  XML IM/EXPORT
#
################################################################################

# ------------------------------------------------------------------------------
#  importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, createIfNotExists=1):
  itemType = item.get('type')
  itemOb = item.get('value')
  if itemType == 'filter':
    newId = itemOb.get('id')
    newAcquired = 0
    newName = itemOb.get('name')
    newFormat = itemOb.get('format')
    newContentType = itemOb.get('content_type')
    newDescription = itemOb.get('description','')
    newRoles = itemOb.get('roles',[])
    newMetaTypes = itemOb.get('meta_types',[])
    filters = getRawFilters(self)
    if createIfNotExists == 1:
      delFilter(self, newId)
      setFilter(self, newId, newAcquired, newName, newFormat, newContentType, newDescription, newRoles, newMetaTypes)
      for process in itemOb.get('processes',[]):
        newProcessId = process.get('id')
        newProcessFile = process.get('file')
        setFilterProcess(self, newId, newProcessId, newProcessFile)
  elif itemType == 'process':
    newId = itemOb.get('id')
    newAcquired = 0
    newName = itemOb.get('name')
    newType = itemOb.get('type','process')
    newCommand = itemOb.get('command')
    processes = getRawProcesses(self)
    if createIfNotExists == 1:
      delProcess(self, newId)
      setProcess(self, newId, newAcquired, newName, newType, newCommand)
  else:
    _globals.writeError(self,"[_importXml]: Unknown type >%s<"%itemType)

def importXml(self, xml, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      id = _importXml(self,item,createIfNotExists)
  else:
    id = _importXml(self,v,createIfNotExists)

# ------------------------------------------------------------------------------
#  exportXml
# ------------------------------------------------------------------------------
def exportXml(self, REQUEST, RESPONSE):
  value = []
  ids = REQUEST.get('ids',[])
  filterIds = []
  for id in self.getFilterIds():
    if id in ids or len(ids) == 0:
      ob = self.getFilter(id).copy()
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
  export = self.getXmlHeader() + self.toXmlString(value,1)
  RESPONSE.setHeader('Content-Type',content_type)
  RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
  return export

"""
################################################################################
#
#   P R O C E S S E S
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _filtermanager.getRawProcesses:
#
#  Returns raw dictionary of processes.
# ------------------------------------------------------------------------------
def getRawProcesses(self):
  # Return attribute.
  return self.getConfProperty('ZMS.filter.processes',{})


# ------------------------------------------------------------------------------
#  _filtermanager.setProcess:
# 
#  Set/add process specified by given Id.
# ------------------------------------------------------------------------------
def setProcess(self, newId, newAcquired=0, newName='', newType='process', newCommand=None):
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
      newCommand += 'print "This is the Python Script %s" % script.getId()\n'
      newCommand += 'print "in", container.absolute_url()\n'
      newCommand += 'return printed\n'
      newCommand += '\n'
      newCommand += '# --// EO '+ newId + ' //--\n'
    elif newType in [ 'External Method']:
      newCommand = ''
      newCommand += '# Example code:\n'
      newCommand += '\n'
      newCommand += 'def ' + newId + '( self, request):\n'
      newCommand += '  return "This is the external method ' + newId + '"\n'
  # Set method.
  container = self.getHome()
  if newType in [ 'DTML Method']:
    if newId not in container.objectIds([newType]):
      container.manage_addDTMLMethod( newId, newName, newCommand)
    newOb = getattr( container, newId)
    newOb.manage_edit( title=newName, data=newCommand)
    roles=[ 'Manager']
    newOb._proxy_roles=tuple(roles)
  elif newType in [ 'Script (Python)']:
    if newId not in container.objectIds([newType]):
      PythonScript.manage_addPythonScript( container, newId)
    newOb = getattr( container, newId)
    newOb.ZPythonScript_setTitle( newName)
    newOb.write(newCommand)
    roles=[ 'Manager']
    newOb._proxy_roles=tuple(roles)
  elif newType in [ 'External Method']:
    newExternalMethod = INSTANCE_HOME+'/Extensions/'+newId+'.py'
    _fileutil.exportObj( newCommand, newExternalMethod)
    if newId not in container.objectIds([newType]):
      ExternalMethod.manage_addExternalMethod( container, newId, newName, newId, newId)
    newOb = getattr( container, newId)
  # Set.
  obs = getRawProcesses(self)
  ob = {}
  ob['acquired'] = newAcquired
  ob['name'] = newName
  ob['type'] = newType
  ob['command'] = newCommand
  obs[newId] = ob
  # Set attribute.
  self.setConfProperty('ZMS.filter.processes',obs.copy())
  # Return with new id.
  return newId


# ------------------------------------------------------------------------------
#  _filtermanager.delProcess:
# 
#  Delete process specified by given Id.
# ------------------------------------------------------------------------------
def delProcess(self, id):
  # Delete.
  cp = getRawProcesses(self)
  obs = {}
  for key in cp.keys():
    if key == id:
      # Delete method.
      if cp[key].get('type','') in [ 'DTML Method', 'External Method', 'Script (Python)']:
        container = self.getHome()
        dtml_method = getattr( container, id, None)
        if dtml_method is not None:
          container.manage_delObjects( ids=[id])
        if cp[key].get('type','') == 'External Method':
          try:
            _fileutil.remove( INSTANCE_HOME+'/Extensions/'+id+'.py')
          except:
            pass
    else:
      obs[key] = cp[key]
  # Set attribute.
  self.setConfProperty('ZMS.filter.processes',obs.copy())
  # Return with empty id.
  return ''


"""
################################################################################
#
#   F I L T E R S
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _filtermanager.getRawFilters:
#
#  Returns raw dictionary of filters.
# ------------------------------------------------------------------------------
def getRawFilters(self):
  # Return attribute.
  raw = self.getConfProperty('ZMS.filter.filters',{})
  for key in raw.keys():
    f = raw[ key]
    processes = f.get( 'processes', [])
    processes = filter( lambda x: x['id'] is not None, processes)
    f[ 'processes'] = processes
  return raw

# ------------------------------------------------------------------------------
#  _filtermanager.setFilter:
# 
#  Set/add filter specified by given Id.
# ------------------------------------------------------------------------------
def setFilter(self, newId, newAcquired=0, newName='', newFormat='', newContentType='', newDescription='', newRoles=[], newMetaTypes=[]):
  # Set.
  obs = getRawFilters(self)
  ob = {}
  ob['acquired'] = newAcquired
  ob['name'] = newName
  ob['format'] = newFormat
  ob['content_type'] = newContentType
  ob['description'] = newDescription
  ob['roles'] = newRoles
  ob['meta_types'] = newMetaTypes
  obs[newId] = ob
  # Set attribute.
  self.setConfProperty('ZMS.filter.filters',obs.copy())
  # Return with new id.
  return newId

# ------------------------------------------------------------------------------
#  _filtermanager.delFilter:
# 
#  Delete filter specified by given Id.
# ------------------------------------------------------------------------------
def delFilter(self, id):
  # Delete.
  cp = getRawFilters(self)
  obs = {}
  for key in cp.keys():
    if key != id:
      obs[key] = cp[key]
  # Set attribute.
  self.setConfProperty('ZMS.filter.filters',obs.copy())
  # Return with empty id.
  return ''


"""
################################################################################
#
#   F I L T E R - P R O C E S S E S
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _filtermanager.setFilterProcess:
# 
#  Set/add filter-process specified by given id.
# ------------------------------------------------------------------------------
def setFilterProcess(self, id, newProcessId, newProcessFile=None):
  # Set.
  obs = getRawFilters(self)
  ob = {}
  ob['id'] = newProcessId
  ob['file'] = newProcessFile
  pobs = obs[id].get('processes',[])
  pobs.append(ob)
  obs[id]['processes'] = pobs
  # Set attribute.
  self.setConfProperty('ZMS.filter.filters',obs.copy())
  # Return with new id.
  return len(pobs)-1


# ------------------------------------------------------------------------------
#  _filtermanager.delFilterProcess:
# 
#  Delete filter-process specified by given Ids.
# ------------------------------------------------------------------------------
def delFilterProcess(self, id, pid):
  # Delete.
  obs = getRawFilters(self)
  pobs = obs[ id].get('processes',[])
  ob = pobs[ pid]
  pobs.remove( pobs[pid])
  obs[id]['processes'] = pobs
  # Set attribute.
  self.setConfProperty('ZMS.filter.filters',obs.copy())
  # Return with empty id.
  return -1


# ------------------------------------------------------------------------------
#  _filtermanager.moveFilterProcess:
# 
#  Move filter-process specified by given Ids to specified position.
# ------------------------------------------------------------------------------
def moveFilterProcess(self, id, pid, pos):
  _globals.writeLog( self, '[moveFilterProcess]:id=%s; pid=%s; dir=%s'%(id,str(pid),str(dir)))
  # Set.
  obs = getRawFilters(self)
  pobs = obs[id].get('processes',[])
  ob = pobs[pid]
  pobs.remove(ob)
  pobs.insert(pos,ob)
  obs[id]['processes'] = pobs
  # Set attribute.
  self.setConfProperty('ZMS.filter.filters',obs.copy())
  # Return with new id.
  return pos


"""
################################################################################
#
#   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  _filtermanager.processData:
#
#  Process data with custom transformation.
# ------------------------------------------------------------------------------
def processData(self, processId, data, trans=None):
  # Create temporary folder.
  folder = tempfile.mktemp()
  # Save data to file.
  filename = _fileutil.getOSPath('%s/in.dat'%folder)
  _fileutil.exportObj(data, filename)
  # Save transformation to file.
  if trans is not None and trans != '':
    transfilename = _fileutil.getOSPath('%s/%s'%(folder,trans.getFilename()))
    _fileutil.exportObj(trans, transfilename)
  # Process file.
  filename = processFile(self, processId, filename, trans)
  # Read data from file.
  f = open(filename, 'rb')
  data = f.read()
  f.close()
  # Remove temporary folder.
  if not _globals.debug( self):
    _fileutil.remove(folder, deep=1)
  # Return data.
  return data


# ------------------------------------------------------------------------------
#  _filtermanager.processMethod:
#
#  Process DTML method.
# ------------------------------------------------------------------------------
def processMethod(self, processId, filename, trans, REQUEST):
  _globals.writeLog( self, '[processMethod]: processId=%s'%processId)
  infilename = filename
  outfilename = filename
  REQUEST.set( 'ZMS_FILTER_IN', infilename)
  REQUEST.set( 'ZMS_FILTER_OUT', outfilename)
  REQUEST.set( 'ZMS_FILTER_TRANS', trans)
  REQUEST.set( 'ZMS_FILTER_CUR_DIR', _fileutil.getFilePath(infilename))
  try:
    value = getattr( self, processId)( self, REQUEST)
  except:
    value = _globals.writeError( self, '[processMethod]: processId=%s'%processId)
  outfilename = REQUEST.get( 'ZMS_FILTER_OUT')
  # Return filename.
  return outfilename


# ------------------------------------------------------------------------------
#  _filtermanager.processCommand:
#
#  Process file with command.
# ------------------------------------------------------------------------------
def processCommand(self, filename, command):
  _globals.writeLog( self, '[processCommand]: infilename=%s'%filename)
  infilename = _fileutil.getOSPath( filename)
  outfilename = _fileutil.getOSPath( filename)
  mZmsHome = '{zms_home}'
  mCurDir = '{cur_dir}'
  mIn = '{in}'
  mOut = '{out}'
  i = command.find(mOut[:-1])
  if i >= 0:
    j = command.find('}',i)
    mExt = command[i+len(mOut[:-1]):j]
    mOut = command[i:j+1]
    if len(mExt) > 0:
      outfilename = outfilename[:outfilename.rfind('.')] + mExt
    else:
      outfilename += '.tmp'
  tmpoutfilename = outfilename + '~'
  instance_home = INSTANCE_HOME
  software_home = os.path.join(SOFTWARE_HOME, '..%s..' % os.sep)
  software_home = os.path.normpath(software_home)  
  command = command.replace( '{software_home}', software_home)
  command = command.replace( '{instance_home}', instance_home)
  command = command.replace( mZmsHome,_fileutil.getOSPath(package_home(globals())))
  command = command.replace( mCurDir,_fileutil.getFilePath(infilename))
  command = command.replace( mIn,infilename)
  command = command.replace( mOut,tmpoutfilename)
  path = _fileutil.getFilePath(filename)
  _globals.writeLog( self, '[processCommand]: path=%s'%path)
  os.chdir(path)
  _globals.writeLog( self, '[processCommand]: command=%s'%command)
  os.system(command)
  # Check if output file exists.
  try: 
    os.stat( _fileutil.getOSPath( tmpoutfilename)) 
    _globals.writeLog( self, '[processCommand]: rename %s to %s'%( tmpoutfilename, outfilename))
    try:
      os.remove( outfilename)
    except OSError:
      pass
    os.rename( tmpoutfilename, outfilename)
  except OSError:
    outfilename = infilename
  # Remove input file if it is the result of a transformation of output file.
  if outfilename != infilename:
    os.remove( infilename)
  # Return filename.
  _globals.writeLog( self, '[processCommand]: outfilename=%s'%( outfilename))
  return outfilename


# ------------------------------------------------------------------------------
#  _filtermanager.processFile:
#
#  Process file with custom transformation.
# ------------------------------------------------------------------------------
def processFile(self, processId, filename, trans=None):
  _globals.writeLog( self, '[processFile]: processId=%s'%processId)
  folder = _fileutil.getFilePath(filename)
  processOb = self.getProcess(processId)
  command = processOb.get('command')
  # Save transformation to file.
  if trans is not None and trans != '':
    transfilename = '%s/%s'%( folder, trans.getFilename())
    command = command.replace( '{trans}', transfilename)
  # Execute command.
  filename = processCommand(self, filename, command)
  # Return filename.
  return filename


# ------------------------------------------------------------------------------
#  _filtermanager.processFilter:
#
#  Process filter.
# ------------------------------------------------------------------------------
def processFilter(self, ob_filter, folder, filename, REQUEST):
  for ob_process in ob_filter.get('processes',[]):
    filename = self.execProcessFilter( ob_process, folder, filename, REQUEST)
  # Return filename.
  return filename


# ------------------------------------------------------------------------------
#  _filtermanager.importFilter:
# ------------------------------------------------------------------------------
def importFilter(self, filename, id, REQUEST):
  ob_filter = self.getFilter(id)
  folder = _fileutil.getFilePath(filename)
  # Process filter.
  filename = processFilter(self, ob_filter, folder, filename, REQUEST)
  # Return filename.
  return filename


# ------------------------------------------------------------------------------
#  _filtermanager.exportFilter:
# ------------------------------------------------------------------------------
def exportFilter(self, id, REQUEST):
  # Set local variables.
  ob_filter = self.getFilter(id)
  tempfolder, outfilename = self.initExportFilter( id, REQUEST)
  # Process filter.
  outfilename = processFilter(self, ob_filter, tempfolder, outfilename, REQUEST)
  # Return values.
  content_type = ob_filter.get('content_type','content/unknown')
  filename = 'exportFilter.%s'%content_type[content_type.find('/')+1:]
  # Zip File.
  if content_type == 'application/zip':
    data = _fileutil.buildZipArchive( outfilename, get_data=True)
  # Read File.
  else:
    _globals.writeLog( self, '[exportFilter]: Read %s'%outfilename)
    f = open(outfilename, 'rb')
    data = f.read()
    f.close()
  # Remove temporary folder.
  if not _globals.debug( self):
    _fileutil.remove( tempfolder, deep=1)
  # Return.
  return filename, data, content_type


################################################################################
################################################################################
###
###   class FilterItem
###
################################################################################
################################################################################
class FilterItem:

    # --------------------------------------------------------------------------
    #  FilterManager.initExportFilter:
    # --------------------------------------------------------------------------
    def initExportFilter(self, id, REQUEST):
      # Set environment variables.
      instance_home = INSTANCE_HOME
      software_home = os.path.join(SOFTWARE_HOME, '..%s..' % os.sep)
      software_home = os.path.normpath(software_home)  
      REQUEST.set( 'ZMS_FILTER', True)
      REQUEST.set( 'ZMS_FILTER_SOFTWARE_HOME', software_home)
      REQUEST.set( 'ZMS_FILTER_INSTANCE_HOME', instance_home)
      REQUEST.set( 'ZMS_FILTER_PACKAGE_HOME', _fileutil.getOSPath(package_home(globals())))
      # Set local variables.
      ob_filter = self.getFilter(id)
      ob_filter_format = ob_filter.get('format','')
      incl_embedded = ob_filter_format == 'XML_incl_embedded'
      # Create temporary folder.
      tempfolder = tempfile.mktemp()
      ressources = self.exportRessources( tempfolder, REQUEST, from_zms=ob_filter_format=='XHTML', from_home=ob_filter_format=='XHTML', incl_embedded=incl_embedded)
      # Export data to file.
      if ob_filter_format == 'export':
        outfilename = _fileutil.getOSPath('%s/INDEX0'%tempfolder)
      elif ob_filter_format in ['XML','XML_incl_embedded']:
        # Set XML.
        data = self.toXml( REQUEST, incl_embedded)
        outfilename = _fileutil.getOSPath('%s/export.xml'%tempfolder)
        _fileutil.exportObj( data, outfilename)
      elif ob_filter_format == 'XHTML':
        # Set XHTML.
        data = self.toXhtml( REQUEST)
        outfilename = _fileutil.getOSPath('%s/export.html'%tempfolder)
        _fileutil.exportObj( data, outfilename)
      elif ob_filter_format == 'myXML':
        # Set myXML.
        data = self.getXmlHeader() + getattr( self, 'getObjToXml_DocElmnt')(context=self)
        outfilename = _fileutil.getOSPath('%s/export.xml'%tempfolder)
        _fileutil.exportObj( data, outfilename)
      else:
        raise zExceptions.InternalError("Unknown format '%s'"%ob_filter.get('format',''))
      return tempfolder, outfilename


    # --------------------------------------------------------------------------
    #  _filtermanager.execProcessFilter:
    # --------------------------------------------------------------------------
    def execProcessFilter(self, ob_process, folder, filename, REQUEST):
      processId = ob_process.get( 'id')
      processOb = self.getProcess( processId)
      if processOb is not None:
        processType = processOb.get( 'type', 'process')
        trans = ob_process.get( 'file', None)
        # Save transformation to file.
        if trans is not None and trans != '':
          transfilename = '%s/%s'%( folder, trans.getFilename())
          _fileutil.exportObj( trans.getData(), transfilename)
        if processType in [ 'DTML Method', 'External Method', 'Script (Python)']:
          filename = processMethod(self, processId, filename, trans, REQUEST)
        else:
          filename = processFile(self, processId, filename, trans)
      # Return filename.
      return filename


################################################################################
################################################################################
###
###   class FilterManager
###
################################################################################
################################################################################
class FilterManager:

    # Management Interface.
    # ---------------------
    manage_importexportDebugFilter = PageTemplateFile('zpt/ZMSContainerObject/manage_importexportdebugfilter', globals())


    # --------------------------------------------------------------------------
    #  FilterManager.getProcessIds:
    # 
    #  Returns list of process-Ids.
    # --------------------------------------------------------------------------
    def getProcessIds(self, sort=1):
      obs = getRawProcesses(self)
      ids = obs.keys()
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        ids.extend( filter( lambda x: x not in ids, portalMaster.getProcessIds()))
      if sort:
        mapping = map(lambda x: (self.getProcess(x)['name'],x),ids)
        mapping.sort()
        ids = map(lambda x: x[1],mapping)
      return ids

    # --------------------------------------------------------------------------
    #  FilterManager.getProcess:
    # 
    #  Returns process specified by Id.
    # --------------------------------------------------------------------------
    def getProcess(self, id):
      processes = getRawProcesses(self)
      process = {}
      if processes.has_key( id):
        process = processes.get( id).copy()
      else:
        # Acquire from parent.
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          if id in portalMaster.getProcessIds():
            process = portalMaster.getProcess(id)
            process['acquired'] = 1
      process['id'] = id
      # Synchronize type.
      try:
        container = self.getHome()
        if process.get('type') in [ 'DTML Method']:
          ob = getattr( container, process['id'])
          process['command'] = ob.raw
        elif process.get('type') in [ 'Script (Python)']:
          ob = getattr( container, process['id'])
          process['command'] = ob.read()
      except:
        pass
      return process


    # --------------------------------------------------------------------------
    #  FilterManager.getFilterIds:
    # 
    #  Returns list of filter-Ids.
    # --------------------------------------------------------------------------
    def getFilterIds(self, sort=1):
      obs = getRawFilters(self)
      ids = obs.keys()
      if sort:
        mapping = map(lambda x: (self.getFilter(x)['name'],x),ids)
        mapping.sort()
        ids = map(lambda x: x[1],mapping)
      return ids


    # --------------------------------------------------------------------------
    #  FilterManager.getFilter:
    # 
    #  Returns filter specified by Id.
    # --------------------------------------------------------------------------
    def getFilter(self, id):
      obs = getRawFilters(self)
      ob = {}
      if obs.has_key( id):
        ob = obs.get( id).copy()
      # Acquire from parent.
      if ob.get('acquired',0) == 1:
        portalMaster = self.getPortalMaster()
	if portalMaster is not None:
          ob = portalMaster.getFilter(id)
          ob['acquired'] = 1
      ob['id'] = id
      return ob


    # --------------------------------------------------------------------------
    #  FilterManager.getFilterProcesses:
    # 
    #  Returns list of processes for filter specified by Id.
    # --------------------------------------------------------------------------
    def getFilterProcesses(self, id):
      obs = []
      c = 0
      for process in self.getFilter( id).get( 'processes', []):
        ob = process.copy()
        ob[ 'type'] = ob.get( 'type', 'process')
        if ob.get('file') not in ['',None]:
          f = ob['file']
          ob['file_href'] = 'get_conf_blob?path=ZMS.filter.filters/%s/processes/%i:int/file'%(id,c)
          ob['file_filename'] = f.getFilename()
          ob['file_content_type'] = f.getContentType()
          ob['file_size'] = f.get_size()
        process = self.getProcess( ob[ 'id'])
        if process is not None:
          obs.append( ob)
        c += 1
      return obs


    ############################################################################
    #  FilterManager.manage_changeFilter:
    #
    #  Customize filter.
    ############################################################################
    def manage_changeFilter(self, lang, btn='', key='', REQUEST=None, RESPONSE=None):
      """ FilterManager.manage_changeFilter """
      message = ''
      id = REQUEST.get('id','')
      pid = REQUEST.get('pid',-1)
      
      # Acquire.
      # --------
      if btn == self.getZMILangStr('BTN_ACQUIRE'):
        newId = REQUEST.get('aq_id')
        newAcquired = 1
        id = setFilter(self, newId, newAcquired)
        message = self.getZMILangStr('MSG_INSERTED')%id
      
      # Change.
      # -------
      elif btn == self.getZMILangStr('BTN_SAVE'):
        cp = self.getFilter(id)
        # Filter.
        newId = REQUEST.get('inpId').strip()
        newAcquired = 0
        newName = REQUEST.get('inpName').strip()
        newFormat = REQUEST.get('inpFormat').strip()
        newContentType = REQUEST.get('inpContentType').strip()
        newDescription = REQUEST.get('inpDescription').strip()
        newRoles = REQUEST.get('inpRoles',[])
        newMetaTypes = REQUEST.get('inpMetaTypes',[])
        id = delFilter(self, id)
        id = setFilter(self, newId, newAcquired, newName, newFormat, newContentType, newDescription, newRoles, newMetaTypes)
        # Filter Processes.
        c = 0
        for filterProcess in cp.get('processes',[]):
          newProcessId = REQUEST.get('newFilterProcessId_%i'%c,'').strip()
          newProcessFile = REQUEST.get('newFilterProcessFile_%i'%c)
          if isinstance(newProcessFile,ZPublisher.HTTPRequest.FileUpload):
            if len(getattr(newProcessFile, 'filename',''))==0:
              newProcessFile = filterProcess.get('file', None)
            else:
              newProcessFile = _blobfields.createBlobField(self, _globals.DT_FILE, newProcessFile)
          setFilterProcess(self, id, newProcessId, newProcessFile)
          c += 1
        newProcessId = REQUEST.get('newFilterProcessId_%i'%c,'').strip()
        newProcessFile = REQUEST.get('newFilterProcessFile_%i'%c)
        if newProcessId:
          setFilterProcess(self, id, newProcessId, newProcessFile)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn == self.getZMILangStr('BTN_DELETE') and key == 'obj':
        ids = REQUEST.get('ids',[])
        for id in ids:
          delFilter(self, id)
        message = self.getZMILangStr('MSG_DELETED')%len(ids)
      elif btn == 'delete' and key == 'attr':
        ids = [REQUEST.get('id')]
        for id in ids:
          if id is not None:
            delFilterProcess(self, id, pid)
        message = self.getZMILangStr('MSG_DELETED')%len(ids)
      
      # Export.
      # -------
      elif btn == self.getZMILangStr('BTN_EXPORT'):
        return exportXml(self, REQUEST, RESPONSE)
      
      # Import.
      # -------
      elif btn == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        if f:
          filename = f.filename
          importXml(self, xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename, createIfNotExists=1)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        if key == 'obj':
          newId = REQUEST.get('newId').strip()
          newAcquired = 0
          newName = REQUEST.get('newName').strip()
          newFormat = REQUEST.get('newFormat').strip()
          newContentType = REQUEST.get('newContentType').strip()
          id = setFilter(self, newId, newAcquired, newName, newFormat, newContentType)
          message = self.getZMILangStr('MSG_INSERTED')%id
        elif key == 'attr':
          newProcessId = REQUEST.get('newFilterProcessId')
          newProcessFile = REQUEST.get('newFilterProcessFile')
          if isinstance(newProcessFile,ZPublisher.HTTPRequest.FileUpload):
            if len(getattr(newProcessFile, 'filename',''))==0:
              newProcessFile = None
            else:
              newProcessFile = _blobfields.createBlobField(self, _globals.DT_FILE, newProcessFile)
          pid = setFilterProcess(self, id, newProcessId, newProcessFile)
          message = self.getZMILangStr('MSG_INSERTED')%newProcessId
      
      # Move to.
      # --------
      elif btn == 'move_to':
        pos = REQUEST['pos']
        pid = moveFilterProcess(self, id, pid, pos)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%pid),(pos+1))
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeFilterForm?id=%s&pid:int=%i&lang=%s&manage_tabs_message=%s'%(id,pid,lang,message))


    ############################################################################
    #  FilterManager.manage_changeProcess:
    #
    #  Customize process.
    ############################################################################
    def manage_changeProcess(self, lang, btn='', key='', REQUEST=None, RESPONSE=None):
      """ FilterManager.manage_changeProcess """
      message = ''
      id = REQUEST.get('id','')

      # Change.
      # -------
      if btn == self.getZMILangStr('BTN_SAVE'):
        newId = REQUEST.get('inpId').strip()
        newAcquired = 0
        newName = REQUEST.get('inpName').strip()
        newType = REQUEST.get('inpType').strip()
        newCommand = REQUEST.get('inpCommand').strip()
        id = delProcess(self, id)
        id = setProcess(self, newId, newAcquired, newName, newType, newCommand)
        message = self.getZMILangStr('MSG_CHANGED')

      # Delete.
      # -------
      elif btn == self.getZMILangStr('BTN_DELETE'):
        ids = REQUEST.get('ids',[])
        for id in ids:
          delProcess(self, id)
        message = self.getZMILangStr('MSG_DELETED')%len(ids)

      # Export.
      # -------
      elif btn == self.getZMILangStr('BTN_EXPORT'):
        return exportXml(self, REQUEST, RESPONSE)

      # Import.
      # -------
      elif btn == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        if f:
          filename = f.filename
          importXml(self, xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename, createIfNotExists=1)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)

      # Insert.
      # -------
      elif btn == self.getZMILangStr('BTN_INSERT'):
        newId = REQUEST.get('newId').strip()
        newAcquired = 0
        newName = REQUEST.get('newName').strip()
        newType = REQUEST.get('newType').strip()
        id = setProcess(self, newId, newAcquired, newName, newType)
        message = self.getZMILangStr('MSG_INSERTED')%id

      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_customizeFilterForm?id=%s&lang=%s&manage_tabs_message=%s'%(id,lang,message))

################################################################################
