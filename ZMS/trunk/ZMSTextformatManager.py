################################################################################
# ZMSTextformatManager.py
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
from App.Common import package_home
import copy
import os
import urllib
# Product Imports.
import ZMSTextformat


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSTextformatManager:

    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.importTextformatXml
    # --------------------------------------------------------------------------

    def _importTextformatXml(self, item, zms_system=0, createIfNotExists=1):
      id = item['key']
      dict = item['value']
      dict['default'] = dict.get('default',0)
      if id in self.textformats:
        i = self.textformats.index(id)
        self.textformats[i+1] = dict
      else:
        self.textformats.extend([id,dict])
      # Make persistent.
      self.textformats = copy.deepcopy(self.textformats)

    def importTextformatXml(self, xml, REQUEST=None, zms_system=0, createIfNotExists=1):
      if zms_system and not createIfNotExists:
        return
      v = self.parseXmlString(xml)
      if type(v) is list:
        for item in v:
          self._importTextformatXml(item,zms_system,createIfNotExists)
      else:
        self._importTextformatXml(v,zms_system,createIfNotExists)


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.getRichttextFormatIds:
    # --------------------------------------------------------------------------
    def getRichtextFormatIds(self):
      ids = []
      filepath = package_home(globals())+'/plugins/rte/'
      for filename in os.listdir(filepath):
        path = filepath + os.sep + filename
        if os.path.isdir(path):
          ids.append(filename)
      return ids


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.delTextformat:
    # --------------------------------------------------------------------------
    def delTextformat(self, id):
      i = self.textformats.index(id)
      del self.textformats[i]
      del self.textformats[i]
      # Make persistent.
      self.textformats = copy.deepcopy(self.textformats)


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.setTextformat:
    # --------------------------------------------------------------------------
    def setTextformat(self, id, newId, newDisplay, newZMILang, newTag='', newSubtag='', newAttrs='', newRichedit=0):
      if id in self.textformats:
        i = self.textformats.index(id)
      else:
        i = len(self.textformats)
        self.textformats.extend([newId,{'display':{},'default':0}])
      dict = self.textformats[i+1]
      dict['display'][newZMILang] = newDisplay
      dict['tag'] = newTag
      dict['subtag'] = newSubtag
      dict['attrs'] = newAttrs
      dict['richedit'] = newRichedit
      self.textformats[i] = newId
      self.textformats[i+1] = dict
      # Make persistent.
      self.textformats = copy.deepcopy(self.textformats)


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.getTextFormat:
    # --------------------------------------------------------------------------
    def getTextFormat(self, id, REQUEST):
      if id in self.textformats:
        i = self.textformats.index(id)
        return ZMSTextformat.ZMSTextformat(id,self.textformats[i+1],REQUEST)
      return None


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.getTextFormats:
    # --------------------------------------------------------------------------
    def getTextFormats(self, REQUEST):
      l = map( lambda x: ZMSTextformat.ZMSTextformat(self.textformats[x*2],self.textformats[x*2+1],REQUEST), range(len(self.textformats)/2))
      l = map( lambda x: (x.getDisplay(), x), l)
      l.sort()
      return map(lambda x: x[1],l)


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.setDefaultTextformat:
    # --------------------------------------------------------------------------
    def setDefaultTextformat(self, id):
      if len(id) > 0 and id in self.textformats:
        map( lambda x: self.operator_setitem(self.textformats[x*2+1],'default',0), range(len(self.textformats)/2))
        i = self.textformats.index(id)
        self.textformats[i+1]['default'] = 1
        # Make persistent.
        self.textformats = copy.deepcopy(self.textformats)


    # --------------------------------------------------------------------------
    #  ZMSTextformatManager.getTextFormatDefault:
    # --------------------------------------------------------------------------
    def getTextFormatDefault(self):
      if len(self.textformats) == 0:
        return ''
      i = 0
      format_default = filter( lambda x: self.textformats[x*2+1].get('default',0)==1, range(len(self.textformats)/2))
      if len(format_default) == 1:
        i = format_default[0]*2
      elif 'body' in self.textformats:
        i = self.textformats.index('body')
      return self.textformats[i]


    ############################################################################
    #  ZMSTextformatManager.manage_changeTextformat:
    #
    #  Change text-formats.
    ############################################################################
    def manage_changeTextformat(self, lang, REQUEST, RESPONSE): 
      """ ZMSTextformatManager.manage_changeTextformat """
      message = ''
      id = REQUEST.get('id','')
      
      # Change.
      # -------
      if REQUEST['btn'] == self.getZMILangStr('BTN_CHANGE'):
        old_id = REQUEST['id']
        id = REQUEST['new_id'].strip()
        display = REQUEST['new_display'].strip()
        tag = REQUEST['new_tag'].strip()
        subtag = REQUEST['new_subtag'].strip()
        attrs = REQUEST['new_attrs'].strip()
        richedit = REQUEST.get('new_richedit',0)
        self.setTextformat(old_id,id,display,self.get_manage_lang(),tag,subtag,attrs,richedit)
        if REQUEST.has_key('new_default'): 
          self.setDefaultTextformat(REQUEST['new_default'])
        id = ''
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_DELETE'):
        id = REQUEST['id']
        self.delTextformat( id) 
        id = ''
        message = self.getZMILangStr('MSG_DELETED')%int(1)
      
      # Insert.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
        id = REQUEST['_id'].strip()
        display = REQUEST['_display'].strip()
        self.setTextformat(None,id,display,self.get_manage_lang())
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Export.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_EXPORT'):
        value = []
        ids = REQUEST.get('ids',[])
        fmts = self.textformats
        for i in range(len(fmts)/2):
          id = fmts[i*2]
          ob = fmts[i*2+1]
          if id in ids or len(ids) == 0:
            value.append({'key':id,'value':ob})
        if len(value)==1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.textfmt.xml'
        export = self.getXmlHeader() + self.toXmlString(value,1)
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','inline;filename=%s'%filename)
        return export
      
      # Import.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importTextformatXml(xml=f)
        else:
          filename = REQUEST['init']
          createIfNotExists = 1
          self.importConf(filename, REQUEST, createIfNotExists)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_textformats?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
