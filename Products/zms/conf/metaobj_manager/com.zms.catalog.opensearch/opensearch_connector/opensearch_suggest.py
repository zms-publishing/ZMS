import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch, RequestsHttpConnection
import re
from Products.zms import standard


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
	
	# CAVE: connection_class RequestsHttpConnection
	client = OpenSearch(
		urls,
		connection_class=RequestsHttpConnection,
		http_compress = False,
		http_auth = auth,
		use_ssl = use_ssl,
		verify_certs = verify,
		ssl_assert_hostname = verify,
		ssl_show_warn = False,
	)
	return client


def get_suggest_terms(self, q='Lorem', index_name='myzms', field_names=['title','attr_dc_subject'], qsize=10, debug=False):
	# Get suggest terms for a given query string q and index_name
	# Assemble SQL Query using f-strings
	sql_tmpl = "SELECT {} FROM {} WHERE {} LIMIT {}"
	sel_fields = ','.join(field_names)
	whr_clause = " OR ".join([f"({field_name} LIKE '%{q}%')" for field_name in field_names])
	if index_name == "unitel":
		# UNITEL: Join Fullname fields with space for matching
		sel_fields = ",' ',".join(field_names)
		sel_fields = f"CONCAT({sel_fields})"
		whr_clause = f"{sel_fields} LIKE '%{q}%'"
	sql = sql_tmpl.format(sel_fields, index_name, whr_clause, qsize)

	# #########################
	# DEBUG-INFO: SQL Query
	if bool(debug): print(10*'#' + '\n# OPENSEARCH SQL: %s\n'%sql +10*'#')
	# #########################

	# Prepare HTTP Request
	headers = {"Content-Type": "application/json"}
	data = { "query": sql }

	# #########################
	# Execute HTTP Request in case of SQL with POST!
	# #########################
	client = get_opensearch_client(self)
	response = {}
	try:
		response = client.transport.perform_request(method='POST', url='/_plugins/_sql', headers=headers, params=None, body=data)
	except opensearchpy.exceptions.NotFoundError as e:
		standard.writeError(self, 'OpenSearch: %s'%(e.error))

	# Postprocess Response
	datarows = response.get('datarows') or []
	terms = []
	if datarows:
		if index_name=='unitel':
			# #########################
			# UNIBE-CUSTOM: UNITEL
			# Suggest words (fullname) shall not get splitted into single words
			# #########################
			terms = [row[0] for row in datarows]
		else:
			# STANDARD: Suggest words (keywords) shall get splitted into single, stripped words
			for row in datarows:
				row_content = ''
				# Concatenate all field values of a row to a single string 
				# because OpenSearch SQL plugin does not support CONCAT/ISNULL
				for i in range(0,len(field_names)):
					s = '%s '%(str(row[i]))
					row_content += s
				terms.extend(re.findall(r'[\w]+|[^\s\w]',row_content))
			terms = [ re.sub(r'[^\w\s]','',w) for w in terms if q.lower() in w.lower() ]

	terms = sorted(set(terms), key=lambda x: x.lower()) # remove duplicates and sort

	# #########################
	# DEBUG-INFO: Result-List
	if bool(debug): print('OPENSEARCH RESULT: %s'%(terms))
	# #########################

	return list(terms)


def get_suggest_fieldsets(self):
	# Get configured json-list-formatted field sets opensearch.suggest.fields.$index_name for any index name
	# E.g. opensearch.suggest.fields.myzms = ["title","attr_dc_subject","attr_dc_description"]
	# At least one fieldset with index_name = zms root element id and a default fieldset will be returned
	key_prefix = 'opensearch.suggest.fields.'
	default = '["title","attr_dc_subject","attr_dc_description"]'
	# Define default fieldset for index_name = zms root element id
	fieldsets = { self.getRootElement().getHome().id : json.loads(default) }
	# Get all configured fieldsets (maybe overwrite default fieldset)
	property_names = [k for k in list(self.getConfProperties(inherited=True)) if k.lower().startswith(key_prefix)]
	# If there are no client conf data check if there are any properties in the portal conf
	# TODO: Remove this fallback to portal conf and take the next parent node with zcatalog_adapters
	if not property_names and self.getPortalMaster():
		property_names = [k for k in list(self.getPortalMaster().getConfProperties().keys()) if k.lower().startswith(key_prefix)]
	for property_name in property_names:
		index_name = property_name[len(key_prefix):]
		property_value = self.getConfProperty(property_name, default)
		if not isinstance(property_value, list):
			property_value = json.loads(str(property_value).replace('\'','\"'))
		fieldsets[index_name] = property_value
	return fieldsets


def opensearch_suggest(self, REQUEST=None):
	request = self.REQUEST
	q = request.get('q','Lorem')
	qsize = request.get('qsize', 12)
	debug = bool(int(request.get('debug',0)))
	prettify = bool(int(request.get('prettify',0)))

	# Get configured or default fieldsets that are used for extracting suggest terms
	fieldsets = get_suggest_fieldsets(self)

	# Get suggest terms for any configured opensearch.suggest.fields.$index_name
	# Example: opensearch.suggest.fields.unitel = ['Vorname','Nachname']
	suggest_terms = []
	resp_text = ''
	for index_name, field_names in fieldsets.items():
		suggest_terms.extend(get_suggest_terms(self, q=q, index_name=index_name, field_names=field_names, qsize=qsize, debug=debug))

	# Finally sort all terms and return as JSON-textTestBan
	suggest_terms = sorted(set(suggest_terms), key=lambda x: x.lower())
	if prettify:
		resp_text = json.dumps(suggest_terms, indent=4)
	else:
		resp_text = json.dumps(suggest_terms)
	return resp_text
