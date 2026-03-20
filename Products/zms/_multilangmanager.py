"""
_multilangmanager.py

Defines langdict, MultiLanguageObject for multilingual content management and language-specific variants.
It maps language codes to content variants, handles fallback logic, and manages translations.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from App.Common import package_home
import OFS.misc_
import json
from zope.interface import implementer
# Product Imports.
from Products.zms import _fileutil
from Products.zms import _xmllib
from Products.zms import standard


def _importXml(self, item):
    """Import one language-dictionary row into custom language configuration."""
    key = item['key']
    lang_dict = self.get_lang_dict()
    lang_dict[key] = {}
    for langId in self.getLangIds():
      if langId in item:
        lang_dict[key][langId] = item[langId]
    self.setConfProperty('ZMS.custom.langs.dict', lang_dict.copy())

def importXml(self, xml):
  """Import one or many language-dictionary rows from XML or worksheet XML."""
  if not isinstance(xml, str):
    xml = xml.read()
  value = standard.parseXmlString(xml)
  if value is None:
    value = []
    builder = _xmllib.XmlBuilder()
    nWorkbook = builder.parse(xml)
    for nWorksheet in _xmllib.xmlNodeSet(nWorkbook, 'Worksheet'):
      for nTable in _xmllib.xmlNodeSet(nWorksheet, 'Table'):
        r = 0
        keys = []
        for nRow in _xmllib.xmlNodeSet(nTable, 'Row'):
          c = 0
          for nCell in _xmllib.xmlNodeSet(nRow, 'Cell'):
            for nData in _xmllib.xmlNodeSet(nCell, 'Data'):
              if r == 0:
                if c == 0:
                  key = 'key'
                else:
                  key = nData.get('cdata', '')
                keys.append(key)
              else:
                if c == 0:
                  value.append({})
                value[-1][keys[c]] = nData.get('cdata', '')
              c += 1
          r += 1
  if isinstance(value, list):
    for item in value:
      _importXml( self, item)
  else:
    _importXml( self, value)

def exportXml(self, ids, REQUEST=None, RESPONSE=None):
  """Export selected language-dictionary rows as XML payload."""
  value = []
  d = self.get_lang_dict()
  for id in sorted(d):
    item = d[id].copy()
    item['key'] = id
    if id in ids or len(ids) == 0:
      value.append(item)
  filename = 'export.langdict.xml'
  # Export value with filename.
  content_type = 'text/xml; charset=utf-8'
  processing_instruction = '<?zms version=\'%s\'?>'%(self.zms_version())
  export = self.getXmlHeader() + processing_instruction + standard.toXmlString(self, value, xhtml=True)
  if RESPONSE:
    RESPONSE.setHeader('Content-Type', content_type)
    RESPONSE.setHeader('Content-Disposition', 'attachment;filename="%s"'%filename)
  return export


def getDescLangs(self, id, langs):
  """Return C{(label, id)} tuples for one language and all descendants."""
  obs = []
  # Primary language is always the first item in the sorted list.
  if id == self.getPrimaryLanguage():
    label = '*'
  elif id in langs:
    label = langs[id]['label']
  else:
    label = id
  obs.append((label, id))
  # Iterate descending languages.
  for key in langs.keys():
    if langs[key]['parent'] == id:
      obs.extend(getDescLangs(self, key, langs))
  return obs


class langdict(object):
    """Load and provide access to the built-in ZMI language dictionary."""
    def __init__(self, filename='_language.xml'):
      """Parse the bundled language XML file into manage-language and key mappings."""
      manage_langs = []
      lang_dict = {}
      filepath = package_home(globals())+'/import/'
      xmlfile = open(_fileutil.getOSPath(filepath+filename), 'rb')
      builder = _xmllib.XmlBuilder()
      nWorkbook = builder.parse(xmlfile)
      for nWorksheet in _xmllib.xmlNodeSet(nWorkbook, 'Worksheet'):
        for nTable in _xmllib.xmlNodeSet(nWorksheet, 'Table'):
          for nRow in _xmllib.xmlNodeSet(nTable, 'Row'):
            lRow = []
            currIndex = 0
            for nCell in _xmllib.xmlNodeSet(nRow, 'Cell'):
              ssIndex = int(nCell.get('attrs', {}).get('ss:Index', currIndex+1))
              currData = None
              for i in range(currIndex+1, ssIndex):
                lRow.append(currData)
              for nData in _xmllib.xmlNodeSet(nCell, 'Data'):
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
                      value[manage_langs[i]] = lRow[i+1]
                lang_dict[key] = value
      xmlfile.close()
      self.manage_langs = manage_langs
      self.langdict = lang_dict

    def get_manage_langs(self):
      """Return the list of available ZMI manage languages."""
      return self.manage_langs

    def get_langdict(self):
      """Return the base language-dictionary mapping loaded from XML."""
      return self.langdict


class MultiLanguageObject(object):
    """Language selection helpers for content objects."""
    def getLanguages(self, REQUEST=None):
      """Return language ids available to the current user (primary language first)."""
      value = ['*']
      if REQUEST is not None:
        value = self.getUserLangs(str(REQUEST.get('AUTHENTICATED_USER',None)))
      value = [x for x in [x[0] for x in self.getLangTree()] if ('*' in value) or (x in value)]
      return value


    def getDescendantLanguages(self, id, REQUEST=None, RESPONSE=None):
      """Return descendant language ids below C{id}, optionally as JSON response."""
      obs = []
      user_langs = ['*']
      if REQUEST is not None:
        user_langs = self.getUserLangs(str(REQUEST.get('AUTHENTICATED_USER',None)))
      langs = self.getLangs()
      obs = getDescLangs(self, id, langs)
      if not '*' in user_langs:
        obs = [x for x in obs if x[1] in user_langs]
      obs.sort()
      rtn = [x[1] for x in obs]
      # Return JSON-Response.
      if RESPONSE is not None:
        rtn = self.str_json(rtn)
      return rtn


class MultiLanguageManager(object):
    """Manage content languages and custom language-dictionary entries."""
    def get_manage_langs(self):
      """Return the list of available ZMI manage languages."""
      return OFS.misc_.misc_.zms['langdict'].get_manage_langs()

    def get_manage_lang(self):
      """Return preferred manage-language for the current management request."""
      manage_lang = None
      request = self.REQUEST
      if standard.isManagementInterface(self):
        manage_langs = self.get_manage_langs()
        # get manage_lang from request.form
        if 'manage_lang' in request.form and request.form['manage_lang'] in manage_langs:
          manage_lang = request.form['manage_lang']
          # save manage_lang from request.form in session
          standard.set_session_value(self, 'manage_lang', manage_lang)
        else:
          # get manage_lang from request or session
          manage_lang = request.get('manage_lang', standard.get_session_value(self, 'manage_lang'))
          if manage_lang not in manage_langs:
            # get manage_lang from request.lang
            manage_lang = None
            lang = request.get('lang')
            if lang in self.getLangIds():
              manage_lang = self.getLang(lang).get('manage')
              # save manage_lang from request.lang in session
              standard.set_session_value(self, 'manage_lang', manage_lang)
      # default manage_lang to English
      if manage_lang is None:
        manage_lang = 'eng'
      return manage_lang

    def getZMILangStr(self, key, REQUEST=None, RESPONSE=None):
      """Return translated ZMI label text for the current manage-language."""
      lang_str = self.getLangStr( key, self.get_manage_lang())
      if RESPONSE is not None:
        if REQUEST.get('nocache'):
          RESPONSE.setHeader('Cache-Control', 'no-cache')
          RESPONSE.setHeader('Pragma', 'no-cache')
        else:
          RESPONSE.setHeader('Cache-Control', 'public, max-age=3600')
        RESPONSE.setHeader('Content-Type', 'text/plain; charset=utf-8')
      return lang_str

    def _getLangStr(self, key, lang=None):
      """Resolve one translation value from custom dictionary first, then system fallback."""
      if lang is None:
        lang = standard.nvl(self.REQUEST.get('lang'), self.getPrimaryLanguage())

      # Return custom value.
      d = self.get_lang_dict()
      if key in d and lang in d[key]:
        return d[key][lang]
      
      # Return system value.
      if hasattr(OFS.misc_.misc_,'zms'):
        d = OFS.misc_.misc_.zms['langdict'].get_langdict()
        if key in d:
          if lang not in d[key]:
            lang = 'eng'
          if lang in d[key]:
            return d[key][lang]
      
      return key


    def getLangStr(self, key, lang=None):
      """Public wrapper returning translated string for the given key and language."""
      return self._getLangStr(key,lang)


    def getPrimaryLanguage(self):
      """Return the id of the configured primary content language."""
      return self.language_primary

    def setPrimaryLanguage(self, v):
      """Set the id of the primary content language."""
      self.language_primary = v

    def getLangs(self):
      """Return the configured language metadata mapping."""
      return getattr(self, 'attr_languages', {})

    def setLangs(self, v):
      """Persist the complete language metadata mapping."""
      self.attr_languages = v.copy()

    def getParentLanguage(self, id):
      """Return the parent language id for the given language id."""
      return self.getLang(id).get('parent')

    def getLanguageLabel(self, id):
      """Return the configured display label for the given language id."""
      return self.getLang(id).get('label', id)

    def getParentLanguages(self, id):
      """Return all parent language ids up to the root language."""
      obs = []
      langs = self.getLangs()
      if id not in langs:
        id = self.getPrimaryLanguage()
      parent = id
      while True:
        parent = langs[parent]['parent']
        if parent:
          obs.append(parent)
        else:
          break
      return obs

    def getLang(self, id):
      """Return language metadata for one language id."""
      return self.getLangs().get(id, {})

    def getLangTree(self, base=None):
      """Return depth-first language tree as C{(id, metadata)} tuples."""
      if base is None:
        base = self.getPrimaryLanguage()
      l = [(base, self.getLang(base))]
      for langId in self.getLangIds():
        lang = self.getLang(langId)
        if lang['parent'] == base:
          l.extend(self.getLangTree(langId))
      return l

    def getLangIds(self, sort=False):
      """Return configured language ids, optionally sorted by display label."""
      obs = []
      langs = self.getLangs()
      if sort:
        for key in langs.keys():
          if key == self.getPrimaryLanguage(): 
            label = '*'
          else: 
            label = langs[key]['label']
          obs.append((label, key))
        obs.sort()
        return [x[1] for x in obs]
      return list(langs.keys())

    def getLanguageFromName(self, name): 
      """Extract language suffix from a filename and return matching language id."""
      lang = None
      i = name.rfind('.')
      if i > 0:
        name = name[:i]
        j = name.rfind('_')
        if j > 0:
          suffix = name[j+1:]
          langs = self.getLangIds()
          if suffix in langs:
            lang = suffix
      return lang

    def getLanguage(self, REQUEST): 
      """Resolve request language from parameter, URL suffix, accept-language, or primary."""
      lang = REQUEST.get('lang', None)
      langs = self.getLangIds()
      if lang not in langs:
        url = REQUEST.get('URL')
        path = url
        i = url.rfind('.')
        if i > 0:
          path = url[:i]
        j = path.rfind('_')
        if j > 0:
          suffix = path[j+1:]
          if suffix in langs:
            lang = suffix
      if lang not in langs:
        lang = self.getHttpAcceptLanguage( REQUEST)
      if lang not in langs:
        lang = self.getPrimaryLanguage()
      return lang

    def getHttpAcceptLanguage(self, REQUEST): 
      """Map HTTP accept-language header to one configured language id if enabled."""
      lang = None
      langs = self.getLangIds()
      if self.getConfProperty('ZMS.http_accept_language', 0)==1:
        accept = REQUEST.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept.find( ';') >= 0:
          accept = accept[ : accept.find( ';')]
        m = { 'de' : 'ger', 'en' : 'eng', 'fr' : 'fra', 'ru' : 'rus', 'es' : 'esp', 'it' : 'ita', 'nl' : 'nld', 'sv' : 'swe'}
        for l in accept.split( ','):
          if l.find( '-') > 0:
            l = l[ : l.find( '-')]
          if l in langs:
            lang = l
            break
          elif l in m.keys() and m[ l] in langs:
            lang = m[ l]
            break
      return lang

    def setLanguage(self, lang, label, parent, newManage):
      """Create or update one language entry and update primary/parent links if needed."""
      if len(parent) == 0:
        for id in self.getLangs().keys():
          if id != lang and self.getParentLanguage(id) == '':
            attr_languages = self.getLangs()
            attr_languages[id]['parent'] = lang
            self.setLangs( attr_languages)
        self.setPrimaryLanguage(lang)
      
      #-- Set/Add language.
      attr_languages = self.getLangs()
      attr_languages[lang] = {}
      attr_languages[lang]['label'] = label
      attr_languages[lang]['parent'] = parent
      attr_languages[lang]['manage'] = newManage
      self.setLangs( attr_languages)


    def delLanguage(self, lang):
      """Delete one language entry from the language metadata mapping."""
      attr_languages = self.getLangs()
      del attr_languages[lang]
      self.setLangs( attr_languages)

    def manage_changeLanguages(self, lang, btn, REQUEST, RESPONSE):
      """Handle ZMI language management actions (save/delete) and redirect with message."""

      target = REQUEST.get('target', None)

      # Delete.
      # -------
      if btn == 'BTN_DELETE':
        ids = REQUEST.get('ids', [])
        for id in ids:
          self.delLanguage(id) 
      
      # Change.
      # -------
      elif btn == 'BTN_SAVE':
        # Change available languages.
        for id in self.getLangIds():
          newLabel = REQUEST.get('%s_label'%id).strip()
          newParent = REQUEST.get('%s_parent'%id).strip()
          newManage = REQUEST.get('%s_manage'%id).strip()
          self.setLanguage(id, newLabel, newParent, newManage)
        # Insert new languages
        # Ref: _multilangmanager.py#L647
          for key in REQUEST.form.keys():
            if key.startswith('_lang_id_'):
              i = int(key[len('_lang_id_'):])
              if REQUEST[key]:
                newId = REQUEST[key].strip()
                if newId not in self.getLangIds():
                  newLabel = REQUEST.get('_lang_label_%i'%i).strip()
                  if len(self.getLangIds()) == 0:
                    newParent = ''
                  else:
                    newParent = REQUEST.get('_lang_parent_%i'%i).strip()
                  newManage = REQUEST.get('_lang_manage_%i'%i).strip()
                  self.setLanguage(newId, newLabel, newParent, newManage)

      # Return with message.
      if target=='zmi_manage_tabs_message':
        if btn == 'BTN_DELETE' and ids:
          message = '%s: %s'%(self.getZMILangStr('MSG_DELETED')%len(ids), id)
        else:
          message = self.getZMILangStr('MSG_CHANGED')
        REQUEST.set('manage_tabs_message', message)
        return self.zmi_manage_tabs_message(lang=lang, id=id, extra={}, REQUEST=REQUEST, RESPONSE=RESPONSE)
      else:
        message = standard.url_quote(self.getZMILangStr('MSG_CHANGED'))
        return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_tabs_message=%s'%(lang, message))

    def get_lang_dict(self, REQUEST=None):
      """Return merged language dictionary from master, custom config, and metaobj providers."""
      
      #-- [ReqBuff]: Fetch buffered value from Http-Request.
      reqBuffId = 'MultiLanguageManager.get_lang_dict'
      try: return self.fetchReqBuff(reqBuffId)
      except: pass
      
      #-- Get value.
      d = {}
      portalMaster = self.getPortalMaster()
      if portalMaster is not None:
        lang_dict = portalMaster.get_lang_dict()
        for key in lang_dict:
          d[key] = lang_dict[key].copy()
          lang_ids = lang_dict[key].keys()
          d[key]['acquired'] = standard.concat_list(d[key].get('acquired', []), lang_ids)
      lang_dict = self.getConfProperty('ZMS.custom.langs.dict', {})
      for key in lang_dict:
        if key in d:
          lang_ids = lang_dict[key].keys()
          for lang_id in lang_ids:
            if lang_id not in d[key].get('acquired', []):
              d[key][lang_id] = lang_dict[key][lang_id]
        else:
          d[key] = lang_dict[key].copy()
      
      #-- Get value fron content-objects.
      metaobjAttrId = 'langdict'
      for metaobjId in self.getMetaobjIds():
        if metaobjAttrId in self.getMetaobjAttrIds(metaobjId):
          v = self.evalMetaobjAttr("%s.%s"%(metaobjId,metaobjAttrId))
          if type(v) is not dict:
            from ast import literal_eval
            v = literal_eval(v)
          for key in v:
            d[key] = v[key]
      
      #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
      self.storeReqBuff( reqBuffId, d)
      if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Cache-Control', 'public, max-age=3600')
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
        return json.dumps(d)
      
      return d

    def set_lang_dict(self, d):
      """Persist custom language dictionary and clear request buffer cache."""
      self.clearReqBuff('MultiLanguageManager')
      self.setConfProperty('ZMS.custom.langs.dict', d.copy())

    def getLangDict(self):
      """Return language-dictionary entries as ordered list including their key field."""
      lang_dict = self.get_lang_dict()
      lang_list = []
      keys = sorted(lang_dict)
      for key in keys:
        d = lang_dict[key]
        d['key'] = key
        lang_list.append(d)
      return lang_list

    def manage_changeLangDictProperties(self, lang, btn, REQUEST, RESPONSE=None):
        """Handle ZMI language-dictionary actions (save/delete/import/export)."""
        
        target = REQUEST.get('target', None)

        # Delete.
        # -------
        if btn == 'BTN_DELETE':
          ids = REQUEST.get('ids', [])
          dict = self.get_lang_dict()
          lang_dict = {}
          for id in dict.keys():
            if not id in ids:
              lang_dict[id] = dict[id]
          self.set_lang_dict(lang_dict)
        
        # Change.
        # -------
        elif btn == 'BTN_SAVE':
          d = self.get_lang_dict()
          lang_dict = {}
          for key in d.keys():
            for lang_id in self.getLangIds():
              lang_dict[key] = lang_dict.get(key, {})
              enabled = lang_id not in d[key].get('acquired', [])
              if enabled:
                lang_dict[key][lang_id] = REQUEST['%s_value_%s'%(key, lang_id)].strip()
          # Insert (multiple) new language keys at once.
          # Ref: ZMSMetaobjManager.py#L1294
          for key in REQUEST.form.keys():
            if key.startswith('_lang_dict_key_'):
              i = int(key[len('_lang_dict_key_'):])
              if REQUEST[key]:
                k = REQUEST[key].strip()
                lang_dict[k] = {}
                for key2 in REQUEST.form.keys():
                  if key2.startswith('_lang_dict_value_%i_'%i):
                    lang_id = key2[len('_lang_dict_value_%i_'%i):]
                    lang_dict[k][lang_id] = REQUEST[key2].strip()
          self.set_lang_dict(lang_dict)
        
        # Export.
        # -------
        elif btn == 'BTN_EXPORT':
          ids = REQUEST.get('ids', [])
          return exportXml(self, ids, REQUEST, RESPONSE)
        
        # Import.
        # -------
        elif btn == 'BTN_IMPORT':
          f = REQUEST['file']
          if f:
            filename = f.filename
            importXml(self, xml=f)
          else:
            filename = REQUEST['init']
            self.importConf(filename)
          message = self.getZMILangStr('MSG_IMPORTED')%('<i>%s</i>'%filename)
        
        # Return with message.
        if target=='zmi_manage_tabs_message':
          if btn == 'BTN_DELETE' and ids:
            message = '%s: %s'%(self.getZMILangStr('MSG_DELETED')%len(ids), id)
          else:
            message = self.getZMILangStr('MSG_CHANGED')
          REQUEST.set('manage_tabs_message', message)
          return self.zmi_manage_tabs_message(lang=lang, id=id, extra={}, REQUEST=REQUEST, RESPONSE=RESPONSE)
        else:
          message = standard.url_quote(self.getZMILangStr('MSG_CHANGED'))
          return RESPONSE.redirect('manage_customizeLanguagesForm?lang=%s&manage_tabs_message=%s#langdict'%(lang, message))

