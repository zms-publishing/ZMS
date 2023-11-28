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


def opensearch_query( self, q):
	REQUEST = self.REQUEST
	qpage_index = REQUEST.get('pageIndex',0)
	qsize = REQUEST.get('size', 10)
	qfrom = REQUEST.get('from', qpage_index*qsize)
	index_name = self.getRootElement().getHome().id
	resp_text = ''

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
		resp_text = json.dumps(response)
	except opensearchpy.exceptions.RequestError as e:
		resp_text = '//%s'%(e.error)

	REQUEST.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
	return resp_text

