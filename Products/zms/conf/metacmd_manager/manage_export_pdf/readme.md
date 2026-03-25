# PDF Export (`manage_export_pdf`)

## What this metacommand does

`manage_export_pdf` exports the current ZMS page as a PDF using [WeasyPrint](https://weasyprint.org/).

The export intentionally renders content-only output:

- page title
- page description
- direct page-elements of the current page
- no website navigation, menus, or frontend chrome

This makes it a good base for project-specific PDF layouts.

## How to get started

1. Install dependency in your Zope/ZMS Python environment:

```sh
pip install weasyprint
```

2. Ensure the metacommand is available:

- Definition: `Products/zms/conf/metacmd_manager/manage_export_pdf/__init__.py`
- Implementation: `Products/zms/conf/metacmd_manager/manage_export_pdf/manage_export_pdf.py`

3. Open a `ZMSDocument` page in ZMS and run the action `PDF Export`.

4. Verify output and then customize in two places:

- rendering logic (`_collect_content_html`) for your content model
- stylesheet (`PDF_CSS`) for your visual design

## Customizing for your own content model

The core adaptation point is `_collect_content_html(zmscontext, request)`.

It walks through page-elements and returns a list of blocks:

```py
[(html_string, meta_id), ...]
```

These blocks are then combined and rendered as PDF.

### Existing rendering strategy

The script currently handles content in this order:

1. Custom template via `standard_html` attribute (if available)
2. Special handling for `ZMSGraphic`
3. Special handling for `ZMSLinkElement`
4. Special handling for `ZMSFile` / `downloadfile`
5. Fallback to `renderShort` or `getBodyContent(request)`

### Typical project adaptation

Add your own `meta_id` handlers before the fallback block.

Example pattern:

```py
if meta_id == 'MyCustomElement':
    title = standard.pystr(pageelement.attr('title') or '')
    body = standard.pystr(pageelement.attr('text') or '')
    html = '<section><h2>%s</h2><div>%s</div></section>' % (title, body)
    blocks.append((_clean_html(html), meta_id))
    continue
```

Notes:

- Always append valid HTML fragments.
- Convert values with `standard.pystr(...)` before string formatting.
- Use `_clean_html(...)` for generated HTML where needed.

## Important API functions (ZMS + script)

### Metacommand entrypoint

- `manage_export_pdf(self)`
  Main function called by the metacommand. It collects blocks, rewrites resource URLs, builds the HTML document, and returns PDF bytes.

### Script helper functions

- `_collect_content_html(zmscontext, request)`
  Most important customization function. It decides how each `meta_id` is converted to HTML.

- `_build_html_document(zmscontext, request, blocks)`
  Wraps blocks into one full HTML document (`<html>`, `<head>`, CSS, metadata).

- `_make_images_absolute(html, base_url)`
  Rewrites relative image URLs so WeasyPrint can load resources.

- `_clean_html(html)`
  Removes scripts/styles/comments before rendering.

### Frequently used ZMS object APIs in this script

- `isPage()`
  Checks if current object is a page or already a page-element.

- `getChildNodes(request)`
  Returns child objects; used to collect direct page-elements.

- `meta_id` and `getType()`
  Identify object/model type and choose rendering branch.

- `attr('<attribute_id>')`
  Reads attribute values from ZMS objects.

- `getMetaobjAttrIds(meta_id)`
  Checks if optional attributes (for example `renderShort`) exist.

- `getBodyContent(request)`
  Generic HTML rendering fallback for many element types.

- `absolute_url()` and `getHref2IndexHtml(request)`
  Create links and base URLs for content/resources.

- `getLinkObj(...).getHref2IndexHtml(request)`
  Resolves internal/external link targets (used in `ZMSLinkElement`).

## Styling and layout customization

Adjust `PDF_CSS` in `manage_export_pdf.py` to change:

- page size/margins (`@page`)
- header/footer text (`@top-left`, `@bottom-center`)
- typography
- table/image behavior
- forced page breaks (`.page-break`)

If your project has special print rules, this is the preferred place to adapt.

## Common extension points

- Project-specific title/meta line: edit `_build_html_document(...)`

- Different element filtering: edit page-element selection in `_collect_content_html(...)`

- Include committed vs preview content: set request flags before rendering (project-specific)

- Custom file naming: change `fn = '%s.pdf' % self.id_quote(self.getTitlealt(request))`

## Troubleshooting

- `ImportError: WeasyPrint is not installed`
  Install dependency in the same interpreter used by Zope.

- Images not visible in PDF
  Check rewritten URLs in `_make_images_absolute(...)` and ensure resources are reachable for the process creating the PDF.

- Content block missing
  Verify `meta_id` branch in `_collect_content_html(...)` and test fallback with `getBodyContent(request)`.

- Broken HTML output
  Sanitize custom HTML and check generated fragment validity.

## Copy/Paste recipes for `_collect_content_html(...)`

The snippets below are intended as quick starters for project models.
Replace the `meta_id` and attribute names with your concrete model fields.

### Recipe 1: Rich text element with optional subtitle

```py
if meta_id == 'MyRichText':
  title = standard.pystr(pageelement.attr('title') or '')
  subtitle = standard.pystr(pageelement.attr('subtitle') or '')
  text_html = standard.pystr(pageelement.attr('text') or '')

  html = ''
  if title:
    html += '<h2>%s</h2>' % title
  if subtitle:
    html += '<p class="description">%s</p>' % subtitle
  html += text_html

  blocks.append((_clean_html(html), meta_id))
  continue
```

### Recipe 2: Recordset/table style element (`ZMSRecordSet`)

```py
if meta_id == 'MyRecordSet':
  rows = pageelement.attr('records') or []
  if rows:
    html = ['<table>']
    html.append('<thead><tr><th>Name</th><th>Value</th></tr></thead>')
    html.append('<tbody>')
    for row in rows:
      name = standard.pystr(row.get('name') or '')
      value = standard.pystr(row.get('value') or '')
      html.append('<tr><td>%s</td><td>%s</td></tr>' % (name, value))
    html.append('</tbody></table>')
    blocks.append((_clean_html(''.join(html)), meta_id))
  continue
```

### Recipe 3: Download list from linked file objects

```py
if meta_id == 'MyDownloadContainer':
  links = []
  for child in pageelement.getChildNodes(request):
    if child.meta_id in ('ZMSFile', 'downloadfile') and child.attr('file'):
      title = standard.pystr(child.attr('title') or child.id)
      href = child.getHref2IndexHtml(request)
      links.append('<li><a href="%s">%s</a></li>' % (href, title))

  if links:
    html = '<h2>Downloads</h2><ul>%s</ul>' % ''.join(links)
    blocks.append((html, meta_id))
  continue
```

### Recipe 4: Force page break before a section

```py
if meta_id == 'MyChapterStart':
  title = standard.pystr(pageelement.attr('title') or '')
  body = standard.pystr(pageelement.getBodyContent(request) or '')
  html = '<div class="page-break"></div><h2>%s</h2>%s' % (title, body)
  blocks.append((_clean_html(html), meta_id))
  continue
```

### Quick integration checklist

1. Insert your handler block before the default fallback in `_collect_content_html(...)`.
2. Keep `continue` at the end of each custom branch.
3. Wrap dynamic values with `standard.pystr(...)`.
4. Run export and inspect one representative page per content type.
5. Adjust `PDF_CSS` only after HTML structure is stable.