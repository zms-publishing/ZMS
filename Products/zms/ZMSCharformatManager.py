"""
ZMSCharformatManager.py

ZMS support for zmscharformat manager.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
import copy
# Product Imports.
from Products.zms import standard


class ZMSCharformatManager(object):
    """
    Manages character formats (charformats) for ZMS rich-text editing,
    including XML import/export, CRUD operations, and reordering.
    """

    def _importCharformatXml(self, item):
        """Import a single character format definition from parsed XML data.

        @param item: Parsed character format description.
        @type item: C{dict}
        """
        newId = standard.id_quote(item.get('display', ''))
        if len(newId) == 0:
          newId = self.getNewId('fmt')
        newId = item.get('id', newId)
        newIconClazz = item.get('icon_clazz', '')
        newDisplay = item.get('display', '')
        newTag = item.get('tag', '')
        newAttrs = item.get('attrs', '')
        newJS = item.get('js', '')
        self.setCharformat( None, newId, newIconClazz, newDisplay, newTag, newAttrs, newJS)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)


    def importCharformatXml(self, xml):
      """Import one or more character formats from XML data.

      @param xml: XML string or uploaded file-like object.
      @type xml: C{str}
      """
      v = standard.parseXmlString(xml)
      if isinstance(v, list):
        for item in v:
          self._importCharformatXml(item)
      else:
        self._importCharformatXml(v)


    def getCharFormats(self):
      """Return the configured character format definitions.

      @return: Character format definitions.
      @rtype: C{list}
      """
      return self.charformats


    def moveCharformat(self, id, pos):
      """Move a character format to another list position.

      @param id: Character format identifier.
      @type id: C{str}
      @param pos: Target list position.
      @type pos: C{int}
      """
      obs = self.charformats
      charformats = [x for x in obs if x['id'] == id]
      if len(charformats) == 1:
        ob = charformats[0]
        self.charformats.remove(ob)
        self.charformats.insert(pos, ob)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)


    def delCharformat(self, id):
      """Delete a character format by id.

      @param id: Character format identifier.
      @type id: C{str}
      @return: Empty string for legacy callers.
      @rtype: C{str}
      """
      obs = self.charformats
      charformats = [x for x in obs if x['id'] == id]
      if len(charformats) > 0:
        ob = charformats[0]
        self.charformats.remove(ob)
        # Make persistent.
        self.charformats = copy.deepcopy(self.charformats)
      return ''


    def setCharformat(self, oldId, newId, newIconClazz, newDisplay, newTag='', newAttrs='', newJS=''):
      """Create or update a character format definition.

      @param oldId: Existing character format id to replace.
      @type oldId: C{str}
      @param newId: Target character format id.
      @type newId: C{str}
      @param newIconClazz: Icon CSS class.
      @type newIconClazz: C{str}
      @param newDisplay: Display label.
      @type newDisplay: C{str}
      @param newTag: HTML tag wrapper.
      @type newTag: C{str}
      @param newAttrs: HTML attributes.
      @type newAttrs: C{str}
      @param newJS: Client-side JavaScript hook.
      @type newJS: C{str}
      @return: The persisted character format id.
      @rtype: C{str}
      """
      obs = self.charformats
      if oldId is None:
        oldId = newId
      oldCharformats = [x for x in obs if x['id'] == oldId]
      if len(oldCharformats) > 0:
        i = obs.index( oldCharformats[0])
      else:
        i = len(obs)
        obs.append({})
      ob = obs[i]
      ob['id'] = newId
      ob['icon_clazz'] = newIconClazz
      ob['display'] = newDisplay
      ob['tag'] = newTag
      ob['attrs'] = newAttrs
      ob['js'] = newJS
      # Make persistent.
      self.charformats = copy.deepcopy(self.charformats)
      return newId


    def manage_changeCharformat(self, lang, btn, REQUEST, RESPONSE):
      """Handle ZMI actions for creating, editing, and deleting char formats.

      @param lang: Active UI language.
      @type lang: C{str}
      @param btn: Submitted button id.
      @type btn: C{str}
      @param REQUEST: The active HTTP request.
      @type REQUEST: C{ZPublisher.HTTPRequest}
      @param RESPONSE: The active HTTP response.
      @type RESPONSE: C{ZPublisher.HTTPResponse}
      @return: Redirect response or XML export payload.
      @rtype: C{object}
      """
      message = ''
      id = REQUEST.get('id', '')
      target = REQUEST.get('target', None)
      
      # Change.
      # -------
      if btn == 'BTN_SAVE':
        newId = REQUEST['new_id'].strip()
        newIconClazz = REQUEST.get('new_icon_clazz', '')
        newDisplay = REQUEST['new_display'].strip()
        newTag = REQUEST['new_tag'].strip()
        newAttrs = REQUEST['new_attrs'].strip()
        newJS = REQUEST['new_js'].strip()
        id = self.setCharformat(id, newId, newIconClazz, newDisplay, newTag, newAttrs, newJS)
        message = self.getZMILangStr('MSG_CHANGED')
      
      # Delete.
      # -------
      elif btn == 'BTN_DELETE':
        if id:
          ids = [id]
        else:
          ids = REQUEST.get('ids', [])
        for id in ids:
          self.delCharformat(id) 
        id = ''
        message = self.getZMILangStr('MSG_DELETED')%len(ids)
      
      # Insert.
      # -------
      elif btn == 'BTN_INSERT':
        fmts = self.getCharFormats()
        newId = REQUEST['_id'].strip()
        newIconClazz = REQUEST.get('_icon_clazz', '')
        newDisplay = REQUEST['_display'].strip()
        id = self.setCharformat(None, newId, newIconClazz, newDisplay)
        message = self.getZMILangStr('MSG_INSERTED')%id
      
      # Export.
      # -------
      elif btn == 'BTN_EXPORT':
        ids = REQUEST.get('ids', [])
        value = [x.copy() for x in self.getCharFormats() if x['id'] in ids or len(ids) == 0]
        if len(value)==1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.charfmt.xml'
        export = self.getXmlHeader() + self.toXmlString(value, 1)
        RESPONSE.setHeader('Content-Type', content_type)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename="%s"'%filename)
        return export
      
      # Import.
      # -------
      elif btn == 'BTN_IMPORT':
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importCharformatXml(xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename)
        message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
      
      # Move to.
      # --------
      elif btn == 'move_to':
        pos = REQUEST['pos']
        id = int(id)
        self.moveCharformat( self, id, pos)
        message = self.getZMILangStr('MSG_MOVEDOBJTOPOS')%(("<i>%s</i>"%str(id)), (pos+1))
        id = ''
      
      # Return with message.
      if target=='zmi_manage_tabs_message' and btn == 'BTN_DELETE' and ids:
        message = '%s: %s'%(self.getZMILangStr('MSG_DELETED')%len(ids), id)
        REQUEST.set('manage_tabs_message', message)
        return self.zmi_manage_tabs_message(lang=lang, id=id, extra={}, REQUEST=REQUEST, RESPONSE=RESPONSE)
      else:
        message = standard.url_quote(message)
        return RESPONSE.redirect('manage_charformats?lang=%s&manage_tabs_message=%s&id=%s'%(lang, message, id))

