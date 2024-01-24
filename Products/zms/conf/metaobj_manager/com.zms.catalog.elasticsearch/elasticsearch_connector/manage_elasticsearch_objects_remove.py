from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_elasticsearch_client(self):
	# ${elasticsearch.url:https://localhost:9200}
	# ${elasticsearch.username:admin}
	# ${elasticsearch.password:admin}
	# ${elasticsearch.ssl.verify:}
	url = self.getConfProperty('elasticsearch.url').rstrip('/')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('elasticsearch.ssl.verify', False))
	username = self.getConfProperty('elasticsearch.username', 'admin')
	password = self.getConfProperty('elasticsearch.password', 'admin')
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

def bulk_elasticsearch_delete(self, sources):
	client = get_elasticsearch_client(self)
	index_name = self.getRootElement().getHome().id
	actions = []
	# Name adaption to elasticsearch schema
	for x in sources:
		# Create language specific elasticsearch id
		_id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
		d = {"_op_type":"delete", "_index":index_name, "_id":_id}
		actions.append(d)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_elasticsearch_objects_remove( self, nodes):
	sources = [{'uid':x.get_uid()} for x in nodes]
	try:
		success, failed = bulk_elasticsearch_delete(self, sources)
	except Exception as e:
		print(e)
		return 0, len(sources)
	return success, failed or 0