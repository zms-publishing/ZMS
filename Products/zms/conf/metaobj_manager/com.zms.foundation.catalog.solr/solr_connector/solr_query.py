from Products.zms import standard
from urllib.parse import urlparse
import json
import pysolr

def get_solr_client(self):
	# ${solr.url:https://localhost:8983/solr}
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



def solr_query( self, REQUEST=None):
	request = self.REQUEST
	q = request.get('q','')
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 10)
	qfrom = request.get('from', qpage_index*qsize)
	index_name = self.getRootElement().getHome().id

	query = {
		"size": qsize,
		"from":qfrom,
		"query":{
			"query_string":{"query":q}
		},
		"highlight": {
			"fields": {
				"title": { "type": "plain"},
				"standard_html": { "type": "plain"}
			}
		},
		"aggs": {
			"response_codes": {
				"terms": {
					"field": "meta_id",
					"size": 5
				}
			}
		}
	}

	client = get_opensearch_client(self)
	if not client:
		return '{"error":"No client"}'

	resp_text = ''
	try:
		response = client.search(body = json.dumps(query), index = index_name)
		resp_text = json.dumps(response)
	except opensearchpy.exceptions.RequestError as e:
		resp_text = '//%s'%(e.error)
	
	return resp_text

