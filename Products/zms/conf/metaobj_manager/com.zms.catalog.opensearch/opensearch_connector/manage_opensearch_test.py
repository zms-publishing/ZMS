from opensearchpy import OpenSearch
from urllib.parse import urlparse
import json
import traceback
import time

def manage_opensearch_test(self):
	client = get_opensearch_client(self)
	request = self.REQUEST
	call_amount = int(request.get('calls', 10))
	request.set('q', request.get('q', 'Universität'))
	prettify = bool(int(request.get('prettify',0)))
	response = {}
	try:
		response['status'] = 200
		response['clusterInfo'] = client.info()
		tests = {}
		tests['options'] = {}
		tests['options']['query'] = request.get('q')
		tests['options']['callAmount'] = call_amount
		response['tests'] = tests
		# Call OpenSearch query multiple times
		query_result = {}
		query_result['performance'] = {}
		query_result_took = query_result['performance']['took'] = {}
		query_result_took['sum'] = 0
		query_start = time.time()
		for i in range(call_amount):
			stringified_query_response = self.opensearch_query()
			query_response = json.loads(stringified_query_response)
			query_result_took['sum'] += query_response['took']
			if i == 0:
				query_result['response'] = query_response
		query_end = time.time()
		query_result_took['average'] = query_result_took['sum'] / call_amount
		query_result_elapsed_time = query_result['performance']['ellapsedTime'] = {}
		query_result_elapsed_time['sum'] = (query_end - query_start) * 1000
		query_result_elapsed_time['average'] = query_result_elapsed_time['sum'] / call_amount
		tests['opensearchQuery'] = query_result

		# Call OpenSearch suggest multiple times
		suggest_result = {}
		suggest_result['performance'] = {}
		suggest_start = time.time()
		for i in range(call_amount):
			stringified_suggest_response = self.opensearch_suggest()
			suggest_response = json.loads(stringified_suggest_response)
			if i == 0:
				suggest_result['response'] = suggest_response
		suggest_end = time.time()
		suggest_result_elapsed_time = suggest_result['performance']['ellapsedTime'] = {}
		suggest_result_elapsed_time['sum'] = (suggest_end - suggest_start) * 1000
		suggest_result_elapsed_time['average'] = suggest_result_elapsed_time['sum'] / call_amount
		tests['opensearchSuggest'] = suggest_result
	except Exception as e:
		response['status'] = 500
		response['error'] = str(e)
		response['trace'] = traceback.format_exc()
	
	if prettify:
		resp_text = json.dumps(response, indent=4)
	else:
		resp_text = json.dumps(response)

	return resp_text
	

def get_opensearch_client(self):
	# ${opensearch.url:https://localhost:9200, https://localhost:9201}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}
	url_string = self.getConfProperty('opensearch.url')
	urls = [url.strip().rstrip('/') for url in url_string.split(',')]
	hosts = []
	use_ssl = False
	# Process (multiple) url(s) (host, port, ssl)
	if not urls:
		return None
	else:
		for url in urls:
			hosts.append( { \
					'host':urlparse(url).hostname, \
					'port':urlparse(url).port } \
				)
			if urlparse(url).scheme=='https':
				use_ssl = True
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	auth = (username,password)
	
	client = OpenSearch(
		hosts = hosts,
		http_compress = False, # enables gzip compression for request bodies
		http_auth = auth,
		use_ssl = use_ssl,
		verify_certs = verify,
		ssl_assert_hostname = verify,
		ssl_show_warn = False,
	)
	return client
