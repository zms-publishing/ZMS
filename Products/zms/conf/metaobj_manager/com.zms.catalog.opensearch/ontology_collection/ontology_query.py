import opensearchpy
from opensearchpy import OpenSearch
import json
from Products.zms import standard

def ontology_query(self, return_type='list'):
	request = self.REQUEST
	q = request.get('q','*')
	q = q.strip()=='' and '*' or q.strip()
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 100)
	qfrom = request.get('from', qpage_index*qsize)
	
	zmscontext = self

	ontology_location = '/'
	if standard.operator_getattr(zmscontext, 'ontology'):
		ontology_location = '/'.join(standard.operator_getattr(zmscontext, 'ontology').absolute_url_path().split('/')[:-1])

	hits = []
	try:
		langs = zmscontext.getLanguages(request)
	except:
		zmscontext = self.content
		langs = zmscontext.getLanguages(request)
		pass

	index_names = []
	index_names.append(zmscontext.getRootElement().getHome().id)

	client = self.opensearch_get_client(self)
	if not client:
		standard.writeStdout(None, 'ERROR: ontology_query() cannot find an OpenSearch Client!')
		return None

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
									"fields": ["attr_dc_subject_ontology"],
									"default_operator": "AND"
								}
							},
							{
								"term": {
									"loc": ontology_location
								}
							},
							{
								"exists": {
									"field": "attr_dc_subject_ontology"
								}
							},
							{
								# Ensure that attr_dc_subject is not empty
								"regexp": { 
									"attr_dc_subject_ontology": {
										"flags": "ALL",
										"max_determinized_states": 10000,
										"rewrite": "constant_score",
										"value": ".+"
									}
								}
							}
						]
					}
				},
				"script": {
					"lang": "painless",
					"source": "return _score;"
				}
			}
		},
		"aggs": {
			"response_codes": {
				"terms": {
					"field": "_index",
					"size": 5
				}
			}
		}
	}

	try:
		response = client.search(body = json.dumps(query), index = index_names)
		if 'hits' in response and 'hits' in response['hits']:
			hits = response['hits']['hits']
	except opensearchpy.exceptions.RequestError as e:
		return '// %s'%(e.error)

	if return_type=='json':
		return json.dumps(hits,indent=2)
	else:
		return hits