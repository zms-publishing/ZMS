from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def bulk_opensearch_index(self, sources):
	# Returns a tuple of two numbers of succeeded and failed indexing actions
	client = self.opensearch_get_client(self)
	index_name = self.getRootElement().getHome().id
	actions = []
	# Name adaption to opensearch schema
	for x in sources:
		# Create language specific opensearch id
		_id = "%s:%s"%(x['uid'],x.get('lang',self.getPrimaryLanguage()))
		d = {"_op_type":"index", "_index":index_name, "_id":_id}
		# Differenciate zms-object id and uid
		x['zmsid'] = x['id']
		x['id'] = x['uid']
		d.update(x)
		actions.append(d)
	if client:
		# The opensearch bulk helper function returns a tuple of two numbers 
		# of succeeded and failed indexing actions if stats_only is set to True.
		# Otherwise it returns the errors for failed actions as a list.
		return bulk(client, actions, stats_only=False)
	# No client available: no indexing possible
	return 0, len(actions)

def manage_opensearch_objects_add( self, objects):
	# Function applies to:
	#	ZMSZCatalogConnector.manage_objects_add 
	#	ZMSZCatalogConnector.reindex_page
	sources = [data for (node, data) in objects]
	try:
		success, failed = bulk_opensearch_index(self, sources)
		if failed and isinstance(failed,list):
			standard.writeError( self, "[OpenSearch] Failed to index objects %s" % failed)
	except Exception as e:
		standard.writeError( self, e)
		return 0, len(sources)
	return success, failed if isinstance(failed,int) else len(failed)