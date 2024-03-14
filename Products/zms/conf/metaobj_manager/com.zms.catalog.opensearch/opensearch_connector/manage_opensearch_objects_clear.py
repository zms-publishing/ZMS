import json
from urllib.parse import urlparse
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_opensearch_client(self):
	# ${opensearch.url:https://localhost:9200}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}
	url = self.getConfProperty('opensearch.url').rstrip('/')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	auth = (username,password)
	
	client = OpenSearch(
		hosts = [{'host': host, 'port': port}],
		http_compress = False, # enables gzip compression for request bodies
		http_auth = auth,
		use_ssl = ssl,
		verify_certs = verify,
		ssl_assert_hostname = False,
		ssl_show_warn = False,
	)
	return client

def bulk_opensearch_delete(self, actions):
	client = get_opensearch_client(self)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_opensearch_objects_clear( self, home_id):
	query = {
		"query": {
			"query_string": {
				"query": "home_id: \"%s\""%home_id
			}
		}
	}
	client = get_opensearch_client(self)
	response = client.search(body = json.dumps(query), index = [], size=10000, _source_includes=['home_id'])
	hits = response["hits"]["hits"]
	actions = [{"_op_type":"delete", "_index":x['_index'], "_id":x['_id']} for x in hits]
	success, failed = bulk_opensearch_delete(self, actions)
	return success, failed or 0