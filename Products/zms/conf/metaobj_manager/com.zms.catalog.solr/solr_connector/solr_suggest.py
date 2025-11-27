from urllib.parse import urlparse
import json
import requests



def solr_suggest( self, REQUEST=None):
	request = self.REQUEST
	index_name = self.getConfProperty('solr.core', self.getRootElement().getHome().id)

	# TODO: implement suggest!
	url = self.getConfProperty('solr.url')
	if not url:
		return None
	host = urlparse(url).hostname
	port = urlparse(url).port
	ssl = urlparse(url).scheme=='https' and True or False
	verify = bool(self.getConfProperty('solr.ssl.verify', False))
	username = self.getConfProperty('solr.username', 'admin')
	password = self.getConfProperty('solr.password', 'admin')
	auth = (username,password)

	# Define the URL of the Solr select API.
	query_url = '{}/{}/suggest'.format(url, index_name)

	q = request.get('q','')
	fulltext_field = self.getConfProperty('solr.fulltext_field', 'standard_html')
	limit = int(REQUEST.get('limit',5))


	# Define the query parameters for the Solr suggest API.
	# Using 'fuzzy' method for suggestions.
	query_params = {
		"suggest": "true",
		"suggest.build": "true",
		'suggest.dictionary': 'default',
		'suggest.q': q,
		'suggest.method': 'fuzzy',
		'suggest.count': limit,
	}

	# IMPORTANT NOTE: Configure SOLR with solrconfig.xml to enable the suggest component.
	# For example, you can add the following to your solrconfig.xml:
	# ###############################################################################
	#   <!-- Suggest Component
	#        http://wiki.apache.org/solr/SuggestComponent
	#        A component to return suggestions for misspelled words, or
	#        suggestions for queries based on the contents of the index.
	#        This is not a replacement for the SpellCheckComponent, which
	#        provides spell checking and query rewriting.
	#    -->
	#   <requestHandler name="/suggest" class="solr.SearchHandler" startup="lazy">
	#     <lst name="defaults">
	#       <str name="suggest">true</str>
	#       <str name="suggest.dictionary">default</str>
	#     </lst>
	#     <arr name="components">
	#       <str>suggest</str>
	#     </arr>
	#   </requestHandler>

	#   <searchComponent name="suggest" class="solr.SuggestComponent">
	#     <lst name="suggester">
	#       <str name="name">default</str>
	#       <str name="lookupImpl">FuzzyLookupFactory</str>
	#       <str name="dictionaryImpl">DocumentDictionaryFactory</str>
	#       <str name="field">title</str>
	#       <str name="suggestAnalyzerFieldType">text_general</str>
	#     </lst>
	#   </searchComponent>
	# ###############################################################################
	# Further steps:
	# 1. Replace your_suggest_field with the field you want to use for suggestions.
	# 2. Reload or restart your Solr core after editing solrconfig.xml.
	# 3. Rebuild the suggester index (by calling with suggest.build=true at least once):
	#    e.g. http://localhost:8983/solr/mycore/suggest?suggest.build=true

 
	# Define the headers for the POST schema request.
	headers = {'Content-type': 'application/json'}
	# Send the GET request.
	response = requests.get(query_url, params=query_params, headers=headers)

	# Parse the response.
	data = response.json()
	
	return json.dumps(data, indent=4, sort_keys=False)