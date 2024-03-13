import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import re
# Disable warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_suggest_terms(self, q='Lorem', index_name='myzms', field_names=['title','attr_dc_subject'], qsize=10, debug=False):
	url = self.getConfProperty('opensearch.url').rstrip('/')
	if not url:
		return None
	url += '/_plugins/_sql'
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	auth = HTTPBasicAuth(username,password)
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))

	# Assemble SQL Query using f-strings
	sql_tmpl = "SELECT CONCAT({}) AS keywords FROM {} WHERE {} LIMIT {}"
	sel_fields = ", ' ', ".join(field_names)
	whr_clause = " OR ".join([f"({field_name} LIKE '%{q}%')" for field_name in field_names])
	if index_name == "unitel":
		whr_clause = f"CONCAT({sel_fields}) LIKE '%{q}%'"
	sql = sql_tmpl.format(sel_fields, index_name, whr_clause, qsize)

	# #########################
	# DEBUG-INFO: SQL Query
	if bool(debug): print(10*'#' + '\n# OPENSEARCH SQL: %s\n'%sql +10*'#')
	# #########################

	# Prepare HTTP Request
	headers = {"Content-Type": "application/json"}
	data = { "query": sql }

	# Execute HTTP Request
	response = requests.post(url, headers=headers, data=json.dumps(data),auth=auth, verify=verify)

	# Postprocess Response
	datarows = response.json().get('datarows') or []
	if datarows:
		# Remove empty rows
		datarows = [row for row in datarows if row[0] is not None]
	if index_name=='unitel':
		# #########################
		# UNIBE-CUSTOM: UNITEL
		#  Suggest words (fullname) shall not get splitted into single words
		# #########################
		terms = [row[0] for row in datarows]
	else:
		# MYZMS: Suggest words (keywords) shall get splitted into single, stripped words
		terms = [ re.sub(r'[^\w\s]','',w) for row in datarows for w in re.split('; |,| ',row[0]) if q.lower() in w.lower() ]
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
	if not property_names:
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
	# Get configured or default fieldsets that are used for extracting suggest terms
	fieldsets = get_suggest_fieldsets(self)
	resp_text = ''
	suggest_terms = []
	# Get suggest terms for any configured opensearch.suggest.fields.$index_name
	# Example: opensearch.suggest.fields.unitel = ['Vorname','Nachname']
	for index_name, field_names in fieldsets.items():
		suggest_terms.extend(get_suggest_terms(self, q=q, index_name=index_name, field_names=field_names, qsize=qsize, debug=debug))
	# Finally sort all terms and return as JSON-text
	suggest_terms = sorted(set(suggest_terms), key=lambda x: x.lower())
	resp_text = json.dumps(suggest_terms, indent=2)
	return resp_text
