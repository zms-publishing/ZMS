import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import re
from Products.zms import standard
# Disable warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_suggest_terms(self, q='Lorem', index_name='myzms', field_names=['title','attr_dc_subject'], qsize=10, debug=False):
	url = self.getConfProperty('elasticsearch.url').rstrip('/')
	if not url:
		return None
	url += '/_sql'
	username = self.getConfProperty('elasticsearch.username', 'admin')
	password = self.getConfProperty('elasticsearch.password', 'admin')
	auth = HTTPBasicAuth(username,password)
	verify = bool(self.getConfProperty('elasticsearch.ssl.verify', False))

	# Assemble SQL Query using f-strings
	sql_tmpl = "SELECT {} AS keywords FROM {} WHERE {} LIMIT {}"
	sel_fields = "''"
	for fn in field_names:
		sel_field = f"CONCAT(CONVERT({fn},STRING),' ')"
		sel_fields = f"CONCAT({sel_fields},{sel_field})"
	whr_clause = " OR ".join([f"QUERY('*{q}*','default_field={field_name}')" for field_name in field_names])
	sql = sql_tmpl.format(sel_fields, index_name, whr_clause, qsize)

	# #########################
	# DEBUG-INFO: SQL Query
	if bool(debug): print(10*'#' + '\n# ELASTICEARCH SQL: %s\n'%sql +10*'#')
	# standard.writeBlock(self,(10*'#' + '\n# ELASTICEARCH SQL: %s\n'%sql +10*'#'))
	# #########################


	# Prepare HTTP Request
	headers = {"Content-Type": "application/json"}
	data = { "query": sql }

	# Execute HTTP Request
	response = requests.post(url, headers=headers, data=json.dumps(data),auth=auth, verify=verify)

	# Postprocess Response
	terms = []
	datarows = response.json().get('rows') or []
	if datarows:
		# Remove empty rows
		datarows = [row for row in datarows if row[0] is not None]
		# Suggest words (keywords) shall get splitted into single, stripped words
		terms = [ re.sub(r'[^\w\s]','',w) for row in datarows for w in re.split('; |,|-|. | ',row[0]) if q.lower() in w.lower() ]
		terms = sorted(set(terms), key=lambda x: x.lower()) # remove duplicates and sort

	# #########################
	# DEBUG-INFO: Result-List
	if bool(debug): print('ELASTICEARCH RESULT: %s'%(terms))
	# #########################

	return list(terms)


def get_suggest_fieldsets(self):
	# Get configured json-list-formatted field sets elasticsearch.suggest.fields.$index_name for any index name
	# E.g. elasticsearch.suggest.fields.myzms = ["title","attr_dc_subject","attr_dc_description"]
	# At least one fieldset with index_name = zms root element id and a default fieldset will be returned
	key_prefix = 'elasticsearch.suggest.fields.'
	default = '["title","attr_dc_subject","attr_dc_description"]'
	# Define default fieldset for index_name = zms root element id
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	fieldsets = { index_name : json.loads(default) }
	# Get all configured fieldsets (maybe overwrite default fieldset)
	property_names = []
	try:
		property_names = [k for k in list(self.getConfProperties().keys()) if k.lower().startswith(key_prefix)]
	except:
		pass
	# If there are no client conf data check if there are any properties in the portal conf
	# TODO: Remove this fallback to portal conf and take the next parent node with zcatalog_adapters
	if not property_names and self.getPortalMaster():
		try:
			property_names = [k for k in list(self.getPortalMaster().getConfProperties().keys()) if k.lower().startswith(key_prefix)]
		except:
			pass
	for property_name in property_names:
		index_name = property_name[len(key_prefix):]
		if not isinstance(property_value, list):
			property_value = json.loads(str(property_value).replace('\'','\"'))
		fieldsets[index_name] = property_value
	# print(fieldsets)
	return fieldsets


def elasticsearch_suggest(self, REQUEST=None):
	request = self.REQUEST
	q = request.get('q','Lorem')
	qsize = request.get('qsize', 12)
	debug = bool(int(request.get('debug',1)))
	# Get configured or default fieldsets that are used for extracting suggest terms
	fieldsets = get_suggest_fieldsets(self)
	resp_text = ''
	suggest_terms = []
	# Get suggest terms for any configured elasticsearch.suggest.fields.$index_name
	# Example: elasticsearch.suggest.fields.unitel = ['Vorname','Nachname']
	for index_name, field_names in fieldsets.items():
		suggest_terms.extend(get_suggest_terms(self, q=q, index_name=index_name, field_names=field_names, qsize=qsize, debug=debug))
	# Finally sort all terms and return as JSON-text
	suggest_terms = sorted(set(suggest_terms), key=lambda x: x.lower())
	resp_text = json.dumps(suggest_terms, indent=2)
	return resp_text