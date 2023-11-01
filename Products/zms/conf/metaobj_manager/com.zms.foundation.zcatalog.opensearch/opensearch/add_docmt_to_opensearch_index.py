from Products.zms import content_extraction
import json
import requests
from requests.auth import HTTPBasicAuth
# import pdb

def add_docmt_to_opensearch_index(self):
	request = self.REQUEST
	self.zmi_page_request(self,request)
	# Determine the page to be indexed
	this_page = [e for e in self.breadcrumbs_obj_path() if e.isPage() or e.meta_id=='ZMSFile'][-1]
	self = this_page
	docmt_id = self.get_uid()

	url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
	# ID of opensearch index is ZMS multisite root node id or explicitly given by request variable 'opensearch_index_id'
	root_id = self.getRootElement().getHome().id
	index_id = request.get('opensearch_index_id',root_id)
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
	auth = HTTPBasicAuth(username,password)

	zca = self.getCatalogAdapter()
	attrs = zca.getAttrs()
	zca = self.getCatalogAdapter()
	attrs = zca.getAttrs()
	content_obj = {}
	for a in attrs:
		html = ''
		text = ''
		if self.meta_id == 'ZMSFile' and a == 'standard_html':
			text = content_extraction.extract_content(self, self.attr('file').getData())
		else:	
			text = content_extraction.extract_text_from_html(self.attr(a))
		content_obj[a] = text
	content_obj['meta_id'] = self.meta_id

	### TEST
	# content_list.append(content_obj)
	# response.setHeader('Content-Type','text/json')
	# return json.dumps(content_obj)
	### README
	# https://realpython.com/api-integration-in-python/#rest-and-python-consuming-apis
	# https://opensearch.org/docs/latest/im-plugin/index/
	
	# Dashboard Exp. ZMS-Index with id = zms
	# http://localhost:5601/app/opensearch_index_management_dashboards#/index-detail/zms

	content_json = json.dumps(content_obj)

	# pdb.set_trace()

	api_url = '%s/%s/_doc/%s'%(url, index_id, docmt_id) 
	headers =  {"Content-Type":"application/json"}
	resp = requests.put(api_url, auth=auth, data=content_json, headers=headers, verify=verify)
	resp.json()
	return resp.status_code
