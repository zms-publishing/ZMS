#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for LLM API functionality and ZMSLLMConnector.

Tests llmapi provider logic and ZMSLLMConnector without requiring a full Zope instance.
"""
import sys
import os
from unittest.mock import Mock, patch
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
    from Products.zms.llmapi import (
        _get_provider, AnthropicProvider, OpenAIProvider, OllamaProvider, RAGProvider,
    )

    ctx = MockContext({'llm.provider': 'openai'})
    assert isinstance(_get_provider(ctx), OpenAIProvider)
    print("✓ OpenAI provider selected correctly")

    ctx = MockContext({'llm.provider': 'ollama'})
    assert isinstance(_get_provider(ctx), OllamaProvider)
    print("✓ Ollama provider selected correctly")

    ctx = MockContext({'llm.provider': 'anthropic'})
    assert isinstance(_get_provider(ctx), AnthropicProvider)
    print("✓ Anthropic provider selected correctly")

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

    ctx = MockContext({
        'llm.provider': 'anthropic',
        'llm.api.key': 'anthropic-test-key',
        'llm.api.model': 'claude-sonnet-4-5',
    })
    info = get_provider_info(ctx)
    assert info['provider'] == 'anthropic'
    assert info['model'] == 'claude-sonnet-4-5'
    assert info['endpoint'] == 'https://api.anthropic.com/v1/messages'
    assert info['has_api_key'] is True
    print("✓ Anthropic provider info correct")

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


def test_anthropic_provider_request_and_response():
    """Anthropic requests and tool-use responses use the common chat schema."""
    from Products.zms.llmapi import AnthropicProvider

    ctx = MockContext({
        'llm.api.key': 'anthropic-test-key',
        'llm.api.model': 'claude-sonnet-4-5',
        'llm.temperature': '0.7',
        'llm.top_p': '0.9',
    })
    response = Mock()
    response.json.return_value = {
        'id': 'msg_test',
        'model': 'claude-sonnet-4-5',
        'content': [
            {'type': 'text', 'text': 'Reading the page.'},
            {'type': 'tool_use', 'id': 'toolu_123', 'name': 'get_page', 'input': {'id': 'home'}},
        ],
        'stop_reason': 'tool_use',
        'usage': {'input_tokens': 12, 'output_tokens': 5},
    }

    with patch('Products.zms.llmapi.requests.post', return_value=response) as post:
        result = AnthropicProvider(ctx).chat(
            [{'role': 'system', 'content': 'Be helpful.'}, {'role': 'user', 'content': 'Read home'}],
            tools=[{
                'type': 'function',
                'function': {
                    'name': 'get_page',
                    'description': 'Read a page',
                    'parameters': {'type': 'object', 'properties': {'id': {'type': 'string'}}},
                },
            }],
            tool_choice='auto',
        )

    args, request = post.call_args
    assert args[0] == 'https://api.anthropic.com/v1/messages'
    assert request['headers']['x-api-key'] == 'anthropic-test-key'
    assert request['headers']['anthropic-version'] == '2023-06-01'
    assert request['json']['system'] == 'Be helpful.'
    assert request['json']['max_tokens'] == 4096
    assert request['json']['temperature'] == 0.7
    assert 'top_p' not in request['json']
    assert request['json']['tools'][0]['input_schema']['type'] == 'object'
    assert request['json']['tool_choice'] == {'type': 'auto'}
    assert result['message']['content'] == 'Reading the page.'
    assert result['message']['tool_calls'][0]['id'] == 'toolu_123'
    assert result['message']['tool_calls'][0]['function']['arguments'] == '{"id": "home"}'
    assert result['choices'][0]['finish_reason'] == 'tool_calls'
    assert result['usage'] == {
        'prompt_tokens': 12,
        'completion_tokens': 5,
        'total_tokens': 17,
    }
    print("✓ Anthropic request and tool response normalization work correctly")


def test_anthropic_tool_result_history():
    """Anthropic tool call history is reconstructed for subsequent agent turns."""
    from Products.zms.llmapi import AnthropicProvider

    provider = AnthropicProvider(MockContext())
    system, messages = provider._prepare_anthropic_messages([
        {'role': 'assistant', 'content': '', 'tool_calls': [{
            'id': 'toolu_123',
            'type': 'function',
            'function': {'name': 'get_page', 'arguments': '{"id": "home"}'},
        }]},
        {'role': 'tool', 'tool_call_id': 'toolu_123', 'name': 'get_page', 'content': '{"title":"Home"}'},
        {'role': 'assistant', 'content': 'The page is titled Home.'},
    ])
    assert system == ''
    assert messages == [
        {'role': 'assistant', 'content': [{
            'type': 'tool_use',
            'id': 'toolu_123',
            'name': 'get_page',
            'input': {'id': 'home'},
        }]},
        {'role': 'user', 'content': [{
            'type': 'tool_result',
            'tool_use_id': 'toolu_123',
            'content': '{"title":"Home"}',
        }]},
        {'role': 'assistant', 'content': [{
            'type': 'text',
            'text': 'The page is titled Home.',
        }]},
    ]
    print("✓ Anthropic tool-result history is translated correctly")


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
        test_anthropic_provider_request_and_response()
        test_anthropic_tool_result_history()
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
