#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for LLM API functionality and ZMSLLMConnector.

Tests llmapi provider logic and ZMSLLMConnector without requiring a full Zope instance.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockContext:
    """Minimal mock for llmapi provider tests (getConfProperty only)."""
    def __init__(self, config=None):
        self.config = config or {}

    def getConfProperty(self, key, default=None):
        return self.config.get(key, default)


# ---------------------------------------------------------------------------
# ZMSLLMConnector unit tests (no Zope runtime needed)
# ---------------------------------------------------------------------------

def _make_connector(config=None):
    """Return a ZMSLLMConnector instance with ZODB persistence disabled."""
    from Products.zms.ZMSLLMConnector import ZMSLLMConnector
    conn = ZMSLLMConnector.__new__(ZMSLLMConnector)
    conn.id = 'llm_connector'
    conn._config = config or {}
    # Stub aq_parent to avoid Acquisition traversal
    conn.aq_parent = MockContext()
    return conn


def test_connector_getConfProperty():
    """ZMSLLMConnector.getConfProperty reads from _config."""
    print("Testing ZMSLLMConnector.getConfProperty…")
    conn = _make_connector({'llm.provider': 'ollama', 'llm.api.model': 'llama2'})
    assert conn.getConfProperty('llm.provider') == 'ollama'
    assert conn.getConfProperty('llm.api.model') == 'llama2'
    assert conn.getConfProperty('llm.api.key', 'DEFAULT') == 'DEFAULT'
    print("✓ getConfProperty reads from _config correctly")


def test_connector_getConfProperty_fallback():
    """ZMSLLMConnector.getConfProperty falls back to aq_parent."""
    print("Testing ZMSLLMConnector.getConfProperty fallback…")
    conn = _make_connector({})
    conn.aq_parent = MockContext({'llm.provider': 'openai'})
    assert conn.getConfProperty('llm.provider') == 'openai'
    print("✓ getConfProperty falls back to parent correctly")


def test_connector_getEnabledFeatures():
    """ZMSLLMConnector.getEnabledFeatures parses JSON."""
    import json
    print("Testing ZMSLLMConnector.getEnabledFeatures…")
    features = {'rte_assist': True, 'translate_assist': False}
    conn = _make_connector({'llm.features': json.dumps(features)})
    result = conn.getEnabledFeatures()
    assert result['rte_assist'] is True
    assert result['translate_assist'] is False
    print("✓ getEnabledFeatures parses feature flags correctly")


def test_connector_isFeatureEnabled():
    """ZMSLLMConnector.isFeatureEnabled returns correct bool."""
    import json
    print("Testing ZMSLLMConnector.isFeatureEnabled…")
    conn = _make_connector({'llm.features': json.dumps({'rag_chat': True})})
    assert conn.isFeatureEnabled('rag_chat') is True
    assert conn.isFeatureEnabled('rte_assist') is False
    print("✓ isFeatureEnabled returns correct bool")


def test_connector_delegates_to_provider():
    """ZMSLLMConnector.chat delegates to llmapi provider using connector as context."""
    print("Testing ZMSLLMConnector.chat delegation (missing key → error)…")
    conn = _make_connector({'llm.provider': 'openai'})
    result = conn.chat("hello")
    assert 'error' in result
    assert result['error']['code'] == 'CONFIGURATION_ERROR'
    print("✓ ZMSLLMConnector.chat delegates to provider and returns error without API key")


# ---------------------------------------------------------------------------
# llmapi unit tests (unchanged from original)
# ---------------------------------------------------------------------------

def test_provider_selection():
    """Test that the correct provider is selected based on configuration."""
    print("\nTesting provider selection…")
    from Products.zms.llmapi import _get_provider, OpenAIProvider, OllamaProvider, RAGProvider

    ctx = MockContext({'llm.provider': 'openai'})
    assert isinstance(_get_provider(ctx), OpenAIProvider)
    print("✓ OpenAI provider selected correctly")

    ctx = MockContext({'llm.provider': 'ollama'})
    assert isinstance(_get_provider(ctx), OllamaProvider)
    print("✓ Ollama provider selected correctly")

    ctx = MockContext({'llm.provider': 'rag'})
    assert isinstance(_get_provider(ctx), RAGProvider)
    print("✓ RAG provider selected correctly")

    ctx = MockContext({})
    assert isinstance(_get_provider(ctx), OpenAIProvider)
    print("✓ Default provider (OpenAI) selected correctly")

    print("All provider selection tests passed!")


def test_provider_info():
    """Test the get_provider_info function."""
    print("\nTesting provider info…")
    from Products.zms.llmapi import get_provider_info

    ctx = MockContext({'llm.provider': 'openai', 'llm.api.key': 'sk-test', 'llm.api.model': 'gpt-4'})
    info = get_provider_info(ctx)
    assert info['provider'] == 'openai'
    assert info['model'] == 'gpt-4'
    assert info['has_api_key'] is True
    print("✓ OpenAI provider info correct")

    ctx = MockContext({'llm.provider': 'ollama', 'llm.ollama.host': 'http://ollama:11434', 'llm.api.model': 'llama2'})
    info = get_provider_info(ctx)
    assert info['provider'] == 'ollama'
    assert info['endpoint'] == 'http://ollama:11434'
    print("✓ Ollama provider info correct")

    ctx = MockContext({'llm.provider': 'rag', 'llm.qdrant.host': 'http://qdrant:6333', 'llm.qdrant.collection': 'docs', 'llm.api.model': 'mistral'})
    info = get_provider_info(ctx)
    assert info['provider'] == 'rag'
    assert info['qdrant_host'] == 'http://qdrant:6333'
    assert info['collection'] == 'docs'
    print("✓ RAG provider info correct")

    print("All provider info tests passed!")


def test_configuration_error():
    """Test that missing API key returns proper error."""
    print("\nTesting configuration error handling…")
    from Products.zms.llmapi import OpenAIProvider

    ctx = MockContext({'llm.provider': 'openai'})
    provider = OpenAIProvider(ctx)
    result = provider.chat("test message")
    assert 'error' in result
    assert result['error']['code'] == 'CONFIGURATION_ERROR'
    print("✓ Configuration error handling works correctly")
    print("Configuration error tests passed!")


if __name__ == '__main__':
    try:
        # ZMSLLMConnector tests
        test_connector_getConfProperty()
        test_connector_getConfProperty_fallback()
        test_connector_getEnabledFeatures()
        test_connector_isFeatureEnabled()
        test_connector_delegates_to_provider()
        # llmapi tests
        test_provider_selection()
        test_provider_info()
        test_configuration_error()
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
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
