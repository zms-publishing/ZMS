from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch


def get_elasticsearch_client(self):
	# ${elasticsearch.url:https://localhost:9200}
	# ${elasticsearch.username:admin}
	# ${elasticsearch.password:admin}
	# ${elasticsearch.ssl.verify:}
	url = self.getConfProperty('elasticsearch.url').rstrip('/')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('elasticsearch.ssl.verify', False))
	username = self.getConfProperty('elasticsearch.username', 'admin')
	password = self.getConfProperty('elasticsearch.password', 'admin')
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


def elasticsearch_query( self, REQUEST=None):
	request = self.REQUEST
	q = request.get('q','')
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 10)
	qfrom = request.get('from', qpage_index*qsize)
	index_name = self.getRootElement().getHome().id
	index_names = []
	index_names = [k.split('.')[-1] for k in list(self.getConfProperties().keys()) if k.lower().startswith('elasticsearch.suggest.fields.')]
	if index_name not in index_names:
		index_names.append(index_names)

	# Refs: query on multiple indexes and composite aggregation
	# https://discuss.elastic.co/t/query-multiple-indexes-but-apply-queries-to-specific-index/127858
	# https://opster.com/guides/opensearch/opensearch-search-apis/opensearch-composite-aggregation/

	query = {
		"size": qsize,
		"from": qfrom,
		"query": {
			"query_string": {
				"query":q
			}
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

	client = get_elasticsearch_client(self)
	if not client:
		return '{"error":"No client"}'

	resp_text = ''
	try:
		response = client.search(body = json.dumps(query), index = index_names)
		resp_text = json.dumps(response)
	except opensearchpy.exceptions.RequestError as e:
		resp_text = '//%s'%(e.error)
	
	return resp_text
