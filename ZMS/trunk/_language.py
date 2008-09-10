################################################################################
# _language.py
#
# $Id: _language.py,v 1.12 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.12 $
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
# Product Imports.
import _fileutil
import _globals


################################################################################
################################################################################
###
###   class Language:
###
################################################################################
################################################################################
class Language:
    
    dctLangStr = {}
    lstManageLangStr = []

    # --------------------------------------------------------------------------
    #  Language.getManageLanguages:
    # --------------------------------------------------------------------------
    def getManageLanguages(self):
      if len(self.lstManageLangStr) == 0:
        self.initLangStr()
      return self.lstManageLangStr


    # --------------------------------------------------------------------------
    #  Language.initLangStr:
    # --------------------------------------------------------------------------
    def initLangStr(self, filename='_language.xml'):
      """ Language.initLangStr """
      manage_langs = []
      lang_strs = {}
      filepath = package_home(globals())+'/import/'
      xmlfile = open(_fileutil.getOSPath(filepath+filename),'rb')
      nWorkbook = self.xmlParse(xmlfile)
      for nWorksheet in self.xmlNodeSet(nWorkbook,'Worksheet'):
        for nTable in self.xmlNodeSet(nWorksheet,'Table'):
          for nRow in self.xmlNodeSet(nTable,'Row'):
            lRow = []
            currIndex = 0
            for nCell in self.xmlNodeSet(nRow,'Cell'):
              ssIndex = int(nCell.get('attrs',{}).get('ss:Index',currIndex+1))
              currData = None
              for i in range(currIndex+1,ssIndex):
                lRow.append(currData)
              for nData in self.xmlNodeSet(nCell,'Data'):
                currData = nData['cdata']
              lRow.append(currData)
              currIndex = ssIndex
            if len(manage_langs) == 0:
              del lRow[0]
              manage_langs = lRow
            else:
              if len(lRow) > 0:
                key = lRow[0]
                value = {}
                for i in range(len(manage_langs)):
                  if i+1 < len(lRow):
                    if lRow[i+1] is not None:
                      value[manage_langs[i]] = lRow[i+1] # unicode(lRow[i+1],'utf-8').encode('utf-8')
                lang_strs[key] = value
      xmlfile.close()
      self.lstManageLangStr = manage_langs
      self.dctLangStr = lang_strs


    # --------------------------------------------------------------------------
    #  Language.get_manage_lang:
    # --------------------------------------------------------------------------
    def get_manage_lang(self):
      manage_lang = None
      req = getattr( self, 'REQUEST', None)
      if req is not None:
        sess = getattr( req, 'SESSION', None)
        if sess is not None:
          if req.form.has_key('reset_manage_lang'):
            sess.set('manage_lang',None)
          manage_lang = sess.get('manage_lang')
        if manage_lang is None:
          lang = req.get('lang')
          if lang is not None:
            manage_lang = self.getManageLanguage( lang)
      if manage_lang is None:
        manage_lang = 'eng'
      return manage_lang


    # --------------------------------------------------------------------------
    #  Language.getZMILangStr:
    # --------------------------------------------------------------------------
    def getZMILangStr(self, key):
      return self.getLangStr( key, self.get_manage_lang())


    # --------------------------------------------------------------------------
    #  Language.getLangStr:
    # --------------------------------------------------------------------------
    def getLangStr(self, key, lang=None):
      # language
      if lang is None:
        try:
          lang = self.getPrimaryLanguage()
        except:
          lang = 'eng'
      
      # Return custom value.
      try:
        #-- [ReqBuff]: Buffered value in Http-Request.
        try:
          value = self.fetchReqBuff( 'get_lang_dict', self.REQUEST, forced=True)
        except:
          value = self.storeReqBuff( 'get_lang_dict', self.get_lang_dict(), self.REQUEST)
        dict = value
        if dict.has_key(key):
          if dict[key].has_key(lang):
            return dict[key][lang]
      except:
        pass
      
      # Return system value.
      if len(self.dctLangStr.keys()) == 0:
        self.initLangStr()
      if self.dctLangStr.has_key(key):
        if not self.dctLangStr[key].has_key(lang):
          lang = 'eng'
        return self.dctLangStr[key][lang]
      
      return key

################################################################################
