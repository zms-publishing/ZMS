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
from AccessControl.SecurityInfo import ModuleSecurityInfo
# Product Imports.
from Products.zms import standard

security = ModuleSecurityInfo('Products.zms.content_extraction')

security.declarePublic('extract_content')
def extract_content(context, b, content_type=None):
    """
    @param context: the ZMS-context
    @type b: C{ZMS}
    @param b: the bytes
    @type b: C{bytes}
    """
    text = extract_content_tika( context, b, content_type)
    if text is None:
        text = extract_content_pdfminer( context, b, content_type)
    return text


security.declarePublic('extract_text_from_html')
def extract_text_from_html(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text() \
        .replace('\n',' ') \
        .replace('\t',' ') \
        .replace('\"',' ')
    text = ' '.join(text.split())
    return text


def extract_content_tika(context, b, content_type=None):
    """
    Apache Tika - a content analysis toolkit
    @see https://tika.apache.org/
    """
    tika_url = context.getConfProperty('tika.url', '') # http://localhost:9998/tika
    if tika_url:
        headers = {'Accept': 'application/json'}
        try:
            import requests
            r = requests.put(tika_url, headers=headers, data=b)
            html = r.json().get('X-TIKA:content')
            return extract_text_from_html(html)
        except:
            standard.writeError( context, "can't extract_content_tika")
    return None


def extract_content_pdfminer(context, b, content_type=None):
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
        in_file = BytesIO(b)
        parser = PDFParser(in_file)
        standard.writeError( context, "pdfminer: doc")
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        return extract_text_from_html(output_string.getvalue())
    except:
        standard.writeError( context, "can't extract_content_pdfminer")
    return None

security.apply(globals())