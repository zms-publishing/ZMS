# E. Appendices

This appendix collects reference material that supports all audience groups: a glossary of ZMS-specific terms, and a curated list of external resources.

---

## Glossary

| Term | Definition |
|---|---|
| **Block element** | A content object that holds actual content and is embedded in a sequence inside a page (e.g. `ZMSTextarea`, `ZMSGraphic`). |
| **Content model** | The site-specific schema of content classes and their attributes, configured in the ZMS administration menu. |
| **Dublin Core (DC)** | A standard set of metadata elements (title, creator, date, …) used by ZMS as the basis for meta-attributes. |
| **Language dictionary** | A table of `TYPE_` / `ATTR_` keys and their per-language translations, used to internationalise ZMI display labels. |
| **Metaobject** | A content class definition stored in the ZODB or filesystem under `metaobj_manager/`. |
| **Meta-attribute** | A site-wide descriptive attribute (Dublin Core–based) inherited by all content objects. |
| **Page node** | A `ZMSFolder` or `ZMSDocument` that aggregates block elements and may nest other page nodes. |
| **Primary language** | The root language in the multilingual dependency tree; the source for translations. |
| **Repository Manager** | The ZMS module that synchronises custom code between ZODB and a filesystem folder (and optionally Git). |
| **ZODB** | Zope Object Database — the native Python object persistence store used by Zope and ZMS. |
| **ZCatalog** | The Zope full-text search catalog, used by ZMS for built-in site search. |
| **ZMI** | ZMS / Zope Management Interface — the browser-based editorial and administrative GUI. |
| **ZMS** | Zope-based Content Management System — the CMS documented here. |
| **ZMSIndex** | A lightweight catalog (`zmsindex_catalog`) mapping ZMS IDs, UUIDs, and Zope paths for fast link resolution. |
| **`version_live_id`** | Pointer to the currently published version of a content block. |
| **`version_work_id`** | Pointer to the working (in-progress) version of a content block. |
| **`TR_ENTER` / `TR_LEAVE`** | Implicit workflow transitions that enter and exit the workflow cycle. |
| **`AC_CHANGED`** | The initial activity state assigned to a page container when any of its content is modified. |

---

## External Resources

### ZMS and Zope

| Resource | URL |
|---|---|
| ZMS source code | <https://github.com/zms-publishing/ZMS> |
| ZMS PyPI package | <https://pypi.org/project/Products.zms/> |
| Zope documentation | <https://zope.readthedocs.io/> |
| Zope source code | <https://github.com/zopefoundation/Zope> |
| Zope Foundation | <https://www.zope.dev/> |

### Python and deployment

| Resource | URL |
|---|---|
| Python 3 documentation | <https://docs.python.org/3/> |
| pip documentation | <https://pip.pypa.io/> |
| Virtualenv / venv | <https://docs.python.org/3/library/venv.html> |
| systemd unit files | <https://www.freedesktop.org/software/systemd/man/systemd.service.html> |

### Search and AI

| Resource | URL |
|---|---|
| Apache Solr | <https://solr.apache.org/> |
| Solr Docker image | <https://hub.docker.com/_/solr/> |
| Qdrant vector database | <https://qdrant.tech/> |
| Ollama local LLM | <https://ollama.com/> |
| OpenAI API | <https://platform.openai.com/docs/> |
| PDFMiner.six | <https://pypi.org/project/pdfminer.six/> |

### Content standards

| Resource | URL |
|---|---|
| Dublin Core Metadata Initiative | <https://www.dublincore.org/> |
| HTML Living Standard | <https://html.spec.whatwg.org/> |
| HTTP caching (MDN) | <https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching> |
| NGINX X-Accel | <https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/> |
