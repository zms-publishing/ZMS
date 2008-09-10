################################################################################
# zmslog.py
#
# $Id: zmslog.py,v 1.2 2004/11/30 20:04:16 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.2 $
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
from Globals import HTMLFile
import logging
import os
import time
import urllib
# Product Imports.
import ZMSItem
import _fileutil


def severity_string(severity, mapping={
    -300: 'TRACE',
    -200: 'DEBUG',
    -100: 'BLATHER',
       0: 'INFO',
     100: 'PROBLEM',
     200: 'ERROR',
     300: 'PANIC',
    }):
    """Convert a severity code to a string."""
    s = mapping.get(int(severity), '')
    return "%s(%s)" % (s, severity)


def log_time():
  """Return a simple time string without spaces suitable for logging."""
  return ("%4.4d-%2.2d-%2.2dT%2.2d:%2.2d:%2.2d"
          % time.localtime()[:6])


################################################################################
###
###   Class
###
################################################################################
class ZMSLog(ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSLog'
    icon = "misc_/zms/ZMSLog.gif"

    # Management Options.
    # -------------------
    manage_options = (
	{ 'label': 'TAB_CONFIGURATION','action': '../manage_customize'},
	)

    # Management Interface.
    # ---------------------
    manage_main = HTMLFile( 'dtml/ZMSLog/manage_main', globals())
    manage_remote = HTMLFile( 'dtml/ZMSLog/manage_remote', globals())

    ############################################################################
    #  ZMSLog.__init__: 
    #
    #  Initialise a new instance of ZMSLog.
    ############################################################################
    def __init__(self, copy_to_stdout=False, logged_entries=[ 'ERROR']):
      self.id = 'zms_log'
      self.entries = []
      self.keep_entries = 20
      self.copy_to_zlog = True
      self.copy_to_stdout = copy_to_stdout
      self.logged_entries = logged_entries

    ############################################################################
    #  ZMSLog.setProperties: 
    #
    #  Set properties.
    ############################################################################
    def setProperties(self, REQUEST, RESPONSE): 
      """ ZMSLog.setProperties """
      self.keep_entries = REQUEST.get( 'keep_entries', 20)
      self.copy_to_zlog = REQUEST.has_key( 'copy_to_zlog')
      self.copy_to_stdout = REQUEST.has_key( 'copy_to_stdout')
      self.logged_entries = REQUEST.get( 'logged_entries', [])
      while len( self.entries) > self.keep_entries:
        self.entries.remove( self.entries[-1])
      return RESPONSE.redirect( REQUEST[ 'HTTP_REFERER'])

    # --------------------------------------------------------------------------
    #  ZMSLog.getLOG:
    # --------------------------------------------------------------------------
    def getLOG(self, REQUEST, RESPONSE): 
      """ ZMSLog.getLOG """
      content_type = 'text/plain; charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      return ''.join( map( lambda x: x+'\n', self.entries))

    # --------------------------------------------------------------------------
    #  ZMSLog.LOG:
    # --------------------------------------------------------------------------
    def LOG(self, severity, info):
      while len( self.entries) > self.keep_entries:
        self.entries.remove( self.entries[-1])
      self.entries.insert( 0 ,log_time() + ' ' + severity_string( severity) + '\n' + info)
      if getattr( self, 'copy_to_zlog', True):
        logging.log( severity, info)
      if getattr( self, 'copy_to_stdout', True):
        print log_time(), severity_string( severity), info

    ############################################################################
    ###
    ###  Remote System
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSLog.getPath
    # --------------------------------------------------------------------------
    def getPath(self, REQUEST): 
      path = SOFTWARE_HOME
      if REQUEST.has_key('path'):
        path = REQUEST['path']
      return path

    # --------------------------------------------------------------------------
    #  ZMSLog.readDir
    # --------------------------------------------------------------------------
    def readDir(self, path): 
      return _fileutil.readDir( path)

    # --------------------------------------------------------------------------
    #  ZMSLog.getParentDir
    # --------------------------------------------------------------------------
    def getParentDir(self, path): 
      return _fileutil.getFilePath( path)


    ############################################################################
    #  ZMSLog.manage_index_html: 
    #
    #  Display file.
    ############################################################################
    def manage_index_html(self, REQUEST, RESPONSE): 
      """ZMSLog.manage_index_html"""
      path = self.getPath( REQUEST)
      RESPONSE.setHeader( 'Content-Type','Unknown')
      RESPONSE.setHeader( 'Content-Disposition','inline;filename=%s'%_fileutil.extractFilename( path))
      file = open( path, 'rb')
      rtn = file.read() 
      file.close()
      return rtn


    ############################################################################
    #  ZMSLog.manage_submit: 
    #
    #  Submit action.
    ############################################################################
    def manage_submit(self, REQUEST, RESPONSE): 
      """ZMSLog.manage_submit"""
      
      path = self.getPath(REQUEST)
      message = ""
      
      if REQUEST.has_key("btn"):
      
        if REQUEST["btn"] == "Delete":
          ids = REQUEST['ids']
          for id in ids:
            _fileutil.remove( id, deep=1)
          message = "%i File(s) deleted."%len(ids)
        
        elif REQUEST["btn"] == "Unzip":
          ids = REQUEST['ids']
          for id in ids:
            _fileutil.unzip(id)
          message = "%i File(s) deleted."%len(ids)
        
        elif REQUEST["btn"] == "Execute":
          command = REQUEST['command']
          _fileutil.executeCommand(path,command)
          message = "Command executed."
          
        elif REQUEST["btn"] == "Upload":
          obj = REQUEST['file']
          type = REQUEST['type']
          filename = "%s%s%s"%(path,os.sep,_fileutil.extractFilename(obj.filename))
          _fileutil.exportObj( obj, filename, type)
          message = "Upload complete."
          
      return REQUEST.RESPONSE.redirect( self.url_append_params( REQUEST[ 'HTTP_REFERER'], { 'manage_tabs_message' :message }))

################################################################################
