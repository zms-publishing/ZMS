from urllib.parse import urlparse
import json
import requests



def solr_suggest( self, REQUEST=None):
	request = self.REQUEST
	index_name = self.getRootElement().getHome().id

	# TODO: implement suggest!
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

	# Define the URL of the Solr select API.
	query_url = '{}/{}/select'.format(url, index_name)


	q = request.get('q','')
	limit = int(REQUEST.get('limit',5))
	index_name = self.getRootElement().getHome().id

	query_params = {
		'q': 'standard_html:%s'%(q),
		'wt': 'json',
		'hl': 'false',
		'hl.fl': 'standard_html',
		'hl.simple.pre': '<b>',
		'hl.simple.post': '</b>',
		'hl.fragsize': 100, # Number of characters to return
		'hl.snippets': 10,	# Number of fragments to return
		'rows': limit,
		'hl.usePhraseHighlighter': 'true'
	}

	# Define the headers for the POST schema request.
	headers = {'Content-type': 'application/json'}
	# Send the GET request.
	response = requests.get(query_url, params=query_params, headers=headers)

	# Parse the response.
	data = response.json()
	
	return json.dumps(data, indent=4, sort_keys=False)