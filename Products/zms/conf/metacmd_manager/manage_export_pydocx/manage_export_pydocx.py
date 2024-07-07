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
import sys

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

# #############################################

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
		c = 0
		for elrun in [elrun for elrun in bs_element.children if elrun.name not in ['ul', 'ol', 'li', 'img']]:
			# Hint: ul/ol/li are handled as blocks in add_htmlblock_to_docx.add_list
			c += 1
			if elrun.name == 'br':
				docx_block.add_run('\n')
			elif elrun.name != None and elrun.text == '↵':
				docx_block.add_run('')
			elif elrun.name == 'strong':
				docx_block.add_run(elrun.text).bold = True
			elif elrun.name == 'q':
				docx_block.add_run(elrun.text, style='q')
			elif elrun.name == 'em':
				docx_block.add_run(elrun.text).italic = True
			elif elrun.name == 'a':
				add_hyperlink(docx_block = docx_block, link_text = elrun.text, url = elrun.get('href'))
				docx_block.add_run(' ')
			elif elrun.name == 'span':
				if elrun.has_attr('class'):
					class_name = elrun['class'][0]
					style_name = (class_name in doc.styles) and class_name or 'Default Paragraph Font'
					docx_block.add_run(elrun.text, style=style_name)
				else:
					docx_block.add_run(elrun.text)
			# #############################################
			## TO-DO: Add inline image to docx
			## Error: adding image as a block element 
			## may result in content replication
			# #############################################
			# elif elrun.name == 'img':
			# 	add_htmlblock_to_docx(zmscontext, doc, str(elrun), zmsid=None)
			# #############################################
			else:
				s = standard.pystr(elrun)
				if c == 1: # Remove trailing spaces on first text element of a block
					s = s.lstrip()
				docx_block.add_run(s)
	else:
		docx_block.text(standard.pystr(bs_element.text))

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
						p = docx_doc.add_paragraph(style='%s%s'%(li_styles[element.name], level_suffix))
						add_runs(docx_block = p, bs_element = li)
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
					img_src = element['src']
					if zmscontext.operator_getattr(zmscontext,zmsid).attr('imghires'):
						# Use high resolution image
						img_src = zmscontext.operator_getattr(zmscontext,zmsid).attr('imghires').getHref(zmscontext.REQUEST)
					img_name = img_src.split('/')[-1]
					if not img_src.startswith('http'):
						src_url0 = zmscontext.absolute_url().split('/content/')[0]
						src_url1 = img_src.split('/content/')[-1]
						if src_url1.startswith('/'): 
							# eg. ZMS assets starting with /++resource++zms_
							src_url1 = src_url1[1:]
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
						if src_url1.startswith('++resource++zms_'):
							# ZMS assets are not resized (alternative: use pass)
							# pass
							docx_doc.add_picture(img_name)
						else:
							docx_doc.add_picture(img_name, width=Emu(imgwidth*9525))
						os.remove(img_name)
						if c==1:
							try:
								prepend_bookmark(docx_doc.paragraphs[-1], zmsid)
							except:
								pass
					except:
						pass

			elif element.name == 'div':
				if element.has_attr('class') and (('ZMSGraphic' in element['class']) or ('graphic' in element['class'])):
					ZMSGraphic_html = ''.join([str(e) for e in element.children])
					add_htmlblock_to_docx(zmscontext, docx_doc, ZMSGraphic_html, zmsid)
				else:
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
						div_html = ''.join([standard.pystr(e) for e in element.children])
						add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)

			elif element.name == 'a':
				# Hyperlink just containing text
				if element.children and list(element.children)[0] == element.text:
					try:
						add_hyperlink(docx_block = docx_doc, link_text = element.text, url = element.get('href'))
					except:
						p = docx_doc.add_paragraph()
						if c==1: 
							prepend_bookmark(p, zmsid)
						add_runs(docx_block = p, bs_element = element)
				# Hyperlink containing a block element
				elif {'div','p','table','img'} & set([e.name for e in element.children]):
					div_html = ''.join([str(e) for e in element.children])
					add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)
				# Hyperlink containing inline elements
				else:
					p = docx_doc.add_paragraph()
					if c==1: 
						prepend_bookmark(p, zmsid)
					add_runs(docx_block = p, bs_element = element)

			elif element.name == 'hr':
				# Omit horizontal rule
				pass
			elif element.name == 'script':
				# Omit javascript
				pass
			elif element.name == 'form':
				p = docx_doc.add_paragraph(style='macro')
				p.add_run('<form>\n').font.bold = True
				if c==1: 
					prepend_bookmark(p, zmsid)
				input_field_count = 0
				for input_field in element.find_all('input', recursive=True):
					input_field_count += 1
					p.add_run('%s. <input> : %s\n'%(input_field_count, input_field.get('name','')))
			else:
				p = docx_doc.add_paragraph(str(element))
				if c==1: 
					prepend_bookmark(p, zmsid)

	return docx_doc



# #############################################
# Helper Functions 3: Set Docx-Styles
# #############################################
def set_docx_styles(doc):
	styles = doc.styles
	# Custom color 1: #017D87
	custom_color1 = docx.shared.RGBColor(1, 125, 135)
	# Custom color 2: #AAAAAA
	custom_color2 = docx.shared.RGBColor(170, 170, 170)
	# Page margins
	doc.sections[0].top_margin = Emu(120*9525)
	# Normal
	styles['Normal'].font.name = 'Arial'
	styles['Normal'].font.size = Pt(9)
	styles['Normal'].paragraph_format.space_after = Pt(6)
	styles['Normal'].paragraph_format.space_before = Pt(6)
	styles['Normal'].paragraph_format.line_spacing = 1.35

	# Headlines derived from Normal
	if sys.version_info[0] > 2:
		styles['Heading 1'].basedOn = doc.styles['Normal']
	styles['Heading 1'].font.name = 'Arial'
	styles['Heading 1'].font.size = Pt(24)
	styles['Heading 1'].font.bold = False
	styles['Heading 1'].paragraph_format.line_spacing = 1.2
	styles['Heading 1'].paragraph_format.space_before = Pt(12)
	styles['Heading 1'].font.color.rgb = custom_color1

	if sys.version_info[0] > 2:
		styles['Heading 2'].basedOn = doc.styles['Normal']
	styles['Heading 2'].font.size = Pt(18)
	styles['Heading 2'].font.color.rgb = custom_color1

	if sys.version_info[0] > 2:
		styles['Heading 3'].basedOn = doc.styles['Normal']
	styles['Heading 3'].font.size = Pt(12)
	styles['Heading 3'].font.bold = True
	styles['Heading 3'].font.color.rgb = custom_color1

	if sys.version_info[0] > 2:
		styles['Heading 4'].basedOn = doc.styles['Normal']
	styles['Heading 4'].font.size = Pt(12)
	styles['Heading 4'].font.bold = False
	styles['Heading 4'].font.color.rgb = custom_color1


	# More styles derived from Normal
	styles.add_style('Description', WD_STYLE_TYPE.PARAGRAPH)
	if sys.version_info[0] > 2:
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

	styles.add_style('q', WD_STYLE_TYPE.CHARACTER)
	styles['q'].font.color.rgb = custom_color2
	styles['q'].font.bold = True
	styles['q'].font.italic = True

	styles.add_style('Hyperlink', WD_STYLE_TYPE.CHARACTER)
	styles['Hyperlink'].font.color.rgb = custom_color1
	styles['Hyperlink'].font.underline = True

	styles.add_style('refGlossary', WD_STYLE_TYPE.CHARACTER)
	styles['refGlossary'].font.color.rgb = custom_color1
	styles['refGlossary'].font.italic = True

	styles['macro'].font.size = Pt(9)
	styles['macro'].paragraph_format.space_before = Pt(12)
	styles['macro'].paragraph_format.space_after = Pt(12)
	styles['macro'].paragraph_format.line_spacing = 1.35

	styles['header'].font.size = Pt(7)
	styles['header'].font.color.rgb = custom_color2
	styles['footer'].font.size = Pt(7)
	styles['footer'].font.color.rgb = custom_color2

	return doc



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

	# Sequence all pageelements including ZMSNote
	# Ref: ZMSObject.isPageElement
	pageelements = [ \
		e for e in zmscontext.filteredChildNodes(request) \
			if ( e.getType() in [ 'ZMSObject', 'ZMSRecordSet' ] ) \
				and not e.meta_id in [ 'ZMSTeaserContainer' ] \
		]
	for pageelement in pageelements:
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
# GLOBALS
# #############################################
# DOCX-Document with custom style-set
# Hint: may use template like docx.Document('template.docx')
doc = docx.Document()
doc = set_docx_styles(doc)
zmscontext = None

# #############################################
# MAIN function for DOCX-Generation
# #############################################
# The function `manage_export_pydocx` may be called
# recursively to create a DOCX document from a 
# document tree. The function is called with the
# `do_return` parameter set to `True` on the last
# node of the tree. The `filename` parameter is used
# to name the DOCX file. The function returns the
# binary data of the DOCX file.
def manage_export_pydocx(self, save_file=True, file_name=None):
	request = self.REQUEST

	# PAGE_COUNT: Counter for recursive export
	page_count = request.get('page_count',0) + 1
	request.set('page_count', page_count)

	global zmscontext
	zmscontext = self

	# INITIALIZE DOCX Document
	# and preserve it while exporting recursively 
	if page_count == 1:
		global doc
		doc = docx.Document()
		doc = set_docx_styles(doc)

	# GET PAGE CONTENT (JSON)
	zmsdoc = apply_standard_json_docx(zmscontext)
	heading = zmsdoc[0]
	blocks = zmsdoc[1:]

	# [A] CREATE SECTION HEADER/FOOTER (on initial page)
	# and preserve it while exporting recursively 
	if page_count == 1:
		dt = standard.getLangFmtDate(zmscontext, heading.get('last_change_dt',''), 'eng', '%Y-%m-%d')
		url = heading.get('url','').replace('nohost','localhost')
		tabs = len(heading.get('title',''))>48 and '\t' or '\t\t'
		doc.sections[0].header.paragraphs[0].text = '%s%s%s\nURL: %s'%(standard.pystr(heading.get('title','')), tabs, dt, url)
		add_page_number(doc.sections[0].footer.paragraphs[0].add_run('Seite '))

	# [B] CREATE PAGE HEADING
	doc.add_heading(standard.pystr(heading.get('title','')), level=1)
	prepend_bookmark(doc.paragraphs[-1], heading.get('id',''))
	
	if heading.get('description','')!='':
		p = doc.add_paragraph(standard.pystr(heading.get('description','')))
		p.style = doc.styles['Description']

	# [C] CREATE PAGE CONTENT-BLOCKS
	for block in blocks:
		v = standard.pystr(block['content'])
		# #############################################
		# [1] HTML-BLOCK (e.g. richtext with inline styles, just a minimum set of inline elements)
		if v and block['docx_format'] == 'html':
			# try:
			add_htmlblock_to_docx(zmscontext=zmscontext, docx_doc=doc, htmlblock=v, zmsid=block['id'])
			# except:
			# 	p = doc.add_paragraph()
			# 	p.add_run('Rendering Error: %s'%block['meta_id'])
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
		# [4] TEXT-BLOCK with given block format (style)
		elif v and block['docx_format'] in [e.name for e in doc.styles]:
				p = doc.add_paragraph(v, style=style_name)
				prepend_bookmark(p, block['id'])
		elif v:
			p = doc.add_paragraph(v)
			prepend_bookmark(p, block['id'])

	# #############################################
	# [d] SAVE DOCX-FILE
	# #############################################
			
	if save_file:
		# Save document in temporary directory
		fn = '%s.docx'%(file_name and file_name or zmscontext.id_quote(zmscontext.getTitlealt(request)))
		tempfolder = tempfile.mkdtemp()
		docx_file_name = os.path.join(tempfolder, fn)
		doc.save(docx_file_name)
		
		# Read the docx file
		with open(docx_file_name, 'rb') as f:
			docx_file_data = f.read()

		# Remove the temporary folder
		shutil.rmtree(tempfolder)

		# Set the HTTP response headers
		request.RESPONSE.setHeader('Content-Disposition', 'inline;filename=%s'%fn)
		request.RESPONSE.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

		# msg = 'DOCX-Export erfolgreich: %s'%fn
		# request.response.redirect(standard.url_append_params('%s/manage_main'%self.absolute_url(),{'lang':request['lang'],'manage_tabs_message':msg}))

		# Return the data of the docx file
		# on single page export or on last page of recursive export
		return docx_file_data
	else:
		# Proceed with recursive export
		pass