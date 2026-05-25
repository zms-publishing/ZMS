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
