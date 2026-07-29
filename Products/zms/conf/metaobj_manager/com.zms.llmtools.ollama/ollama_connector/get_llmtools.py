import copy
from Products.zms import llmtools


def get_llmtools(connector, context):
    """
    Tool schemas (OpenAI function-calling format)

    Return MCP/OpenAI-compatible tool declarations for this profile.
    You can return the built-in tools from llmtools.BUILTIN_LLM_TOOLS with
    return copy.deepcopy(llmtools.BUILTIN_LLM_TOOLS)
    or define custom ones here as shown as default code below.
    The tool definitions must be JSON-serializable.
    """

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

    return LLM_TOOLS
