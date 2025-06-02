from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def bulk_elasticsearch_delete(self, actions):
	client = self.elasticsearch_get_client(self)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_elasticsearch_objects_clear( self, home_id):
	index_names = []
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	index_names.append(index_name)
	query = {
		"query": {
			"query_string": {
				"query": "home_id: \"%s\""%home_id
			}
		}
	}
	client = self.elasticsearch_get_client(self)
	response = client.search(body = json.dumps(query), index = index_names, size=10000, _source_includes=['home_id'])
	hits = response["hits"]["hits"]
	actions = [{"_op_type":"delete", "_index":x['_index'], "_id":x['_id']} for x in hits]
	success, failed = bulk_elasticsearch_delete(self, actions)
	return success, failed or 0