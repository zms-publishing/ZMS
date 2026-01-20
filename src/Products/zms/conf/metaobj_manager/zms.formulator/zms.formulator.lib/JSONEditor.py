################################################################################
#
#  Copyright (c) 2019 HOFFMANN+LIEBENBERG in association with SNTL Publishing
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import json
import os
import Products.zms.standard as standard


def JSONEditor(self, obj):
  return JSONEditor_class(obj)


class JSONEditor_class:
  
  def __init__(self, obj):
    
    self.JSONDict                = {}
    self.JSONDict['id']          = obj.titlealt.upper()
    self.JSONDict['title']       = obj.title
    self.JSONDict['type']        = 'object'
    self.JSONDict['properties']  = {}
    self.mandatory_validators    = ''
  
    mattach = False
    
    for i, item in enumerate(obj.items, start=1):
      
      if item.meta_id == 'ZMSTextarea':
        
        var = 'TEXTAREA_%s'%(item.eid)
        
        self.JSONDict['properties'][var]                   = {}
        self.JSONDict['properties'][var]['type']           = 'string'
        self.JSONDict['properties'][var]['format']         = 'text'
        self.JSONDict['properties'][var]['description']    = item.bodycontent
        self.JSONDict['properties'][var]['propertyOrder']  = i
      
      elif item.meta_id == 'ZMSFormulatorItem':
      
        if item.type == 'mailattachment' and mattach:
          continue
        
        var = '%s'%(item.titlealt.upper())
        values = item.select.strip().splitlines()
        
        self.JSONDict['properties'][var]                     = {}
        self.JSONDict['properties'][var]['type']             = item.type == 'float' and 'number' or item.type == 'mailattachment' and 'object' or item.type
        self.JSONDict['properties'][var]['title']            = item.title + (item.mandatory and ' *' or '')
        self.JSONDict['properties'][var]['description']      = item.description + (item.type == 'multiselect' and obj.this.getLangStr('zms.formulator.lib.HINT_MULTISELECT',obj.this.REQUEST.get('lang')) or '')
        self.JSONDict['properties'][var]['propertyOrder']    = i
        self.JSONDict['properties'][var]['options']          = {}
        
        if item.default.strip() != '':
          self.JSONDict['properties'][var]['default']        = item.default 
    
        if item.minimum>0 or item.mandatory:
          if item.type in ['string', 'textarea', 'email']:
            self.JSONDict['properties'][var]['minLength']    = item.minimum > 0 and item.minimum or 1
          elif item.type in ['integer']:
            self.mandatory_validators += """
              if(path==="root.%s") {
                  if (Number.isInteger(ZMSFormulator.getValue().%s)) {
                    errors = [];
                  }
              }
              """%(item.titlealt.upper(), item.titlealt.upper())
          elif item.type in ['date', 'checkbox', 'multiselect']:
            self.mandatory_validators += """
              if(path==="root.%s") {
                  if (ZMSFormulator.getValue().%s==='' || ZMSFormulator.getValue().%s.length===0) {
                    errors.push({
                      path: path,
                      property: 'format',
                      message: 'check_%s' in JSONEditor.defaults.languages.%s ? JSONEditor.defaults.translate('check_%s') : JSONEditor.defaults.translate('error_mandatory')
                    });   
                  }
              }
              """%(item.titlealt.upper(), item.titlealt.upper(), item.titlealt.upper(),
                   item.titlealt.lower(), obj.this.REQUEST.get('lang'), item.titlealt.lower())
          else:
            self.JSONDict['properties'][var]['minimum']      = item.minimum > 0 and item.minimum or 1
    
        if item.maximum>0:
          if item.type in ['string', 'textarea']:
            self.JSONDict['properties'][var]['maxLength']    = item.maximum
          else:
            self.JSONDict['properties'][var]['maximum']      = item.maximum
        
        if item.type == 'select':
          self.JSONDict['properties'][var]['type']           = 'string'
          self.JSONDict['properties'][var]['enum']           = []
          self.JSONDict['properties'][var]['options']['enum_titles'] = []
          if len(values)>0:
            if not item.mandatory:
              self.JSONDict['properties'][var]['enum'].append('')
            for val in values:
              self.JSONDict['properties'][var]['enum'].append(val)
            if not item.mandatory:
              self.JSONDict['properties'][var]['options']['enum_titles'].append(obj.this.getLangStr('CAPTION_SELECT'))
            for val in values:
              self.JSONDict['properties'][var]['options']['enum_titles'].append(val)
        
        if item.type == 'textarea':
          self.JSONDict['properties'][var]['type']           = 'string'
          self.JSONDict['properties'][var]['format']         = 'textarea'
          self.JSONDict['properties'][var]['options']['input_height']  = '150px'
        
        if item.type == 'color':
          self.JSONDict['properties'][var]['type']           = 'string'
          self.JSONDict['properties'][var]['format']         = 'color'
    
        if item.type == 'date':
          self.JSONDict['properties'][var]['type']           = 'string'
          self.JSONDict['properties'][var]['format']         = 'date'
  
        if item.type == 'email':
          self.JSONDict['properties'][var]['type']           = 'string'
          self.JSONDict['properties'][var]['format']         = 'email'
          #self.JSONDict['properties'][var]['pattern']        = '^([a-zA-Z0-9_.+-])+\\@(([a-zA-Z0-9-])+\\.)+([a-zA-Z0-9]{2,4})+$'        
  
        if item.type == 'mailattachment':
          # TODO: just one mailattachment-item per form is supported - see line 50
          mattach = True
          self.JSONDict['properties'][var]['properties']     = {}
          self.JSONDict['properties'][var]['properties']['FILEDATA'] = {}
          self.JSONDict['properties'][var]['properties']['FILEDATA']['type']  = 'string'
          self.JSONDict['properties'][var]['properties']['FILEDATA']['title'] = item.title
          self.JSONDict['properties'][var]['properties']['FILEDATA']['format'] = 'mailattachment'
          self.JSONDict['properties'][var]['properties']['FILEDATA']['media'] = {'binaryEncoding': 'base64'}
          self.JSONDict['properties'][var]['properties']['FILENAME'] = {}
          self.JSONDict['properties'][var]['properties']['FILENAME']['type']  = 'string'
          self.JSONDict['properties'][var]['properties']['FILENAME']['options'] = {'hidden': True}       
          
        if item.type in ['checkbox', 'multiselect']:
          self.JSONDict['properties'][var]['type']           = 'array'
          self.JSONDict['properties'][var]['uniqueItems']    = 'true'
          if item.type == 'multiselect':
            self.JSONDict['properties'][var]['format']       = 'select'
          elif item.type == 'checkbox':
            self.JSONDict['properties'][var]['format']       = 'checkbox'
          self.JSONDict['properties'][var]['items']          = {}
          self.JSONDict['properties'][var]['items']['type']  = 'string'
          self.JSONDict['properties'][var]['items']['enum']  = []
          if len(values)>0:
            for val in values:
              self.JSONDict['properties'][var]['items']['enum'].append(val)
    
        if item.hidden:
          self.JSONDict['properties'][var]['options']['hidden']  = 'true'
    
        if item.type in ['custom'] and item.rawJSON != '':
          try:
            self.JSONDict['properties'][var]                  = json.loads(item.rawJSON)
          except:
            self.JSONDict['properties'][var]                  = '{ // ERROR in custom JSON }'

  def render(self, obj):
    
    script = '<script src="%s/metaobj_manager/zms.formulator.lib.jsoneditor.min.js"></script>\n<script>%s</script>'
    editor = standard.http_import(obj.this, obj.this.getMetaobjManager().absolute_url() + '/zms.formulator.lib.jsoneditor.custom.js')
    editor = editor.decode('utf-8') % (self.getLangDict(obj), obj.thisURLPath,
                       obj.this.REQUEST.get('lang'), obj.GoogleAPIKey, 
                       obj.options, self.mandatory_validators, obj.onReady,
                       obj.this.REQUEST.get('lang'), obj.thisURLPath, obj.onChange)
    output = script % (obj.baseURLPath, editor)
    
    return output
  
  def getSchema(self):
  
    JSONSchema = json.dumps(self.JSONDict, sort_keys=True, indent=4, separators=(',', ': '))
    return JSONSchema
  
  def getLangDict(self, obj):
    
    lang    = obj.this.REQUEST.get('lang')
    langstr = ''

    for item in obj.this.getLangDict():
      if item['key'].startswith('zms.formulator.lib.'):
        langstr += '\n%s: "%s",'%(item['key'].replace('zms.formulator.lib.','').lower(), item[lang])
    
    return """JSONEditor.defaults.languages.%s = { %s };\nJSONEditor.defaults.language = "%s";
    """%(lang, langstr, lang)