#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for LLM API functionality

This script tests the different LLM providers without requiring a full ZMS instance.
"""

class MockContext:
    """Mock ZMS context for testing"""
    def __init__(self, config=None):
        self.config = config or {}
    
    def getConfProperty(self, key, default=None):
        return self.config.get(key, default)


def test_provider_selection():
    """Test that the correct provider is selected based on configuration"""
    print("Testing provider selection...")
    
    # Import after sys.path is set
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from Products.zms.llmapi import _get_provider, OpenAIProvider, OllamaProvider, RAGProvider
    
    # Test OpenAI provider
    ctx = MockContext({'llm.provider': 'openai'})
    provider = _get_provider(ctx)
    assert isinstance(provider, OpenAIProvider), "Should create OpenAI provider"
    print("✓ OpenAI provider selected correctly")
    
    # Test Ollama provider
    ctx = MockContext({'llm.provider': 'ollama'})
    provider = _get_provider(ctx)
    assert isinstance(provider, OllamaProvider), "Should create Ollama provider"
    print("✓ Ollama provider selected correctly")
    
    # Test RAG provider
    ctx = MockContext({'llm.provider': 'rag'})
    provider = _get_provider(ctx)
    assert isinstance(provider, RAGProvider), "Should create RAG provider"
    print("✓ RAG provider selected correctly")
    
    # Test default (should be OpenAI)
    ctx = MockContext({})
    provider = _get_provider(ctx)
    assert isinstance(provider, OpenAIProvider), "Should default to OpenAI provider"
    print("✓ Default provider (OpenAI) selected correctly")
    
    print("\nAll provider selection tests passed!")


def test_provider_info():
    """Test the get_provider_info function"""
    print("\nTesting provider info...")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from Products.zms.llmapi import get_provider_info
    
    # Test OpenAI info
    ctx = MockContext({
        'llm.provider': 'openai',
        'llm.api.key': 'sk-test123',
        'llm.api.model': 'gpt-4'
    })
    info = get_provider_info(ctx)
    assert info['provider'] == 'openai'
    assert info['model'] == 'gpt-4'
    assert info['has_api_key'] == True
    print("✓ OpenAI provider info correct")
    
    # Test Ollama info
    ctx = MockContext({
        'llm.provider': 'ollama',
        'llm.ollama.host': 'http://ollama:11434',
        'llm.api.model': 'llama2'
    })
    info = get_provider_info(ctx)
    assert info['provider'] == 'ollama'
    assert info['model'] == 'llama2'
    assert info['endpoint'] == 'http://ollama:11434'
    print("✓ Ollama provider info correct")
    
    # Test RAG info
    ctx = MockContext({
        'llm.provider': 'rag',
        'llm.qdrant.host': 'http://qdrant:6333',
        'llm.qdrant.collection': 'docs',
        'llm.api.model': 'mistral'
    })
    info = get_provider_info(ctx)
    assert info['provider'] == 'rag'
    assert info['qdrant_host'] == 'http://qdrant:6333'
    assert info['collection'] == 'docs'
    print("✓ RAG provider info correct")
    
    print("\nAll provider info tests passed!")


def test_configuration_error():
    """Test that missing API key returns proper error"""
    print("\nTesting configuration error handling...")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from Products.zms.llmapi import OpenAIProvider
    
    # Test with missing API key
    ctx = MockContext({
        'llm.provider': 'openai'
    })
    
    provider = OpenAIProvider(ctx)
    result = provider.chat("test message")
    assert 'error' in result, "Should return error when API key is missing"
    assert result['error']['code'] == 'CONFIGURATION_ERROR'
    print("✓ Configuration error handling works correctly")
    
    print("\nConfiguration error tests passed!")


if __name__ == '__main__':
    try:
        test_provider_selection()
        test_provider_info()
        test_configuration_error()
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
