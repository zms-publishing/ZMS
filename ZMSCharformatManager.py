# -*- coding: utf-8 -*- 
################################################################################
# ZMSCharformatManager.py
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
import ZPublisher.HTTPRequest
import copy
import urllib
# Product Imports.
import standard
import zopeutil
import _blobfields


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSCharformatManager:

    """
    ############################################################################
    #
    #  XML IM/EXPORT
    #
    ############################################################################
    """

    # --------------------------------------------------------------------------
    #  ZMSCharformatManager.importCharformatXml
    # --------------------------------------------------------------------------

    def _importCharformatXml(self, item, createIfNotExists=1):
      if createIfNotExists == 1:
        newId = self.id_quote(item.get('display',''))
        if len(newId) == 0:
          newId = self.getNewId('fmt')
        newId = item.get('id',newId)
        newBtn = item.get('btn','')
        newDisplay = item.get('display','')
        newTag = item.get('tag','')
        newAttrs = item.get('attrs','')
        newJS = item.get('js','')
        self.setCharformat( None, newId, newBtn, newDisplay, newTag, newAttrs, newJS)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)

    def importCharformatXml(self, xml, createIfNotExists=1):
      v = self.parseXmlString(xml)
      if type(v) is list:
        for item in v:
          self._importCharformatXml(item,createIfNotExists)
      else:
        self._importCharformatXml(v,createIfNotExists)


    # --------------------------------------------------------------------------
    #  ZMSCharformatManager.getCharFormats:
    # --------------------------------------------------------------------------
    def getCharFormats(self):
      return self.charformats


    # ------------------------------------------------------------------------------
    #  ZMSCharformatManager.moveCharformat:
    # ------------------------------------------------------------------------------
    def moveCharformat(self, id, pos):
      obs = self.charformats
      charformats = filter( lambda x: x['id'] == id, obs)
      if len(charformats) == 1:
        ob = charformats[0]
        self.charformats.remove(ob)
        self.charformats.insert(pos,ob)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)


    # ------------------------------------------------------------------------------
    #  ZMSCharformatManager.delCharformat:
    # ------------------------------------------------------------------------------
    def delCharformat(self, id):
      obs = self.charformats
      charformats = filter( lambda x: x['id'] == id, obs)
      if len(charformats) > 0:
        ob = charformats[0]
        if ob.get('btn') in self.objectIds():
          self.manage_delObjects(ids=[ob['btn']])
        self.charformats.remove(ob)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)
      return ''


    # ------------------------------------------------------------------------------
    #  ZMSCharformatManager.setCharformat:
    # ------------------------------------------------------------------------------
    def setCharformat(self, oldId, newId, newBtn, newDisplay, newTag='', newAttrs='', newJS=''):
      obs = self.charformats
      if oldId is None:
        oldId = newId
      oldCharformats = filter( lambda x: x['id'] == oldId, obs)
      if len(oldCharformats) > 0:
        i = obs.index( oldCharformats[0])
      else:
        i = len(obs)
        obs.append({})
      ob = obs[i]
      if isinstance( newBtn, _blobfields.MyImage):
        if ob.get('btn') in self.objectIds():
          self.manage_delObjects(ids=[ob['btn']])
        zopeutil.addObject(self, 'Image', id=newBtn.getFilename(), title='', data=newBtn.getData())
        newBtn = newBtn.getFilename()
      else:
        newBtn = ob.get('btn')
      ob['id'] = newId
      ob['btn'] = newBtn
      ob['display'] = newDisplay
      ob['tag'] = newTag
      ob['attrs'] = newAttrs
      ob['js'] = newJS
      # Make persistent.
      self.charformats = copy.deepcopy(self.charformats)
      return newId


    ############################################################################
    #  ZMSCharformatManager.manage_changeCharformat:
    #
    #  Change char-formats.
    ############################################################################
    def manage_changeCharformat(self, lang, REQUEST, RESPONSE):
      """ ZMSCharformatManager.manage_changeCharformat """
      message = ''
      id = REQUEST.get('id','')
      
      # Change.
      # -------
      if REQUEST['btn'] == self.getZMILangStr('BTN_SAVE'):
        newId = REQUEST['new_id'].strip()
        newBtn = REQUEST.get('new_btn','')
        if isinstance(newBtn,ZPublisher.HTTPRequest.FileUpload) and newBtn.filename != '':
          newBtn = _blobfields.createBlobField(self,_blobfields.MyImage,newBtn)
        newDisplay = REQUEST['new_display'].strip()
        newTag = REQUEST['new_tag'].strip()
        newAttrs = REQUEST['new_attrs'].strip()
        newJS = REQUEST['new_js'].strip()
        id = self.setCharformat(id,newId,newBtn,newDisplay,newTag,newAttrs,newJS)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif REQUEST['btn'] in [ self.getZMILangStr('BTN_DELETE'), 'delete']:
        if id:
          ids = [id]
        else:
          ids = REQUEST.get('ids',[])
        for id in ids:
          self.delCharformat(id) 
        id = ''
        message = self.getZMILangStr('MSG_DELETED')%len(ids)
      
      # Insert.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_INSERT'):
        fmts = self.getCharFormats()
        newId = REQUEST['_id'].strip()
        newBtn = REQUEST.get('_btn','')
        if isinstance(newBtn,ZPublisher.HTTPRequest.FileUpload) and newBtn.filename != '':
          newBtn = _blobfields.createBlobField(self,_blobfields.MyImage,newBtn)
        newDisplay = REQUEST['_display'].strip()
        id = self.setCharformat(None,newId,newBtn,newDisplay)
        message = self.getZMILangStr('MSG_INSERTED')%id
      
      # Export.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_EXPORT'):
        ids = REQUEST.get('ids',[])
        value = filter( lambda x: x['id'] in ids or len(ids) == 0, self.getCharFormats())
        value = map( lambda x: x.copy(), value)
        for x in value:
          if x.get('btn'):
            x['btn'] = _blobfields.createBlobField( self, _blobfields.MyImage, file={'data':getattr( self, x.get('btn')).data,'filename':x.get('btn')})
        if len(value)==1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.charfmt.xml'
        export = self.getXmlHeader() + self.toXmlString(value,1)
        RESPONSE.setHeader('Content-Type',content_type)
        RESPONSE.setHeader('Content-Disposition','attachment;filename="%s"'%filename)
        return export
      
      # Import.
      # -------
      elif REQUEST['btn'] == self.getZMILangStr('BTN_IMPORT'):
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importCharformatXml(xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename, createIfNotExists=1)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Move to.
      # --------
      elif REQUEST['btn'] == 'move_to':
        pos = REQUEST['pos']
        id = int(id)
        self.moveCharformat( self, id, pos)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%str(id)),(pos+1))
        id = ''
      
      # Return with message.
      message = urllib.quote(message)
      return RESPONSE.redirect('manage_charformats?lang=%s&manage_tabs_message=%s&id=%s'%(lang,message,id))

################################################################################
