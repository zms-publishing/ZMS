from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def bulk_elasticsearch_index(self, sources):
	client = self.elasticsearch_get_client(self)
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	actions = []
	# Name adaption to elasticsearch schema
	for x in sources:
		# Create language specific elasticsearch id
		_id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
		d = {"_op_type":"index", "_index":index_name, "_id":_id}
		# Differenciate zms-object id and uid
		x['zmsid'] = x['id']
		x['id'] = x['uid']
		d.update(x)
		actions.append(d)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_elasticsearch_objects_add( self, objects):
	# Function applies to:
	#	ZMSZCatalogConnector.manage_objects_add 
	#	ZMSZCatalogConnector.reindex_page
	sources = [data for (node, data) in objects]
	try:
		success, failed = bulk_elasticsearch_index(self, sources)
	except Exception as e:
		print(e)
		return 0, len(sources)
	return success, failed or 0