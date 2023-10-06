# --// manage_zcatalog_put_data //--

def manage_zcatalog_put_data( self):
  request = self.REQUEST
  RESPONSE =  request.RESPONSE
  zmscontext = self.getLinkObj(request.get('uid','{$}'))
  home = zmscontext.getDocumentElement()
  home_id = home.getPhysicalPath()
  home_id = home_id[home_id.index('content')-1]
  inst_home = zmscontext.Control_Panel.getINSTANCE_HOME()
  path = home_id
  node = home
  while True:
    node = node.getPortalMaster()
    if node is None: break
    path = node.getHome().getId() + '/' + path
  jsonpath = '%s/var/%s/opensearch/%s.json'%(inst_home,path,home_id)
  f = open(jsonpath,'r')
  dictionary = f.read()
  f.close()

  import requests
  from requests.auth import HTTPBasicAuth
  import json
  url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
  root_id = zmscontext.getRootElement().getHome().id
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
  auth = HTTPBasicAuth(username,password)
  headers = {'Content-type': 'application/x-ndjson'}
  response = requests.put('%s/%s/_bulk'%(url,root_id),auth=auth,headers=headers,data=dictionary,verify=verify)
  response.raise_for_status()
  json_obj = response.json()
  data = json.dumps(json_obj, separators=(",", ":"), indent=2)
  return data

# --// /manage_zcatalog_put_data //--