from Products.zms import standard
from urllib.parse import urlparse
import json
import pysolr


def get_solr_client(self):
	# ${solr.url:http://localhost:8983/solr}
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

	client = pysolr.Solr(url, auth=auth, verify=verify)
	return client

def manage_solr_init( self):
	index_name = self.getRootElement().getHome().id
	schema = self.getConfProperty('solr.schema','{}')
	resp_text = '//RESPONSE\n'
	client = get_solr_client(self)
	# Create Solr index
	try:
		resp_text += 'Deleting Solr index: %s\n' % index_name
		client.delete_index(index_name)
	except pysolr.SolrError:
		pass

	resp_text += 'Creating Solr index: %s\n' % index_name
	client.create_index(index_name)
	# Create Solr schema
	resp_text += 'Creating Solr schema: %s\n' % schema
	client.schema.create(json.loads(schema))







	return resp_text