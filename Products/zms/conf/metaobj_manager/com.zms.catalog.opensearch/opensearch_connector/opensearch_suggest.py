import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import re
# Disable warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_suggest_terms(self, q='Lorem', index_name='myzms', field_names=['title','attr_dc_subject'], size=10, debug=False):
	url = self.getConfProperty('opensearch.url')
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
	sql = sql_tmpl.format(sel_fields, index_name, whr_clause, size)

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
	if index_name=='unitel':
		# #########################
		# UNIBE-CUSTOM: UNITEL
		#  Suggest words (fullname) shall not get splitted into single words
		# #########################
		terms = [row[0] for row in datarows]
	else:
		# MYZMS: Suggest words (keywords) shall get splitted into single, stripped words
		terms = [re.sub(r'[^\w\s]','',w) for row in datarows for w in re.split('; |,| ',row[0]) if q in w ]
	terms = sorted(set(terms), key=lambda x: x.lower()) # remove duplicates and sort

	# #########################
	# DEBUG-INFO: Result-List
	if bool(debug): print('OPENSEARCH RESULT: %s'%(terms))
	# #########################

	return list(terms)


def opensearch_suggest(self, REQUEST=None):
	request = self.REQUEST
	q = request.get('q','')
	debug = bool(int(request.get('debug',0)))
	index_name = self.getRootElement().getHome().id
	resp_text = ''
	suggest_terms = []
	# Get suggest terms from $index_name
	suggest_terms.extend(get_suggest_terms(self, q=q, index_name=index_name, field_names=['title','attr_dc_subject','attr_dc_description'], size=20, debug=debug))

	# #########################
	# UNIBE-CUSTOM:
	# Add another index "unitel" to get more suggest terms (names from university phonebook)
	# #########################
	suggest_terms.extend(get_suggest_terms(self, q=q, index_name='unitel', field_names=['Vorname','Nachname'], size=10, debug=debug))
	# #########################

	# Finally sort all terms and return as JSON-text
	suggest_terms = sorted(set(suggest_terms), key=lambda x: x.lower())
	resp_text = json.dumps(suggest_terms, indent=2)
	return resp_text
