# Recursive PDF Export (`manage_export_pdf_recursive`)

## What this metacommand does

`manage_export_pdf_recursive` exports the current ZMS document together with all descendant pages into one PDF file.

It is the recursive counterpart of `manage_export_pdf`:

- `manage_export_pdf` renders one page
- `manage_export_pdf_recursive` renders the current page plus its document subtree

The generated PDF contains one section per ZMS page and inserts a page break between sections.

## How it works

The recursive export does not merge finished PDF files.
Instead, it builds one combined HTML document and renders that HTML in a single WeasyPrint pass.

This is important because the existing `manage_export_pdf` implementation already contains the relevant HTML logic:

- collection of page-element HTML blocks
- rewriting of relative image URLs
- PDF rendering via WeasyPrint

The recursive metacommand reuses these helpers and applies them to all pages in the tree.

## How to get started

1. Install dependency in the Python environment used by Zope/ZMS:

    ```
    pip install weasyprint
    ```

2. Ensure the new metacommand package exists:
    - `Products/zms/conf/metacmd_manager/manage_export_pdf_recursive/__init__.py`
    - `Products/zms/conf/metacmd_manager/manage_export_pdf_recursive/manage_export_pdf_recursive.py`

3. Open a `ZMSDocument` in ZMS and run `PDF Export (Recursive)`.

4. Test first with a small subtree so you can verify:

    - document order
    - page breaks
    - image loading
    - rendering of custom page-elements

## Document selection and order

The export includes:

1. the current document (`self`)
2. all descendants returned by `self.filteredTreeNodes(request, self.PAGES)`

The order in the final PDF follows that list.
If your project expects a different traversal or filtering strategy, adapt the `zmsdocs` construction in `manage_export_pdf_recursive(self)`.

## Important API functions

### Main entrypoint

- `manage_export_pdf_recursive(self)`
  Collects all documents in the subtree, renders each as an HTML section, builds one combined HTML document, and returns the final PDF bytes.

### Recursive helper functions

- `_build_document_section(zmscontext, request, blocks)`
  Builds one HTML `<article>` for one page in the tree.

- `_build_recursive_html_document(zmscontext, request, sections_html)`
  Wraps all section fragments into one full HTML document.

### Reused helpers from `manage_export_pdf`

- `_collect_content_html(zmscontext, request)`
  Converts the page-elements of one page into HTML blocks.

- `_make_images_absolute(html, base_url)`
  Rewrites relative image references so WeasyPrint can load them.

- `PDF_CSS`
  Base stylesheet of the single-page PDF export.

## Customization points

### 1. Reuse or adapt single-page content rendering

Most project-specific content-model customization should still happen in:

- `Products/zms/conf/metacmd_manager/manage_export_pdf/manage_export_pdf.py`

Especially in:

- `_collect_content_html(...)`
- `PDF_CSS`

Reason: `manage_export_pdf_recursive` intentionally reuses those helpers. If you improve page-element rendering there, both exports benefit.

### 2. Change section layout for recursive export only

Use `RECURSIVE_PDF_CSS` in:

- `Products/zms/conf/metacmd_manager/manage_export_pdf_recursive/manage_export_pdf_recursive.py`

This stylesheet extends `PDF_CSS` and is the right place for recursive-only layout rules, for example:

- page break between sections
- reduced top margin for each section title
- tree-level heading styling
- table of contents styling if you add one later

### 3. Change per-page section metadata

Edit `_build_document_section(...)` if you want each subtree page to show different metadata, for example:

- breadcrumb/path
- authorship
- workflow state
- internal identifiers
- custom headings instead of page title

### 4. Change subtree traversal

Edit this part in `manage_export_pdf_recursive(self)`:

```py
zmsdocs = [self]
zmsdocs.extend(self.filteredTreeNodes(request, self.PAGES))
```

Typical customizations:

- exclude utility pages
- include only visible/active pages
- sort pages differently
- stop at a certain depth

## Styling notes

The recursive export adds this section-level rule on top of `PDF_CSS`:

```css
.document-section + .document-section {
  page-break-before: always;
}
```

This means each page in the document tree starts on a new PDF page.
If that is too strict for your use case, you can change or remove this rule.

## Troubleshooting

- `ImportError: WeasyPrint is not installed`
  Install `weasyprint` in the same interpreter used by your Zope instance.

- Images work in single-page export but not in recursive export
  Check the `base_url` handling for each `zmsdoc` in `manage_export_pdf_recursive.py`.

- Missing page content in one subtree page
  Inspect `_collect_content_html(...)` in `manage_export_pdf.py`; the issue is usually in page-element rendering, not in the recursion itself.

- PDF is too large or slow to render
  Test with a smaller subtree first and inspect image sizes and the number of rendered pages.

## File reference

- `Products/zms/conf/metacmd_manager/manage_export_pdf_recursive/manage_export_pdf_recursive.py`
- `Products/zms/conf/metacmd_manager/manage_export_pdf_recursive/__init__.py`
- `Products/zms/conf/metacmd_manager/manage_export_pdf/manage_export_pdf.py`
