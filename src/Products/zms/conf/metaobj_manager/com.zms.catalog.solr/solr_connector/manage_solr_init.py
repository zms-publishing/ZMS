from urllib import *
from urllib.parse import urlparse
import json
import requests


def manage_solr_init( self):
	# Set connection variables
	index_name = self.getRootElement().getHome().id
	schema = self.getConfProperty('solr.schema','{}')
	url = self.getConfProperty('solr.url','http://localhost:8983/solr/')
	if not url:
		return None
	else:
		if url.endswith('/'):
			url = url[:-1]	# Remove trailing slash
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('solr.ssl.verify', False))
	username = self.getConfProperty('solr.username', 'admin')
	password = self.getConfProperty('solr.password', 'admin')
	auth = (username,password)

	resp = []

	# Define the URL of the Solr Schema API.
	schema_url = '{}/{}/schema'.format(url, index_name)
	# Define the headers for the POST schema request.
	headers = {'Content-type': 'application/json'}
	# Send the POST schema request.
	schema = json.loads(schema)
	response = requests.post(schema_url, data=json.dumps(schema), headers=headers)
	# Check the response.
	if response.status_code == 200:
		resp.append('Schema added successfully.')
	else:
		resp.append('Failed to add schema. Please check, whether corresponding Solr core %s exists. Otherwise one has to be created by shell script \'./solr create -c %s \'.\nRESPONSE:\n%s'%(index_name, index_name, response.text))

	return '\n'.join(resp)