"""
llmtools.py – ZMS tool registry for LLM function/tool calling.

Provides:
    - ``LLM_TOOLS``: list of OpenAI-format tool schemas (also accepted by Ollama v0.3+).
    - ``execute_llmtool(name, args, context)``: dispatcher that maps tool names to live ZMS
    API calls via ``context.metaobj_manager``.

All tools operate on the metamodel manager reachable via the ZMS acquisition context.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

import json
from Products.zms import zopeutil
from Products.zms import standard


# ---------------------------------------------------------------------------
# Tool schemas (OpenAI function-calling format)
# ---------------------------------------------------------------------------

LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_content_types",
            "description": (
                "Return the list of all content type IDs defined in the ZMS metamodel. "
                "Use this first to discover what types already exist before creating new ones."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_type",
            "description": (
                "Return the full definition of a single ZMS content type including its "
                "attribute list, type string, display name and revision."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Content type ID, e.g. 'ZMSTeaser'.",
                    }
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_content_type",
            "description": (
                "Create a new ZMS content type (meta-object) in the metamodel. "
                "Optionally seed initial attributes and then generate a default "
                "standard_html template that binds known fields. "
                "By default, a standard_html ZPT rendering attribute is created as well. "
                "Use add_standard_html=false to skip that behavior. "
                "Avoid creating a type that already exists — check list_content_types first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": (
                            "Technical identifier (CamelCase, no spaces), e.g. 'ZMSTeaser'."
                        ),
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable display name, e.g. 'Teaser'.",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["ZMSObject", "ZMSDocument", "ZMSRecordSet", "ZMSTeaserElement"],
                        "description": (
                            "Base type. Use 'ZMSObject' for reusable/embeddable blocks, "
                            "'ZMSDocument' for page-level content."
                        ),
                    },
                    "add_standard_html": {
                        "type": "boolean",
                        "description": (
                            "Whether to create a default zpt attribute named "
                            "'standard_html'. Default is true."
                        ),
                    },
                    "attributes": {
                        "type": "array",
                        "description": (
                            "Optional list of initial attributes to create before "
                            "generating standard_html."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "attr_id": {
                                    "type": "string",
                                    "description": "Attribute identifier (snake_case).",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Human-readable label.",
                                },
                                "datatype": {
                                    "type": "string",
                                    "enum": [
                                        "amount", "autocomplete", "boolean", "color", "constant",
                                        "date", "datetime", "delimiter", "dictionary", "file",
                                        "float", "hint", "identifier", "image", "int",
                                        "interface", "list", "method", "multiautocomplete",
                                        "multiselect", "password", "py", "resource", "richtext",
                                        "select", "string", "text", "time", "url", "xml", "zpt",
                                        "DTML Method", "DTML Document", "External Method", "File",
                                        "Folder", "Image", "Page Template", "Script (Python)", "Z SQL Method"
                                    ],
                                    "description": "Attribute data type.",
                                },
                                "mandatory": {
                                    "type": "boolean",
                                    "description": "Whether the field is required.",
                                },
                                "multilang": {
                                    "type": "boolean",
                                    "description": "Whether the field is language-specific.",
                                },
                                "repetitive": {
                                    "type": "boolean",
                                    "description": "Whether the field is repetitive.",
                                },
                                "default": {
                                    "type": "string",
                                    "description": "Optional default value for the field.",
                                },
                                "custom": {
                                    "type": "string",
                                    "description": (
                                        "Optional custom/source value. For datatype 'constant', "
                                        "this is the primary value shown in the ZMS GUI."
                                    ),
                                },
                            },
                            "required": ["attr_id", "datatype"],
                        },
                    },
                },
                "required": ["id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_attribute",
            "description": (
                "Add a single attribute/field to an existing ZMS content type. "
                "Call this once per attribute after creating the content type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "meta_id": {
                        "type": "string",
                        "description": "Content type ID to add the attribute to.",
                    },
                    "attr_id": {
                        "type": "string",
                        "description": "Attribute identifier (snake_case), e.g. 'teaser_text'.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable label shown in the ZMI form.",
                    },
                    "datatype": {
                        "type": "string",
                        "enum": [
                            "amount", "autocomplete", "boolean", "color", "constant",
                            "date", "datetime", "delimiter", "dictionary", "file",
                            "float", "hint", "identifier", "image", "int",
                            "interface", "list", "method", "multiautocomplete",
                            "multiselect", "password", "py", "resource", "richtext",
                            "select", "string", "text", "time", "url", "xml", "zpt",
                            "DTML Method", "DTML Document", "External Method", "File",
                            "Folder", "Image", "Page Template", "Script (Python)", "Z SQL Method"
                        ],
                        "description": "Attribute data type.",
                    },
                    "mandatory": {
                        "type": "boolean",
                        "description": "Whether the field is required. Default false.",
                    },
                    "multilang": {
                        "type": "boolean",
                        "description": (
                            "Whether the field is language-specific. Default true for "
                            "text/richtext, false for images/urls."
                        ),
                    },
                    "repetitive": {
                        "type": "boolean",
                        "description": "Whether the field is repetitive. Default false.",
                    },
                    "default": {
                        "type": "string",
                        "description": "Optional default value for the field.",
                    },
                    "custom": {
                        "type": "string",
                        "description": (
                            "Optional custom/source value. For datatype 'constant', "
                            "this is the primary value shown in the ZMS GUI."
                        ),
                    },
                },
                "required": ["meta_id", "attr_id", "datatype"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_attribute_custom",
            "description": (
                "Update the custom/source payload of an existing content type "
                "attribute without regenerating defaults. Use this to write back "
                "edited ZPT, Python, method, interface, resource, or constant "
                "code/content after the user asked to save a specific change. "
                "Preserves the existing attribute metadata and does not invent "
                "default template code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "meta_id": {
                        "type": "string",
                        "description": "Content type ID, e.g. 'alertbox'.",
                    },
                    "attr_id": {
                        "type": "string",
                        "description": "Existing attribute ID, e.g. 'standard_html'.",
                    },
                    "custom": {
                        "type": "string",
                        "description": (
                            "New raw source/content to store in the attribute's "
                            "custom payload, for example beautified ZPT code."
                        ),
                    },
                },
                "required": ["meta_id", "attr_id", "custom"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "regenerate_standard_html",
            "description": (
                "Generate default standard_html code from the current attribute "
                "list of an existing content type, but only write it when the "
                "standard_html attribute is missing or empty. Existing non-empty "
                "templates are always preserved. Do not use this tool to edit, "
                "beautify, optimize, or rewrite existing custom template code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Content type ID, e.g. 'ZMSTeaser'.",
                    },
                    "create_if_missing": {
                        "type": "boolean",
                        "description": (
                            "Create standard_html as zpt when missing. Default true."
                        ),
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": (
                            "If true, return generated template only and do not "
                            "persist any changes. Default false."
                        ),
                    },
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_standard_html_to_default",
            "description": (
                "Explicitly replace the current standard_html template with newly "
                "generated default code based on the current attribute list. "
                "Use only when the user clearly and explicitly asks to reset, "
                "replace, or overwrite the existing standard_html template with "
                "default generated code. Never use this for beautifying, "
                "reviewing, or preserving existing custom code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Content type ID, e.g. 'ZMSTeaser'.",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": (
                            "If true, return generated template only and do not "
                            "persist any changes. Default false."
                        ),
                    },
                    "create_if_missing": {
                        "type": "boolean",
                        "description": (
                            "Create standard_html as zpt when missing. Default true."
                        ),
                    },
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_content_type",
            "description": (
                "Permanently delete a ZMS content type from the metamodel. "
                "Only use when explicitly requested — this is irreversible."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Content type ID to delete.",
                    }
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_content_type_xml",
            "description": (
                "Export one or more content types as ZMS metamodel XML. "
                "Useful for inspecting the raw definition or backup."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of content type IDs to export.",
                    }
                },
                "required": ["ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "index_qdrant",
            "description": (
                "Index all published ZMS page content into the Qdrant vector database "
                "so it can be searched by the RAG provider. "
                "Call this when the user says something like 'index all content', "
                "'please index the site', or 'update the RAG index'. "
                "It crawls every page in the ZMS tree, renders the body content, "
                "splits it into chunks, embeds each chunk with a SentenceTransformer "
                "model, and upserts the vectors into Qdrant. "
                "Use the 'lang' parameter to restrict indexing to a single language; "
                "by default all configured site languages are indexed. "
                "Set reset=false to append to an existing collection instead of "
                "rebuilding it from scratch."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "lang": {
                        "type": "string",
                        "description": (
                            "Language code to index, e.g. 'eng' or 'deu'. "
                            "Omit to index all site languages."
                        ),
                    },
                    "collection": {
                        "type": "string",
                        "description": (
                            "Qdrant collection name. Defaults to the value of "
                            "llm.qdrant.collection site property (usually 'zms_docs')."
                        ),
                    },
                    "reset": {
                        "type": "boolean",
                        "description": (
                            "When true (default), drop and recreate the collection "
                            "before indexing so stale entries are removed."
                        ),
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Maximum characters per chunk (default 1200).",
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between consecutive chunks (default 200).",
                    },
                },
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Tool executor
# ---------------------------------------------------------------------------

def execute_llmtool(name, args, context):
    """
    Dispatch a tool call to the corresponding ZMS API.

    @param name: Tool name as returned in the LLM tool_call.
    @param args: Dict of parsed arguments from the LLM.
    @param context: ZMS acquisition context (must have ``metaobj_manager`` attribute).
    @return: JSON-serialisable result dict.
    """
    try:
        mm = context.metaobj_manager

        if name == 'list_content_types':
            ids = mm.getMetaobjIds(sort=False)
            types = []
            for tid in ids:
                ob = mm.getMetaobj(tid)
                types.append({
                    'id': tid,
                    'name': ob.get('name', tid),
                    'type': ob.get('type', ''),
                })
            return {'content_types': types, 'count': len(types)}

        elif name == 'get_content_type':
            tid = args['id']
            ob = mm.getMetaobj(tid)
            if not ob:
                return {'error': f"Content type '{tid}' not found."}
            attrs = []
            for attr_id in mm.getMetaobjAttrIds(tid):
                a = mm.getMetaobjAttr(tid, attr_id, sync=True)
                if not a:
                    continue
                custom = a.get('custom', '')
                if a.get('type') in mm.valid_zopeattrs + mm.valid_zopetypes:
                    ob_attr = a.get('ob')
                    if ob_attr is not None:
                        custom = zopeutil.readData(ob_attr, default=custom)
                attrs.append({
                    'id': a.get('id'),
                    'name': a.get('name', ''),
                    'datatype': a.get('type', 'string'),
                    'mandatory': bool(a.get('mandatory', 0)),
                    'multilang': bool(a.get('multilang', 1)),
                    'keys': a.get('keys', []),
                    'custom': custom,
                    'default': a.get('default', '')
                })
            return {
                'id': ob.get('id'),
                'name': ob.get('name', ''),
                'type': ob.get('type', ''),
                'revision': ob.get('revision', '0.0.0'),
                'attributes': attrs,
            }

        elif name == 'create_content_type':
            tid = args['id']
            existing = mm.getMetaobjIds()
            if tid in existing:
                return {'error': f"Content type '{tid}' already exists. Use add_attribute to extend it."}
            ob = {
                'id': tid,
                'name': args.get('name', tid),
                'type': args.get('type', 'ZMSObject'),
                'revision': '0.0.0',
                'attrs': [],
            }
            mm.setMetaobj(ob)

            created_attrs = []
            for spec in args.get('attributes', []):
                attr_id = spec['attr_id']
                datatype = spec.get('datatype', 'string')
                mandatory = 1 if spec.get('mandatory', False) else 0
                default_multilang = datatype in ('string', 'text', 'richtext', 'select', 'multiselect')
                multilang = 1 if spec.get('multilang', default_multilang) else 0
                repetitive = 1 if spec.get('repetitive', False) else 0
                default_value = spec.get('default', '')
                custom_value = spec.get('custom', '')
                # In ZMS, constants are edited via attr_custom_* in the GUI,
                # so map provided default into custom for compatibility.
                if datatype == 'constant' and custom_value in (None, '') and default_value not in (None, ''):
                    custom_value = default_value
                    default_value = ''
                name = spec.get('name', attr_id.replace('_', ' ').title())

                mm.setMetaobjAttr(
                    tid,
                    None,
                    attr_id,
                    name,
                    mandatory,
                    multilang,
                    repetitive,
                    datatype,
                    [],
                    custom_value,
                    default_value,
                )
                created_attrs.append({'id': attr_id, 'type': datatype, 'repetitive': repetitive})

            add_standard_html = args.get('add_standard_html', True)
            standard_html_added = False
            if add_standard_html and 'standard_html' not in mm.getMetaobjAttrIds(tid):
                mm.setMetaobjAttr(
                    tid,              # id (content type)
                    None,             # oldId (None = insert new)
                    'standard_html',  # newId
                    'Template: Default',
                    0,                # newMandatory
                    1,                # newMultilang
                    0,                # newRepetitive
                    'zpt',            # newType
                    [],               # newKeys
                    mm.manage_create_default_zpt(tid, target_id='standard_html', attrs=created_attrs),
                    '',               # newDefault
                )
                standard_html_added = True

            return {
                'created': tid,
                'name': ob['name'],
                'type': ob['type'],
                'attributes_added': len(created_attrs),
                'standard_html_added': standard_html_added,
            }

        elif name == 'add_attribute':
            meta_id = args['meta_id']
            attr_id = args['attr_id']
            datatype = args.get('datatype', 'string')
            mandatory = 1 if args.get('mandatory', False) else 0
            repetitive = 1 if args.get('repetitive', False) else 0
            default_value = args.get('default', '')
            custom_value = args.get('custom', '')
            # In ZMS, constants are edited via attr_custom_* in the GUI,
            # so map provided default into custom for compatibility.
            if datatype == 'constant' and custom_value in (None, '') and default_value not in (None, ''):
                custom_value = default_value
                default_value = ''
            # Sensible multilang defaults: text fields yes, media/url fields no
            default_multilang = datatype in ('string', 'text', 'richtext', 'select', 'multiselect')
            multilang = 1 if args.get('multilang', default_multilang) else 0
            name = args.get('name', attr_id.replace('_', ' ').title())
            mm.setMetaobjAttr(
                meta_id,    # id (content type)
                None,       # oldId (None = insert new)
                attr_id,    # newId
                name,       # newName
                mandatory,  # newMandatory
                multilang,  # newMultilang
                repetitive, # newRepetitive
                datatype,   # newType
                [],         # newKeys
                custom_value,
                default_value,
            )
            return {
                'added': attr_id,
                'to': meta_id,
                'datatype': datatype,
                'mandatory': bool(mandatory),
                'multilang': bool(multilang),
                'repetitive': bool(repetitive),
                'default': default_value,
                'custom': custom_value,
            }

        elif name == 'update_attribute_custom':
            meta_id = args['meta_id']
            attr_id = args['attr_id']
            custom_value = args.get('custom', '')

            existing = mm.getMetaobjAttr(meta_id, attr_id, sync=True)
            if not existing:
                return {
                    'error': (
                        f"Attribute '{attr_id}' not found in content type '{meta_id}'."
                    )
                }

            mm.setMetaobjAttr(
                meta_id,
                attr_id,
                attr_id,
                existing.get('name', attr_id),
                existing.get('mandatory', 0),
                existing.get('multilang', 1),
                existing.get('repetitive', 0),
                existing.get('type', 'string'),
                existing.get('keys', []),
                custom_value,
                existing.get('default', ''),
            )

            return {
                'updated': attr_id,
                'to': meta_id,
                'datatype': existing.get('type', 'string'),
                'custom_length': len(custom_value),
            }

        elif name in ('regenerate_standard_html', 'reset_standard_html_to_default'):
            tid = args['id']
            ob = mm.getMetaobj(tid)
            if not ob:
                return {'error': f"Content type '{tid}' not found."}

            attrs = []
            for attr_id in mm.getMetaobjAttrIds(tid):
                attr = mm.getMetaobjAttr(tid, attr_id)
                if not attr:
                    continue
                attrs.append({
                    'id': attr.get('id', attr_id),
                    'type': attr.get('type', 'string'),
                    'repetitive': attr.get('repetitive', 0),
                })

            has_standard_html = 'standard_html' in mm.getMetaobjAttrIds(tid)
            create_if_missing = args.get('create_if_missing', True)
            dry_run = args.get('dry_run', False)
            allow_overwrite = (name == 'reset_standard_html_to_default')
            if not has_standard_html and not create_if_missing:
                return {
                    'error': (
                        f"Content type '{tid}' has no standard_html attribute. "
                        "Set create_if_missing=true to create it."
                    )
                }

            existing = {}
            existing_template = ''
            if has_standard_html:
                existing = mm.getMetaobjAttr(tid, 'standard_html', sync=True) or {}
                existing_template = existing.get('custom', '')
                existing_ob = existing.get('ob')
                if existing_ob is not None:
                    existing_template = zopeutil.readData(existing_ob, default=existing_template)
                existing_template = existing_template or ''

            template = mm.manage_create_default_zpt(tid, target_id='standard_html', attrs=attrs)
            if dry_run:
                return {
                    'dry_run': True,
                    'id': tid,
                    'would_create_standard_html': not has_standard_html,
                    'would_overwrite_existing': bool(has_standard_html and existing_template and allow_overwrite),
                    'has_existing_template': bool(existing_template),
                    'attributes_seen': len(attrs),
                    'template': template,
                }

            if has_standard_html and existing_template and not allow_overwrite:
                return {
                    'skipped': tid,
                    'reason': (
                        "standard_html already contains template code. "
                        "Use reset_standard_html_to_default only when the user "
                        "explicitly requests overwriting it."
                    ),
                    'attributes_seen': len(attrs),
                    'has_existing_template': True,
                }

            if has_standard_html:
                mm.setMetaobjAttr(
                    tid,
                    'standard_html',
                    'standard_html',
                    existing.get('name', 'Template: Default'),
                    existing.get('mandatory', 0),
                    existing.get('multilang', 1),
                    existing.get('repetitive', 0),
                    'zpt',
                    existing.get('keys', []),
                    template,
                    existing.get('default', ''),
                )
            else:
                mm.setMetaobjAttr(
                    tid,
                    None,
                    'standard_html',
                    'Template: Default',
                    0,
                    1,
                    0,
                    'zpt',
                    [],
                    template,
                    '',
                )

            return {
                'updated': tid,
                'standard_html_created': not has_standard_html,
                'attributes_seen': len(attrs),
            }

        elif name == 'delete_content_type':
            tid = args['id']
            if tid not in mm.getMetaobjIds():
                return {'error': f"Content type '{tid}' not found."}
            mm.delMetaobj(tid)
            return {'deleted': tid}

        elif name == 'export_content_type_xml':
            ids = args.get('ids', [])
            xml = mm.exportMetaobjXml(ids)
            # Trim to avoid flooding the LLM context
            if isinstance(xml, bytes):
                xml = xml.decode('utf-8', errors='replace')
            if len(xml) > 4000:
                xml = xml[:4000] + '\n... (truncated)'
            return {'xml': xml}

        elif name == 'index_qdrant':
            return _tool_index_qdrant(args, context)

        else:
            return {'error': f"Unknown tool: {name}"}

    except Exception as exc:
        return {'error': str(exc)}


# ---------------------------------------------------------------------------
# index_qdrant implementation
# ---------------------------------------------------------------------------

def _tool_index_qdrant(args, context):
    """
    Crawl every ZMS page, render its body content, chunk + embed the text,
    and upsert all vectors into the configured Qdrant collection.

    Runs fully inside the Zope process — no external HTTP calls required.
    """
    import re

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        return {
            'error': (
                f"Missing dependency: {exc}. "
                "Install qdrant-client and sentence-transformers in the Zope Python environment."
            )
        }

    # --- configuration -------------------------------------------------------
    connector = context.getLLMConnector()
    if connector is None:
        return {'error': 'No ZMSLLMConnector found. Add one to the ZMS root first.'}

    from urllib.parse import urlparse
    qdrant_host = connector.getConfProperty('llm.qdrant.host', 'http://localhost:6333')
    collection  = args.get('collection') or connector.getConfProperty('llm.qdrant.collection', 'zms_docs')
    embed_model = connector.getConfProperty('llm.embedding.model', 'all-MiniLM-L6-v2')
    reset       = args.get('reset', True)
    chunk_size  = int(args.get('chunk_size', 1200))
    overlap     = int(args.get('chunk_overlap', 200))

    parsed = urlparse(qdrant_host)
    qdrant = QdrantClient(host=parsed.hostname or 'localhost', port=parsed.port or 6333)

    # --- (re)create collection -----------------------------------------------
    if reset:
        try:
            qdrant.delete_collection(collection_name=collection)
        except Exception:
            pass
        qdrant.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    # --- helpers -------------------------------------------------------------
    def strip_html(html):
        text = re.sub(r'<[^>]+>', ' ', html or '')
        return re.sub(r'\s+', ' ', text).strip()

    def chunk_text(text):
        chunks, start, step = [], 0, max(chunk_size - overlap, 1)
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += step
        return chunks

    # --- discover pages ------------------------------------------------------
    from Products.zms import mock_http

    root = context.getDocumentElement()
    lang_arg = args.get('lang')
    langs = [lang_arg] if lang_arg else root.getLangIds()

    records, processed, skipped = [], 0, 0

    for lng in langs:
        request = mock_http.MockHTTPRequest({'lang': lng})
        # zcatalog_index returns lightweight brain objects with getPath()
        brains = root.zcatalog_index({'path':'/'})
        for brain in brains:
            try:
                path = brain.getPath()
                node = root.unrestrictedTraverse(path)
                if not getattr(node, 'isPage', lambda: False)():
                    continue
                html = node.getBodyContent(request, forced=False)
                text = strip_html(html)
                if not text:
                    skipped += 1
                    continue
                title = node.getTitle(request)
                url   = node.absolute_url()
                for i, chunk in enumerate(chunk_text(text)):
                    records.append({
                        'text':        chunk,
                        'path':        path,
                        'url':         url,
                        'title':       title,
                        'lang':        lng,
                        'meta_id':     getattr(node, 'meta_id', ''),
                        'chunk_index': i,
                    })
                processed += 1
                standard.writeStdout(node, f"Qdrant Indexing: {path} (lang={lng}, chunks={len(records)})")
            except Exception:
                standard.writeStdout(node, f"Qdrant Indexing: {path} skipped due to error")
                skipped += 1

    # --- embed and upsert in batches -----------------------------------------
    model      = SentenceTransformer(embed_model)
    batch_size = 64
    point_id   = 0

    for i in range(0, len(records), batch_size):
        batch   = records[i:i + batch_size]
        vectors = model.encode([r['text'] for r in batch]).tolist()
        points  = [
            PointStruct(id=point_id + j, vector=vec, payload=rec)
            for j, (rec, vec) in enumerate(zip(batch, vectors))
        ]
        qdrant.upsert(collection_name=collection, points=points)
        point_id += len(batch)

    return {
        'collection': collection,
        'languages':  langs,
        'pages_indexed': processed,
        'pages_skipped': skipped,
        'total_chunks':  point_id,
    }
