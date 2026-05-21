# LLM API Configuration Guide

ZMS now supports multiple Large Language Model (LLM) providers through an abstract interface. This allows you to use different AI backends including OpenAI, local Ollama deployments, and RAG (Retrieval-Augmented Generation) with Qdrant vector database.

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
| `llm.temperature` | Sampling temperature 0.0-2.0 (higher = more creative) | `0.7` (RAG: `0.1` recommended) |
| `llm.top_p` | Nucleus sampling 0.0-1.0 | `0.9` |
| `llm.max_tokens` | Maximum tokens to generate (optional) | (not set) |
| `llm.num_ctx` | Context window size for Ollama/RAG | `4096` |

### OpenAI Configuration

For using OpenAI's cloud API:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.api.key` | Your OpenAI API key | (required) |
| `llm.api.endpoint` | Custom endpoint URL | `https://api.openai.com/v1/chat/completions` |
| `llm.api.model` | Model name | `gpt-4o-mini` |
| `llm.store` | Enable storage for OpenAI's responses API | `False` |

### Ollama Configuration

For using local Ollama deployment:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name (e.g., `llama2`, `mistral`, `codellama`) | `llama2` |
| `llm.num_ctx` | Context window size | `4096` |

### RAG Configuration

For using RAG with Qdrant vector database and Ollama:

| Property | Description | Default |
|----------|-------------|---------|
| `llm.qdrant.host` | Qdrant server URL | `http://localhost:6333` |
| `llm.qdrant.collection` | Collection name for vector search | `zms_docs` |
| `llm.ollama.host` | Ollama server URL | `http://localhost:11434` |
| `llm.api.model` | Model name | `llama2` |
| `llm.embedding.model` | SentenceTransformer model for embeddings | `all-MiniLM-L6-v2` |
| `llm.rag.top_k` | Number of documents to retrieve | `16` |
| `llm.rag.score_threshold` | Minimum similarity score (0.0-1.0) | `0.0` |
| `llm.temperature` | Temperature for RAG responses | `0.1` (recommended) |
| `llm.num_ctx` | Context window size | `4096` |

**Important**: RAG requires the `sentence-transformers` package:
```bash
pip install sentence-transformers
```

## Configuration Examples

### Example 1: OpenAI (Cloud)

```python
# In your ZMS configuration
llm.provider = openai
llm.api.key = sk-your-openai-api-key-here
llm.api.model = gpt-4o-mini
llm.temperature = 0.7
llm.top_p = 0.9
llm.store = True  # Enable responses API storage
```

### Example 2: Ollama (Local)

```python
# In your ZMS configuration
llm.provider = ollama
llm.ollama.host = http://localhost:11434
llm.api.model = llama2
llm.temperature = 0.7
llm.num_ctx = 4096
```

For Docker deployments, you might use:
```python
llm.provider = ollama
llm.ollama.host = http://ollama:11434  # Docker service name
llm.api.model = mistral
llm.temperature = 0.8
llm.num_ctx = 8192
```

### Example 3: RAG with Qdrant

```python
# In your ZMS configuration
llm.provider = rag
llm.qdrant.host = http://localhost:6333
llm.qdrant.collection = zms_documentation
llm.ollama.host = http://localhost:11434
llm.api.model = llama2
llm.embedding.model = all-MiniLM-L6-v2
llm.rag.top_k = 16
llm.rag.score_threshold = 0.0
llm.temperature = 0.1  # Lower temperature for factual answers
llm.num_ctx = 4096
```

For Docker Compose setup:
```python
llm.provider = rag
llm.qdrant.host = http://qdrant:6333
llm.ollama.host = http://ollama:11434
llm.qdrant.collection = zms_docs
llm.api.model = llama2
llm.embedding.model = all-MiniLM-L6-v2
llm.rag.top_k = 16
llm.rag.score_threshold = 0.3  # Filter low-quality matches
llm.temperature = 0.1
```

**Note**: Make sure to use the same embedding model (`llm.embedding.model`) that was used to ingest your data into Qdrant!

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
from sentence_transformers import SentenceTransformer

# Initialize embedding model (use the same as llm.embedding.model)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="zms_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Add documents with embeddings
documents = [
    "ZMS is a content management system...",
    "To configure LLM settings...",
    # ... your documents
]

points = []
for idx, doc in enumerate(documents):
    vector = model.encode(doc).tolist()
    points.append(
        PointStruct(
            id=idx,
            vector=vector,
            payload={"text": doc}
        )
    )

client.upsert(collection_name="zms_docs", points=points)
```

## API Usage

### REST API Endpoint

The LLM chat is available via REST API:

```
GET /++rest_api/llm_chat?message=Your+question+here
```

Response format (OpenAI /v1/chat/completions compatible):
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4o-mini",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The AI's response"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
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

You can use the LLM API from Python code:

```python
from Products.zms import llmapi

# Send a simple message (string)
response = llmapi.chat(context, "What is ZMS?")

# Send a conversation (list of messages)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is ZMS?"}
]
response = llmapi.chat(context, messages)

# With additional parameters
response = llmapi.chat(
    context, 
    "Explain ZMS configuration",
    temperature=0.5,
    max_tokens=500
)

# Check for errors
if 'error' in response:
    print(f"Error: {response['error']['message']}")
else:
    # Access the response content
    print(f"Response: {response['message']['content']}")
    # Or using the OpenAI format
    print(f"Response: {response['choices'][0]['message']['content']}")

# Get provider info
info = llmapi.get_provider_info(context)
print(f"Using {info['provider']} with model {info['model']}")
```

## Configuration Parameters Explained

### Temperature (`llm.temperature`)
Controls randomness in responses:
- **0.0**: Deterministic, always picks most likely tokens
- **0.7**: Balanced (default for general use)
- **0.1**: More focused and deterministic (recommended for RAG)
- **1.5-2.0**: Very creative, more random

### Top P (`llm.top_p`)
Nucleus sampling threshold (0.0-1.0):
- **0.9**: Default, good balance
- Lower values = more focused responses
- Higher values = more diverse responses

### Max Tokens (`llm.max_tokens`)
Maximum length of generated response. Useful to control costs or response length.

### Context Window (`llm.num_ctx`)
Size of context window for Ollama/RAG models:
- **4096**: Default, good for most use cases
- **8192** or higher: For longer conversations or documents

### Score Threshold (`llm.rag.score_threshold`)
Minimum similarity score for RAG document retrieval:
- **0.0**: Include all retrieved documents (default)
- **0.3-0.5**: Filter out low-quality matches
- **0.7+**: Only very relevant documents

### Top K (`llm.rag.top_k`)
Number of documents to retrieve for RAG context:
- **3**: Quick, focused answers
- **16**: Default, good balance (updated from 3)
- **30+**: Comprehensive context (may exceed token limits)

### Store (`llm.store`)
When set to `True`, enables OpenAI's responses API storage for model training and fine-tuning.

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
5. Reduce `llm.num_ctx` if using very large context windows

### RAG Not Finding Relevant Documents

**Problem**: RAG returns generic answers or "I don't know"

**Solutions**:
1. Check that documents are properly ingested in Qdrant
2. Verify `llm.embedding.model` matches the model used for ingestion
3. Lower `llm.rag.score_threshold` to include more documents
4. Increase `llm.rag.top_k` to retrieve more context
5. Check Qdrant collection: `curl http://localhost:6333/collections/zms_docs`

## Best Practices

1. **Use OpenAI for production** if you need reliable, fast responses and can afford the API costs
2. **Use Ollama for development** or when you need privacy and control over your data
3. **Use RAG** when you need the LLM to answer questions based on your specific documentation
4. **Monitor costs** when using OpenAI - set up billing alerts
5. **Test locally first** with Ollama before switching to OpenAI
6. **Keep models updated** - regularly update Ollama models for improvements
7. **Use lower temperature (0.1-0.3) for RAG** to ensure factual, grounded responses
8. **Match embedding models** - always use the same `llm.embedding.model` for ingestion and retrieval
9. **Tune score threshold** - adjust `llm.rag.score_threshold` based on your data quality
10. **Enable OpenAI storage** (`llm.store = True`) only if you want to contribute to model training

## Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Limit network access to Ollama/Qdrant in production
- Regularly rotate OpenAI API keys
- Use HTTPS endpoints when possible
- Implement rate limiting for the chat endpoint
- Be aware that `llm.store = True` sends your data to OpenAI for training
