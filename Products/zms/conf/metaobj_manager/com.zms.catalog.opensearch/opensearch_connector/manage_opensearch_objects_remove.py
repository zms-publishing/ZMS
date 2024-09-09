from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

langs = ['ger','eng']

def get_opensearch_client(self):
	# ${opensearch.url:https://localhost:9200, https://localhost:9201}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}
	url_string = self.getConfProperty('opensearch.url')
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
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
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

def bulk_opensearch_delete(self, sources):
	client = get_opensearch_client(self)
	index_name = self.getRootElement().getHome().id
	actions = []
	# Name adaption to opensearch schema
	for x in sources:
		# Create language specific opensearch id
		for lang in globals()['langs']:
			_id = "%s:%s"%(x['uid'],lang)
			d = {"_op_type":"delete", "_index":index_name, "_id":_id}
			actions.append(d)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_opensearch_objects_remove( self, nodes):
	sources = [{'uid':x.get_uid()} for x in nodes]
	for node in nodes:
		# Set node's language list as global variable.
		global langs
		langs = node.getLangIds()
		break
	try:
		success, failed = bulk_opensearch_delete(self, sources)
	except Exception as e:
		standard.writeBlock( self, str(e))
		return 0, len(sources)
	return success, failed or 0