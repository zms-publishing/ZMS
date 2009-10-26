################################################################################
# _ftpmanager.py
#
# $Id: _ftpmanager.py,v 1.3 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.3 $
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
from App.special_dtml import HTMLFile
import urllib
import ftplib
import tempfile
import time
import os
import stat
# Product Imports.
import _fileutil
import _globals


# ------------------------------------------------------------------------------
#  _ftpmanager.recurse_Local:
# ------------------------------------------------------------------------------
def recurse_Local(ftp, remoteFolder='', localFolder='', sPath=''):
  for sFile in os.listdir(localFolder+sPath+'/'):
    fStat = os.stat(localFolder+sPath+'/'+sFile)
    fSize = fStat[stat.ST_SIZE]
    fMode = fStat[stat.ST_MODE]
    if stat.S_ISDIR(fMode):
      # Change to new directory (if it does not exist it will be created).
      ftpCwd(ftp,remoteFolder+sPath,sFile)
      # Recurse.
      recurse_Local(ftp,remoteFolder,localFolder,sPath+'/'+sFile)
      # Change back to current directory.
      ftp.cwd(remoteFolder+sPath+'/')
    else:
      # Delete existing file.
      try:
        ftp.delete(sFile)
      except: pass
      # Create new file.
      try:
        file = open(localFolder+sPath+'/'+sFile,'rb')
        ftp.storbinary('STOR %s'%sFile,file,fSize)
        file.close()
      except: pass


# ------------------------------------------------------------------------------
#  _ftpmanager.ftpCwd:
#	
#  Change work directory on ftp-host.
# ------------------------------------------------------------------------------
def ftpCwd(ftp, path, dir):
  # Change to new directory.
  try:
    ftp.cwd(path + '/' + dir)
  # Create new directory.
  except:
    try:
      ftp.mkd(dir)
    except:
      pass
    ftp.cwd(path + '/' + dir)


# ------------------------------------------------------------------------------
#  _ftpmanager.ftpToProvider:
# ------------------------------------------------------------------------------
def ftpToProvider(self, lang, REQUEST, RESPONSE):
    message = ''
    
    # Profile time.
    tStart = time.time()
    
    # Create temporary local-folder.
    tempfolder = tempfile.mktemp()
    ressources = self.exportRessources( tempfolder, REQUEST, from_content=self.getLevel() == 0, from_zms=True, from_home=True)
    
    # Download HTML-pages (to temporary local-folder).
    for lang in self.getLangIds():
      REQUEST.set( 'ZMS_HTML_EXPORT' ,1)
      REQUEST.set( 'lang' ,lang)
      REQUEST.set( 'preview' ,None)
      self.recurse_downloadHtmlPages( self, tempfolder, lang, REQUEST)
    
    # Connect to FTP-server.
    # ----------------------
    dctFtp = self.getFtp(REQUEST)
    try:
      ftp = ftplib.FTP(dctFtp['site'])
      ftp.set_debuglevel(1) # 0=no, 1=moderate, 2=maximum debugging output
      ftp.login(dctFtp['userid'],dctFtp['password'])
      ftpCwd(ftp,'',dctFtp['path'])
      recurse_Local(ftp,dctFtp['path'],tempfolder)
      message += ftp.getwelcome()+'<br/>'
      ftp.quit()
      
    except:
      message += _globals.writeError(self,"[_ftpmanager.ftpToProvider]:")+'<br/>'
    
    # Remove temporary local-folder.
    _fileutil.remove(tempfolder,deep=1)
    
    # Return with message.
    message += self.getZMILangStr('MSG_EXPORTED')%('%s <b>%s</b> in %d sec.'%(self.display_type(REQUEST),dctFtp['site']+dctFtp['path'],(time.time()-tStart)))
    return message


################################################################################
################################################################################
###
###   class FtpManager
###
################################################################################
################################################################################
class FtpManager: 

    # Management Interface.
    # ---------------------
    manage_importexportFtp = HTMLFile('dtml/ZMSContainerObject/manage_importexportftp', globals()) 


    # --------------------------------------------------------------------------
    #  FtpManager.getFtp: 
    #
    #  Get parameters of FTP access to provider.
    # --------------------------------------------------------------------------
    def getFtp(self, REQUEST): 
      if getattr(self,'attr_provider_ftp_site','') and \
      	 getattr(self,'attr_provider_ftp_userid','') and \
      	 getattr(self,'attr_provider_ftp_password',''):
        rtn = {}
        rtn['site'] = getattr(self,'attr_provider_ftp_site','')
        rtn['path'] = getattr(self,'attr_provider_ftp_path','')
        rtn['userid'] = getattr(self,'attr_provider_ftp_userid','')
        rtn['password'] = getattr(self,'attr_provider_ftp_password','')
        return rtn
      return None         

    ############################################################################
    # FtpManager.manage_customizeFtp: 
    #
    # Change parameters of FTP access to provider.
    ############################################################################
    def manage_customizeFtp(self, btn, lang, REQUEST, RESPONSE):
      """ FtpManager.manage_customizeFtp """
      
      message = ''
      
      # Change.
      # -------
      self.attr_provider_ftp_site = REQUEST.form.get('site')
      self.attr_provider_ftp_path = REQUEST.form.get('path')
      self.attr_provider_ftp_userid = REQUEST.form.get('userid')
      self.attr_provider_ftp_password = REQUEST.form.get('password')
      message = self.getZMILangStr('MSG_CHANGED')
      
      # Ping.
      # -----
      if btn == self.getZMILangStr('BTN_PING'):
        try:
          # Profile time.
          tStart = time.time()
          ftp = ftplib.FTP(self.attr_provider_ftp_site)
          ftp.set_debuglevel(1) # moderate output
          ftp.login(self.attr_provider_ftp_userid,self.attr_provider_ftp_password)
          message = '%s%s<br/>'%(message,ftp.getwelcome())
          ftp.quit()
          message = 'Ping in %d sec.'%(time.time()-tStart)
        except:
          message = _globals.writeError(self,"[manage_customizeFtp]:")
      
      # Export.
      # -------
      if btn == self.getZMILangStr('BTN_EXPORT'):
        REQUEST.set( 'site', None )
        REQUEST.set( 'path', None )
        REQUEST.set( 'userid', None )
        REQUEST.set( 'password', None )
        message = ftpToProvider(self,lang,REQUEST,RESPONSE)
      
      # Return with message.
      return REQUEST.RESPONSE.redirect('manage_importexportFtp?lang=%s&manage_tabs_message=%s'%(lang,urllib.quote(message)))

################################################################################
