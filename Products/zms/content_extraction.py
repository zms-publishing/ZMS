#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# content_extraction.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

"""ZMS content extraction toolkit module

This module provides helpful functions and classes for use in Python
Scripts.  It can be accessed from Python with the statement
"import Products.zms.content_extraction"
"""
# Imports.
import html
from bs4 import BeautifulSoup
import html
from bs4 import BeautifulSoup
from AccessControl.SecurityInfo import ModuleSecurityInfo
# Product Imports.
from Products.zms import standard

security = ModuleSecurityInfo('Products.zms.content_extraction')

security.declarePublic('extract_content')
def extract_content(context, b, content_type=''):
    """
    @param context: the ZMS-context
    @type b: C{ZMS}
    @param b: the bytes
    @type b: C{bytes}
    """
    text = extract_content_tika( context, b, content_type)
    if text is None and [x for x in ['application/pdf'] if content_type.startswith(x)]:
        text = extract_content_pdfminer( context, b, content_type)
    if text is None and [x for x in ['text/','application/css','application/javascript','image/svg'] if content_type.startswith(x)]:
        text = standard.pystr(b)
    return text


security.declarePublic('extract_text_from_html')
def extract_text_from_html(context, html_data):
    """
    Removes html tags and converts html entities to plain text.
    @param context: the ZMS-context
    @param html_data: html data stream
    @type html_data: C{str} or C{bytes}
    """
    soup = BeautifulSoup(html_data, features="html.parser")
    text_data = soup.get_text() \
        .replace('\n',' ') \
        .replace('\t',' ') \
        .replace('\"',' ')
    text_data = ' '.join(text_data.split())
    try:
        text_data = html.unescape(text_data)
    except Exception as e:
        standard.writeError( context, "can't unescape text_data: %s" % e)
    return text_data


def extract_content_tika(context, b, content_type=None):
    """
    Apache Tika - a content analysis toolkit
    @see https://tika.apache.org/
    """
    parser_names = [k for k in list(context.getConfProperties(inherited=True)) if k.lower() == 'tika.url' or k.lower().endswith('.parser')]
    if parser_names:
        parser_name = parser_names[0]
        parser_url = context.getConfProperty(parser_name,'http://localhost:9998/tika')
        headers = {'Accept': 'application/json'}
        try:
            import requests
            r = requests.put(parser_url, headers=headers, data=b)
            html = r.json().get('X-TIKA:content')
            return extract_text_from_html(context, html)
        except:
            standard.writeError( context, "can't extract_content_tika")
    else:
        standard.writeError( context, "config parameter opensearch.parser or tika.url are not set")
    return None


def extract_content_pdfminer(context, b, content_type=None):
    """
    Apply the pdfminer.six library to extract text from a PDF file.
    Pdfminer.six is a community maintained fork of the original PDFMiner. 
    It is a tool for extracting information from PDF documents. It focuses
    on getting and analyzing text data. Pdfminer.six extracts the text 
    from a page directly from the sourcecode of the PDF. 
    Install: pip install pdfminer.six
    @see https://github.com/pdfminer/pdfminer.six

    @param context: the ZMS-context
    @param b: pdf data stream
    @type b: C{bytes}
    @param content_type: the content type
    @type content_type: C{str} or None
    """
    try:
        from io import BytesIO, StringIO
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.pdfpage import PDFPage
        from pdfminer.pdfparser import PDFParser
        output_string = StringIO()
        in_file = BytesIO(b)
        parser = PDFParser(in_file)
        standard.writeError( context, "pdfminer: doc")
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        return extract_text_from_html(context, output_string.getvalue())
    except:
        standard.writeError( context, "can't extract_content_pdfminer")
    return None

security.apply(globals())