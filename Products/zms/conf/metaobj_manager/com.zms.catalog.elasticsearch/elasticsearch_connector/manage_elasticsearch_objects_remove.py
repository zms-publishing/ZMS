from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

langs = ['ger','eng']

def bulk_elasticsearch_delete(self, sources):
	client = self.elasticsearch_get_client(self)
	index_name = self.getConfProperty('elasticsearch.index_name', self.getRootElement().getHome().id )
	actions = []
	# Name adaption to elasticsearch schema
	for x in sources:
		# Create language specific elasticsearch id
		for lang in globals()['langs']:
			_id = "%s:%s"%(x['uid'],lang)
			d = {"_op_type":"delete", "_index":index_name, "_id":_id}
			actions.append(d)
	if client: 
		return bulk(client, actions)
	return 0, len(actions)

def manage_elasticsearch_objects_remove( self, nodes):
	sources = [{'uid':x.get_uid()} for x in nodes]
	for node in nodes:
		# Set node's language list as global variable.
		global langs
		langs = node.getLangIds()
		break
	try:
		success, failed = bulk_elasticsearch_delete(self, sources)
	except Exception as e:
		standard.writeBlock( self, str(e))
		return 0, len(sources)
	return success, failed or 0