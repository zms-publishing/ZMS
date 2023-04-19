import json
import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# import pdb

def manage_zcatalog_export_schema( self):
  zmscontext = self
  properties = {}
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
    property = {}
    property['type'] = attr_type
    properties[attr_id] = property
  properties['home_id'] = {'type':'keyword'}
  mappings = {'properties':properties}
  dictionary = {'mappings':mappings}

  url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
  root_id = self.getRootElement().getHome().id
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
  auth = HTTPBasicAuth(username,password)
  headers = {'Content-type': 'application/x-ndjson'}
  # pdb.set_trace()
  response = requests.delete('%s/%s'%(url,root_id),auth=auth,verify=verify)
  response = requests.put('%s/%s'%(url,root_id),auth=auth,headers=headers,json=dictionary,verify=verify)
  response.raise_for_status()
  # json_obj = response.json()
  # data = json.dumps(json_obj, separators=(",", ":"), indent=2)
  data = json.dumps(mappings, indent=2)
  return data