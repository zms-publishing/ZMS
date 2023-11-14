import requests
from requests.auth import HTTPBasicAuth
import json

def opensearch_query( self, q):
  request = self.REQUEST
  qpage_index = request.get('pageIndex',0)
  qsize = request.get('size', 10)
  qfrom = request.get('from', qpage_index*qsize)

  d = {
    "size": qsize,
    "from": qfrom,
    "query":{
      "query_string":{"query":q}
    },
    "highlight": {
      "fields": {
        "title": { "type": "plain"},
        "standard_html": { "type": "plain"}
      }
    },
    "aggs": {
      "response_codes": {
        "terms": {
          "field": "meta_id",
          "size": 5
        }
      }
    }
  }

  url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
  # ID of opensearch index is ZMS multisite root node id or explicitly given by request variable 'opensearch_index_id'
  root_id = self.getRootElement().getHome().id
  index_id = request.get('opensearch_index_id',root_id)
  username = self.getConfProperty('opensearch.username', 'admin')
  password = self.getConfProperty('opensearch.password', 'admin')
  verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
  auth = HTTPBasicAuth(username,password)
  response = requests.get('%s/%s/_search?pretty=true'%(url,index_id),auth=auth,json=d,verify=verify)
  response.raise_for_status()
  json_obj = response.json()
  data = json.dumps(json_obj, separators=(",", ":"), indent=4)
  request.RESPONSE.setHeader('Content-Type','text/json; charset=utf-8')
  return data

