#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# llmapi.py
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
################################################################################

"""ZMS LLM API utility module

This module provides an abstract interface for Large Language Model providers.
Supported providers:
- OpenAI (gpt-4, gpt-3.5-turbo, etc.)
- Ollama (local deployment)
- RAG with Qdrant vector database

Configuration properties:
- llm.provider: 'openai', 'ollama', or 'rag' (default: 'openai')
- llm.api.key: API key for OpenAI (if provider is 'openai')
- llm.api.model: Model name (default: 'gpt-4o-mini' for OpenAI, 'llama2' for Ollama)
- llm.api.endpoint: Custom endpoint URL
- llm.ollama.host: Ollama host (default: 'http://localhost:11434')
- llm.qdrant.host: Qdrant host (default: 'http://localhost:6333')
- llm.qdrant.collection: Qdrant collection name (default: 'zms_docs')
- llm.embedding.model: SentenceTransformer model (default: 'all-MiniLM-L6-v2')
- llm.rag.top_k: Number of documents to retrieve (default: '3')

Requirements for RAG:
- pip install sentence-transformers
"""

# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
import requests
import json

# Global cache for embedding model (singleton)
_EMBEDDING_MODEL_CACHE = {}

security = ModuleSecurityInfo('Products.zms.llmapi')


class LLMProvider:
    """Abstract base class for LLM providers"""
    
    def __init__(self, context):
        self.context = context
    
    def chat(self, message, **kwargs):
        """
        Send a message to the LLM and get a response.
        
        Args:
            message (str): The user's message
            **kwargs: Additional provider-specific parameters
            
        Returns:
            dict: Response in the format {'message': {'content': str}} or {'error': {'code': str, 'message': str}}
        """
        raise NotImplementedError("Subclasses must implement chat()")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def chat(self, message, **kwargs):
        """Send a message to OpenAI's API"""
        try:
            api_key = self.context.getConfProperty('llm.api.key')
            if not api_key:
                return {
                    'error': {
                        'code': 'CONFIGURATION_ERROR',
                        'message': 'OpenAI API key not configured. Set llm.api.key'
                    }
                }
            
            model = self.context.getConfProperty('llm.api.model', 'gpt-4o-mini')
            endpoint = self.context.getConfProperty('llm.api.endpoint', 'https://api.openai.com/v1/chat/completions')
            
            response = requests.post(
                endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}],
                    **kwargs
                },
                timeout=30
            )
            
            result = response.json()
            
            # Handle OpenAI error responses
            if 'error' in result:
                return {
                    'error': {
                        'code': result['error'].get('code', 'UNKNOWN'),
                        'message': result['error'].get('message', 'Unknown error')
                    }
                }
            
            # Extract the assistant's message
            if 'choices' in result and len(result['choices']) > 0:
                return result["choices"][0]
            
            return {
                'error': {
                    'code': 'INVALID_RESPONSE',
                    'message': 'Unexpected response format from OpenAI'
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': {
                    'code': 'REQUEST_ERROR',
                    'message': f'Request to OpenAI failed: {str(e)}'
                }
            }
        except Exception as e:
            return {
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': f'Internal error: {str(e)}'
                }
            }


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def chat(self, message, **kwargs):
        """Send a message to Ollama"""
        try:
            host = self.context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
            model = self.context.getConfProperty('llm.api.model', 'llama2')
            endpoint = f"{host}/api/chat"
            
            response = requests.post(
                endpoint,
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}],
                    "stream": False,
                    **kwargs
                },
                timeout=60  # Ollama can be slower for local processing
            )
            
            result = response.json()
            
            # Ollama response format: {"message": {"role": "assistant", "content": "..."}}
            if 'message' in result:
                return result
            
            return {
                'error': {
                    'code': 'INVALID_RESPONSE',
                    'message': 'Unexpected response format from Ollama'
                }
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'error': {
                    'code': 'CONNECTION_ERROR',
                    'message': f'Cannot connect to Ollama at {host}. Is Ollama running?'
                }
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': {
                    'code': 'REQUEST_ERROR',
                    'message': f'Request to Ollama failed: {str(e)}'
                }
            }
        except Exception as e:
            return {
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': f'Internal error: {str(e)}'
                }
            }


class RAGProvider(LLMProvider):
    """RAG (Retrieval-Augmented Generation) provider using Qdrant and Ollama"""
    
    def _get_embedding_model(self):
        """Get cached embedding model (singleton pattern to avoid repeated HuggingFace API calls)"""
        model_name = self.context.getConfProperty('llm.embedding.model', 'all-MiniLM-L6-v2')
        
        # Use global cache to avoid reloading model for each request
        if model_name not in _EMBEDDING_MODEL_CACHE:
            try:
                from sentence_transformers import SentenceTransformer
                _EMBEDDING_MODEL_CACHE[model_name] = SentenceTransformer(model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for RAG. "
                    "Install with: pip install sentence-transformers"
                )
        return _EMBEDDING_MODEL_CACHE[model_name]
    
    def chat(self, message, **kwargs):
        """Send a message using RAG with vector search and LLM"""
        try:
            qdrant_host = self.context.getConfProperty('llm.qdrant.host', 'http://localhost:6333')
            collection = self.context.getConfProperty('llm.qdrant.collection', 'zms_docs')
            ollama_host = self.context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
            model = self.context.getConfProperty('llm.api.model', 'llama2')
            top_k = int(self.context.getConfProperty('llm.rag.top_k', '3'))
            
            # Step 1: Generate embeddings for the query
            try:
                embedding_model = self._get_embedding_model()
                query_vector = embedding_model.encode(message).tolist()
            except Exception as e:
                return {
                    'error': {
                        'code': 'EMBEDDING_ERROR',
                        'message': f'Failed to generate embeddings: {str(e)}'
                    }
                }
            
            # Step 2: Search Qdrant for relevant context using embeddings
            try:
                search_response = requests.post(
                    f"{qdrant_host}/collections/{collection}/points/query",
                    headers={"Content-Type": "application/json"},
                    json={
                        "query": query_vector,
                        "limit": top_k,
                        "with_payload": True
                    },
                    timeout=10
                )
                
                context_docs = []
                if search_response.status_code == 200:
                    results = search_response.json()
                    if 'result' in results and 'points' in results['result']:
                        for doc in results['result']['points']:
                            payload = doc.get('payload', {})
                            # Extract text from payload (adapt to your data structure)
                            text = payload.get('text') or payload.get('body') or payload.get('content', '')
                            if text:
                                context_docs.append(text)
                    elif 'result' in results:
                        # Fallback for different Qdrant response formats
                        for doc in results['result']:
                            payload = doc.get('payload', {})
                            text = payload.get('text') or payload.get('body') or payload.get('content', '')
                            if text:
                                context_docs.append(text)
            except Exception as e:
                # If Qdrant search fails, continue without context
                context_docs = []
                # Optionally log the error for debugging
                import traceback
                traceback.print_exc()
            
            # Step 3: Build prompt with context
            if context_docs:
                context_text = "\n\n---\n\n".join(context_docs)
                enhanced_message = f"""Basierend auf den folgenden Informationen, beantworte die Frage:

{context_text}

Frage: {message}

Antwort:"""
            else:
                enhanced_message = message
            
            # Step 4: Send to Ollama with context
            response = requests.post(
                f"{ollama_host}/api/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": enhanced_message}],
                    "stream": False,
                    **kwargs
                },
                timeout=120
            )
            
            result = response.json()
            
            if 'message' in result:
                return result
            
            return {
                'error': {
                    'code': 'INVALID_RESPONSE',
                    'message': 'Unexpected response format from RAG provider'
                }
            }
            
        except requests.exceptions.ConnectionError as e:
            return {
                'error': {
                    'code': 'CONNECTION_ERROR',
                    'message': f'Cannot connect to services. Check Qdrant and Ollama: {str(e)}'
                }
            }
        except Exception as e:
            return {
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': f'Internal error in RAG: {str(e)}'
                }
            }


def _get_provider(context):
    """
    Factory function to get the appropriate LLM provider based on configuration.
    
    Args:
        context: ZMS context object
        
    Returns:
        LLMProvider: An instance of the configured provider
    """
    provider_type = context.getConfProperty('llm.provider', 'openai').lower()
    
    providers = {
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
        'rag': RAGProvider,
    }
    
    provider_class = providers.get(provider_type, OpenAIProvider)
    return provider_class(context)


security.declarePublic('chat')
def chat(context, message, **kwargs):
    """
    Send a message to the configured LLM provider and get a response.
    
    This is the main entry point for LLM interactions in ZMS.
    
    Args:
        context: ZMS context object
        message (str): The user's message/prompt
        **kwargs: Additional provider-specific parameters
        
    Returns:
        dict: Response in the format:
            Success: {'message': {'role': 'assistant', 'content': 'response text'}}
            Error: {'error': {'code': 'ERROR_CODE', 'message': 'error description'}}
    
    Configuration:
        Set llm.provider to one of: 'openai', 'ollama', 'rag'
        
        For OpenAI:
            - llm.api.key: Your OpenAI API key
            - llm.api.model: Model name (default: 'gpt-4o-mini')
            
        For Ollama:
            - llm.ollama.host: Ollama server URL (default: 'http://localhost:11434')
            - llm.api.model: Model name (default: 'llama2')
            
        For RAG:
            - llm.qdrant.host: Qdrant server URL (default: 'http://localhost:6333')
            - llm.qdrant.collection: Collection name (default: 'zms_docs')
            - llm.ollama.host: Ollama server URL (default: 'http://localhost:11434')
            - llm.api.model: Model name (default: 'llama2')
    """
    provider = _get_provider(context)
    return provider.chat(message, **kwargs)


security.declarePublic('get_provider_info')
def get_provider_info(context):
    """
    Get information about the currently configured LLM provider.
    
    Args:
        context: ZMS context object
        
    Returns:
        dict: Provider information including type, model, and endpoint
    """
    provider_type = context.getConfProperty('llm.provider', 'openai').lower()
    
    info = {
        'provider': provider_type,
        'model': context.getConfProperty('llm.api.model', 'not configured'),
    }
    
    if provider_type == 'openai':
        info['endpoint'] = context.getConfProperty('llm.api.endpoint', 'https://api.openai.com/v1/chat/completions')
        info['has_api_key'] = bool(context.getConfProperty('llm.api.key'))
    elif provider_type == 'ollama':
        info['endpoint'] = context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
    elif provider_type == 'rag':
        info['ollama_host'] = context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
        info['qdrant_host'] = context.getConfProperty('llm.qdrant.host', 'http://localhost:6333')
        info['collection'] = context.getConfProperty('llm.qdrant.collection', 'zms_docs')
    
    return info


security.apply(globals())
