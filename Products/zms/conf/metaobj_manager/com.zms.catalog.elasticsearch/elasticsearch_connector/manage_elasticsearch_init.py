from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def manage_elasticsearch_init( self):
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	schema = self.getConfProperty('elasticsearch.schema','{}')
	resp_text = '//RESPONSE\n'
	client = self.elasticsearch_get_client(self)
	try:
		response = client.indices.create(index_name, body=schema)
	except opensearchpy.exceptions.RequestError as e:
		if 'resource_already_exists_exception' != e.error:
			raise
		else:
			client.indices.delete(index_name)
			response = client.indices.create(index_name, body=schema)
			resp_text += '//%s\n'%(e.error)
	resp_text += json.dumps(response, indent=2)
	# concatinate elasticsearch response and schema
	resp_text += '\n\n'
	resp_text += '//SCHEMA\n'
	resp_text += schema

	return resp_text