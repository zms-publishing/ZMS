import opensearchpy
from opensearchpy import OpenSearch
import json
from chameleon import PageTemplate
from Products.zms import standard

def ontology_query( self):
	request = self.REQUEST
	q = request.get('q','lorem ipsum')
	qpage_index = request.get('pageIndex',0)
	qsize = request.get('size', 10)
	qfrom = request.get('from', qpage_index*qsize)

	# Get the ZMS context, which may be the current object or its content
	zmscontext = self
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
		"aggs": {
			"response_codes": {
				"terms": {
					"field": "_index",
					"size": 5
				}
			}
		}
	}

	# Define the template as a string with Chameleon syntax for repeating hits
	pt = PageTemplate("""
	<main>
		<article class="infoxbox" tal:repeat="hit hits">
			<div tal:define="title hit['_source']['title']; attr_dc_description hit['_source']['attr_dc_description']">
				<h1 tal:content="title">Title</h1>
				<p tal:content="attr_dc_description">Description</p>
			</div>
		</article>
	</main>
	""")

	hits = []
	resp_html =	''
	try:
		response = client.search(body = json.dumps(query), index = index_names)
		if 'hits' in response and 'hits' in response['hits']:
			hits = response['hits']['hits']
		if hits:
			resp_html = pt.render(hits=hits)

	except opensearchpy.exceptions.RequestError as e:
		return '// %s'%(e.error)
	
	return resp_html
