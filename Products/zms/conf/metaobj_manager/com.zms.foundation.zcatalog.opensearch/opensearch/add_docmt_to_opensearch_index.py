from Products.zms import standard
import json
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
# import pdb

def extract_text_from_html(html):
	soup = BeautifulSoup(html, features="html.parser")
	text = soup.get_text() \
		.replace('\n',' ') \
		.replace('\t',' ') \
		.replace('\"',' ')
	text = ' '.join(text.split())
	return text

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
	tika_url = self.getConfProperty('opensearch.parser', 'http://localhost:9998/tika')

	zca = self.getCatalogAdapter()
	attrs = zca.getAttrs()
	content_obj = {}
	for a in attrs:
		html = ''
		text = ''
		if self.meta_id == 'ZMSFile' and a == 'standard_html':
			if tika_url:
				f = self.attr('file').data
				headers = {'Accept': 'application/json'}
				try:
					r = requests.put(tika_url, headers=headers, data=f)
					html = r.json().get('X-TIKA:content')
					text = extract_text_from_html(html)
				except Exception as e:
					# Catch all exceptions, most likely connection refused
					standard.writeError(self, "[add_docmt_to_opensearch_index]: %s"%str(e))
			else:
				try:
					# pdfminer.six (https://github.com/pdfminer/pdfminer.six)
					# Pdfminer.six is a community maintained fork of the original PDFMiner. 
					# It is a tool for extracting information from PDF documents. It focuses
					# on getting and analyzing text data. Pdfminer.six extracts the text 
					# from a page directly from the sourcecode of the PDF. 
					# pip install pdfminer.six
					from io import BytesIO, StringIO
					from pdfminer.converter import TextConverter
					from pdfminer.layout import LAParams
					from pdfminer.pdfdocument import PDFDocument
					from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
					from pdfminer.pdfpage import PDFPage
					from pdfminer.pdfparser import PDFParser
					output_string = StringIO()
					ob_file = self.attr('file')
					in_file = BytesIO(ob_file.getData())
					parser = PDFParser(in_file)
					standard.writeError(self,"pdfminer: doc")
					doc = PDFDocument(parser)
					rsrcmgr = PDFResourceManager()
					device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
					interpreter = PDFPageInterpreter(rsrcmgr, device)
					for page in PDFPage.create_pages(doc):
						interpreter.process_page(page)
					text = output_string.getvalue()
				except:
					standard.writeError(self,"can't pdfminer")
					text = '@@%s:%s'%('/'.join(self.getPhysicalPath()),'file')
		else:	
			text = extract_text_from_html(self.attr(a))
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
