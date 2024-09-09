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

def manage_elasticsearch_destroy( self):
	index_name = self.getRootElement().getHome().id
	client = get_elasticsearch_client(self)
	resp_text = '//RESPONSE\n'
	try:
		response = client.indices.delete(index_name)
	except opensearchpy.exceptions.RequestError as e:
		resp_text += '//%s\n'%(e.error)
	resp_text += json.dumps(response, indent=2)
	return resp_text