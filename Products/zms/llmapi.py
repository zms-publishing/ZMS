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
All providers follow the OpenAI /v1/chat/completions API schema for consistency.

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
- llm.rag.score_threshold: Minimum similarity score (0.0-1.0, default: '0.0')
- llm.temperature: LLM temperature 0.0-2.0 (default: '0.7', RAG: 0.1 recommended)
- llm.top_p: Nucleus sampling 0.0-1.0 (default: '0.9')
- llm.max_tokens: Maximum tokens to generate (optional)
- llm.num_ctx: Context window size (default: '4096')
- llm.store: Enable storage for 'responses' API (default: False)

Response format (OpenAI /v1/chat/completions compatible):
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4o-mini",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "Response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}

For backwards compatibility, a convenience property 'message' is also provided
at the top level containing the first choice's message.

Requirements for RAG:
- pip install sentence-transformers
"""

# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo
import requests
import json
import time
import hashlib

# Global cache for embedding model (singleton)
_EMBEDDING_MODEL_CACHE = {}

security = ModuleSecurityInfo('Products.zms.llmapi')


def _generate_request_id(provider, model, message):
    """Generate a unique request ID for tracking"""
    timestamp = str(time.time())
    content = f"{provider}:{model}:{message}:{timestamp}"
    hash_digest = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    return f"chatcmpl-{hash_digest}"


def _normalize_response(response_data, provider, model, original_message):
    """
    Normalize provider-specific responses to OpenAI /v1/chat/completions format.
    
    This ensures all providers return a consistent schema compatible with the
    OpenAI API and the upcoming 'responses' schema.
    
    Args:
        response_data: Raw response from provider
        provider: Provider name ('openai', 'ollama', 'rag')
        model: Model name used
        original_message: Original user message
        
    Returns:
        dict: Normalized response in OpenAI format
    """
    # Handle error responses
    if 'error' in response_data:
        return response_data
    
    # If already in OpenAI format (from OpenAI provider), ensure backwards compatibility
    if 'choices' in response_data:
        # Add convenience 'message' property for backwards compatibility
        if response_data['choices'] and 'message' not in response_data:
            response_data['message'] = response_data['choices'][0].get('message', {})
        return response_data
    
    # Normalize Ollama/RAG format to OpenAI format
    if 'message' in response_data:
        normalized = {
            "id": _generate_request_id(provider, model, original_message),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": response_data['message'],
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,  # Not provided by Ollama
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        # Add backwards compatibility
        normalized['message'] = response_data['message']
        return normalized
    
    # Unexpected format
    return {
        'error': {
            'code': 'INVALID_RESPONSE',
            'message': 'Unexpected response format from provider'
        }
    }


class LLMProvider:
    """Abstract base class for LLM providers"""
    
    def __init__(self, context):
        self.context = context
    
    def chat(self, messages, **kwargs):
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages (list|str): List of message dicts [{"role": "user", "content": "..."}]
                                 or a string for simple single-turn conversations
            **kwargs: Additional provider-specific parameters
            
        Returns:
            dict: Response in OpenAI /v1/chat/completions format or error dict
        """
        raise NotImplementedError("Subclasses must implement chat()")
    
    def _prepare_messages(self, messages):
        """Convert string message to proper messages array"""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            return messages
        else:
            raise ValueError("messages must be a string or list of message dicts")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (v1/chat/completions compatible)"""
    
    def chat(self, messages, **kwargs):
        """Send messages to OpenAI's /v1/chat/completions API"""
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
            
            # Prepare messages array
            messages_array = self._prepare_messages(messages)
            
            # Build request payload according to OpenAI spec
            payload = {
                "model": model,
                "messages": messages_array,
            }
            
            # Add optional parameters from config or kwargs
            if 'temperature' in kwargs:
                payload['temperature'] = float(kwargs['temperature'])
            elif self.context.getConfProperty('llm.temperature'):
                payload['temperature'] = float(self.context.getConfProperty('llm.temperature', '0.7'))
            
            if 'top_p' in kwargs:
                payload['top_p'] = float(kwargs['top_p'])
            elif self.context.getConfProperty('llm.top_p'):
                payload['top_p'] = float(self.context.getConfProperty('llm.top_p', '0.9'))
            
            if 'max_tokens' in kwargs:
                payload['max_tokens'] = int(kwargs['max_tokens'])
            elif self.context.getConfProperty('llm.max_tokens'):
                payload['max_tokens'] = int(self.context.getConfProperty('llm.max_tokens'))
            
            # Enable storage for responses API if configured
            if 'store' in kwargs:
                payload['store'] = bool(kwargs['store'])
            elif self.context.getConfProperty('llm.store'):
                payload['store'] = self.context.getConfProperty('llm.store', '').lower() in ['true', '1', 'yes']
            
            # Add metadata for responses API
            if 'metadata' in kwargs:
                payload['metadata'] = kwargs['metadata']
            
            # Add any other kwargs (streaming, functions, tools, etc.)
            for key, value in kwargs.items():
                if key not in ['temperature', 'top_p', 'max_tokens', 'store', 'metadata']:
                    payload[key] = value
            
            response = requests.post(
                endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=payload,
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
            
            # Return full OpenAI response (includes id, object, created, choices, usage)
            # Add backwards compatibility convenience property
            if 'choices' in result and len(result['choices']) > 0:
                result['message'] = result['choices'][0].get('message', {})
            
            return result
            
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
    """Ollama local LLM provider (normalized to OpenAI format)"""
    
    def chat(self, messages, **kwargs):
        """Send messages to Ollama and normalize response to OpenAI format"""
        try:
            host = self.context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
            model = self.context.getConfProperty('llm.api.model', 'llama2')
            endpoint = f"{host}/api/chat"
            
            # Prepare messages array
            messages_array = self._prepare_messages(messages)
            
            # Build Ollama request
            payload = {
                "model": model,
                "messages": messages_array,
                "stream": False,
            }
            
            # Add Ollama-specific options
            options = {}
            if 'temperature' in kwargs:
                options['temperature'] = float(kwargs['temperature'])
            elif self.context.getConfProperty('llm.temperature'):
                options['temperature'] = float(self.context.getConfProperty('llm.temperature', '0.7'))
            
            if 'top_p' in kwargs:
                options['top_p'] = float(kwargs['top_p'])
            elif self.context.getConfProperty('llm.top_p'):
                options['top_p'] = float(self.context.getConfProperty('llm.top_p', '0.9'))
            
            if 'num_ctx' in kwargs:
                options['num_ctx'] = int(kwargs['num_ctx'])
            elif self.context.getConfProperty('llm.num_ctx'):
                options['num_ctx'] = int(self.context.getConfProperty('llm.num_ctx', '4096'))
            
            if options:
                payload['options'] = options
            
            # Add any other kwargs
            for key, value in kwargs.items():
                if key not in ['temperature', 'top_p', 'num_ctx']:
                    payload[key] = value
            
            response = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            result = response.json()
            
            # Normalize Ollama response to OpenAI format
            original_msg = messages_array[0]['content'] if messages_array else ''
            return _normalize_response(result, 'ollama', model, original_msg)
            
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
    
    def chat(self, messages, **kwargs):
        """Send messages using RAG with vector search and LLM (normalized to OpenAI format)"""
        try:
            qdrant_host = self.context.getConfProperty('llm.qdrant.host', 'http://localhost:6333')
            collection = self.context.getConfProperty('llm.qdrant.collection', 'zms_docs')
            ollama_host = self.context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
            model = self.context.getConfProperty('llm.api.model', 'llama2')
            top_k = int(self.context.getConfProperty('llm.rag.top_k', '16'))
            score_threshold = float(self.context.getConfProperty('llm.rag.score_threshold', '0.0'))
            
            # Prepare messages array
            messages_array = self._prepare_messages(messages)
            
            # Extract the last user message for RAG retrieval
            user_message = None
            for msg in reversed(messages_array):
                if msg.get('role') == 'user':
                    user_message = msg.get('content', '')
                    break
            
            if not user_message:
                return {
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'No user message found in messages array'
                    }
                }
            
            # Get LLM parameters with RAG-optimized defaults
            temperature = float(kwargs.get('temperature') or self.context.getConfProperty('llm.temperature', '0.1'))
            top_p = float(kwargs.get('top_p') or self.context.getConfProperty('llm.top_p', '0.9'))
            num_ctx = int(kwargs.get('num_ctx') or self.context.getConfProperty('llm.num_ctx', '4096'))
            
            # Step 1: Generate embeddings for the query
            try:
                embedding_model = self._get_embedding_model()
                query_vector = embedding_model.encode(user_message).tolist()
            except Exception as e:
                return {
                    'error': {
                        'code': 'EMBEDDING_ERROR',
                        'message': f'Failed to generate embeddings: {str(e)}'
                    }
                }
            
            # Step 2: Search Qdrant for relevant context using embeddings
            context_docs = []
            try:
                search_payload = {
                    "query": query_vector,
                    "limit": top_k,
                    "with_payload": True
                }
                
                # Add score threshold if configured
                if score_threshold > 0:
                    search_payload["score_threshold"] = score_threshold
                
                search_response = requests.post(
                    f"{qdrant_host}/collections/{collection}/points/query",
                    headers={"Content-Type": "application/json"},
                    json=search_payload,
                    timeout=10
                )
                
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
                import traceback
                traceback.print_exc()
            
            # Step 3: Build enhanced messages with context
            enhanced_messages = messages_array.copy()
            if context_docs:
                context_text = "\n\n---\n\n".join(context_docs)
                # Find the last user message and enhance it
                for i in range(len(enhanced_messages) - 1, -1, -1):
                    if enhanced_messages[i].get('role') == 'user':
                        enhanced_messages[i] = {
                            "role": "user",
                            "content": f"""Basierend auf den folgenden Informationen, beantworte die Frage präzise und sachlich.
Verwende nur Informationen aus dem bereitgestellten Kontext.

KONTEXT:
{context_text}

FRAGE: {user_message}

ANTWORT:"""
                        }
                        break
            
            # Step 4: Send to Ollama with context and optimized parameters
            ollama_params = {
                "model": model,
                "messages": enhanced_messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_ctx": num_ctx
                }
            }
            
            # Add any additional kwargs
            for key, value in kwargs.items():
                if key not in ['temperature', 'top_p', 'num_ctx']:
                    ollama_params[key] = value
            
            response = requests.post(
                f"{ollama_host}/api/chat",
                headers={"Content-Type": "application/json"},
                json=ollama_params,
                timeout=120
            )
            
            result = response.json()
            
            # Normalize RAG response to OpenAI format
            return _normalize_response(result, 'rag', model, user_message)
            
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
def chat(context, messages, **kwargs):
    """
    Send messages to the configured LLM provider and get a response.
    
    This is the main entry point for LLM interactions in ZMS.
    All responses follow the OpenAI /v1/chat/completions format.
    
    Args:
        context: ZMS context object
        messages (list|str): List of message dicts [{"role": "user", "content": "..."}]
                            or a string for backwards compatibility
        **kwargs: Additional provider-specific parameters:
            - temperature (float): Sampling temperature 0.0-2.0
            - top_p (float): Nucleus sampling 0.0-1.0
            - max_tokens (int): Maximum tokens to generate
            - store (bool): Enable storage for responses API
            - metadata (dict): Metadata for responses API
            
    Returns:
        dict: Response in OpenAI /v1/chat/completions format:
            Success: {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-4o-mini",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Response text"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                },
                "message": {...}  # Backwards compatibility: first choice's message
            }
            
            Error: {
                "error": {
                    "code": "ERROR_CODE",
                    "message": "error description"
                }
            }
    
    Configuration:
        Set llm.provider to one of: 'openai', 'ollama', 'rag'
        
        For OpenAI:
            - llm.api.key: Your OpenAI API key
            - llm.api.model: Model name (default: 'gpt-4o-mini')
            - llm.api.endpoint: Custom endpoint (default: https://api.openai.com/v1/chat/completions)
            - llm.store: Enable responses API storage (default: False)
            
        For Ollama:
            - llm.ollama.host: Ollama server URL (default: 'http://localhost:11434')
            - llm.api.model: Model name (default: 'llama2')
            
        For RAG:
            - llm.qdrant.host: Qdrant server URL (default: 'http://localhost:6333')
            - llm.qdrant.collection: Collection name (default: 'zms_docs')
            - llm.ollama.host: Ollama server URL (default: 'http://localhost:11434')
            - llm.api.model: Model name (default: 'llama2')
            - llm.rag.top_k: Number of documents to retrieve (default: '3')
    """
    provider = _get_provider(context)
    return provider.chat(messages, **kwargs)


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
        info['store_enabled'] = context.getConfProperty('llm.store', '').lower() in ['true', '1', 'yes']
    elif provider_type == 'ollama':
        info['endpoint'] = context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
    elif provider_type == 'rag':
        info['ollama_host'] = context.getConfProperty('llm.ollama.host', 'http://localhost:11434')
        info['qdrant_host'] = context.getConfProperty('llm.qdrant.host', 'http://localhost:6333')
        info['collection'] = context.getConfProperty('llm.qdrant.collection', 'zms_docs')
        info['top_k'] = context.getConfProperty('llm.rag.top_k', '3')
    
    return info


security.apply(globals())