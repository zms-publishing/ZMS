from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
import json

# Get Opensearch Client:
#
# ${opensearch.url:https://localhost:9200}
# ${opensearch.username:admin}
# ${opensearch.password:admin}
# ${opensearch.ssl.verify:}
def get_opensearch_client(self):
  url = self.getConfProperty('opensearch.url')
  if not url:
    return None
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
  use_ssl = url.find('https://')>-1
  url = url.split('://')[-1]
  host = url[:url.find(':')]
  port = int(url[url.find(':')+1:])
  auth = (username, password)
  return OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    use_ssl = use_ssl,
    verify_certs = verify,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
  ) 

def bulk_opensearch_delete(self, sources):
  client = get_opensearch_client(self)
  index = self.getRootElement().getHome().id
  actions = []
  # Name adaption to opensearch schema
  for x in sources:
    # Create language specific opensearch id
    _id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
    d = {"_op_type":"delete", "_index":index, "_id":_id}
    actions.append(d)
  if client: 
    return bulk(client, actions)
  return 0, len(actions)

def manage_opensearch_objects_remove( self, nodes):
  sources = [{'uid':x.get_uid()} for x in nodes]
  success, failed = bulk_opensearch_delete(self, sources)
  return json.dumps({'success':success, 'failed':failed})