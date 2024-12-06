from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_elasticsearch_client(self):
	# ${elasticsearch.url:https://localhost:9200, https://localhost:9201}
	# ${elasticsearch.username:admin}
	# ${elasticsearch.password:admin}
	# ${elasticsearch.ssl.verify:}
	url_string = self.getConfProperty('elasticsearch.url')
	urls = [url.strip().rstrip('/') for url in url_string.split(',')]
	hosts = []
	use_ssl = False
	# Process (multiple) url(s) (host, port, ssl)
	if not urls:
		return None
	else:
		for url in urls:
			hosts.append( { \
					'host':urlparse(url).hostname, \
					'port':urlparse(url).port } \
				)
			if urlparse(url).scheme=='https':
				use_ssl = True
	verify = bool(self.getConfProperty('elasticsearch.ssl.verify', False))
	username = self.getConfProperty('elasticsearch.username', 'admin')
	password = self.getConfProperty('elasticsearch.password', 'admin')
	auth = (username,password)
	
	client = OpenSearch(
		hosts = hosts,
		http_compress = False, # enables gzip compression for request bodies
		http_auth = auth,
		use_ssl = use_ssl,
		verify_certs = verify,
		ssl_assert_hostname = False,
		ssl_show_warn = False,
	)
	return client

def bulk_elasticsearch_delete(self, actions):
	client = get_elasticsearch_client(self)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_elasticsearch_objects_clear( self, home_id):
	index_names = []
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	index_names.append(index_name)
	query = {
		"query": {
			"query_string": {
				"query": "home_id: \"%s\""%home_id
			}
		}
	}
	client = get_elasticsearch_client(self)
	response = client.search(body = json.dumps(query), index = index_names, size=10000, _source_includes=['home_id'])
	hits = response["hits"]["hits"]
	actions = [{"_op_type":"delete", "_index":x['_index'], "_id":x['_id']} for x in hits]
	success, failed = bulk_elasticsearch_delete(self, actions)
	return success, failed or 0