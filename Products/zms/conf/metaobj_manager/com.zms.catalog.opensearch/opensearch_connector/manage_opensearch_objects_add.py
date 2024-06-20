from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


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

def bulk_opensearch_index(self, sources):
	# Returns a tuple of two numbers of succeeded and failed indexing actions
	client = get_opensearch_client(self)
	index_name = self.getRootElement().getHome().id
	actions = []
	# Name adaption to opensearch schema
	for x in sources:
		# Create language specific opensearch id
		_id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
		d = {"_op_type":"index", "_index":index_name, "_id":_id}
		# Differenciate zms-object id and uid
		x['zmsid'] = x['id']
		x['id'] = x['uid']
		d.update(x)
		actions.append(d)
	if client:
		# The opensearch bulk helper function returns a tuple of two numbers 
		# of succeeded and failed indexing actions if stats_only is set to True.
		# Otherwise it returns the errors for failed actions as a list.
		return bulk(client, actions, stats_only=False)
	# No client available: no indexing possible
	return 0, len(actions)

def manage_opensearch_objects_add( self, objects):
	# Function applies to:
	#	ZMSZCatalogConnector.manage_objects_add 
	#	ZMSZCatalogConnector.reindex_page
	sources = [data for (node, data) in objects]
	try:
		success, failed = bulk_opensearch_index(self, sources)
		if failed and isinstance(failed,list):
			standard.writeError( self, "[OpenSearch] Failed to index objects %s" % failed)
	except Exception as e:
		standard.writeError( self, e)
		return 0, len(sources)
	return success, failed if isinstance(failed,int) else len(failed)