from Products.zms import standard
import json
import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# import pdb

def manage_zcatalog_export_schema(self):
  zmscontext = self
  properties = {}
  resp_text = '//RESPONSE\n'
  allowed_property_types = [
	'alias',
	'binary',
	'boolean',
	'completion',
	'date',
	'date_range',
	'double',
	'double_range',
	'float',
	'geo_point',
	'geo_shape',
	'half_float',
	'integer',
	'ip',
	'ip_range',
	'keyword',
	'long',
	'long_range',
	'object',
	'percolator',
	'rank_feature',
	'rank_features',
	'search_as_you_type',
	'text',
	'token_count'
]
  properties['id'] = {'type':'text'}
  properties['zmsid'] = {'type':'text'}
  properties['uid'] = {'type':'text'}
  properties['loc'] = {'type':'text'}
  properties['index_html'] = {'type':'text'}
  properties['meta_id'] = {'type':'keyword'}
  properties['lang'] = {'type':'keyword'}
  properties['home_id'] = {'type':'keyword'}
  zca = zmscontext.getCatalogAdapter()
  attrs = zca.getAttrs()
  for attr_id in zca._getAttrIds():
    attr = attrs.get(attr_id,{})
    attr_type = attr.get('type', 'string')
    attr_type = {'string':'text'}.get(attr_type,attr_type)
    attr_type = attr_type == 'select'and 'keyword' or attr_type
    if attr_type not in allowed_property_types:
      attr_type = 'text'
    property = {}
    property['type'] = attr_type
    properties[attr_id] = property
  properties['home_id'] = {'type':'keyword'}
  mappings = {'properties':properties}
  dictionary = {'mappings':mappings}

  url = self.getConfProperty('opensearch.url')
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  self.setConfProperty('opensearch.schema', json.dumps(dictionary, indent=2))
  verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
  auth = HTTPBasicAuth(username,password)
  headers = {'Content-type': 'application/x-ndjson'}
  # pdb.set_trace()
  root_id = self.getRootElement().getHome().id
  try:
    response = requests.delete('%s/%s'%(url,root_id),auth=auth,verify=verify)
    response = requests.put('%s/%s'%(url,root_id),auth=auth,headers=headers,json=dictionary,verify=verify)
    resp_text += json.dumps(response.json(), separators=(",", ":"), indent=2)
    response.raise_for_status()
  except:
    standard.writeError(self,'Error: %s'%(resp_text))
    return resp_text
  
  # concatinate opensearch response and schema
  resp_text += '\n\n'
  resp_text += '//SCHEMA\n'

  resp_text += json.dumps(mappings, indent=2)
  return resp_text