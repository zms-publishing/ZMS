from Products.zms import content_extraction
import json
import requests
from requests.auth import HTTPBasicAuth
# import pdb

def add_docmt_to_opensearch_index(self):
	request = self.REQUEST
	self.zmi_page_request(self,request)
	request.set('preview', None)
	# Determine the page to be indexed
	this_page = [e for e in self.breadcrumbs_obj_path() if e.isPage() or e.meta_id=='ZMSFile'][-1]
	self = this_page
	lang = request.get('lang', self.getPrimaryLanguage())
	# OpenSearch document ID id is the uid of the node plus the language
	_id = '%s:%s'%(self.get_uid(), lang)

	url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
	# ID of opensearch index is ZMS multisite root node id or explicitly given by request variable 'opensearch_index_id'
	root_id = self.getRootElement().getHome().id
	index_id = request.get('opensearch_index_id',root_id)
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
	auth = HTTPBasicAuth(username,password)

	# From ZMSZCatalogAdapter.get_sitemap.add_catalog_index.to_xml()
	def to_xml(o):
		xml = ''
		if isinstance(o, list):
			for i in o:
				xml += '<%s>'%i['__nodeName__']
				xml += to_xml(i)
				xml += '</%s>'%i['__nodeName__']
		elif isinstance(o, dict):
			for k in [x for x in o if x != '__nodeName__']:
				xml += '<%s>'%k
				xml += to_xml(o[k])
				xml += '</%s>'%k
		else:
			xml = str(o)
		return xml

	content_obj = {}

	# [1] Add basic fields
	content_obj['id'] = self.get_uid()
	content_obj['uid'] = self.get_uid()
	content_obj['zmsid'] = '%s_%s'%(self.id,lang)
	content_obj['home_id'] = self.getHome().id
	content_obj['loc'] = '/'.join(self.getPhysicalPath())
	content_obj['index_html'] = self.getHref2IndexHtmlInContext(self.getRootElement(), REQUEST=request)
	content_obj['meta_id'] = self.meta_id
	# [2] Breadcrumbs as 'custom' field	
	breadcrumbs = []
	for obj in [x for x in self.breadcrumbs_obj_path()[1:-1] if x.isPage()]:
		breadcrumbs.append({
			'__nodeName__': 'breadcrumb',
			'loc': '/'.join(obj.getPhysicalPath()),
			'index_html': obj.getHref2IndexHtmlInContext(obj.getRootElement(), REQUEST=request),
			'title': obj.getTitlealt(request),
		})
	content_obj['custom'] = '<![CDATA[<custom><breadcrumbs>%s</breadcrumbs></custom>]]>'%(to_xml(breadcrumbs))

	# [3] Get attribute schema from ZCatalog adapter and 
	# the attribute content from the context node (self)
	zca = self.getCatalogAdapter()
	attrs = zca.getAttrs()
	for a in attrs:
		text = ''
		if self.meta_id == 'ZMSFile' and a == 'standard_html':
			text = content_extraction.extract_content(self, self.attr('file').getData())
		else:	
			text = content_extraction.extract_text_from_html(self.attr(a))
		content_obj[a] = text

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

	api_url = '%s/%s/_doc/%s'%(url, index_id, _id) 
	headers =  {"Content-Type":"application/json"}
	resp = requests.put(api_url, auth=auth, data=content_json, headers=headers, verify=verify)
	resp.json()
	return resp.status_code