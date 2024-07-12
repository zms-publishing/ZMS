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

# X/HTML LIBRARIES
from bs4 import BeautifulSoup
from lxml import etree

# IMPORT DOCX LIBRARIES
import docx
from docx.text.paragraph import Paragraph
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.section import WD_SECTION_START
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


def get_normalized_image_width(w, h, max_w = 460):
	if w:
		if h > w:
			scale =  h>max_w and float(h)/float(max_w) or 1
		else:
			scale =  w>max_w and float(w)/float(max_w) or 1
		w = int(w/scale)
	else:
		w = max_w
	return w

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
	if not url.startswith('javascript:'): # Omit javascript links
		r_id = docx_block.part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
		hyper_link = create_element('w:hyperlink')
		create_attribute(hyper_link, 'r:id', r_id)
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
	try:
		style.element.pPr.append(border) # pPr = Paragraph properties
	except:
		standard.write('Error: Could not add bottom border to style %s' % style.name)

def add_paragraph_bgcolor(style, color):
	"""
	Add shadow and borders to paragraph properties
	Parameters:
		style = styles['ZMSNotiz']
		color = 'fff5ce'
	"""
	shading = create_element('w:shd') # shd = Shading
	create_attribute(shading, 'w:val', 'clear')
	create_attribute(shading, 'w:color', 'auto')
	create_attribute(shading, 'w:fill', color)
	style.element.pPr.append(shading)
	border = create_element('w:pBdr') # pBdr = Paragraph border
	for side in ['left', 'right', 'top', 'bottom']:
		border_side = create_element('w:%s' % side)
		create_attribute(border_side, 'w:val', 'single')
		create_attribute(border_side, 'w:sz', '4')
		create_attribute(border_side, 'w:space', '5')
		create_attribute(border_side, 'w:color', color)
		border.append(border_side)
	style.element.pPr.append(border)

def add_table_bgcolor(style, color):
	"""
	Add shadow and borders to table properties
	Parameters:
		style = styles['Normal Table']
		color = 'fff5ce'
	"""
	shading = create_element('w:shd') # shd = Shading
	create_attribute(shading, 'w:val', 'clear')
	create_attribute(shading, 'w:color', 'auto')
	create_attribute(shading, 'w:fill', color)
	style.element.tblPr.append(shading)
	border = create_element('w:tblBorders') # tblBorders = Table borders
	create_attribute(border, 'w:val', 'single')
	create_attribute(border, 'w:sz', '4')
	create_attribute(border, 'w:space', '5')
	create_attribute(border, 'w:color', color)
	style.element.tblPr.append(border)

def add_character_bgcolor(style, color):
	"""
	Add shadow and borders to run properties
	Parameters:
		style = styles['Macro Text Char']
		color = '017D87'
	"""
	shading = create_element('w:shd') # shd = Shading
	create_attribute(shading, 'w:val', 'clear')
	create_attribute(shading, 'w:color', 'auto')
	create_attribute(shading, 'w:fill', color)
	style.element.rPr.append(shading)
	border = create_element('w:bdr') # bdr = run border
	create_attribute(border, 'w:val', 'single')
	create_attribute(border, 'w:sz', '12')
	create_attribute(border, 'w:space', '1')
	create_attribute(border, 'w:color', color)
	style.element.rPr.append(border)




# #############################################
# Helper Functions 2: HTML/Richtext-Processing 
# #############################################

# Clean HTML
def clean_html(html):
	# Clean comments, styles, empty tags
	# and handle special characters: left-to-right, triangle
	left_to_right_char = '\u200e'
	triangle_char = '\U0001F806'

	html = re.sub(r'<!.*?->','', html)
	html = re.sub(r'<style.*?</style>','', html)
	html = standard.re_sub(r'\n|\t', ' ', html)
	html = standard.re_sub(r'\s\s', ' ', html)
	html = html.replace('<span class="unicode">&crarr;</span><br />','')
	html = html.replace('<span class="unicode">&crarr;</span>','')
	html = html.replace('">\n','">')
	# refGlossary
	html = html.replace(left_to_right_char,'')
	html = html.replace('[[', triangle_char)
	html = html.replace(']]', '')
	return html

# ADD RUNS TO DOCX-BLOCK
def add_runs(docx_block, bs_element):
	# Adding a minimum set of inline runs
	# any BeautifulSoup block element may contain
	# to the docx-block, e.g. <strong>, <em>, <a>
	if bs_element.children:
		c = 0
		for elrun in [elrun for elrun in bs_element.children if elrun.name not in ['ul', 'ol', 'li', 'img', 'figure']]:
			# Hint: ul/ol/li are handled as blocks in add_htmlblock_to_docx.add_list
			c += 1
			if elrun.name == 'br':
				docx_block.add_run('\n')
			elif elrun.name != None and elrun.text == '↵':
				docx_block.add_run('')
			elif elrun.name == 'strong':
				docx_block.add_run(elrun.text).bold = True
			elif elrun.name == 'q':
				docx_block.add_run(elrun.text, style='Quote Char')
			elif elrun.name == 'em' or elrun.name == 'i':
				docx_block.add_run(elrun.text).italic = True
			elif elrun.name in ['samp', 'code', 'tt', 'var', 'pre']:
				docx_block.add_run(elrun.text, style='Macro Text Char')
			elif elrun.name == 'kbd':
				docx_block.add_run(elrun.text, style='Keyboard')
				# r.font.highlight_color = WD_COLOR_INDEX.BLACK
			elif elrun.name == 'sub':
				docx_block.add_run(elrun.text).font.subscript = True
			elif elrun.name == 'sup':
				docx_block.add_run(elrun.text).font.superscript = True
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
			elif elrun.name == 'p':
				add_runs(docx_block = docx_block, bs_element = elrun)
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
			# #############################################
			# HEADINGS
			# #############################################
			if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
				heading_level = int(element.name[1])
				heading_text = element.text.strip()
				p = docx_doc.add_heading(heading_text, level=heading_level)
				if c==1 and zmsid: 
					prepend_bookmark(p, zmsid)
				if element.text == 'Inhaltsverzeichnis':
					p.style = docx_doc.styles['TOC-Header']
			# #############################################
			# PARAGRAPH
			# #############################################
			elif element.name == 'p':
				p = docx_doc.add_paragraph()
				if c==1 and zmsid: 
					prepend_bookmark(p, zmsid)
				# htmlblock.__contains__('ZMSTable')
				if element.has_attr('class'):
					if 'caption' in element['class']:
						p.style = docx_doc.styles['Caption']
					else:
						class_name = element['class'][0]
						style_name = (class_name in docx_doc.styles) and class_name or 'Normal'
						p.style = docx_doc.styles[style_name]
				add_runs(docx_block = p, bs_element = element)
			# #############################################
			# LIST
			# #############################################
			elif element.name in ['ul','ol']:
				def add_list(docx_doc, element, level=0, c=0):
					li_styles = {'ul':'ListBullet', 'ol':'ListNumber'}
					level_suffix = level!=0 and str(level+1) or ''
					for li in element.find_all('li', recursive=False):
						p = docx_doc.add_paragraph(style='%s%s'%(li_styles[element.name], level_suffix))
						add_runs(docx_block = p, bs_element = li)
						if c==1 and zmsid:  
							prepend_bookmark(p, zmsid)
						for ul in li.find_all(['ul','ol'], recursive=False):
							add_list(docx_doc, ul, level+1)
				add_list(docx_doc, element, level=0, c=c)
			# #############################################
			# TABLE
			# #############################################
			elif element.name == 'table':
				### debug: element.has_attr('class') and element['name']=='abgabekriterium'
				caption = element.find('caption')
				caption_text = caption and caption.text or ''
				if zmsid == 'changeHistory':
					caption_text = 'Änderungshistorie'
				p = docx_doc.add_paragraph(standard.pystr(caption_text), style='Caption')
				if c==1 and zmsid:
					prepend_bookmark(p, zmsid)
				rows = element.find_all('tr')
				cols = rows[0].find_all(['td','th'])
				docx_table = docx_doc.add_table(rows=len(rows), cols=len(cols))
				docx_table.style = 'Table Grid'
				docx_table.alignment = WD_TABLE_ALIGNMENT.CENTER
				r=-1
				for row in rows:
					r+=1
					cells = row.find_all(['td','th'])
					for i, cl in enumerate(cells):
						docx_cell = docx_table.cell(r,i)
						if {'div','ol','ul','table','p'} & set([e.name for e in cl.children]):
							# [A] Cell contains block elements
							# Hint: Cell implicitly contains a paragraph
							cl_html = standard.pystr(''.join([str(child) for child in cl.contents if child!=' ']))
							add_htmlblock_to_docx(zmscontext, docx_cell, cl_html, zmsid=None)
						else:
							# [B] Cell contains inline elements
							p = docx_cell.paragraphs[0]
							p.style = docx_doc.styles['Normal']
							if zmsid == 'changeHistory':
								p.style = docx_doc.styles['Table-Small']
							add_runs(p, cl)
						if cl.name == 'th':
							docx_table.cell(r,i).paragraphs[0].runs[0].bold = True
				# Add linebreak or pagebreak after table
				p = docx_doc.add_paragraph()
				if zmsid == 'changeHistory':
					p.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)
			# #############################################
			# IMAGE
			# #############################################
			elif element.name == 'img' or element.name == 'figure':
				if element.name == 'figure':
					element = element.find('img')
				if element.has_attr('src'):
					img_src = element['src']
					try:
						if zmscontext.operator_getattr(zmscontext,zmsid).attr('imghires'):
							# Use high resolution image
							img_src = zmscontext.operator_getattr(zmscontext,zmsid).attr('imghires').getHref(zmscontext.REQUEST)
					except:
						pass
					img_name = img_src.split('/')[-1]
					if not img_src.startswith('http'):
						src_url0 = zmscontext.absolute_url().split('/content/')[0]
						src_url1 = img_src.split('/content/')[-1]
						if src_url1.startswith('/'): 
							# eg. ZMS assets starting with /++resource++zms_
							src_url1 = src_url1[1:]
						element['src'] = '%s/content/%s'%(src_url0, src_url1)

					# Normalize image size to 460px
					imgheight = element.has_attr('height') and int(float(element['height'])) or None
					imgwidth = element.has_attr('width') and int(float(element['width'])) or None
					imgwidth = get_normalized_image_width(w = imgwidth, h = imgheight, max_w = 460)

					try:
						response = requests.get(element['src'])
						with open(img_name, 'wb') as f:
							f.write(response.content)
						if src_url1.startswith('++resource++zms_'):
							docx_doc.add_picture(img_name)
						else:
							docx_doc.add_picture(img_name, width=Emu(imgwidth*9525))
						os.remove(img_name)
						if c==1 and zmsid:
							try:
								prepend_bookmark(docx_doc.paragraphs[-1], zmsid)
							except:
								pass
					except:
						pass
			# #############################################
			# DIV
			# #############################################
			elif element.name == 'div':
				if element.has_attr('class') and (('ZMSGraphic' in element['class']) or ('graphic' in element['class'])):
					ZMSGraphic_html = ''.join([str(e) for e in element.children])
					add_htmlblock_to_docx(zmscontext, docx_doc, ZMSGraphic_html, zmsid)
				else:
					child_tags = [e.name for e in element.children if e.name]
					if 'em' in child_tags or 'strong' in child_tags:
						p = docx_doc.add_paragraph()
						if c==1 and zmsid: 
							prepend_bookmark(p, zmsid)
						if element.has_attr('class'):
							class_name = element['class'][0]
							style_name = (class_name in docx_doc.styles) and class_name or 'Normal'
							p.style = docx_doc.styles[style_name]
						add_runs(docx_block = p, bs_element = element)
					else:
						div_html = ''.join([standard.pystr(e) for e in element.children])
						add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)

			# #############################################
			# Link/A containing text or block elements
			# #############################################
			elif element.name == 'a':
				# Hyperlink just containing text
				if element.children and list(element.children)[0] == element.text:
					try:
						add_hyperlink(docx_block = docx_doc, link_text = element.text, url = element.get('href'))
					except:
						p = docx_doc.add_paragraph()
						if c==1 and	zmsid:
							prepend_bookmark(p, zmsid)
						add_runs(docx_block = p, bs_element = element)
				# Hyperlink containing a block element
				elif {'div','p','table','img'} & set([e.name for e in element.children]):
					div_html = ''.join([str(e) for e in element.children])
					add_htmlblock_to_docx(zmscontext, docx_doc, div_html, zmsid)
				# Hyperlink containing inline elements
				else:
					p = docx_doc.add_paragraph()
					if c==1 and zmsid:
						prepend_bookmark(p, zmsid)
					add_runs(docx_block = p, bs_element = element)
			# #############################################
			# FORM
			# #############################################
			elif element.name == 'form':
				p = docx_doc.add_paragraph(style='macro')
				p.add_run('<form>\n').font.bold = True
				if c==1: 
					prepend_bookmark(p, zmsid)
				input_field_count = 0
				for input_field in element.find_all('input', recursive=True):
					input_field_count += 1
					p.add_run('%s. <input> : %s\n'%(input_field_count, input_field.get('name','')))
			# #############################################
			# OTHERS
			# #############################################
			elif element.name == 'hr':
				# Omit horizontal rule
				pass
			elif element.name == 'script':
				# Omit javascript
				pass
			else:
				try:
					p = docx_doc.add_paragraph(str(element))
					if c==1 and zmsid: 
						prepend_bookmark(p, zmsid)
				except:
					pass

	return docx_doc



# #############################################
# Helper Functions 3: Set Docx-Styles
# #############################################
# print('\n'.join([s.name for s in styles]))
"""
	Normal
	Header
	Header Char
	Footer
	Footer Char
	Heading 1
	Heading 2
	Heading 3
	Heading 4
	Heading 5
	Heading 6
	Heading 7
	Heading 8
	Heading 9
	Default Paragraph Font
	Normal Table
	No List
	No Spacing
	Heading 1 Char
	Heading 2 Char
	Heading 3 Char
	Title
	Title Char
	Subtitle
	Subtitle Char
	List Paragraph
	Body Text
	Body Text Char
	Body Text 2
	Body Text 2 Char
	Body Text 3
	Body Text 3 Char
	List
	List 2
	List 3
	List Bullet
	List Bullet 2
	List Bullet 3
	List Number
	List Number 2
	List Number 3
	List Continue
	List Continue 2
	List Continue 3
	macro
	Macro Text Char
	Quote
	Quote Char
	Heading 4 Char
	Heading 5 Char
	Heading 6 Char
	Heading 7 Char
	Heading 8 Char
	Heading 9 Char
	Caption
	Strong
	Emphasis
	Intense Quote
	Intense Quote Char
	Subtle Emphasis
	Intense Emphasis
	Subtle Reference
	Intense Reference
	Book Title
	TOC Heading
	Table Grid
	Light Shading
	Light Shading Accent 1
	Light Shading Accent 2
	Light Shading Accent 3
	Light Shading Accent 4
	Light Shading Accent 5
	Light Shading Accent 6
	Light List
	Light List Accent 1
	Light List Accent 2
	Light List Accent 3
	Light List Accent 4
	Light List Accent 5
	Light List Accent 6
	Light Grid
	Light Grid Accent 1
	Light Grid Accent 2
	Light Grid Accent 3
	Light Grid Accent 4
	Light Grid Accent 5
	Light Grid Accent 6
	Medium Shading 1
	Medium Shading 1 Accent 1
	Medium Shading 1 Accent 2
	Medium Shading 1 Accent 3
	Medium Shading 1 Accent 4
	Medium Shading 1 Accent 5
	Medium Shading 1 Accent 6
	Medium Shading 2
	Medium Shading 2 Accent 1
	Medium Shading 2 Accent 2
	Medium Shading 2 Accent 3
	Medium Shading 2 Accent 4
	Medium Shading 2 Accent 5
	Medium Shading 2 Accent 6
	Medium List 1
	Medium List 1 Accent 1
	Medium List 1 Accent 2
	Medium List 1 Accent 3
	Medium List 1 Accent 4
	Medium List 1 Accent 5
	Medium List 1 Accent 6
	Medium List 2
	Medium List 2 Accent 1
	Medium List 2 Accent 2
	Medium List 2 Accent 3
	Medium List 2 Accent 4
	Medium List 2 Accent 5
	Medium List 2 Accent 6
	Medium Grid 1
	Medium Grid 1 Accent 1
	Medium Grid 1 Accent 2
	Medium Grid 1 Accent 3
	Medium Grid 1 Accent 4
	Medium Grid 1 Accent 5
	Medium Grid 1 Accent 6
	Medium Grid 2
	Medium Grid 2 Accent 1
	Medium Grid 2 Accent 2
	Medium Grid 2 Accent 3
	Medium Grid 2 Accent 4
	Medium Grid 2 Accent 5
	Medium Grid 2 Accent 6
	Medium Grid 3
	Medium Grid 3 Accent 1
	Medium Grid 3 Accent 2
	Medium Grid 3 Accent 3
	Medium Grid 3 Accent 4
	Medium Grid 3 Accent 5
	Medium Grid 3 Accent 6
	Dark List
	Dark List Accent 1
	Dark List Accent 2
	Dark List Accent 3
	Dark List Accent 4
	Dark List Accent 5
	Dark List Accent 6
	Colorful Shading
	Colorful Shading Accent 1
	Colorful Shading Accent 2
	Colorful Shading Accent 3
	Colorful Shading Accent 4
	Colorful Shading Accent 5
	Colorful Shading Accent 6
	Colorful List
	Colorful List Accent 1
	Colorful List Accent 2
	Colorful List Accent 3
	Colorful List Accent 4
	Colorful List Accent 5
	Colorful List Accent 6
	Colorful Grid
	Colorful Grid Accent 1
	Colorful Grid Accent 2
	Colorful Grid Accent 3
	Colorful Grid Accent 4
	Colorful Grid Accent 5
	Colorful Grid Accent 6
	Description
	Hyperlink
	refGlossary
	Table-Small
	TOC-Header
"""

def set_docx_styles(doc):
	styles = doc.styles

	# Custom color 1: #017D87 dark turquoise
	color_turquoise = docx.shared.RGBColor(1, 125, 135)
	# Custom color 2: #AAAAAA light grey
	color_lightgrey = docx.shared.RGBColor(170, 170, 170)
	# Custom color 3: #333333 dark grey
	color_darkgrey = docx.shared.RGBColor(51, 51, 51)
	# Custom color 4: #FFFFFF white
	color_white = docx.shared.RGBColor(255, 255, 255)
	# Custom color 5: #0070FF blue
	color_blue = docx.shared.RGBColor(0, 112, 255)

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
	styles['Heading 1'].paragraph_format.space_before = Pt(18)
	styles['Heading 1'].font.color.rgb = color_turquoise

	if sys.version_info[0] > 2:
		styles['Heading 2'].basedOn = doc.styles['Normal']
	styles['Heading 2'].font.name = 'Arial'
	styles['Heading 2'].font.size = Pt(18)
	styles['Heading 2'].font.bold = False
	styles['Heading 2'].paragraph_format.line_spacing = 1.2
	styles['Heading 2'].paragraph_format.space_before = Pt(24)
	styles['Heading 2'].font.color.rgb = color_turquoise

	if sys.version_info[0] > 2:
		styles['Heading 3'].basedOn = doc.styles['Normal']
	styles['Heading 3'].font.name = 'Arial'
	styles['Heading 3'].font.size = Pt(13)
	styles['Heading 3'].font.bold = True
	styles['Heading 3'].paragraph_format.space_before = Pt(22)
	styles['Heading 3'].font.color.rgb = color_turquoise

	if sys.version_info[0] > 2:
		styles['Heading 4'].basedOn = doc.styles['Normal']
	styles['Heading 4'].font.name = 'Arial'
	styles['Heading 4'].font.size = Pt(10)
	styles['Heading 4'].paragraph_format.space_before = Pt(14)
	styles['Heading 4'].font.bold = False
	styles['Heading 4'].font.bold = True
	styles['Heading 4'].font.color.rgb = color_turquoise


	# More styles derived from Normal
	styles.add_style('Description', WD_STYLE_TYPE.PARAGRAPH)
	if sys.version_info[0] > 2:
		styles['Description'].basedOn = doc.styles['Normal']
	styles['Description'].font.name = 'Arial'
	styles['Description'].font.size = Pt(9)
	styles['Description'].font.italic = True
	styles['Description'].font.color.rgb = color_turquoise
	styles['Description'].paragraph_format.space_after = Pt(18)
	styles['Description'].paragraph_format.line_spacing = 1.35
	add_bottom_border(styles['Description'])

	styles['Caption'].font.size = Pt(8)
	styles['Caption'].font.italic = True
	styles['Caption'].font.color.rgb = color_turquoise
	styles['Caption'].paragraph_format.space_before = Pt(24)
	styles['Caption'].paragraph_format.space_after = Pt(6)
	styles['Caption'].paragraph_format.keep_with_next = True

	styles['Quote Char'].font.color.rgb = color_lightgrey
	styles['Quote Char'].font.bold = True
	styles['Quote Char'].font.italic = True

	styles.add_style('Hyperlink', WD_STYLE_TYPE.CHARACTER)
	styles['Hyperlink'].font.color.rgb = color_turquoise
	styles['Hyperlink'].font.underline = True

	styles.add_style('refGlossary', WD_STYLE_TYPE.CHARACTER)
	styles['refGlossary'].font.color.rgb = color_turquoise
	styles['refGlossary'].font.italic = False

	styles['macro'].font.size = Pt(9)
	styles['macro'].paragraph_format.space_before = Pt(12)
	styles['macro'].paragraph_format.space_after = Pt(12)
	styles['macro'].paragraph_format.line_spacing = 1.35

	styles['Macro Text Char'].font.bold = True
	styles['Macro Text Char'].font.color.rgb = color_blue

	styles.add_style('Keyboard', WD_STYLE_TYPE.CHARACTER)
	styles['Keyboard'].font.name = 'Courier New'
	styles['Keyboard'].font.size = Pt(8)
	styles['Keyboard'].font.bold = True
	styles['Keyboard'].font.color.rgb = color_white
	add_character_bgcolor(styles['Keyboard'], '000000')

	styles['header'].font.size = Pt(7)
	styles['header'].font.color.rgb = color_lightgrey
	styles['footer'].font.size = Pt(7)
	styles['footer'].font.color.rgb = color_lightgrey

	# Table small
	styles.add_style('Table-Small', WD_STYLE_TYPE.PARAGRAPH)
	styles['Table-Small'].font.name = 'Arial'
	styles['Table-Small'].font.size = Pt(7)
	styles['Table-Small'].paragraph_format.space_after = Pt(2)
	styles['Table-Small'].paragraph_format.space_before = Pt(2)
	styles['Table-Small'].paragraph_format.line_spacing = 1.2

	# Inhaltsverzeichnis
	styles.add_style('TOC-Header', WD_STYLE_TYPE.PARAGRAPH)
	if sys.version_info[0] > 2:
		styles['TOC-Header'].basedOn = doc.styles['Heading 2']
	styles['TOC-Header'].font.name = 'Arial'
	styles['TOC-Header'].font.size = Pt(12)
	styles['TOC-Header'].font.bold = True
	styles['TOC-Header'].font.color.rgb = color_lightgrey
	styles['TOC-Header'].paragraph_format.space_before = Pt(12)
	add_bottom_border(styles['TOC-Header'])

	# Notiz
	styles.add_style('ZMSNotiz', WD_STYLE_TYPE.PARAGRAPH)
	if sys.version_info[0] > 2:
		styles['ZMSNotiz'].basedOn = doc.styles['Normal']
	styles['ZMSNotiz'].font.name = 'Arial'
	styles['ZMSNotiz'].font.size = Pt(8)
	styles['ZMSNotiz'].paragraph_format.space_before = Pt(12)
	styles['ZMSNotiz'].paragraph_format.space_after = Pt(12)
	styles['ZMSNotiz'].paragraph_format.line_spacing = 1.5
	# Add background color
	add_paragraph_bgcolor(styles['ZMSNotiz'], 'fff5ce')

	# Merksatz
	styles.add_style('emphasis', WD_STYLE_TYPE.PARAGRAPH)
	if sys.version_info[0] > 2:
		styles['emphasis'].basedOn = doc.styles['Normal']
	styles['emphasis'].font.name = 'Arial'
	styles['emphasis'].font.size = Pt(9)
	styles['emphasis'].font.bold = False
	styles['emphasis'].font.italic = True
	styles['emphasis'].paragraph_format.space_before = Pt(12)
	styles['emphasis'].paragraph_format.space_after = Pt(12)
	styles['emphasis'].paragraph_format.line_spacing = 1.5
	# Add background color
	add_paragraph_bgcolor(styles['emphasis'], 'f0f8ff')

	return doc



# #############################################
# Helper Functions 4: GET DOCX NORMALIZED JSON
# #############################################

def apply_standard_json_docx(self):
	"""
	The function creates a normalized JSON stream of 
	a PAGE-like ZMS node. This JSON stream is used for 
	transforming the content to DOCX. 
	It is a list of dicts (key/value-pairs), where the 
	first dict is representing the container meta data
	and the following blocks are representing the PAGEELEMENTS
	of the document.
	Each object dictionary has the following keys:
	- id: the id of the node
	- meta_id: the meta_id of the node
	- parent_id: the id of the parent node
	- parent_meta_id: the meta_id of the parent node
	- title: the title of the node
	- description: the description of the node
	- last_change_dt: the last change date of the node
	- docx_format: the format of the content (html/xml/image 
	  or text-stylename e.g.'Normal')
	- content: the content of the node

	Any PAGEELEMENT-node may have a specific 'standard_json_docx'
	attribute which preprocesses it's ZMS content model close to
	the translation into the DOCX model. The key 'docx_format'
	is used to determine the style of the content block.

	If this attribute method (py-primtive) is not available, 
	the object's class standard_html-method is used to get the 
	content, so that the (maybe not optimum) html will be 
	transformed to DOCX.

	Depending on the complexity of the content it's JSON 
	representation may consist of ore or multiple key/value-
	sequences. Any of these blocks will create a new block 
	element (e.g. paragraph) in the DOCX document.
	"""

	zmscontext = self
	request = zmscontext.REQUEST
	# request.set('preview', 'preview')
	is_page = zmscontext.isPage()

	id = zmscontext.id
	meta_id = zmscontext.meta_id
	parent_id = zmscontext.id
	parent_meta_id = zmscontext.meta_id 
	title = zmscontext.attr('title')
	description = zmscontext.attr('attr_dc_description')
	last_change_dt = zmscontext.attr('change_dt') or zmscontext.attr('created_dt')
	url = zmscontext.getHref2IndexHtml(request)

	# Meta data as 1st block
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

	if not is_page:
		pageelements = [zmscontext]
	else:
		# Sequence all pageelements including ZMSNote
		# Ref: ZMSObject.isPageElement
		pageelements = [ \
			e for e in zmscontext.getChildNodes(request)  \
				if ( ( e.getType() in [ 'ZMSObject', 'ZMSRecordSet'] ) \
					and not e.meta_id in [ 'ZMSTeaserContainer'] \
					and not e.isPage() ) \
					or e.meta_id in [ 'ZMSLinkElement' ]
			]

	for pageelement in pageelements:
		if pageelement.attr('change_dt') and pageelement.attr('change_dt') >= last_change_dt:
			last_change_dt = pageelement.attr('change_dt')
		json_block = []

		# Check for standard_json_docx attribute
		json_block = pageelement.attr('standard_json_docx')

		if not json_block:

			# #############################################
			# ZMSGraphic
			# #############################################
			if pageelement.meta_id == 'ZMSGraphic':
				id = pageelement.id
				meta_id = pageelement.meta_id
				parent_id = pageelement.getParentNode().id 
				parent_meta_id = pageelement.getParentNode().meta_id 
				text = BeautifulSoup(pageelement.attr('text'), 'html.parser').get_text()
				img = pageelement.attr('imghires') or pageelement.attr('img')
				# img_url = img.getHref(request)
				img_url = '%s/%s'%(pageelement.absolute_url(),img.getHref(request).split('/')[-1])
				imgwidth = img and int(img.getWidth()) or 0
				imgheight = img and int(img.getHeight()) or 0

				json_block = [ {
						'id':id,
						'meta_id':meta_id,
						'parent_id':parent_id,
						'parent_meta_id':parent_meta_id,
						'docx_format':'Caption',
						'content':'[Abb. %s] %s'%(id, text)
					},
					{
						'id':'%s_img'%(id), 
						'meta_id':meta_id,
						'parent_id':parent_id,
						'parent_meta_id':parent_meta_id,
						'docx_format':'image',
						'imgwidth':	imgwidth,
						'imgheight':imgheight,
						'content':img_url
					}
				]
			# #############################################
			# ZMSLinkElement
			# #############################################
			elif pageelement.meta_id == 'ZMSLinkElement':
				# and pageelement.attr('attr_type') in ['','replace','new']:
				id = pageelement.id
				meta_id = pageelement.meta_id
				parent_id = pageelement.getParentNode().id
				parent_meta_id = pageelement.getParentNode().meta_id
				icon = '\U0001F517'
				title = pageelement.attr('title')
				text = pageelement.attr('attr_dc_description')
				try:
					href = zmscontext.getLinkObj(pageelement.attr('attr_url'),request).getHref2IndexHtml(request)
				except:
					href = '#'

				json_block = [ {
						'id':id,
						'meta_id':meta_id,
						'parent_id':parent_id,
						'parent_meta_id':parent_meta_id,
						'docx_format':'html',
						'content':'<p>%s <a href="%s">%s</a><br/>%s</p>'%(icon, href, title, text)
					}
				]
			# #############################################
			# ZMSFile
			# #############################################
			elif (pageelement.meta_id == 'ZMSFile' or pageelement.meta_id == 'downloadfile') and pageelement.attr('file'):
				id = pageelement.id
				meta_id = pageelement.meta_id
				parent_id = pageelement.getParentNode().id
				parent_meta_id = pageelement.getParentNode().meta_id
				icon = '\U0001F87E'
				title = pageelement.attr('title')
				text = pageelement.attr('attr_dc_description')
				try:
					href = pageelement.getHref2IndexHtml(request)
				except:
					href = '#'

				json_block = [ {
						'id':id,
						'meta_id':meta_id,
						'parent_id':parent_id,
						'parent_meta_id':parent_meta_id,
						'docx_format':'html',
						'content':'<p>%s <a href="%s">%s</a><br/>%s</p>'%(icon, href, title, text)
					}
				]

			# #############################################
			else:
				html = ''
				# Get standard content of pageelement
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
# Helper Functions 5: READ HEADLINE LEVELS
# #############################################
# Based on number-prefix of headlines
def get_headline_levels_from_numbering(headline_paragraphs=[]):
	list2 = [ \
		(
			len(p.text.split(' ')[0].rstrip('.').split('.'))+1 \
			if '.' in p.text.split(' ')[0] else 1 \
		) \
		for p in headline_paragraphs
	]

	return list2


# #############################################
# Helper Functions 6: NORMALIZE HEADLINE LEVELS
# #############################################
# VARIANT-1
# Better for very volatile headline jumping
def normalize_headline_levels(list1):
	"""
	Normalize headline levels
	expects a list of headline levels as integer values
	"""
	list2 = list1[:]  # Create a copy of list1
	l = len(list2)
	i = 0
	n = 0
	# Start with headline level 1
	list2[0] = 1
	while i < l:
		i = (n == 0 or i > n) and i+1 or n + 1
		n = 0
		if i >= l:
			break
		v = list2[i]
		if v == list1[i-1]:
			continue
		if v - list1[i-1] > 1 or v - list2[i-1] > 1:
			list2[i] = list1[i-1] + 1
			if v - list2[i-1] > 1:
				list2[i] = list2[i-1] + 1
			n = i
		if n + 1 >= l:
			break
		while list1[n+1] == list1[n]:
			n += 1
			if n + 1 >= l:
				break
			list2[n] = list2[i]
	return list2

# VARIANT-2
# Better for systmatical headline jumps
# e.g. omitted h2 (see Test-Case 1)
def normalize_headline_levels2(list1):
	"""
	Normalize headline levels
	expects a list of headline levels as integer values
	"""
	s = []
	list2 = [1]
	for i in list1[1:]:
		i1 = i + 1
		if s and s[-1] == i1:
			pass
		elif not s or s[-1] < i1:
			s.append(i1)
		elif s:
			while len(s) > 1 and s[-1] > i1:
				s = s[:-1]
		list2.append(len(s) + 1)
	return list2




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

	# PAGE_COUNTER: Counter for recursive export
	page_counter = request.get('page_counter',0) + 1
	request.set('page_counter', page_counter)

	global zmscontext
	zmscontext = self
	is_page = zmscontext.isPage()

	# INITIALIZE DOCX Document
	# and preserve it while exporting recursively 
	if page_counter == 1:
		global doc
		doc = docx.Document()
		doc = set_docx_styles(doc)
	
	# GET PAGE CONTENT (JSON)
	zmsdoc = apply_standard_json_docx(self)
	heading = zmsdoc[0]
	blocks = zmsdoc[1:]

	# [A] CREATE SECTION HEADER/FOOTER
	# On recursive export change header for any new page (self)
	# while preserving footer all the same (zmscontext)

	dt = standard.getLangFmtDate(self, heading.get('last_change_dt',''), 'eng', '%Y-%m-%d')
	url = heading.get('url','').replace('nohost','localhost')
	tabs = len(heading.get('title',''))>68 and '\t' or '\t\t'

	if page_counter == 1:
		doc.sections[0].header.paragraphs[0].text = '%s%s%s\nURL: %s'%(standard.pystr(heading.get('title','')), tabs, dt, url)
		add_page_number(doc.sections[0].footer.paragraphs[0].add_run('Seite '))
	else:
		new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
		new_section.header.is_linked_to_previous = False # ESSENTIAL FOR CHANGING HEADER!!!
		header_paragraph = new_section.header.paragraphs[0] if new_section.header.paragraphs else new_section.header.add_paragraph()
		header_paragraph.text = '%s%s%s\nURL: %s'%(standard.pystr(heading.get('title','')), tabs, dt, url)
		# new_section.header.first_page_header = True
		# new_section.footer.first_page_footer = True

	# [B] CREATE PAGE HEADING
	if is_page:
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
			try:
				add_htmlblock_to_docx(zmscontext=zmscontext, docx_doc=doc, htmlblock=v, zmsid=block['id'])
			except:
				p = doc.add_paragraph()
				p.add_run('Rendering Error: %s'%block['meta_id'])
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
			# Get image width and height from 'image' data block
			imgwidth = block.get('imgwidth',0)
			imgheight = block.get('imgheight',0)
			try:
				imgwidth = get_normalized_image_width(w = imgwidth, h = imgheight, max_w = 460)
			except:
				imgwidth = 460
			r.add_picture(image_file, width=Emu(imgwidth*9525))
			prepend_bookmark(p, block['id'])
		# #############################################
		# [4] TEXT-BLOCK with given block format (style)
		elif v and block['docx_format'] in [e.name for e in doc.styles]:
				p = doc.add_paragraph(v, style=block['docx_format'])
				prepend_bookmark(p, block['id'])
		elif v:
			p = doc.add_paragraph(v)
			prepend_bookmark(p, block['id'])


	# #############################################
	# Normalize Headline Hierarchy
	# using function normalize_headline_levels2 
	# up-levelling systematic gaps in headline levels
	# ---------------------------------------------
	# TODO: Make it work with recursive export
	# #############################################
	if is_page:
		# Get all headline paragraphs for any page / section
		for sect in doc.sections:
			headline_paragraphs = [p for p in sect.header.paragraphs if 'Heading' in p.style.name]
			if headline_paragraphs:
				# 1. Get headline levels on HTML/stylenames 
				# and its normalization with function normalize_headline_levels2()
				headline_levels_on_stylenames = [int(p.style.name[-1]) for p in headline_paragraphs]
				headline_levels_normalized = normalize_headline_levels2(headline_levels_on_stylenames)

				# 2. Get headline levels on its numbering-prefixes
				headline_levels_on_numbering = get_headline_levels_from_numbering(headline_paragraphs)

				# 3. Which method for getting the normalized levels is more reliable?
				# Sum up prefix-based level-numbers and divide by number of levels
				# Approach: if there are no numbers, all levels are considered as 1
				# what is supposed to be unreliable
				if sum(headline_levels_on_numbering)/len(headline_levels_on_numbering) > 1.25: 
					headline_levels_normalized = headline_levels_on_numbering

				# 4. Reset levels of headline-paragraphs
				for i, p in enumerate(headline_paragraphs):
					p.style = doc.styles['Heading %s'%headline_levels_normalized[i]]



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