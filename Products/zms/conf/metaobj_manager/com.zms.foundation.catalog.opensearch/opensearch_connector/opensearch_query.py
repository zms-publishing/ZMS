from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_opensearch_client(self):
	# ${opensearch.url:https://localhost:9200}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}
	url = self.getConfProperty('opensearch.url')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
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


def opensearch_query( self, request):
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

	try:
		response = client.search(body = json.dumps(query), index = index_name)
	except opensearchpy.exceptions.RequestError as e:
		response = '//%s'%(e.error)
	
	return response

