import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch, RequestsHttpConnection
import re
import unicodedata
from Products.zms import standard


def remove_diacritics(text):
	"""
	Returns a string with all diacritics (aka non-spacing marks) removed.
	For example "Héllô" will become "Hello".
	Useful for comparing strings in an accent-insensitive fashion.
	Source: https://stackoverflow.com/questions/35783135/regex-match-a-character-and-all-its-diacritic-variations-aka-accent-insensiti
	"""
	normalized = unicodedata.normalize("NFKD", text)
	return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def get_suggest_terms(self, q='Lorem', index_name='myzms', field_names=['title','attr_dc_subject'], qsize=10, debug=False):
	if not q:
		return {}

	# Parse field names to fields: Field names can contain a "full" filter (e.g. "title|full") which defines
	# that the whole content should be returned. If there is no filter then only the highlights get returned.
	# Therefore the field names have to be parsed to {"name": string, "only_highlights": boolean} dictionaries.
	# We return the whole contents of the field if only_highlights = False.
	# If it's True we return the highlighted words only.
	fields = []
	for field_name in field_names:
		split = field_name.split('|')
		full = len(split) > 1 and split[1] == 'full'
		field = {
			"name": split[0],
			"only_highlights": not full
		}
		fields.append(field)

	query = {
		"size": qsize,
		"_source": False,
		"fields": [ field['name'] for field in fields ]
	}

	# This query is more performant if the fields are of type "search_as_you_type".
	# A "search-as-you-type" field creates 2-/3-gram subfields of this field. Additionally, it creates an index prefix subfield.
	# The OpenSearch search automatically/magically uses the prefixes to improve the query
	# and the performance (index-time solution).
	# The 2-/3-grams are used to weight the resulting hits based on the order of the terms.
	# More information at https://opensearch.org/docs/latest/field-types/supported-field-types/search-as-you-type/
	#
	# Query on "search_as_you_type" attribute: 
	# "((+attr:my +attr:autocomplete +ConstantScore(attr._index_prefix:quer)) | 
	#   (+attr._2gram:my autocomplete +ConstantScore(attr._index_prefix:autocomplete quer)) | 
	#   ConstantScore(attr._index_prefix:my autocomplete quer))~1.0" 
	#
	# The query gets executed the usual less performant way without order boosts
	# if the field is of type "text" (query-time solution):
	# "+attr:my +attr:autocomplete +attr:quer*"
	#
	# A "bool_prefix" multi-field query which uses the "and" operator checks each field separately to find a match:
	# "((+attr1:my +attr1:autocomplete +attr1:quer*) | (+attr2:my +attr2:autocomplete +attr2:quer*))~1.0"
	#
	# "simple_query_string" queries are different:
	# "+(attr1:my | attr2:my)~1.0 +(attr1:autocomplete | attr2:autocomplete)~1.0 +(attr1:quer* | attr2:quer*)~1.0"
	#
	query_fields = []
	for field in fields:
		query_fields.extend([f"{field['name']}", f"{field['name']}._2gram", f"{field['name']}._3gram"])
	query['query'] = {
		"multi_match": {
			"query": q,
			"type": "bool_prefix",
			"operator": "and", 
			"fields": query_fields
		}
	}
	
	if bool(debug):
		standard.writeLog(self, f"OpenSearch autosuggest query ({index_name}): {query}")

	# #########################
	# Execute search query
	# #########################
	client = self.opensearch_get_client(self)
	response = {}
	try:
		response = client.search(body = json.dumps(query), index = index_name)
	except opensearchpy.exceptions.NotFoundError as e:
		standard.writeError(self, 'OpenSearch: %s'%(e.error))
		return {}

	# Postprocess Response
	# Suggestions contains the suggestion strings (key) with its corresponing score (value)
	suggestions = {}
	hits = response['hits']['hits']
	q_terms = q.split()
	# Remove prefix (last term) from q_terms
	q_terms.pop()
	cleaned_q = remove_diacritics(q.lower())
	cleaned_q_terms = cleaned_q.split()
	# Remove prefix (last term) from cleaned_q_terms
	cleaned_q_prefix = cleaned_q_terms.pop()
	for hit in hits:
		# Extract matching fields if it is a multi-field query.
		matches = []
		if len(fields) == 1:
			matches.append({
				"content": hit['fields'][fields[0]['name']][0],
				"only_highlights": fields[0]['only_highlights']
				})
		else:
			# Check if field matches the query if there are multiple fields
			for field in fields:
				content = hit['fields'][field['name']][0]
				cleaned_content = remove_diacritics(content.lower())
				cleaned_content_terms = cleaned_content.split()
				is_matching = all(cleaned_q_term in cleaned_content_terms for cleaned_q_term in cleaned_q_terms) and \
					any(cleaned_content_term.startswith(cleaned_q_prefix) for cleaned_content_term in cleaned_content_terms)
				if is_matching:
					matches.append({
						"content": content,
						"only_highlights": field['only_highlights'],
						})
		
		for match in matches:
			if match['only_highlights']:
				# In this case only highlights/matching words get returned.
				# E.g. query = "Universität B":
				#   [
				#     "Universität Bern",
				#     "Universität Basel",
				#     ...	
				#   ]
				field_content_terms = match['content'].split()
				for term in field_content_terms:
					cleaned_term = remove_diacritics(term.lower())
					if cleaned_term.startswith(cleaned_q_prefix) and cleaned_term not in cleaned_q_terms:
						# Only the prefix match gets added here. The other terms don't get altered.
						term_without_non_word_chars = re.sub(r"[^\w-]+", "", term)
						suggestion_terms = q_terms.copy()
						suggestion_terms.append(term_without_non_word_chars)
						suggestion = ' '.join(suggestion_terms)
						if suggestion not in suggestions:
							suggestions[suggestion] = hit['_score']
			else:
				# In this case the whole content of matching fields is returned.
				# There is no need for postprocessing.
				if match['content'] not in suggestions:
					suggestions[match['content']] = hit['_score']
	
	# #########################
	# DEBUG-INFO: Result
	if bool(debug):
		standard.writeLog(self, f"OpenSearch autosuggest result ({index_name}): {suggestions}")
	# #########################

	return suggestions


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
	suggest_terms = {}
	resp_text = ''
	for index_name, field_names in fieldsets.items():
		index_suggest_terms = get_suggest_terms(self, q=q, index_name=index_name, field_names=field_names, qsize=qsize, debug=debug)
		# Only add suggestion if not already included. Update the matching score if it's included and the score is higher.
		for key in index_suggest_terms:
			if key not in suggest_terms or suggest_terms[key] < index_suggest_terms[key]:
				suggest_terms[key] = index_suggest_terms[key]
	
	# Finally sort all suggestions based on the score and return as JSON-text
	result = sorted(suggest_terms.items(), key=lambda item: item[1], reverse=True)
	# Only return keys of sorted items.
	result = [item[0] for item in result]
	if prettify:
		resp_text = json.dumps(result, indent=4)
	else:
		resp_text = json.dumps(result)
	return resp_text
