# ZMS Documentation

ZMS is a free open-source content management system (CMS) based on the Python application server Zope. The name *ZMS* stands for **Zope-based Content Management System**. It focuses on building multilingual, multi-site portals for educational and scientific/technical/medical (STM) publishing.

## Table of Contents

### A. [Getting Started](a_getting_started.md)
Installation prerequisites, setting up a virtual environment, creating a Zope instance, and first login.

### B. [For Editors](b_for_editors.md)
Working with the ZMS Management Interface (ZMI): navigating content trees, creating and editing pages and content blocks, multilingual content production, workflow and publishing.

### C. [For Site Administrators](c_for_site_administrators.md)
Configuring ZMS: user management, languages, meta-attributes, content models, search engines (ZCatalog / Apache Solr), AI/LLM connectors, theming, and operational topics including caching and deployment.

### D. [For Developers](d_for_developers.md)
Setting up a development environment, understanding the ZMS object model, using the ZMS API, path traversal, cache control, extending ZMS with custom content classes, and contributing.

### E. [Appendices](e_appendices.md)
Workflow and versioning reference, glossary, external links, and release notes pointers.

---

## Legacy documents

The following source documents remain in `docs/` and are cross-referenced from the chapters above:

| Document | Audience | Topic |
|---|---|---|
| [index_en.md](index_en.md) | All | Original landing page |
| [edit_intro_en.md](edit_intro_en.md) | Editors | Editing GUI walkthrough (EN) |
| [edit_intro_de.md](edit_intro_de.md) | Editors | Editing GUI walkthrough (DE) |
| [admin_intro_en.md](admin_intro_en.md) | Admins | Configuration menu reference |
| [admin_solr_en.md](admin_solr_en.md) | Admins | Apache Solr connector setup |
| [develop_intro_en.md](develop_intro_en.md) | Developers | Installation & environment setup |
| [develop_api_examples_en.md](develop_api_exampels_en.md) | Developers | API code examples |
| [develop_cache.md](develop_cache.md) | Developers | Proxy cache and NGINX control |
| [llm_configuration.md](llm_configuration.md) | Admins | LLM / AI provider configuration |
| [versioning.md](versioning.md) | Admins / Devs | Workflow and versioning model |

---

## External resources

- [Zope Documentation](https://zope.readthedocs.io/)
- [ZMS Code Repository on GitHub](https://github.com/zms-publishing/ZMS)
- [Zope Repository on GitHub](https://github.com/zopefoundation/Zope)
