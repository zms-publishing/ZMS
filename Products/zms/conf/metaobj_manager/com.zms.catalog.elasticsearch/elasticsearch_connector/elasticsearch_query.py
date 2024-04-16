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
	home_id = request.get('home_id', '')
	multisite_search = int(request.get('multisite_search', 1))
	multisite_exclusions = request.get('multisite_exclusions', '').split(',')
	index_names = []
	# Search in a specific index given by Request-parameter 'facet'
	if request.get('facet') not in ['all','undefined', None, '']:
		index_names.append(request.get('facet'))
	else:
	# Search in all configured indexes
		root_name = self.getRootElement().getHome().id
		index_names.append(root_name)
		# suggest.fields may be configured explicitly for any index, like 'elasticsearch.suggest.fields.persons = ['lastname','firstname']'
		for index_name in [k.split('.')[-1] for k in list(self.getConfProperties(inherited=True)) if k.lower().startswith('elasticsearch.suggest.fields.')]:
			if index_name != root_name:
				index_names.append(index_name)

	# Refs: query on multiple indexes and composite aggregation
	# https://discuss.elastic.co/t/query-multiple-indexes-but-apply-queries-to-specific-index/127858
	# https://opster.com/guides/opensearch/opensearch-search-apis/opensearch-composite-aggregation/

	query = {
		"size": qsize,
		"from": qfrom,
		"query": {
			"script_score": {
				"query": {
					"bool": {
						"must": [
							{
								"simple_query_string": {
									"query": q,
									"default_operator": "AND"
								}
							}
						]
					}
				},
				"script": {
					"lang":"painless",
					"source": "return _score;"
				}
			}
		},
		"highlight": {
			"fragment_size" : 256,
			"fields": {
				"title": { "type": "plain"},
				"standard_html": { "type": "plain"},
			}
		},
		"aggs": {
			"response_codes": {
				"terms": {
					"field": "home_id",
					"size": 5
				}
			}
		}
	}

	# No multisite-search: show only results of current ZMS-client
	if multisite_search==0 and len(home_id) > 0:
		query['query']['bool']['must'].append( {
			"match": {
				"home_id": str(home_id)
			}
		})

	# Exclusion of ZMS-Clients (home_id exclusions) via 'must_not' operator
	if multisite_exclusions[0]!='':
		# init 'must_not' operator
		query['query']['bool']['must_not'] = []
		# add must_not for each home_id
		for home_id in multisite_exclusions:
			query['query']['bool']['must_not'].append( {
				"match": {
					"home_id": str(home_id)
				}
			})

	# Script Score Query: Boosting by Field Value
	# https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-score-query.html
	# https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-scripting-painless.html
	# https://www.elastic.co/guide/en/elasticsearch/painless/8.13/painless-lang-spec.html
	
	score_script = self.getConfProperty('opensearch.score_script', '')
	if score_script:
		query['query']['script_score']['script']['source'] = score_script

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
