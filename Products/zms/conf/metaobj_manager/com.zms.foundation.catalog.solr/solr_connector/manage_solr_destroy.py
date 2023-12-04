from Products.zms import standard
import json
from urllib.parse import urlparse

def manage_solr_destroy( self):

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

	import requests
	index_name = self.getRootElement().getHome().id
	response = requests.post('%s/%s/update'%(url,index_name), auth=auth, json={'delete':{"query":"*"}, 'commit':{}})
	print(f"Status Code: {response.status_code}, Response: {response.json()}")

	resp_text += json.dumps(response, indent=2)
	return resp_text