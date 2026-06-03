# ZMSLLMConnector

`ZMSLLMConnector` is a Zope object that bridges ZMS content management with Large Language Model (LLM) provider backends. It can be added as _ZMS component_ like the workflow- or repository-manager; like these ZMSLLMConnector is instanciated as a child object to the ZMS root. A new item "AI-Lab" will appear in the tab-navigation and offers a UI for configuration, communication and live testing.

## Architecture

```
ZMS root
 └─ ZMSLLMConnector  (id: llm_connector)
     ├─ manage_main  →  tabbed ZMI page
     │     Config   – provider, model, API key, endpoints, generation params
     │     Chat     – live chat / test interface (inline, no iframe)
     │     Features – enable/disable individual AI features
     └─ ZMSCustom children  (optional 3rd-view UI extensions)
```

The connector stores its own configuration in ZODB (`_config` dict). It is
retrieved from any ZMS context via `getLLMConnector()`:

```python
connector = context.getLLMConnector()
reply = connector.chat("Summarise this document")
```

## Frontend block integration

The metaobject class `llm_chat` (package `com.zms.foundation`) provides a page-embed chat block that reuses the same REST API (`++rest_api/llm_chat`) and connector backend (`llmapi` / `llmtools`) used by the connector UI.

## Supported Providers

| Provider | Description |
|----------|-------------|
| `openai` | OpenAI API (gpt-4o-mini, gpt-4, gpt-3.5-turbo, …) |
| `ollama` | Local Ollama deployment |
| `rag`    | Retrieval-Augmented Generation via Qdrant + Ollama |

All providers normalise responses to the OpenAI `/v1/chat/completions` schema.

## Configuration Properties

| Key | Description | Default |
|-----|-------------|---------|
| `llm.provider` | Provider type | `openai` |
| `llm.api.key` | OpenAI API key | – |
| `llm.api.model` | Model name | `gpt-4o-mini` |
| `llm.api.endpoint` | Custom endpoint URL | OpenAI default |
| `llm.llmtools.id` | Custom `*_llmtools` connector ID (empty = built-in tools) | – |
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.qdrant.host` | Qdrant server URL | `http://localhost:6333` |
| `llm.qdrant.collection` | Qdrant collection | `zms_docs` |
| `llm.embedding.model` | SentenceTransformer model | `all-MiniLM-L6-v2` |
| `llm.temperature` | Sampling temperature | `0.7` |
| `llm.top_p` | Nucleus sampling | `0.9` |
| `llm.max_tokens` | Max tokens (optional) | – |
| `llm.num_ctx` | Context window (Ollama) | `4096` |
| `llm.rag.top_k` | RAG: documents retrieved | `16` |
| `llm.rag.score_threshold` | RAG: min similarity | `0.0` |

## AI Features

Enable/disable via the **Features** tab:

| Feature key | Description |
|-------------|-------------|
| `rte_assist` | AI writing assistant in the Rich Text Editor |
| `translate_assist` | LLM-powered translation suggestions in the Translation tab |
| `metadata_gen` | Auto-generate keywords, abstract, SEO metadata on save |
| `rag_chat` | Document Q&A chat using RAG (requires Qdrant) |

## Custom LLM tools connector (`*_llmtools`)

To avoid hard-coding all agent tools in core, the connector supports a connector abstraction
similar to the catalog connector pattern:

1. Create/import a `ZMSLibrary` meta-object whose id either ends with `_llmtools` or
   ends with `_connector` and belongs to package `com.zms.llmtools.*` (for example `ollama_connector`).
2. Add script `get_llmtools(connector, context)` that returns OpenAI-style tool schemas.
3. Add optional scripts `llmtool_<name>(connector, context, args)` for execution.
4. Select this connector in **Configuration → LLM Tools Connector** (`llm.llmtools.id`).

If no connector is selected, ZMS uses the built-in `llmtools.py` toolset.

## Python API

```python
# Chat
reply = context.getLLMConnector().chat("What is ZMS?")
content = reply['message']['content']   # convenience accessor
# or via full OpenAI schema:
content = reply['choices'][0]['message']['content']

# Multi-turn
messages = [
    {"role": "system", "content": "You are a helpful ZMS assistant."},
    {"role": "user",   "content": "How do I add a new content type?"},
]
reply = context.getLLMConnector().chat(messages)

# Provider info
info = context.getLLMConnector().get_provider_info()

# Feature check
if context.getLLMConnector().isFeatureEnabled('rte_assist'):
    # show AI toolbar
    pass
```

```html
<tal:block tal:define="connector python:here.getLLMConnector()"
    tal:condition="python:connector and connector.isFeatureEnabled('rte_assist')">
  <!-- inject AI toolbar JS here -->
</tal:block>
```

## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `++rest_api/llm_chat?message=…` | GET | Single-turn chat |
| `++rest_api/llm_provider_info` | GET | Provider info |

## Repository Export

The connector configuration is included in ZMS repository exports as
`llm_connector/config.json`, enabling version-controlled configuration
management.

# AI-Coauthor (manage_coauthor)

This metacommand provides an editorial workspace for side-by-side content work in ZMS.
It supports two workflows:

- Auto-Translate between two different languages.
- Auto-Editing in the same language, using an LLM to improve quality and optionally complete metadata.

The tab is intended for structured editorial work on multilingual fields of a node.

## Purpose

AI-Coauthor helps editors:

- Compare source and target content side by side.
- Keep one side as read-only reference and edit the other side safely.
- Use AI-assisted suggestions directly in context.
- Accept or reject suggested changes on a token level before saving.

## Access and Scope

- Metacommand name: AI-Coauthor
- Stereotype: tab
- Available for all meta types
- Typical roles: ZMSEditor, ZMSAuthor, ZMSAdministrator

The tab renders multilingual attributes and skips technical/system attributes.

## Main UI Concepts

### 1) Two-column layout

- Left column: source/reference language (read-only during editing).
- Right column: target language (editable and save target).

### 2) Language selectors

- Separate selector for left and right language.
- Language choices are persisted in session.
- Changing a selector reloads the tab with the selected language pair.

### 3) Mode switch

- VIEW mode:
	- Shows rendered node output side by side.
	- Shows rendered child nodes and allows navigation into their AI-Coauthor tab.
- EDIT mode:
	- Shows editable form fields for multilingual attributes.
	- Provides Auto-Translate or Auto-Editing action depending on language selection.

## Auto Action Button Behavior

The green action button changes behavior based on language pair:

- Different languages (lang1 != lang2):
	- Button label: Auto-Translate
	- Workflow: copies source values and translates to target language.

- Same language (lang1 == lang2):
	- Button label: Auto-Editing
	- Workflow: requests LLM suggestions to improve style, clarity, and quality.
	- If no LLM connector is configured, the button is disabled.

## Auto-Translate Workflow (different languages)

1. Editor confirms action.
2. Source values from left column are read.
3. Translation is requested client-side for text inputs and textareas.
4. Result is written to right-side fields.
5. Updated fields are highlighted.

Use this for first-pass translation drafts.

## Auto-Editing Workflow (same language)

1. Editor confirms action.
2. Form rows are collected into a structured payload:
	 - field id
	 - label
	 - source value
	 - current target value
	 - metadata flag for common metadata fields
3. A strict JSON prompt is sent to the LLM endpoint.
4. Returned suggestions are mapped per field id.
5. For each changed field, HTML diff is generated and rendered in the right column.

Goal of this workflow:

- Improve grammar, wording, readability, consistency.
- Keep factual meaning unchanged.
- Optionally complete weak or missing metadata when metadata generation is enabled.

## Interactive Diff Review

In Auto-Editing mode, the right column displays interactive diff markup:

- Green additions (ins): click to reject an addition.
- Red deletions (del): click to restore deleted text.

Visual behavior:

- Rejected additions are dimmed and struck through.
- Restored deletions are highlighted and no longer struck through.

This allows editorial control before committing suggestions.

## Save Behavior and Content Handling

On form submit, diff editors are consolidated into final field values:

- Accepted additions are kept.
- Rejected additions are removed.
- Restored deletions are kept.
- Non-restored deletions are removed.

For richtext fields:

- HTML content is preserved.
- Diff wrapper containers are removed.

For plain text inputs:

- Output is normalized to plain text.

## Character Limit Warning (right column)

AI-Coauthor monitors right-side content length using text length without HTML tags.

- Threshold: more than 5000 characters.
- If exceeded, a visible warning banner is shown in the affected right-side field cell.

This warning is updated:

- during manual typing
- after paste/change events
- after diff token toggles
- after auto-edit result rendering
- before submit

## LLM and Metadata Integration

AI-Coauthor checks runtime connector capabilities:

- ai_enabled: LLM connector available
- metadata_enabled: metadata generation feature available

When metadata generation is enabled, the Auto-Editing prompt allows metadata completion for known metadata fields.

## Navigation and Editing Safety

The tab enforces full-page navigation for breadcrumbs and tabs in this workspace, so language and mode context are preserved.

Additional safeguards:

- Left-side edit controls are disabled and styled as reference.
- View mode rows are clickable for fast navigation to child node editing.

## Typical Editorial Workflow

1. Open AI-Coauthor tab on a node.
2. Choose source and target languages.
3. Use VIEW mode to compare rendered content quickly.
4. Switch to EDIT mode.
5. Run Auto-Translate (different languages) or Auto-Editing (same language).
6. Review and adjust right-side results.
7. In Auto-Editing, click diff tokens to accept/reject granular changes.
8. Check warnings for oversized target text.
9. Save.

## Notes for Administrators

- Auto-Editing requires a configured ZMSLLMConnector.
- Metadata completion in Auto-Editing depends on the connector feature metadata_gen.
- If LLM responses are invalid JSON, no automatic field mapping is applied.

## Troubleshooting

- Button disabled in same-language mode:
	- Verify LLM connector is configured and reachable.
- No fields updated after Auto-Editing:
	- Check that the LLM returned valid JSON object with field mappings.
- Unexpectedly long text warning:
	- Review the right-side field content; warning is based on plain text length without HTML tags.
