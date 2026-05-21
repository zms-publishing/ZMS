"""
llmtools.py – ZMS tool registry for LLM function/tool calling.

Provides:
- ``LLM_TOOLS``: list of OpenAI-format tool schemas (also accepted by Ollama v0.3+).
- ``execute_llmtool(name, args, context)``: dispatcher that maps tool names to live ZMS
  API calls via ``context.metaobj_manager``.

All tools operate on the metamodel manager reachable via the ZMS acquisition context.
"""

import json


def _shorten_attr_id(attr_id):
    """Mirror manage_main.zpt shorten_id() for default template generation."""
    sid = str(attr_id)
    sid = sid.split('attr_')[-1]
    sid = sid.split('dc_')[-1]
    sid = sid.split('/')[-1]
    return sid


def _build_default_standard_html(meta_id, attrs=None, target_id='standard_html'):
    """Build a default ZPT template and include bindings for known attributes."""
    attrs = attrs or []
    ignored_ids = {'standard_html', 'check_constraints'}
    ignored_types = {'delimiter', 'interface', 'constant'}

    tal_defs = []
    tal_content = []

    for attr in attrs:
        attr_id = str(attr.get('id', '')).strip()
        attr_type = str(attr.get('type', '')).strip()
        is_repetitive = bool(attr.get('repetitive', 0))
        if not attr_id or not attr_type:
            continue
        if attr_id in ignored_ids or attr_type in ignored_types:
            continue

        sid = _shorten_attr_id(attr_id)
        escaped_attr_id = attr_id.replace("'", "\\'")

        if attr_type == 'url':
            tal_defs.append(f"\n\t\t{sid} python:zmscontext.attr('{escaped_attr_id}');")
            tal_defs.append(
                f"\n\t\t{sid}_obj python:'{{' in {sid} and zmscontext.getLinkObj({sid},request) or None;"
            )
            tal_defs.append(
                f"\n\t\t{sid}_target python:{sid}_obj and {sid}_obj.getHref2IndexHtml(request) or {sid};"
            )
        elif is_repetitive:
            if attr_type != '*':
                escaped_attr_type = attr_type.replace("'", "\\'")
                tal_defs.append(
                    f"\n\t\t{sid}_list python:zmscontext.filteredChildNodes(request,'{escaped_attr_type}');"
                )
            else:
                tal_defs.append(f"\n\t\t{sid}_list python:zmscontext.filteredChildNodes(request);")
        elif attr_type == 'Script (Python)':
            tal_defs.append(f"\n\t\t{sid} here/{escaped_attr_id};")
        else:
            tal_defs.append(f"\n\t\t{sid} python:zmscontext.attr('{escaped_attr_id}');")

        if attr_type == 'image':
            tal_content.append(
                f"\n\t<img class=\"{sid}\" tal:attributes=\"src python:{sid}.getHref(request)\" alt=\"Image\" />"
            )
        elif attr_type == 'url':
            tal_content.append(
                f"\n\t<a class=\"{sid}\" tal:condition=\"{sid}\" "
                f"tal:attributes=\"href python:{sid}_obj and {sid}_target or {sid}; "
                f"target python:{sid}_obj and '_self' or '_blank';\">Link...</a>"
            )
        elif attr_type == 'file':
            tal_content.append(
                f"\n\t<a class=\"{sid}\" tal:condition=\"{sid}\" "
                f"tal:attributes=\"href python:{sid}.getHref(request);"
                f"title python:'Download-File Size: %s, Type: %s'%({sid}.getDataSizeStr(),{sid}.getContentType())\" "
                f"tal:content=\"python:{sid}.getFilename()\">Filename</a>"
            )
        elif attr_type == 'richtext':
            tal_content.append(f"\n\t<div class=\"{sid}\" tal:content=\"structure {sid}\">{sid}</div>")
        elif attr_type == 'datetime':
            tal_content.append(
                f"\n\t<div class=\"{sid}\" tal:condition=\"{sid}\" "
                f"tal:content=\"python:zmscontext.getLangFmtDate({sid},request.get('lang'))\">{sid}</div>"
            )
        elif is_repetitive:
            tal_content.append(
                f"\n\t<div class=\"{sid} repetitive\" tal:condition=\"{sid}_list\">"
                f"\n\t\t<tal:block tal:repeat=\"{sid}_listitem {sid}_list\" "
                f"tal:content=\"structure python:{sid}_listitem.renderShort(request)\">{sid}</tal:block>"
                f"\n\t</div>"
            )
        elif attr_type == 'Script (Python)':
            tal_content.append(f"\n\t<div class=\"{sid}\" tal:content=\"structure {sid}\">{attr_id}</div>")
        else:
            tal_content.append(f"\n\t<div class=\"{sid}\" tal:content=\"{sid}\">{sid}</div>")

    comment = f"<!-- {meta_id}.{target_id} -->"
    default_template = (
        '<div title="Default-ZPT-Code"\n'
        '\ttal:define="zmscontext options/zmscontext;\n'
        '\t\tid python:zmscontext.getId();\n'
        f"\t\tcss_class python:zmscontext.meta_id;{''.join(tal_defs)}\"\n"
        f"\ttal:attributes=\"id id;class css_class\">{''.join(tal_content)}\n</div>"
    )
    return f"{comment}\n{default_template}\n{comment}"


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
            "name": "regenerate_standard_html",
            "description": (
                "Regenerate the standard_html zpt template from the current "
                "attribute list of an existing content type. "
                "Useful after adding or changing attributes."
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
            for a in ob.get('attrs', []):
                attrs.append({
                    'id': a.get('id'),
                    'name': a.get('name', ''),
                    'datatype': a.get('type', 'string'),
                    'mandatory': bool(a.get('mandatory', 0)),
                    'multilang': bool(a.get('multilang', 1)),
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
                    _build_default_standard_html(tid, created_attrs, target_id='standard_html'),
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

        elif name == 'regenerate_standard_html':
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
            if not has_standard_html and not create_if_missing:
                return {
                    'error': (
                        f"Content type '{tid}' has no standard_html attribute. "
                        "Set create_if_missing=true to create it."
                    )
                }

            template = _build_default_standard_html(tid, attrs, target_id='standard_html')
            if dry_run:
                return {
                    'dry_run': True,
                    'id': tid,
                    'would_create_standard_html': not has_standard_html,
                    'attributes_seen': len(attrs),
                    'template': template,
                }

            if has_standard_html:
                existing = mm.getMetaobjAttr(tid, 'standard_html') or {}
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

        else:
            return {'error': f"Unknown tool: {name}"}

    except Exception as exc:
        return {'error': str(exc)}
