#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
manage_export_pdf_recursive.py
==============================
ZMS metacommand: export the current ZMS document tree as one PDF file.

The recursive export reuses the HTML collection and PDF generation helpers
from ``manage_export_pdf`` and concatenates the current document plus all
sub-pages into a single WeasyPrint render pass.
"""

from Products.zms import standard
from Products.zms.conf.metacmd_manager.manage_export_pdf.manage_export_pdf import (
    PDF_CSS,
    _WEASYPRINT_AVAILABLE,
    _collect_content_html,
    _make_images_absolute,
    weasyprint,
)


RECURSIVE_PDF_CSS = PDF_CSS + """
.document-section + .document-section {
    page-break-before: always;
}

.document-section > h1.doc-title {
    margin-top: 0;
}
"""


def _build_document_section(zmscontext, request, blocks):
    """Render one ZMS page as an HTML section inside the combined PDF."""
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

    body_parts = ['<article class="document-section">']
    body_parts.append('<h1 class="doc-title">%s</h1>' % title)

    meta_parts = []
    if change_dt:
        meta_parts.append('Stand: %s' % change_dt)
    if url:
        safe_url = url.replace('nohost', 'localhost').replace('http:///', 'http://localhost/')
        meta_parts.append('URL: <a href="%s">%s</a>' % (safe_url, safe_url))
    if meta_parts:
        body_parts.append('<p class="doc-meta">%s</p>' % ' &nbsp;|&nbsp; '.join(meta_parts))

    if description:
        body_parts.append('<p class="description">%s</p>' % description)

    for html, _meta_id in blocks:
        body_parts.append(html)

    body_parts.append('</article>')
    return '\n'.join(body_parts)


def _build_recursive_html_document(zmscontext, request, sections_html):
    """Build a full HTML document for the complete recursive PDF export."""
    lang = request.get('lang', 'de')
    title = standard.pystr(
        zmscontext.attr('title') or zmscontext.getTitlealt(request)
    )

    body_html = '\n'.join(sections_html)
    return (
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
        css=RECURSIVE_PDF_CSS,
        body=body_html,
    )


def manage_export_pdf_recursive(self):
    """Export the current document and all descendant pages as one PDF file."""
    if not _WEASYPRINT_AVAILABLE:
        raise ImportError(
            'WeasyPrint is not installed. '
            'Run: pip install weasyprint'
        )

    request = self.REQUEST
    request.set('lang', request.get('lang', self.getPrimaryLanguage()))

    standard.writeStdout(
        None,
        'manage_export_pdf_recursive: rendering %s' % self.absolute_url()
    )

    zmsdocs = [self]
    zmsdocs.extend(self.filteredTreeNodes(request, self.PAGES))

    sections_html = []
    for zmsdoc in zmsdocs:
        blocks = _collect_content_html(zmsdoc, request)
        base_url = zmsdoc.absolute_url()
        blocks = [
            (_make_images_absolute(html, base_url), meta_id)
            for html, meta_id in blocks
        ]
        sections_html.append(_build_document_section(zmsdoc, request, blocks))

    html_doc = _build_recursive_html_document(self, request, sections_html)
    pdf_bytes = weasyprint.HTML(string=html_doc, base_url=self.absolute_url()).write_pdf()

    fn = '%s.pdf' % self.id_quote(self.getTitlealt(request))
    request.RESPONSE.setHeader(
        'Content-Disposition', 'inline;filename=%s' % fn
    )
    request.RESPONSE.setHeader('Content-Type', 'application/pdf')
    request.RESPONSE.setHeader('Content-Length', str(len(pdf_bytes)))

    return pdf_bytes
