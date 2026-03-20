"""
_filtermanager.py

Import/export filter pipeline helpers for ZMS.

This module provides the procedural building blocks that execute configured
filter pipelines during import/export. A pipeline consists of ordered process
steps (commands, methods, scripts) and optional transformation files.

The module-level functions handle file-based processing and command execution,
while C{FilterItem} integrates those helpers with object export context and
request/session state.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
import os
import tempfile
import zExceptions
# Product Imports.
from Products.zms import _fileutil
from Products.zms import standard
from Products.zms import zopeutil

def getTransFilename(self, folder, trans):
  """
  Build the filesystem path for a transformation resource.

  @param self: Context object providing logging utilities.
  @type self: C{object}
  @param folder: Working directory used by the current filter run.
  @type folder: C{str}
  @param trans: Transformation object with an id in
    C{<process-id>.<nr>.<filename>} format.
  @type trans: C{object}
  @return: Absolute transformation filename inside C{folder}.
  @rtype: C{str}
  """
  transid = trans.getId()
  transid = '.'.join(transid.split('.')[2:]) # <process-id>.<process-nr>.<filename>
  transfilename = os.path.join(folder, transid)
  standard.writeLog(self,"[getTransFilename]: transfilename=%s"%(transfilename))
  return transfilename


def processData(self, processId, data, trans=None):
  """
  Process raw bytes data with one configured process step.

  @param self: Context object exposing filter manager and configuration.
  @type self: C{object}
  @param processId: Filter-process id to execute.
  @type processId: C{str}
  @param data: Input payload written to a temporary input file.
  @type data: C{bytes} | C{str}
  @param trans: Optional transformation object written to disk and referenced
    by the process command.
  @type trans: C{object} | C{None}
  @return: Processed payload read from the resulting output file.
  @rtype: C{bytes}
  """
  # Create temporary folder.
  tempfolder = tempfile.mkdtemp()
  # Save data to file.
  filename = _fileutil.getOSPath('%s/in.dat'%tempfolder)
  _fileutil.exportObj(data, filename)
  # Save transformation to file.
  if trans:
      _fileutil.exportObj(trans, getTransFilename(self, tempfolder, trans))
  # Process file.
  filename = processFile(self, processId, filename, trans)
  # Read data from file.
  f = open(filename, 'rb')
  data = f.read()
  f.close()
  # Remove temporary folder.
  if not self.getConfProperty('ZMS.mode.debug', 0):
      _fileutil.remove(tempfolder, deep=True)
  # Return data.
  return data


def processMethod(self, processId, filename, trans, REQUEST):
  """
  Execute a method/script-based process step with request-bound file markers.

  @param self: Context object exposing filter manager.
  @type self: C{object}
  @param processId: Filter-process id to execute.
  @type processId: C{str}
  @param filename: Input filename to be processed.
  @type filename: C{str}
  @param trans: Optional transformation object used by the process.
  @type trans: C{object} | C{None}
  @param REQUEST: Active request used to pass process variables.
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Output filename selected by the process step.
  @rtype: C{str}
  """
  standard.writeBlock( self, '[processMethod]: processId=%s'%processId)
  infilename = filename
  outfilename = filename
  REQUEST.set( 'ZMS_FILTER_IN', infilename)
  REQUEST.set( 'ZMS_FILTER_OUT', outfilename)
  REQUEST.set( 'ZMS_FILTER_TRANS', trans)
  REQUEST.set( 'ZMS_FILTER_CUR_DIR', _fileutil.getFilePath(infilename))
  try:
      process = self.getFilterManager().getProcess(processId) 
      ob = process['ob'] 
      value = zopeutil.callObject( ob, zmscontext=self)
  except:
      value = standard.writeError( self, '[processMethod]: processId=%s'%processId)
  outfilename = REQUEST.get( 'ZMS_FILTER_OUT')
  # Return filename.
  return outfilename


def processCommand(self, filename, command):
  """
  Execute an external command-based process step on a file.

  Placeholders supported in C{command} include C{{in}}, C{{out}},
  C{{cur_dir}}, C{{package_home}}, and C{{instance_home}}.

  @param self: Context object exposing configuration and logging.
  @type self: C{object}
  @param filename: Input filename passed into the command.
  @type filename: C{str}
  @param command: Command template containing replacement markers.
  @type command: C{str}
  @return: Final output filename (or original input filename on failure).
  @rtype: C{str}
  """
  standard.writeBlock( self, '[processCommand]: infilename=%s'%filename)
  infilename = _fileutil.getOSPath( filename)
  outfilename = _fileutil.getOSPath( filename)
  mCurDir = '{cur_dir}'
  mIn = '{in}'
  mOut = '{out}'
  i = command.find(mOut[:-1])
  if i >= 0:
      j = command.find('}', i)
      mExt = command[i+len(mOut[:-1]):j]
      mOut = command[i:j+1]
      if len(mExt) > 0:
          outfilename = outfilename[:outfilename.rfind('.')] + mExt
      else:
          outfilename += '.tmp'
  tmpoutfilename = outfilename + '~'
  instance_home = standard.getINSTANCE_HOME()
  package_home = standard.getPACKAGE_HOME()
  package_home = os.path.normpath(package_home)
  command = command.replace( '{package_home}', package_home)
  command = command.replace( '{instance_home}', instance_home)
  command = command.replace( mCurDir, _fileutil.getFilePath(infilename))
  command = command.replace( mIn, infilename)
  command = command.replace( mOut, tmpoutfilename)
  # Change directory (deprecated!).
  if self.getConfProperty('ZMS.filtermanager.processCommand.chdir', 0):
      path = _fileutil.getFilePath(filename)
      standard.writeBlock( self, '[processCommand]: path=%s'%path)
      os.chdir(path)
  # Execute command.
  standard.writeBlock( self, '[processCommand]: command=%s'%command)
  os.system(command)
  # Check if output file exists.
  try: 
      os.stat( _fileutil.getOSPath( tmpoutfilename)) 
      standard.writeBlock( self, '[processCommand]: rename %s to %s'%( tmpoutfilename, outfilename))
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
  standard.writeBlock( self, '[processCommand]: outfilename=%s'%( outfilename))
  return outfilename


def processFile(self, processId, filename, trans=None):
  """
  Process one file using the configured command for a process id.

  @param self: Context object exposing filter manager.
  @type self: C{object}
  @param processId: Filter-process id whose command is executed.
  @type processId: C{str}
  @param filename: Input filename.
  @type filename: C{str}
  @param trans: Optional transformation object referenced by command.
  @type trans: C{object} | C{None}
  @return: Output filename.
  @rtype: C{str}
  """
  standard.writeBlock( self, '[processFile]: processId=%s'%processId)
  folder = _fileutil.getFilePath(filename)
  processOb = self.getFilterManager().getProcess(processId)
  command = processOb.get('command')
  # Save transformation to file.
  if trans:
      command = command.replace( '{trans}', getTransFilename(self, folder, trans))
  # Execute command.
  filename = processCommand(self, filename, command)
  # Return filename.
  return filename


def processFilter(self, ob_filter, folder, filename, REQUEST):
  """
  Execute all process steps configured for a filter definition.

  @param self: Context object exposing filter manager.
  @type self: C{object}
  @param ob_filter: Filter definition containing id and process assignments.
  @type ob_filter: C{dict}
  @param folder: Working folder used during filter execution.
  @type folder: C{str}
  @param filename: Input filename passed through each process step.
  @type filename: C{str}
  @param REQUEST: Active request context.
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Final output filename after all process steps.
  @rtype: C{str}
  """
  for ob_process in self.getFilterManager().getFilterProcesses(ob_filter['id']):
    filename = self.execProcessFilter( ob_process, folder, filename, REQUEST)
  # Return filename.
  return filename


def importFilter(self, filename, id, REQUEST):
  """
  Run the import pipeline for one configured filter.

  @param self: Context object exposing filter manager.
  @type self: C{object}
  @param filename: Source filename to import/process.
  @type filename: C{str}
  @param id: Filter id.
  @type id: C{str}
  @param REQUEST: Active request context.
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Final processed filename.
  @rtype: C{str}
  """
  ob_filter = self.getFilterManager().getFilter(id)
  folder = _fileutil.getFilePath(filename)
  # Process filter.
  filename = processFilter(self, ob_filter, folder, filename, REQUEST)
  # Return filename.
  return filename


def exportFilter(self, id, REQUEST):
  """
  Run the export pipeline and return downloadable file payload metadata.

  @param self: Context object exposing filter manager and export helpers.
  @type self: C{object}
  @param id: Filter id to execute.
  @type id: C{str}
  @param REQUEST: Active request context.
  @type REQUEST: C{ZPublisher.HTTPRequest}
  @return: Tuple C{(filename, data, content_type)}.
  @rtype: C{tuple}
  """
  # Set local variables.
  ob_filter = self.getFilterManager().getFilter(id)
  tempfolder, outfilename = self.initExportFilter( id, REQUEST)
  # Process filter.
  outfilename = processFilter(self, ob_filter, tempfolder, outfilename, REQUEST)
  # Return values.
  content_type = ob_filter.get('content_type', 'content/unknown')
  filename = 'exportFilter.%s'%content_type[content_type.find('/')+1:]
  # Zip File.
  if content_type == 'application/zip':
    data = _fileutil.buildZipArchive( outfilename, get_data=True)
  # Read File.
  else:
    standard.writeBlock( self, '[exportFilter]: Read %s'%outfilename)
    f = open(outfilename, 'rb')
    data = f.read()
    f.close()
  # Remove temporary folder.
  if not self.getConfProperty('ZMS.mode.debug', 0):
    _fileutil.remove( tempfolder, deep=1)
  # Return.
  return filename, data, content_type

class FilterItem(object):
    """Mixin exposing helper methods to initialise and execute filter exports."""

    def initExportFilter(self, id, REQUEST):
      """
      Prepare export context, temp workspace, and initial export input file.

      @param id: Filter id.
      @type id: C{str}
      @param REQUEST: Active request used for env/session variables.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Tuple C{(tempfolder, outfilename)} used by subsequent steps.
      @rtype: C{tuple}
      """
      # Set environment variables.
      instance_home = standard.getINSTANCE_HOME()
      package_home = standard.getPACKAGE_HOME()
      package_home = os.path.normpath(package_home)
      REQUEST.set( 'ZMS_FILTER', True)
      REQUEST.set( 'ZMS_FILTER_INSTANCE_HOME', instance_home)
      REQUEST.set( 'ZMS_FILTER_PACKAGE_HOME', package_home)
      # Set session variables
      session = REQUEST.SESSION
      session['ZMS_FILTER_CONTEXT'] = self.getRefObjPath(self)
      # Set local variables.
      ob_filter = self.getFilterManager().getFilter(id)
      ob_filter_format = ob_filter.get('format', '')
      # Create temporary folder.
      tempfolder = tempfile.mkdtemp()
      ressources = self.exportRessources( tempfolder, REQUEST, from_zms=ob_filter_format=='XHTML', from_home=ob_filter_format=='XHTML')
      # Export data to file.
      if ob_filter_format == 'export':
        outfilename = _fileutil.getOSPath('%s/INDEX0'%tempfolder)
      elif ob_filter_format in ['XML', 'XML_incl_embedded']:
        # Set XML.
        data = self.toXml( REQUEST)
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
        raise zExceptions.InternalError("Unknown format '%s'"%ob_filter.get('format', ''))
      return tempfolder, outfilename


    def execProcessFilter(self, ob_process, folder, filename, REQUEST):
      """
      Execute one process step inside a filter pipeline.

      @param ob_process: Filter-process assignment record.
      @type ob_process: C{dict}
      @param folder: Working folder for temp process artefacts.
      @type folder: C{str}
      @param filename: Current pipeline filename.
      @type filename: C{str}
      @param REQUEST: Active request context.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @return: Updated pipeline filename.
      @rtype: C{str}
      """
      processId = ob_process.get( 'id')
      standard.writeBlock(self,"[execProcessFilter]: processId=%s"%(processId))
      processOb = self.getFilterManager().getProcess(processId)
      if processOb is not None:
        processType = processOb.get( 'type', 'process')
        standard.writeBlock(self,"[execProcessFilter]: processId=%s, processType=%s"%(processId,processType))
        trans = ob_process.get('file')
        # Save transformation to file.
        if trans:
          _fileutil.exportObj( trans, getTransFilename(self, folder, trans))
        if processType in [ 'DTML Method', 'External Method', 'Script (Python)']:
          filename = processMethod(self, processId, filename, trans, REQUEST)
        else:
          filename = processFile(self, processId, filename, trans)
      # Return filename.
      return filename

