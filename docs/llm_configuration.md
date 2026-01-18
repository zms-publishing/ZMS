# LLM API Configuration Guide

ZMS now supports multiple Large Language Model (LLM) providers through an abstract API interface. This allows you to use different AI backends including OpenAI, local Ollama deployments, and RAG (Retrieval-Augmented Generation) with Qdrant vector database.

## Overview

The LLM integration provides a chat interface accessible from the ZMS management interface. You can configure different providers based on your needs:

- **OpenAI**: Cloud-based GPT models (requires API key and internet connection)
- **Ollama**: Local LLM deployment (no API key needed, runs on your infrastructure)
- **RAG**: Retrieval-Augmented Generation using Qdrant vector database with Ollama

## Configuration Properties

All configuration is done via ZMS configuration properties. Set these in your ZMS instance configuration.

### General Settings

| Property | Description | Default |
|----------|-------------|---------|
| `llm.provider` | Provider type: `openai`, `ollama`, or `rag` | `openai` |
| `llm.api.model` | Model name to use | `gpt-4o-mini` (OpenAI), `llama2` (Ollama) |

### OpenAI Configuration

For using OpenAI's cloud API:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.api.key` | Your OpenAI API key | (required) |
| `llm.api.endpoint` | Custom endpoint URL | `https://api.openai.com/v1/chat/completions` |
| `llm.api.model` | Model name | `gpt-4o-mini` |

### Ollama Configuration

For using local Ollama deployment:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name (e.g., `llama2`, `mistral`, `codellama`) | `llama2` |

### RAG Configuration

For using RAG with Qdrant vector database and Ollama:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.qdrant.host` | Qdrant server URL | `http://localhost:6333` |
| `llm.qdrant.collection` | Collection name for vector search | `zms_docs` |
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name | `llama2` |

## Configuration Examples

### Example 1: OpenAI (Cloud)

```python
# In your ZMS configuration
llm.provider = openai
llm.api.key = sk-your-openai-api-key-here
llm.api.model = gpt-4o-mini
```

### Example 2: Ollama (Local)

```python
# In your ZMS configuration
llm.provider = ollama
llm.ollama.host = http://localhost:11434
llm.api.model = llama2
```

For Docker deployments, you might use:
```python
llm.provider = ollama
llm.ollama.host = http://ollama:11434  # Docker service name
llm.api.model = mistral
```

### Example 3: RAG with Qdrant

```python
# In your ZMS configuration
llm.provider = rag
llm.qdrant.host = http://localhost:6333
llm.qdrant.collection = zms_documentation
llm.ollama.host = http://localhost:11434
llm.api.model = llama2
```

For Docker Compose setup:
```python
llm.provider = rag
llm.qdrant.host = http://qdrant:6333
llm.ollama.host = http://ollama:11434
llm.qdrant.collection = zms_docs
llm.api.model = llama2
```

## Setting Up Ollama

### Installation

1. **Install Ollama**: Visit [https://ollama.ai](https://ollama.ai) and download for your platform
2. **Pull a model**:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   # or
   ollama pull codellama
   ```
3. **Start Ollama**: 
   ```bash
   ollama serve
   ```

### Docker Setup

Add to your `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - zms_network

volumes:
  ollama_data:
```

Then pull your desired model:
```bash
docker exec -it ollama ollama pull llama2
```

## Setting Up RAG with Qdrant

### Docker Compose Setup

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    networks:
      - zms_network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - zms_network

volumes:
  qdrant_storage:
  ollama_data:

networks:
  zms_network:
```

### Populate Qdrant

You'll need to populate your Qdrant collection with embeddings. Here's a Python example:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="zms_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Add documents (you'll need to generate embeddings)
# This is a simplified example
points = [
    PointStruct(
        id=1,
        vector=[...],  # Your embedding vector
        payload={"text": "Your document text here"}
    ),
]
client.upsert(collection_name="zms_docs", points=points)
```

## API Usage

### REST API Endpoint

The LLM chat is available via REST API:

```
GET /++rest_api/llm_chat?message=Your+question+here
```

Response format:
```json
{
  "message": {
    "role": "assistant",
    "content": "The AI's response"
  }
}
```

Error format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

### Provider Info Endpoint

Get information about the current provider:

```
GET /++rest_api/llm_provider_info
```

Response:
```json
{
  "provider": "ollama",
  "model": "llama2",
  "endpoint": "http://localhost:11434"
}
```

### Python API

You can also use the LLM API from Python code:

```python
from Products.zms import llmapi

# Send a message
response = llmapi.chat(context, "What is ZMS?")

if 'error' in response:
    print(f"Error: {response['error']['message']}")
else:
    print(f"Response: {response['message']['content']}")

# Get provider info
info = llmapi.get_provider_info(context)
print(f"Using {info['provider']} with model {info['model']}")
```

## Troubleshooting

### Connection Errors

**Problem**: "Cannot connect to Ollama" or "Cannot connect to Qdrant"

**Solutions**:
1. Check if the service is running: `curl http://localhost:11434/api/tags` (Ollama)
2. Check Docker containers: `docker ps`
3. Verify network connectivity between containers
4. Check firewall settings

### Model Not Found

**Problem**: "Model 'xyz' not found"

**Solution**: Pull the model first:
```bash
ollama pull llama2
# or in Docker
docker exec -it ollama ollama pull llama2
```

### OpenAI API Key Issues

**Problem**: "API key not configured" or "Invalid API key"

**Solutions**:
1. Set `llm.api.key` property with your OpenAI API key
2. Verify the key is correct at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Check for any whitespace in the key

### Slow Responses

**Problem**: Ollama responses are very slow

**Solutions**:
1. Use a smaller model (e.g., `llama2:7b` instead of `llama2:13b`)
2. Increase Docker memory allocation
3. Use GPU acceleration if available
4. Consider using OpenAI for faster responses

## Migration from OpenAI-only Setup

The old `openapi.py` module has been removed and replaced with `llmapi.py`. 

### Configuration Migration

If you were using the old OpenAI-only configuration, update your properties:

```python
# Old configuration (no longer supported)
openai.api.key = sk-...
openai.api.model = gpt-4o-mini

# New configuration (required)
llm.provider = openai  # This is the default
llm.api.key = sk-...
llm.api.model = gpt-4o-mini
```

### Code Migration

If you have Python code using the old module:

```python
# Old code (no longer works)
from Products.zms import openapi
response = openapi.chat_with_gpt(context, message)

# New code (required)
from Products.zms import llmapi
response = llmapi.chat(context, message)
```

### REST API Migration

Update your REST API calls:

```javascript
// Old endpoint (removed)
"++rest_api/openai_chat"

// New endpoint (use this)
"++rest_api/llm_chat"
```

## Best Practices

1. **Use OpenAI for production** if you need reliable, fast responses and can afford the API costs
2. **Use Ollama for development** or when you need privacy and control over your data
3. **Use RAG** when you need the LLM to answer questions based on your specific documentation
4. **Monitor costs** when using OpenAI - set up billing alerts
5. **Test locally first** with Ollama before switching to OpenAI
6. **Keep models updated** - regularly update Ollama models for improvements

## Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Limit network access to Ollama/Qdrant in production
- Regularly rotate OpenAI API keys
- Use HTTPS endpoints when possible
- Implement rate limiting for the chat endpoint
