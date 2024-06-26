from Products.zms import standard
import requests

langs = ['ger','eng']

def bulk_solr_delete_documents(self, sources):
	ids = []
	# Name adaption to solr schema
	for x in sources:
		# Create language specific solr id
		for lang in globals()['langs']:
			_id = "%s:%s"%(x['uid'],lang)
		ids.append(_id)

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
	response = requests.post('%s/%s/update'%(url,index_name), auth=auth, json={'delete':ids, 'commit':{}})
	print(f"Status Code: {response.status_code}, Response: {response.json()}")

	return 0, len(ids)

def manage_solr_objects_remove( self, nodes):
	sources = [{'uid':x.get_uid()} for x in nodes]
	for node in nodes:
		# Set node's language list as global variable.
		global langs
		langs = node.getLangIds()
		break
	try:
		failed, success = bulk_solr_delete_documents(self, sources)
	except Exception as e:
		standard.writeBlock( self, str(e))
		return 0, len(sources)
	return success, failed or 0