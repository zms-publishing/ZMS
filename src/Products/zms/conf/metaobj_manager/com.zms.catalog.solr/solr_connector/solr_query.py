from Products.zms import standard
from urllib.parse import urlparse
import json
import requests



def solr_query( self, REQUEST=None):
	request = self.REQUEST
	index_name = self.getConfProperty('solr.core', self.getRootElement().getHome().id)


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
	fulltext_field = self.getConfProperty('solr.fulltext_field', 'standard_html')
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 10)
	qfrom = request.get('from', qpage_index*qsize)

	query_params = {
		'q': '%s:%s'%(fulltext_field,q),
		'wt': 'json',
		'hl': 'false',
		'hl.fl': fulltext_field,
		'hl.simple.pre': '<b>',
		'hl.simple.post': '</b>',
		'hl.fragsize': 100, # Number of characters to return
		'hl.snippets': 10,	# Number of fragments to return
		'start': qfrom,
		'rows': qsize,
		'hl.usePhraseHighlighter': 'true'
	}

	# Define the headers for the POST schema request.
	headers = {'Content-type': 'application/json'}
	# Send the GET request.
	response = requests.get(query_url, params=query_params, headers=headers)

	# Parse the response.
	data = response.json()
	
	return json.dumps(data, indent=4, sort_keys=False)