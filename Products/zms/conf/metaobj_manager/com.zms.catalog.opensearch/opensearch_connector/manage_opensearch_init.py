from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

# import pdb
# pdb.set_trace()

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

def manage_opensearch_init( self):
	index_name = self.getRootElement().getHome().id
	schema = self.getConfProperty('opensearch.schema','{}')
	resp_text = '//RESPONSE\n'
	client = get_opensearch_client(self)
	try:
		response = client.indices.create(index_name, body=schema)
	except opensearchpy.exceptions.RequestError as e:
		if 'resource_already_exists_exception' != e.error:
			raise
		else:
			client.indices.delete(index_name)
			response = client.indices.create(index_name, body=schema)
			resp_text += '//%s\n'%(e.error)
	resp_text += json.dumps(response, indent=2)
	# concatinate opensearch response and schema
	resp_text += '\n\n'
	resp_text += '//SCHEMA\n'
	resp_text += schema

	return resp_text