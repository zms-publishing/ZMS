from urllib import *
from urllib.parse import urlparse
import json
import requests
import os


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

	# DUMMY: Use solrconfig.xml from the extension.
	# ##############
	solrconfig_src = os.path.join('/home/zope/src/zms-publishing/ZMS5/docker/solr/solrconfig.xml')
	solrconfig_dst = os.path.join('/home/zope/src/zms-publishing/ZMS5/docker/var/solr/data', index_name, 'conf', 'solrconfig.xml')
	if not os.path.exists(solrconfig_dst):
		os.makedirs(os.path.dirname(solrconfig_dst), exist_ok=True)
		with open(solrconfig_src, 'r') as f:
			with open(solrconfig_dst, 'w') as g:
				g.write(f.read())
	# ##############

	# Define the headers for the POST schema request.
	headers = {'Content-type': 'application/json'}
	# Send the POST schema request.
	response = requests.post('%s/%s/schema'%(url,index_name), data=json.dumps(schema), headers=headers)

	# Check the response.
	if response.status_code == 200:
		resp.append('Schema added successfully.')
	else:
		resp.append('Failed to add field. Response: %s'%(response.text))


	# Define the parameters for the CREATE index request.
	params = {
		'action': 'CREATE',
		'name': index_name,
		'instanceDir': index_name,
		'config': 'solrconfig.xml',
		'schema': 'schema.xml',
		'dataDir': 'data'
	}

	# Send the CREATE request.
	response = requests.get('%s/admin/cores'%url, params=params)

	# Check the response.
	if response.status_code == 200:
		resp.append('Core created successfully.')
	else:
		resp.append('Failed to create core. Response: %s'%(response.text))

	return '\n'.join(resp)
