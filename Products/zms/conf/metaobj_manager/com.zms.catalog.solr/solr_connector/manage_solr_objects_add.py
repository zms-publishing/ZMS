import requests

def bulk_solr_add_documents(self, sources):
	actions = []
	# Name adaption to solr schema
	for x in sources:
		# Create language specific solr id
		_id = "%s:%s"%(x['uid'], x.get('lang',self.getPrimaryLanguage()))
		d = {"_id":_id}
		# Differenciate zms-object id and uid
		x['zmsid'] = x['id']
		x['id'] = x['uid']
		d.update(x)
		actions.append(d)

	# ${solr.url:http://localhost:8983/solr}
	# ${solr.username:admin}
	# ${solr.password:admin}
	# ${solr.ssl.verify:}
	url = self.getConfProperty('solr.url')
	if not url:
		return None
	username = self.getConfProperty('solr.username', 'admin')
	password = self.getConfProperty('solr.password', 'admin')
	auth = (username,password)

	index_name = self.getRootElement().getHome().id
	response = requests.post('%s/%s/update'%(url,index_name), auth=auth, json=actions)
	# print(f"Status Code: {response.status_code}, Response: {response.json()}")
	response = requests.post('%s/%s/update'%(url,index_name), auth=auth, json={'commit':{}})
	# print(f"Status Code: {response.status_code}, Response: {response.json()}")

	return 0, len(actions)

def manage_solr_objects_add( self, objects):
	# Function applies to:
	#	ZMSZCatalogConnector.manage_objects_add 
	#	ZMSZCatalogConnector.reindex_page
	sources = [data for (node, data) in objects]
	try:
		failed, success = bulk_solr_add_documents(self, sources)
	except Exception as e:
		print(e)
		return 0, len(sources)
	return success, failed or 0