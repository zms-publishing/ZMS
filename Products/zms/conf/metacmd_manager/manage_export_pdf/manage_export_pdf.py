#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
manage_export_pdf.py
====================
ZMS metacommand: export the current ZMS page content as a PDF file.

The PDF is generated from the clean HTML of each page element
(i.e. the output of getBodyContent / standard_html), without any
website navigation or layout chrome.  The HTML is assembled into a
minimal, print-friendly document and rendered with WeasyPrint.

Requirements
------------
  pip install weasyprint

Usage
-----
Called as a ZMS External Method named ``manage_export_pdf`` on any
ZMSDocument node.  The command is registered via the accompanying
``__init__.py`` in this folder.

"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import re
import tempfile
import os

# ---------------------------------------------------------------------------
# ZMS helpers
# ---------------------------------------------------------------------------
from Products.zms import standard

# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
try:
	import weasyprint
	_WEASYPRINT_AVAILABLE = True
except ImportError:
	_WEASYPRINT_AVAILABLE = False


# ===========================================================================
# CSS for the PDF document
# ===========================================================================
PDF_CSS = """
@page {
	size: A4;
	margin: 2cm 2.5cm 2.5cm 2.5cm;
	@bottom-center {
		content: "Seite " counter(page) " von " counter(pages);
		font-family: Arial, Helvetica, sans-serif;
		font-size: 9pt;
		color: #666;
	}
	@top-left {
		content: string(page-title);
		font-family: Arial, Helvetica, sans-serif;
		font-size: 9pt;
		color: #666;
	}
}

body {
	font-family: Arial, Helvetica, sans-serif;
	font-size: 11pt;
	line-height: 1.5;
	color: #222;
}

/* Store page title for running header */
h1.doc-title {
	string-set: page-title content();
}

h1, h2, h3, h4, h5, h6 {
	color: #111;
	page-break-after: avoid;
	margin-top: 1em;
	margin-bottom: 0.3em;
}
h1 { font-size: 18pt; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }
h4, h5, h6 { font-size: 11pt; }

p {
	margin: 0 0 0.6em 0;
	orphans: 2;
	widows: 2;
}

a {
	color: #1a56a0;
	text-decoration: none;
}

/* Meta info block below the title */
p.doc-meta {
	font-size: 9pt;
	color: #666;
	margin-bottom: 1.2em;
	border-bottom: 1px solid #eee;
	padding-bottom: 0.5em;
}

p.description {
	font-style: italic;
	color: #444;
	margin-bottom: 1em;
}

/* Tables */
table {
	border-collapse: collapse;
	width: 100%;
	margin: 0.8em 0;
	font-size: 10pt;
}
th, td {
	border: 1px solid #bbb;
	padding: 4px 8px;
	text-align: left;
	vertical-align: top;
}
th {
	background-color: #e8e8e8;
	font-weight: bold;
}
tr:nth-child(even) td {
	background-color: #f9f9f9;
}
table caption {
	font-size: 9pt;
	color: #555;
	font-style: italic;
	caption-side: bottom;
	padding-top: 4px;
}

/* Images */
img {
	/* A4 width (21cm) minus left/right @page margins (2.5cm each) */
	max-width: 16cm !important;
	width: auto !important;
	height: auto !important;
	display: block;
	margin: 0.5em 0;
	box-sizing: border-box;
}
figure {
	margin: 0.8em 0;
	page-break-inside: avoid;
	max-width: 16cm !important;

}
figcaption {
	font-size: 9pt;
	color: #555;
	font-style: italic;
}

/* Lists */
ul, ol {
	margin: 0.4em 0 0.6em 0;
	padding-left: 1.5em;
}
li {
	margin-bottom: 0.2em;
}

/* Code / pre */
pre, code, samp, kbd, tt, var {
	font-family: "Courier New", Courier, monospace;
	font-size: 9.5pt;
	background: #f4f4f4;
	padding: 0 2px;
}
pre {
	padding: 8px;
	border: 1px solid #ddd;
	overflow-x: auto;
	white-space: pre-wrap;
	word-wrap: break-word;
}

/* Blockquote */
blockquote {
	border-left: 3px solid #ccc;
	padding-left: 0.8em;
	margin: 0.6em 0 0.6em 0.5em;
	color: #555;
}

/* Page break helpers */
.page-break { page-break-before: always; }
"""


# ===========================================================================
# HTML cleaning
# ===========================================================================

def _clean_html(html):
	"""Remove scripts, styles, comments and normalise whitespace."""
	html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
	html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
	html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
	return html


def _make_images_absolute(html, base_url):
	"""
	Rewrite relative ``src`` and ``href`` attributes to absolute URLs
	so WeasyPrint can fetch images/resources without a live HTTP request
	to Zope (which would require session auth).

	Only ``src`` on ``img`` tags and ``href`` on ``a`` tags are adjusted;
	the rest of the HTML is left unchanged.
	"""
	if not base_url:
		return html

	# Ensure base_url has no trailing slash
	base_url = base_url.rstrip('/')

	soup = BeautifulSoup(html, 'html.parser')

	for img in soup.find_all('img'):
		src = img.get('src', '')

		# Enforce responsive image behavior in PDF output by removing
		# author-provided dimensions that can exceed printable width.
		if img.has_attr('width'):
			del img['width']
		if img.has_attr('height'):
			del img['height']
		if img.has_attr('style'):
			del img['style']

		if src and not src.startswith(('http://', 'https://', 'data:')):
			if src.startswith('./'):
				src = src[2:]
			if src.startswith('/'):
				# Absolute path – reconstruct scheme+host only
				from urllib.parse import urlparse
				parsed = urlparse(base_url)
				img['src'] = '%s://%s%s' % (parsed.scheme, parsed.netloc, src)
			else:
				img['src'] = '%s/%s' % (base_url, src)

	return str(soup)


# ===========================================================================
# Collect page content HTML
# ===========================================================================

def _collect_content_html(zmscontext, request):
	"""
	Walk through all direct page-element children of *zmscontext* and
	return a list of (html_string, meta_id) tuples – one per element.

	This mirrors the logic of ``apply_standard_json_docx`` but returns
	raw HTML strings instead of JSON blocks.
	"""
	is_page = zmscontext.isPage()

	if not is_page:
		# zmscontext itself is a page-element
		pageelements = [zmscontext]
	else:
		# All direct non-page children (page-elements)
		pageelements = [
			e for e in zmscontext.getChildNodes(request)
			if (
				(e.getType() in ['ZMSObject', 'ZMSRecordSet'])
				and e.meta_id not in ['LgChangeHistory', 'ZMSTeaserContainer']
				and not e.isPage()
			)
			or e.meta_id in ['ZMSLinkElement']
		]

	blocks = []

	for pageelement in pageelements:

		meta_id = pageelement.meta_id

		# 1. Prefer a custom ``standard_html`` attribute (py-primitive)
		#    if the object provides one (same heuristic as pydocx export).
		try:
			custom_html = pageelement.attr('standard_html')
			if custom_html:
				blocks.append((_clean_html(standard.pystr(custom_html)), meta_id))
				continue
		except Exception:
			pass

		# 2. ZMSGraphic – render image + caption
		if meta_id == 'ZMSGraphic':
			img = pageelement.attr('imghires') or pageelement.attr('img')
			if img:
				img_url = '%s/%s' % (
					pageelement.absolute_url(),
					img.getHref(request).split('/')[-1]
				)
				caption = standard.pystr(
					BeautifulSoup(pageelement.attr('text') or '', 'html.parser').get_text()
				)
				html = '<figure><img src="%s" alt="%s"/>' % (img_url, caption)
				if caption:
					html += '<figcaption>%s</figcaption>' % caption
				html += '</figure>'
				blocks.append((html, meta_id))
			continue

		# 3. ZMSLinkElement – render as a paragraph with a link
		if meta_id == 'ZMSLinkElement':
			title = standard.pystr(pageelement.attr('title'))
			text = standard.pystr(pageelement.attr('attr_dc_description') or '')
			try:
				href = zmscontext.getLinkObj(
					pageelement.attr('attr_url'), request
				).getHref2IndexHtml(request)
			except Exception:
				href = '#'
			html = '<p><a href="%s">%s</a>' % (href, title)
			if text:
				html += '<br/>%s' % text
			html += '</p>'
			blocks.append((html, meta_id))
			continue

		# 4. ZMSFile / downloadfile – render as a link paragraph
		if meta_id in ('ZMSFile', 'downloadfile') and pageelement.attr('file'):
			title = standard.pystr(pageelement.attr('title'))
			text = standard.pystr(pageelement.attr('attr_dc_description') or '')
			try:
				href = pageelement.getHref2IndexHtml(request)
			except Exception:
				href = '#'
			html = '<p>&#128382; <a href="%s">%s</a>' % (href, title)
			if text:
				html += ' – %s' % text
			html += '</p>'
			blocks.append((html, meta_id))
			continue

		# 5. Default: getBodyContent  (or renderShort if present)
		try:
			if 'renderShort' in pageelement.getMetaobjAttrIds(meta_id):
				html = pageelement.attr('renderShort') or ''
			else:
				html = pageelement.getBodyContent(request)
			html = _clean_html(standard.pystr(html))
		except Exception as exc:
			html = '<p><em>Rendering Error (%s): %s</em></p>' % (meta_id, exc)

		if html.strip():
			blocks.append((html, meta_id))

	return blocks


# ===========================================================================
# Assemble the HTML document
# ===========================================================================

def _build_html_document(zmscontext, request, blocks):
	"""
	Combine all content blocks into a single, self-contained HTML string
	suitable for WeasyPrint.
	"""
	lang = request.get('lang', 'de')
	title = standard.pystr(
		zmscontext.attr('title') or zmscontext.getTitlealt(request)
	)
	description = standard.pystr(
		zmscontext.attr('attr_dc_description') or ''
	)
	url = zmscontext.getHref2IndexHtml(request)

	try:
		change_dt = standard.getLangFmtDate(
			zmscontext,
			zmscontext.attr('change_dt') or zmscontext.attr('created_dt') or '',
			'eng',
			'%Y-%m-%d'
		)
	except Exception:
		change_dt = ''

	# Build body parts
	body_parts = []

	# Title heading
	body_parts.append('<h1 class="doc-title">%s</h1>' % title)

	# Meta info line (date + URL)
	meta_parts = []
	if change_dt:
		meta_parts.append('Stand: %s' % change_dt)
	if url:
		safe_url = url.replace('nohost', 'localhost').replace('http:///', 'http://localhost/')
		meta_parts.append('URL: <a href="%s">%s</a>' % (safe_url, safe_url))
	if meta_parts:
		body_parts.append('<p class="doc-meta">%s</p>' % ' &nbsp;|&nbsp; '.join(meta_parts))

	# Description
	if description:
		body_parts.append('<p class="description">%s</p>' % description)

	# Content blocks
	for html, _meta_id in blocks:
		body_parts.append(html)

	body_html = '\n'.join(body_parts)

	# Full HTML document
	html_doc = (
		'<!DOCTYPE html>\n'
		'<html lang="{lang}">\n'
		'<head>\n'
		'  <meta charset="utf-8"/>\n'
		'  <meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
		'  <title>{title}</title>\n'
		'  <style>{css}</style>\n'
		'</head>\n'
		'<body>\n'
		'{body}\n'
		'</body>\n'
		'</html>'
	).format(
		lang=lang,
		title=title,
		css=PDF_CSS,
		body=body_html,
	)

	return html_doc


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

def manage_export_pdf(self):
	"""
	Export the current ZMS page as a PDF file.

	The PDF contains only the page content (title, description, and all
	page-element body HTML), without website navigation or layout chrome.

	Requires WeasyPrint to be installed in the Python environment:
	    pip install weasyprint
	"""
	if not _WEASYPRINT_AVAILABLE:
		raise ImportError(
			'WeasyPrint is not installed. '
			'Run: pip install weasyprint'
		)

	request = self.REQUEST
	request.set('lang', request.get('lang', self.getPrimaryLanguage()))

	standard.writeStdout(
		None,
		'manage_export_pdf: rendering %s' % self.absolute_url()
	)

	# --- Collect content blocks ------------------------------------------------
	blocks = _collect_content_html(self, request)

	# --- Fix image URLs so WeasyPrint can resolve them -------------------------
	base_url = self.absolute_url()
	blocks = [
		(_make_images_absolute(html, base_url), meta_id)
		for html, meta_id in blocks
	]

	# --- Build HTML document ---------------------------------------------------
	html_doc = _build_html_document(self, request, blocks)

	# --- Render PDF with WeasyPrint -------------------------------------------
	# base_url tells WeasyPrint where to resolve any remaining relative URLs
	wp_html = weasyprint.HTML(string=html_doc, base_url=base_url)
	pdf_bytes = wp_html.write_pdf()

	# --- Return PDF -----------------------------------------------------------
	fn = '%s.pdf' % self.id_quote(self.getTitlealt(request))
	request.RESPONSE.setHeader(
		'Content-Disposition', 'inline;filename=%s' % fn
	)
	request.RESPONSE.setHeader('Content-Type', 'application/pdf')
	request.RESPONSE.setHeader('Content-Length', str(len(pdf_bytes)))

	return pdf_bytes