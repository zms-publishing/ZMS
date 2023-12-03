from Products.zms import standard
import json
from urllib.parse import urlparse


def get_solr_client(self):
	# ${solr.url:https://localhost:9200}
	# ${solr.username:admin}
	# ${solr.password:admin}
	# ${solr.ssl.verify:}
	url = self.getConfProperty('solr.url')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('solr.ssl.verify', False))
	username = self.getConfProperty('solr.username', 'admin')
	password = self.getConfProperty('solr.password', 'admin')
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

def bulk_solr_index(self, sources):
	client = get_solr_client(self)
	index_name = self.getRootElement().getHome().id
	actions = []
	# Name adaption to solr schema
	for x in sources:
		# Create language specific solr id
		_id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
		d = {"_op_type":"index", "_index":index_name, "_id":_id}
		# Differenciate zms-object id and uid
		x['zmsid'] = x['id']
		x['id'] = x['uid']
		d.update(x)
		actions.append(d)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_solr_objects_add( self, objects):
	sources = [data for (node, data) in objects]
	success, failed = bulk_solr_index(self, sources)
	return success, failed or 0