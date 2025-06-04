from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def manage_opensearch_destroy(self):
	index_name = self.getRootElement().getHome().id
	client = self.opensearch_get_client(self)
	resp_text = '//RESPONSE\n'
	try:
		response = client.indices.delete(index_name)
	except opensearchpy.exceptions.RequestError as e:
		resp_text += '//%s\n'%(e.error)
	resp_text += json.dumps(response, indent=2)
	return resp_text