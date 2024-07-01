#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORT GENERAL LIBRARIES
import os
import re
import shutil
import tempfile
import urllib
import json
import requests
from io import BytesIO

# IMPORT ZMS LIBRARIES
from Products.zms import standard
from Products.zms import rest_api

# HTML LIBRARIES
from bs4 import BeautifulSoup

# IMPORT DOCX LIBRARIES
import docx
from docx.text.paragraph import Paragraph
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement, ns, parse_xml
from docx.shared import Emu


# #############################################
# Helper Functions 1: DOCX-XML
# 1. `add_page_number(run)` : add page number to text-run (e.g. footer)
# 2. `add_bottom_border(style)` : adds border-properties to paragraph-style-object
# Hint: the docx API does not support the page counter directly. 
# We have to create a custom footer with a page counter.
# #############################################

# XML-Helpers
def create_element(name):
	return OxmlElement(name)

def create_attribute(element, name, value):
	element.set(ns.qn(name), value)

# PAGE NUMBER
def add_page_number(run):
	fldChar1 = create_element('w:fldChar')
	create_attribute(fldChar1, 'w:fldCharType', 'begin')
	instrText = create_element('w:instrText')
	create_attribute(instrText, 'xml:space', 'preserve')
	instrText.text = "PAGE"
	fldChar2 = create_element('w:fldChar')
	create_attribute(fldChar2, 'w:fldCharType', 'end')
	run._r.append(fldChar1)
	run._r.append(instrText)
	run._r.append(fldChar2)

# BOOKMARK ZMS-ID
def prepend_bookmark(docx_block, bookmark_id):
	bookmark_start = create_element('w:bookmarkStart')
	create_attribute(bookmark_start, 'w:id', bookmark_id)
	create_attribute(bookmark_start, 'w:name', bookmark_id)
	bookmark_end = create_element('w:bookmarkEnd')
	create_attribute(bookmark_end, 'w:id', bookmark_id)
	try:
		docx_block._element.insert(0, bookmark_end)
		docx_block._element.insert(0, bookmark_start)
	except:
		pass

def add_hyperlink(docx_block, link_text, url):
	r_id = docx_block.part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
	hyper_link = create_element('w:hyperlink')
	create_attribute(hyper_link, 'w:id', r_id)
	hyper_link_run = create_element('w:r')
	hyper_link_run_prop = create_element('w:rPr')
	hyper_link_run_prop_style = create_element('w:rStyle')
	create_attribute(hyper_link_run_prop_style, 'w:val', 'Hyperlink')
	hyper_link_run_prop.append(hyper_link_run_prop_style)
	hyper_link_run.append(hyper_link_run_prop)
	hyper_link_text = create_element('w:t')
	hyper_link_text.text = link_text
	hyper_link_run.append(hyper_link_text)
	hyper_link.append(hyper_link_run)
	docx_block._p.append(hyper_link)


# BORDER BOTTOM
def add_bottom_border(style):
	border = create_element('w:pBdr') # pBdr = Paragraph border
	bottom = create_element('w:bottom')
	create_attribute(bottom, 'w:val', 'single')
	create_attribute(bottom, 'w:sz', '2')
	create_attribute(bottom, 'w:space', '9')
	create_attribute(bottom, 'w:color', '017D87')
	border.append(bottom)
	style.element.pPr.append(border) # pPr = Paragraph properties

# #############################################


# #############################################
# Helper Functions 2: HTML/Richtext-Processing 
# #############################################

# Clean HTML
def clean_html(html):
	# Clean comments, styles, empty tags
	html = re.sub(r'<!.*?->','', html)
	html = re.sub(r'<style.*?</style>','', html)
	html = standard.re_sub(r'\n|\t', ' ', html)
	html = standard.re_sub(r'\s\s', ' ', html)
	return html

# ADD RUNS TO DOCX-BLOCK
def add_runs(docx_block, bs_element):
	# Adding a minimum set of inline runs
	# any BeautifulSoup block element may contain
	# to the docx-block, e.g. <strong>, <em>, <a>
	if bs_element.children:
		for elrun in bs_element.children:
			if elrun.name == 'strong':
				docx_block.add_run(elrun.text).bold = True
			elif elrun.name == 'em':
				docx_block.add_run(elrun.text).italic = True
			elif elrun.name == 'a':
				add_hyperlink(docx_block = docx_block, link_text = elrun.text, url = elrun.get('href'))
				docx_block.add_run(' ')
			else:
				docx_block.add_run(str(elrun))
	else:
		docx_block.text(bs_element.text)

# ADD HTML-BLOCK TO DOCX
def add_htmlblock_to_docx(zmscontext, docx_doc, htmlblock, zmsid=None):
	# Clean HTML
	htmlblock = clean_html(htmlblock)

	# Apply BeautifulSoup and iterate over elements
	soup = BeautifulSoup(htmlblock, 'html.parser')

	# Counter for html elements: set bookmark before first element
	c = 0

	# Iterate over elements
	for element in soup.children:
		if element.name != None and element not in ['\n']:
			c+=1
			if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
				heading_level = int(element.name[1])
				p = docx_doc.add_heading(element.text, level=heading_level)
				if c==1: 
					prepend_bookmark(p, zmsid)

			elif element.name == 'p':
				p = docx_doc.add_paragraph()
				if c==1: 
					prepend_bookmark(p, zmsid)
				if element.has_attr('class'):
					if 'caption' in element['class']:
						p.style = docx_doc.styles['Caption']
					else:
						class_name = element['class'][0]
						style_name = (class_name in docx_doc.styles) and class_name or 'Normal'
						p.style = docx_doc.styles[style_name]
				add_runs(docx_block = p, bs_element = element)

			elif element.name in ['ul','ol']:
				def add_list(docx_doc, element, level=0, c=0):
					li_styles = {'ul':'ListBullet', 'ol':'ListNumber'}
					level_suffix = level!=0 and str(level+1) or ''
					for li in element.find_all('li', recursive=False):
						p = docx_doc.add_paragraph(li.contents[0].strip(), style='%s%s'%(li_styles[element.name], level_suffix))
						if c==1: 
							prepend_bookmark(p, zmsid)
						for ul in li.find_all(['ul','ol'], recursive=False):
							add_list(docx_doc, ul, level+1)
				add_list(docx_doc, element, level=0, c=c)

			elif element.name == 'table':
				caption = element.find('caption')
				if caption:
					p = docx_doc.add_paragraph(caption.text, style='Caption')
					if c==1: 
						prepend_bookmark(p, zmsid)
				rows = element.find_all('tr')
				cols = rows[0].find_all(['td','th'])
				table = docx_doc.add_table(rows=len(rows), cols=len(cols))
				table.style = 'Table Grid'
				table.alignment = WD_TABLE_ALIGNMENT.CENTER
				r=-1
				for row in rows:
					r+=1
					cells = row.find_all(['td','th'])
					for i, cl in enumerate(cells):
						table.cell(r,i).text = cl.text
						if cl.name == 'th':
							table.cell(r,i).paragraphs[0].runs[0].bold = True
				if not caption and c==1:
					prepend_bookmark(table, zmsid)


			elif element.name == 'img' or element.name == 'figure':
				if element.name == 'figure':
					element = element.find('img')
				if element.has_attr('src'):
					img_name = element['src'].split('/')[-1]
					if not element['src'].startswith('http'):
						src_url0 = zmscontext.absolute_url().split('/content/')[0]
						src_url1 = element['src'].split('/content/')[-1]
						element['src'] = '%s/content/%s'%(src_url0, src_url1)

				maxwidth = 460
				imgwidth = element.has_attr('width') and int(float(element['width'])) or None
				if imgwidth:
					scale =  imgwidth>maxwidth and imgwidth/maxwidth or 1
					imgwidth = imgwidth/scale
				else:
					imgwidth = maxwidth

				try:
					response = requests.get(element['src'])
					with open(img_name, 'wb') as f:
						f.write(response.content)
					docx_doc.add_picture(img_name, width=Emu(imgwidth*9525))
					if c==1:
						prepend_bookmark(docx_doc.paragraphs[-1], zmsid)
				except:
					pass

			elif element.name == 'div':
				child_tags = [e.name for e in element.children if e.name]
				if 'em' in child_tags or 'strong' in child_tags:
					p = docx_doc.add_paragraph()
					if c==1: 
						prepend_bookmark(p, zmsid)
					if element.has_attr('class'):
						class_name = element['class'][0]
						style_name = (class_name in docx_doc.styles) and class_name or 'Normal'
						p.style = docx_doc.styles[style_name]
					add_runs(docx_block = p, bs_element = element)
				else:
					div_html = ''.join([str(e) for e in element.children])
					add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)

			elif element.name == 'a':
				# Hyperlink containing a block element 
				div_html = ''.join([str(e) for e in element.children])
				add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)

			elif element.name == 'hr':
				# ignore horizontal rule
				pass

			else:
				p = docx_doc.add_paragraph(str(element))
				if c==1: 
					prepend_bookmark(p, zmsid)

	return docx_doc

# #############################################


# #############################################
# Helper Functions 3: Set Docx-Styles
# #############################################
def set_docx_styles(doc):
	styles = doc.styles
	# Custom colors: #017D87
	custom_color1 = docx.shared.RGBColor(1, 125, 135)
	# Page margins
	doc.sections[0].top_margin = Emu(120*9525)
	# Normal
	styles['Normal'].font.name = 'Arial'
	styles['Normal'].font.size = Pt(9)
	styles['Normal'].paragraph_format.space_after = Pt(6)
	styles['Normal'].paragraph_format.space_before = Pt(6)
	styles['Normal'].paragraph_format.line_spacing = 1.35
	# Headlines derived from Normal
	styles['Heading 1'].basedOn = doc.styles['Normal']
	styles['Heading 1'].font.size = Pt(24)
	styles['Heading 1'].font.color.rgb = custom_color1
	styles['Heading 2'].basedOn = doc.styles['Normal']
	styles['Heading 2'].font.size = Pt(18)
	styles['Heading 2'].font.color.rgb = custom_color1
	styles['Heading 3'].basedOn = doc.styles['Normal']
	styles['Heading 3'].font.size = Pt(12)
	styles['Heading 3'].font.bold = True
	styles['Heading 3'].font.color.rgb = custom_color1
	# More styles derived from Normal
	styles.add_style('Description', WD_STYLE_TYPE.PARAGRAPH)
	styles['Description'].basedOn = doc.styles['Normal']
	styles['Description'].font.name = 'Arial'
	styles['Description'].font.size = Pt(9)
	styles['Description'].font.italic = True
	styles['Description'].font.color.rgb = custom_color1
	styles['Description'].paragraph_format.space_after = Pt(18)
	styles['Description'].paragraph_format.line_spacing = 1.35
	add_bottom_border(styles['Description'])
	styles['Caption'].font.size = Pt(8)
	styles['Caption'].font.italic = True
	styles['Caption'].font.color.rgb = custom_color1
	styles['Caption'].paragraph_format.space_before = Pt(14)
	styles['Caption'].paragraph_format.space_after = Pt(4)
	styles.add_style('Hyperlink', WD_STYLE_TYPE.CHARACTER)
	styles['Hyperlink'].font.color.rgb = custom_color1
	styles['Hyperlink'].font.underline = True
	styles['Header'].font.size = Pt(8)
	styles['footer'].font.size = Pt(8)
	
	return doc

# #############################################



# #############################################
# Helper Functions 4: GET DOCX NORMALIZED JSON
# #############################################

# The function creates a normalized JSON stream of 
# a PAGE-like ZMS node. This JSON stream is used for 
# transforming the content to DOCX. 
# It is a list of dicts (key/value-pairs), where the 
# first dict is representing the container meta data
# and the following blocks are representing the PAGEELEMENTS
# of the document.
# Each object dictionary has the following keys:
# - id: the id of the node
# - meta_id: the meta_id of the node
# - parent_id: the id of the parent node
# - parent_meta_id: the meta_id of the parent node
# - title: the title of the node
# - description: the description of the node
# - last_change_dt: the last change date of the node
# - docx_format: the format of the content (html/xml/image 
#   or text-stylename e.g.'Normal')
# - content: the content of the node

# Any PAGEELEMENT-node may have a specific 'standard_json_docx'
# attribute which preprocesses it's ZMS content model close to
# the translation into the DOCX model. The key 'docx_format'
# is used to determine the style of the content block.

# If this attribute method (py-primtive) is not available, 
# the object's class standard_html-method is used to get the 
# content, so that the (maybe not optimum) html will be 
# transformed to DOCX.

# Depending on the complexity of the content it's JSON 
# representation may consist of ore or multiple key/value-
# sequences. Any of these blocks will create a new block 
# element (e.g. paragraph) in the DOCX document.


def apply_standard_json_docx(self):

	zmscontext = self
	request = zmscontext.REQUEST

	id = zmscontext.id
	meta_id = zmscontext.meta_id
	parent_id = zmscontext.id
	parent_meta_id = zmscontext.meta_id 
	title = zmscontext.attr('title')
	description = zmscontext.attr('attr_dc_description')
	last_change_dt = zmscontext.attr('change_dt') or zmscontext.attr('created_dt')
	url = zmscontext.getHref2IndexHtml(request)

	# 1st block is container meta data
	blocks = [
		{
			'id':id,
			'url':url,
			'meta_id':meta_id,
			'parent_id':parent_id,
			'parent_meta_id':parent_meta_id,
			'title':title,
			'description':description,
			'last_change_dt':last_change_dt
		}
	]

	# Sequence all pageelements
	for pageelement in zmscontext.filteredChildNodes(request,zmscontext.PAGEELEMENTS):
		if pageelement.attr('change_dt') and pageelement.attr('change_dt') >= last_change_dt:
			last_change_dt = pageelement.attr('change_dt')
		json_block = []
		json_block = pageelement.attr('standard_json_docx')
		if not json_block:
			html = ''
			try:
				html = pageelement.getBodyContent(request)
				# Clean html data
				html = clean_html(html)
			except:
				html = '<table>'
				html += '<caption>Rendering Error: %s</caption>' % pageelement.meta_id
				attrs = [d['id'] for d in zmscontext.getMetaobjAttrs(pageelement.meta_id) if d['type'] not in ['dtml','zpt','py','constant','resource','interface']]
				for attr in attrs:
					html += '<tr><td>%s</td><td>%s</td></tr>' % (attr, pageelement.attr(attr))
				html += '</table>'
			# Create a json block
			json_block = [{
				'id': pageelement.id,
				'meta_id': pageelement.meta_id,
				'parent_id': pageelement.getParentNode().id,
				'parent_meta_id': pageelement.getParentNode().meta_id,
				'docx_format': 'html',
				'content': html
			}]
		blocks.extend(json_block)

	# Update last_change_dt
	blocks[0]['last_change_dt'] = last_change_dt

	return blocks


# #############################################
# MAIN function for DOCX-Generation
# #############################################
def manage_export_pydocx(self):
	request = self.REQUEST

	# #############################################
	# 1. INIT DOCUMENT
	# #############################################
	doc = docx.Document()	# Hint: may use template like docx.Document('template.docx')

	# #############################################
	# 2. SET DOCX STYLES
	# #############################################
	doc = set_docx_styles(doc)

	# #############################################
	# 3. ITERATE JSON CONTENT TO DOCX
	# #############################################
	# zmsdoc = self.attr('standard_json')
	zmsdoc = apply_standard_json_docx(self)
	heading = zmsdoc[0]
	blocks = zmsdoc[1:]

	dt = standard.getLangFmtDate(self, heading.get('last_change_dt',''), 'eng', '%Y-%m-%d')
	url = heading.get('url','').replace('nohost','localhost')
	doc.sections[0].header.paragraphs[0].text = '%s\t\t%s\nURL: %s'%(heading.get('title',''), dt, url)
	add_page_number(doc.sections[0].footer.paragraphs[0].add_run('Seite '))
	
	doc.add_heading(heading.get('title',''), level=1)
	prepend_bookmark(doc.paragraphs[-1], heading.get('id',''))
	
	if heading.get('description','')!='':
		p = doc.add_paragraph(heading.get('description',''))
		p.style = doc.styles['Description']
	
	docx_elements = []
	# Transform JSON content to DOCX elements
	for block in blocks:
		v = block['content']
		# #############################################
		# [1] HTML-BLOCK (e.g. richtext with inline styles, just a minimum set of inline elements)
		if v and block['docx_format'] == 'html':
			add_htmlblock_to_docx(zmscontext=self, docx_doc=doc, htmlblock=v, zmsid=block['id'])
		# #############################################
		# [2] XML-BLOCK
		elif v and block['docx_format'] == 'xml':
			# Create a paragraph object from parsed xml
			parsed_xml = parse_xml(v)
			doc.add_paragraph()
			# Replace last paragraph with parsed xml
			doc.element.body[-1] = parsed_xml
		# #############################################
		# [3] IMAGE-BLOCK
		elif v and block['docx_format'] == 'image':
			# Add image to document
			image_url = v
			resp = requests.get(image_url)
			image_file = BytesIO(resp.content)
			# Add a paragraph containing the image as run
			# see: /python-docx/src/docx/document.py
			p = doc.add_paragraph()
			r = p.add_run()
			# Normalize image width to 460px
			r.add_picture(image_file, width=Emu(460*9525))
			prepend_bookmark(p, block['id'])
		# #############################################
		# [4] TEXT-BLOCK with given style
		else:
			# Add text block with given style to document
			p = doc.add_paragraph(v, style=block['docx_format'])
			prepend_bookmark(p, block['id'])

	# Save document in temporary directory
	fn = '%s.docx'%(self.id_quote(self.getTitlealt(request)))
	tempfolder = tempfile.mkdtemp()
	docx_filename = os.path.join(tempfolder, fn)
	doc.save(docx_filename)
	
	# Read the docx file
	with open(docx_filename, 'rb') as f:
		data = f.read()

	# Remove the temporary folder
	shutil.rmtree(tempfolder)

	# Set the HTTP response headers
	request.RESPONSE.setHeader('Content-Disposition', f'inline;filename={fn}')
	request.RESPONSE.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

	# msg = 'DOCX-Export erfolgreich: %s'%fn
	# request.response.redirect(standard.url_append_params('%s/manage_main'%self.absolute_url(),{'lang':request['lang'],'manage_tabs_message':msg}))

	# Return the data of the docx file
	return data