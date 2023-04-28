from Products.zms import standard
import json
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
# import pdb

def add_docmt_to_opensearch_index(self):
	request = self.REQUEST
	self.zmi_page_request(self,request)
	docmt_id = self.get_uid()

	url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
	# ID of opensearch index is ZMS multisite root node id or explicitly given by request variable 'opensearch_index_id'
	root_id = self.getRootElement().getHome().id
	index_id = request.get('opensearch_index_id',root_id)
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
	auth = HTTPBasicAuth(username,password)

	attrs = ['title','standard_html']
	content_obj = {}
	for a in attrs:
		html = self.attr(a)
		soup = BeautifulSoup(html, features="html.parser")
		text = soup.get_text() \
			.replace('\n',' ') \
			.replace('\t',' ') \
			.replace('\"',' ')
		text = ' '.join(text.split())
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
