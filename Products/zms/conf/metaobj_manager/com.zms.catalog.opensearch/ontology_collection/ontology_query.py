import opensearchpy
from opensearchpy import OpenSearch
import json
from Products.zms import standard

def ontology_query(self, fmt=None):
	request = self.REQUEST
	q = request.get('q','lorem ipsum')
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 10)
	qfrom = request.get('from', qpage_index*qsize)

	zmscontext = self
	# Default fields are attr_dc_subject or attr_dc_subject_ontology
	fields = zmscontext.metaobj_manager.getMetadictAttr('attr_dc_subject_ontology') and ['attr_dc_subject_ontology'] or ['attr_dc_subject']
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
		return '// Error: No OpenSearch Client found.'

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
									"fields": ["attr_dc_subject"],
									"default_operator": "AND"
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

	if fmt=='json':
		return json.dumps(hits,indent=2)
	else:
		return hits