"""
ZMSTextformatManager.py

Defines ZMSTextformatManager for text content formatting and rendering.
It applies format-specific conversion, escaping, and transformation rules to content at display time.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
import copy

from Products.zms import ZMSTextformat
from Products.zms import standard


class ZMSTextformatManager(object):
    """Manage block text formats used by rich-text editing and export/import."""

    def _importTextformatXml(self, item):
      """Import a single serialized text-format entry into C{self.textformats}."""
      id = item['key']
      dict = item['value']
      dict['default'] = dict.get('default', 0)
      if id in self.textformats:
        i = self.textformats.index(id)
        self.textformats[i + 1] = dict
      else:
        self.textformats.extend([id, dict])
      self.textformats = copy.deepcopy(self.textformats)


    def importTextformatXml(self, xml):
      """Import one or many text-format records from XML content."""
      v = standard.parseXmlString(xml)
      if isinstance(v, list):
        for item in v:
          self._importTextformatXml(item)
      else:
        self._importTextformatXml(v)


    def delTextformat(self, id):
      """Remove one text format by id and persist the resulting list."""
      i = self.textformats.index(id)
      del self.textformats[i]
      del self.textformats[i]
      self.textformats = copy.deepcopy(self.textformats)


    def setTextformat(self, id, newId, newDisplay, newZMILang, newTag='', newSubtag='', newAttrs='', newRichedit=0, newUsage=[]):
      """Create or update one text-format definition."""
      if id in self.textformats:
        i = self.textformats.index(id)
      else:
        i = len(self.textformats)
        self.textformats.extend([newId, {'display': {}, 'default': 0}])
      dict = self.textformats[i + 1]
      dict['display'][newZMILang] = newDisplay
      dict['tag'] = newTag
      dict['subtag'] = newSubtag
      dict['attrs'] = newAttrs
      dict['richedit'] = newRichedit
      dict['usage'] = newUsage
      self.textformats[i] = newId
      self.textformats[i + 1] = dict
      self.textformats = copy.deepcopy(self.textformats)


    def getTextFormat(self, id, REQUEST):
      """Return one C{ZMSTextformat} wrapper for the given format id."""
      if id in self.textformats:
        i = self.textformats.index(id)
        d = self.textformats[i + 1]
        manage_lang = self.get_manage_lang()
        return ZMSTextformat.ZMSTextformat(id, d, manage_lang)
      return None


    def getTextFormats(self, REQUEST):
      """Return all configured text formats sorted by display label."""
      l = [self.getTextFormat(self.textformats[x * 2], REQUEST) for x in range(len(self.textformats) // 2)]
      return sorted(l, key=lambda x: x.getDisplay())


    def setDefaultTextformat(self, id):
      """Mark the given text-format id as default and clear previous defaults."""
      if len(id) > 0 and id in self.textformats:
        [self.operator_setitem(self.textformats[x * 2 + 1], 'default', 0) for x in range(len(self.textformats) // 2)]
        i = self.textformats.index(id)
        self.textformats[i + 1]['default'] = 1
        self.textformats = copy.deepcopy(self.textformats)


    def getTextFormatDefault(self):
      """Return the default text-format id, falling back to the first or C{body}."""
      if len(self.textformats) == 0:
        return ''
      i = 0
      format_default = [x for x in range(len(self.textformats) // 2) if self.textformats[x * 2 + 1].get('default', 0) == 1]
      if len(format_default) == 1:
        i = format_default[0] * 2
      elif 'body' in self.textformats:
        i = self.textformats.index('body')
      return self.textformats[i]


    def manage_changeTextformat(self, lang, btn, REQUEST, RESPONSE):
      """Handle add/edit/delete/import/export actions for text-format entries."""
      message = ''
      id = REQUEST.get('id', '')
      target = REQUEST.get('target', None)

      if btn == 'BTN_SAVE':
        old_id = REQUEST['id']
        id = REQUEST['new_id'].strip()
        display = REQUEST['new_display'].strip()
        tag = REQUEST['new_tag'].strip()
        subtag = REQUEST['new_subtag'].strip()
        attrs = REQUEST['new_attrs'].strip()
        richedit = REQUEST.get('new_richedit', 0)
        usage = REQUEST.get('new_usage', [])
        self.setTextformat(old_id, id, display, self.get_manage_lang(), tag, subtag, attrs, richedit, usage)
        if 'new_default' in REQUEST:
          self.setDefaultTextformat(id)
        id = ''
        message = self.getZMILangStr('MSG_CHANGED')

      elif btn == 'BTN_DELETE':
        if id:
          ids = [id]
        else:
          ids = REQUEST.get('ids', [])
        for id in ids:
          self.delTextformat(id)
        id = ''
        message = self.getZMILangStr('MSG_DELETED') % len(ids)

      elif btn == 'BTN_INSERT':
        id = REQUEST['_id'].strip()
        display = REQUEST['_display'].strip()
        self.setTextformat(None, id, display, self.get_manage_lang())
        message = self.getZMILangStr('MSG_CHANGED')

      elif btn == 'BTN_EXPORT':
        value = []
        ids = REQUEST.get('ids', [])
        fmts = self.textformats
        for i in range(len(fmts) // 2):
          id = fmts[i * 2]
          ob = fmts[i * 2 + 1]
          if id in ids or len(ids) == 0:
            value.append({'key': id, 'value': ob})
        if len(value) == 1:
          value = value[0]
        content_type = 'text/xml; charset=utf-8'
        filename = 'export.textfmt.xml'
        export = self.getXmlHeader() + self.toXmlString(value, 1)
        RESPONSE.setHeader('Content-Type', content_type)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename="%s"' % filename)
        return export

      elif btn == 'BTN_IMPORT':
        f = REQUEST['file']
        if f:
          filename = f.filename
          self.importTextformatXml(xml=f)
        else:
          filename = REQUEST['init']
          self.importConf(filename)
        message = self.getZMILangStr('MSG_IMPORTED') % ('<i>%s</i>' % filename)

      if target == 'zmi_manage_tabs_message' and btn == 'BTN_DELETE' and ids:
        message = '%s: %s' % (self.getZMILangStr('MSG_DELETED') % len(ids), id)
        REQUEST.set('manage_tabs_message', message)
        return self.zmi_manage_tabs_message(lang=lang, id=id, extra={}, REQUEST=REQUEST, RESPONSE=RESPONSE)
      else:
        if RESPONSE:
          message = standard.url_quote(message)
          return RESPONSE.redirect('manage_textformats?lang=%s&manage_tabs_message=%s&id=%s' % (lang, message, id))

        return message
