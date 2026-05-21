"""
llmtools.py – ZMS tool registry for LLM function/tool calling.

Provides:
- ``LLM_TOOLS``: list of OpenAI-format tool schemas (also accepted by Ollama v0.3+).
- ``execute_llmtool(name, args, context)``: dispatcher that maps tool names to live ZMS
  API calls via ``context.metaobj_manager``.

All tools operate on the metamodel manager reachable via the ZMS acquisition context.
"""

import json


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
                "The type is initially created without attributes; use add_attribute "
                "afterwards to add individual fields. Avoid creating a type that already "
                "exists — check list_content_types first."
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
                            "string", "text", "richtext", "boolean", "int", "float",
                            "date", "datetime", "url", "email", "image", "file",
                            "select", "multiselect",
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
                },
                "required": ["meta_id", "attr_id", "datatype"],
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
            return {'created': tid, 'name': ob['name'], 'type': ob['type']}

        elif name == 'add_attribute':
            meta_id = args['meta_id']
            attr_id = args['attr_id']
            datatype = args.get('datatype', 'string')
            mandatory = 1 if args.get('mandatory', False) else 0
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
                0,          # newRepetitive
                datatype,   # newType
                [],         # newKeys
                '',         # newCustom
                '',         # newDefault
            )
            return {
                'added': attr_id,
                'to': meta_id,
                'datatype': datatype,
                'mandatory': bool(mandatory),
                'multilang': bool(multilang),
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
