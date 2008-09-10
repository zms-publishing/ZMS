################################################################################
# _filtermanager.py
#
# $Id: _filtermanager.py,v 1.8 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.8 $
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
from App.Common import package_home
from Globals import HTMLFile
import ZPublisher.HTTPRequest
import copy
import os
import tempfile
import time
import urllib
# Product Imports.
import _blobfields
import _fileutil
import _globals


"""
################################################################################
#
#   X M L   I M / E X P O R T
#
################################################################################
"""

# ------------------------------------------------------------------------------
#  importXml
# ------------------------------------------------------------------------------

def _importXml(self, item, zms_system=0, createIfNotExists=1):
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
    ids = filters.keys()
    ids = filter( lambda x: filters[x].get('zms_system',0)==1, ids)
    if createIfNotExists == 1 or newId in ids:
      delFilter(self, newId)
      setFilter(self, newId, newAcquired, newName, newFormat, newContentType, newDescription, newRoles, newMetaTypes, zms_system)
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
    ids = processes.keys()
    ids = filter( lambda x: processes[x].get('zms_system',0)==1, ids)
    if createIfNotExists == 1 or newId in ids:
      delProcess(self, newId)
      setProcess(self, newId, newAcquired, newName, newType, newCommand, zms_system)
  else:
    _globals.writeException(self,"[_importXml]: Unknown type >%s<"%itemType)

def importXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
  v = self.parseXmlString(xml)
  if type(v) is list:
    for item in v:
      id = _importXml(self,item,zms_system,createIfNotExists)
  else:
    id = _importXml(self,v,zms_system,createIfNotExists)

# ------------------------------------------------------------------------------
#  exportXml
# ------------------------------------------------------------------------------
def exportXml(self, REQUEST, RESPONSE):
  value = []
  ids = REQUEST.get('ids',[])
  for id in self.getFilterIds():
    if id in ids or len(ids) == 0:
      ob = self.getFilter(id).copy()
      if ob.has_key('zms_system'):
        del ob['zms_system']
      value.append({'type':'filter','value':ob})
  for id in self.getProcessIds():
    if id in ids or len(ids) == 0:
      ob = self.getProcess(id).copy()
      if ob.has_key('zms_system'):
        del ob['zms_system']
      value.append({'type':'process','value':ob})
  # XML.
  if len(value)==1:
    value = value[0]
  content_type = 'text/xml; charset=utf-8'
  filename = 'export.filter.xml'
  export = self.getXmlHeader() + self.toXmlString(value,1)
  RESPONSE.setHeader('Content-Type',content_type)
  RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
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
def setProcess(self, newId, newAcquired=0, newName='', newType='process', newCommand=None, zms_system=0):
  if newCommand is None:
    if newType == 'DTML Method':
      newCommand = []
      newCommand.append( '<!-- BO %s -->\n\n'%newId)
      newCommand.append( '<!-- EO %s -->\n'%newId)
      newCommand = ''.join( newCommand)
    else:
      newCommand = ''
  # Set method.
  if newType == 'DTML Method':
    container = self.getHome()
    if newId in container.objectIds([newType]):
      dtml_method = getattr( container, newId)
      dtml_method.manage_edit( newName, newCommand)
    else:
      container.manage_addDTMLMethod( newId, newName, newCommand)
  # Set.
  obs = getRawProcesses(self)
  ob = {}
  ob['acquired'] = newAcquired
  ob['name'] = newName
  ob['type'] = newType
  ob['command'] = newCommand
  ob['zms_system'] = zms_system
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
      if cp[key].get('type','') == 'DTML Method':
        container = self.getHome()
        dtml_method = getattr( container, id, None)
        if dtml_method is not None:
          container.manage_delObjects( ids = [ id])
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
def setFilter(self, newId, newAcquired=0, newName='', newFormat='', newContentType='', newDescription='', newRoles=[], newMetaTypes=[], zms_system=0):
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
  ob['zms_system'] = zms_system
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
  if _globals.debug( self):
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
  if _globals.debug( self):
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
    value = _globals.writeException( self, '[processMethod]: processId=%s'%processId)
  outfilename = REQUEST.get( 'ZMS_FILTER_OUT')
  # Return filename.
  return outfilename


# ------------------------------------------------------------------------------
#  _filtermanager.processCommand:
#
#  Process file with command.
# ------------------------------------------------------------------------------
def processCommand(self, filename, command):
  if _globals.debug( self):
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
  if _globals.debug( self):
    _globals.writeLog( self, '[processCommand]: command=%s'%command)
  os.system(command)
  # Check if output file exists.
  try: 
    os.stat( _fileutil.getOSPath( tmpoutfilename)) 
    if _globals.debug( self):
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
  if _globals.debug( self):
    _globals.writeLog( self, '[processCommand]: outfilename=%s'%( outfilename))
  return outfilename


# ------------------------------------------------------------------------------
#  _filtermanager.processFile:
#
#  Process file with custom transformation.
# ------------------------------------------------------------------------------
def processFile(self, processId, filename, trans=None):
  if _globals.debug( self):
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
# ------------------------------------------------------------------------------
def processFilter(self, ob_filter, folder, filename, REQUEST):
  for process in ob_filter.get('processes',[]):
    processId = process.get( 'id')
    processOb = self.getProcess(processId)
    if processOb is not None:
      processType = processOb.get( 'type', 'process')
      trans = process.get( 'file', None)
      # Save transformation to file.
      if trans is not None and trans != '':
        transfilename = '%s/%s'%( folder, trans.getFilename())
        _fileutil.exportObj( trans.getData(), transfilename)
      if processType == 'DTML Method':
        filename = processMethod(self, processId, filename, trans, REQUEST)
      else:
        filename = processFile(self, processId, filename, trans)
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
  ressources = self.exportRessources( tempfolder, REQUEST, from_content=True, from_zms=ob_filter_format=='XHTML', from_home=ob_filter_format=='XHTML', incl_embedded=incl_embedded)
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
    raise "Unknown format '%s'"%ob_filter.get('format','')
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
    if _globals.debug( self):
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
###   class FilterManager
###
################################################################################
################################################################################
class FilterManager: 

    # Management Interface.
    # ---------------------
    manage_customizeFilterForm = HTMLFile('dtml/ZMS/manage_customizefilterform', globals())


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
      obs = getRawProcesses(self)
      ob = {}
      if obs.has_key( id):
        ob = obs.get( id).copy()
      else:
        # Acquire from parent.
        portalMaster = self.getPortalMaster()
        if portalMaster is not None:
          if id in portalMaster.getProcessIds():
            ob = portalMaster.getProcess(id)
            ob['acquired'] = 1
      ob['id'] = id
      return ob


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
      for process in self.getFilter( id).get( 'processes', []):
        ob = process.copy()
        ob[ 'type'] = ob.get( 'type', 'process')
        process = self.getProcess( ob[ 'id'])
        if process is not None:
          obs.append( ob)
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
      elif btn == self.getZMILangStr('BTN_CHANGE'):
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
          newProcessId = REQUEST.get('newFilterProcessId_%i'%c)
          newProcessFile = REQUEST.get('newFilterProcessFile_%i'%c)
          if isinstance(newProcessFile,ZPublisher.HTTPRequest.FileUpload):
            if len(getattr(newProcessFile, 'filename',''))==0:
              newProcessFile = filterProcess.get('file', None)
            else:
              newProcessFile = _blobfields.createBlobField(self, _globals.DT_FILE, newProcessFile)
          setFilterProcess(self, id, newProcessId, newProcessFile)
          c += 1
        message = self.getZMILangStr('MSG_CHANGED')

      # Delete.
      # -------
      elif btn == self.getZMILangStr('BTN_DELETE') and key == 'obj':
        id = delFilter(self, id)
        message = self.getZMILangStr('MSG_DELETED')%int(1)
      elif btn == 'delete' and key == 'attr':
        pid = delFilterProcess(self, id, pid)
        message = self.getZMILangStr('MSG_DELETED')%int(1)

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
          createIfNotExists = 1
          self.importConf(filename, REQUEST, createIfNotExists)
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
      if btn == self.getZMILangStr('BTN_CHANGE'):
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
        id = delProcess(self, id)
        message = self.getZMILangStr('MSG_DELETED')%int(1)

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
          createIfNotExists = 1
          self.importConf(filename, REQUEST, createIfNotExists)
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
