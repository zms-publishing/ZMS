# ZMS LLM Integration

## Quick Start

### Option 1: OpenAI (Cloud)

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Configure in ZMS:
   ```python
   llm.provider = openai
   llm.api.key = sk-your-key-here
   llm.api.model = gpt-4o-mini
   ```

### Option 2: Ollama (Local)

1. Start Ollama service:
   ```bash
   cd docker/addons/llm
   docker compose -f docker-compose.llm.yml up -d ollama
   docker exec -it zms_ollama ollama pull llama2
   ```

2. Configure in ZMS:
   ```python
   llm.provider = ollama
   llm.ollama.host = http://localhost:11434
   llm.api.model = llama2
   ```

### Option 3: RAG with Qdrant

1. Start both services:
   ```bash
   cd docker/addons/llm
   docker compose -f docker-compose.llm.yml up -d
   docker exec -it zms_ollama ollama pull llama2
   ```

2. Configure in ZMS:
   ```python
   llm.provider = rag
   llm.ollama.host = http://localhost:11434
   llm.qdrant.host = http://localhost:6333
   llm.qdrant.collection = zms_docs
   llm.api.model = llama2
   ```

## Features

- **Multi-provider support**: Switch between OpenAI, Ollama, or RAG without code changes
- **Docker-ready**: Includes docker-compose setup for local deployment
- **REST API**: Access via `++rest_api/llm_chat` endpoint
- **Provider info**: Check current configuration via `++rest_api/llm_provider_info`


## Files

- `llmapi.py` - Main LLM API module with provider abstraction
- `docker/llm/docker-compose.llm.yml` - Docker setup for Ollama and Qdrant
- `docs/llm_configuration.md` - Complete configuration guide
- `tests/test_llmapi.py` - Unit tests

## Architecture

```
┌─────────────────┐
│  ZMS Interface  │
│  (manage_llm)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   llmapi.chat() │
│   (REST API)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Provider│
    │ Factory │
    └────┬────┘
         │
    ┌────┴────────────────────────┐
    │                             │
    ▼                             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  OpenAI  │  │  Ollama  │  │   RAG    │
│ Provider │  │ Provider │  │ Provider │
└──────────┘  └──────────┘  └────┬─────┘
                                  │
                            ┌─────┴─────┐
                            ▼           ▼
                        ┌────────┐  ┌────────┐
                        │ Qdrant │  │ Ollama │
                        │(Vector)│  │  (LLM) │
                        └────────┘  └────────┘
```


## Documentation

See [docs/llm_configuration.md](../docs/llm_configuration.md) for:
- Complete configuration reference
- Docker setup instructions
- RAG with Qdrant setup
- Troubleshooting guide
- API usage examples
- Best practices

## Testing

Run the unit tests:

```bash
cd tests
python test_llmapi.py
```

