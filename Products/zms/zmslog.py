"""
zmslog.py - ZMS Log Viewer

Defines ZMSLog for runtime logging, error reporting, and debugging output.
It writes to application logs, formats diagnostic messages, 
and provides trace-level introspection.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import logging
import os
import time

from Products.zms import standard
from Products.zms import ZMSItem
from Products.zms import _fileutil


def severity_string(severity, mapping={
    logging.DEBUG: 'DEBUG',
    logging.INFO:  'INFO',
    logging.ERROR: 'ERROR',
    }):
    """Convert a severity code to a string."""
    return mapping.get(int(severity), '')


def log_time():
    """Return a compact ISO-like timestamp suitable for log lines."""
    return "%4.4d-%2.2d-%2.2dT%2.2d:%2.2d:%2.2d" % time.localtime()[:6]


class ZMSLog(ZMSItem.ZMSItem):
    """ZMI-accessible log viewer and remote filesystem utility."""

    meta_type = 'ZMSLog'
    zmi_icon = "fas fa-bug"
    icon_clazz = zmi_icon

    def manage_options(self):
      """Return ZMI tabs for this item."""
      return (
        {'label': 'Settings', 'action': '../manage_customize'},
      )

    manage_main = PageTemplateFile('zpt/ZMSLog/manage_main', globals())
    manage_remote = PageTemplateFile('zpt/ZMSLog/manage_remote', globals())

    LOGGER = logging.getLogger("ZMS")

    def __init__(self, copy_to_stdout=False, logged_entries=['ERROR']):
      """Initialize with stdout-mirroring option and active severity list."""
      self.id = 'zms_log'
      self.copy_to_stdout = copy_to_stdout
      self.logged_entries = logged_entries


    def setProperties(self, REQUEST, RESPONSE):
      """Persist logging settings submitted from the ZMI form."""
      self.tail_event_log_linesback = REQUEST.get('tail_event_log_linesback', 100)
      self.copy_to_stdout = 'copy_to_stdout' in REQUEST
      self.logged_entries = REQUEST.get('logged_entries', [])
      return RESPONSE.redirect(REQUEST['HTTP_REFERER'])


    def hasSeverity(self, severity):
      """Return whether the given severity level is currently being logged."""
      return severity_string(severity) in self.logged_entries


    def LOG(self, severity, info):
      """Emit one log record at the given severity and optionally echo to stdout."""
      if severity == logging.DEBUG:
        severity = logging.INFO
      self.LOGGER.log(severity, info)
      if getattr(self, 'copy_to_stdout', True):
        standard.writeStdout(
          self,
          '%s %s(%i) %s' % (str(log_time()), severity_string(severity), int(severity), info)
        )


    def getLOG(self, REQUEST, RESPONSE=None):
      """Stream the active Zope event log file as a plain-text download."""
      filename = self.get_log_filename()
      RESPONSE.setHeader('Content-Type', 'text/plain')
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"' % _fileutil.extractFilename(filename))
      with open(filename, 'r') as f:
        return f.read()


    def tail_event_log(self, linesback=100, returnlist=True):
      """Return the last C{linesback} lines of the active event log."""
      filename = self.get_log_filename()
      return _fileutil.tail_lines(filename, linesback, returnlist)


    def get_log_filename(self):
      """Return the filesystem path of the active Zope event log file."""
      logging_file_handlers = [x for x in logging.root.handlers if isinstance(x, logging.FileHandler)]
      if len(logging_file_handlers) == 0:
        raise RuntimeError('No event log file handler defined in zope.ini ([handler_eventlog])')
      return logging_file_handlers[0].baseFilename


    def getPath(self, REQUEST):
      """Return the filesystem path from the request, defaulting to the package home."""
      path = standard.getPACKAGE_HOME()
      if 'path' in REQUEST:
        path = REQUEST['path']
      return path.strip()


    def readDir(self, path):
      """Return a directory listing for the given filesystem path."""
      return _fileutil.readDir(path)


    def getParentDir(self, path):
      """Return the parent directory component of a filesystem path."""
      return _fileutil.getFilePath(path)


    def manage_index_html(self, REQUEST, RESPONSE):
      """Serve a binary file from the remote filesystem as an inline download."""
      path = self.getPath(REQUEST)
      RESPONSE.setHeader('Content-Type', 'Unknown')
      RESPONSE.setHeader('Content-Disposition', 'inline;filename="%s"' % _fileutil.extractFilename(path))
      with open(path, 'rb') as f:
        return f.read()


    def manage_submit(self, REQUEST, RESPONSE):
      """Handle remote-filesystem actions: execute a shell command or upload a file."""
      path = self.getPath(REQUEST)
      message = ""
      if REQUEST.get("btn") == "Execute":
        command = REQUEST['command']
        _fileutil.executeCommand(path, command)
        message = "Command executed."
      elif REQUEST.get("btn") == "Upload":
        obj = REQUEST['file']
        filename = "%s%s%s" % (path, os.sep, _fileutil.extractFilename(obj.filename))
        _fileutil.exportObj(obj, filename)
        message = "Upload complete."
      return REQUEST.RESPONSE.redirect(
        standard.url_append_params(REQUEST['HTTP_REFERER'], {'manage_tabs_message': message})
      )
