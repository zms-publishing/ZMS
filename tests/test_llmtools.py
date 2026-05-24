#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for llmtools profile abstraction.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Products.zms import llmtools


class MockRoot:
    def __init__(self, metaobjs=None, attrs=None):
        self._metaobjs = metaobjs or {}
        self._attrs = attrs or {}

    def getRootElement(self):
        return self

    def getMetaobjIds(self):
        return list(self._metaobjs.keys())

    def getMetaobj(self, mid):
        return self._metaobjs[mid]

    def getMetaobjAttrs(self, mid):
        if mid not in self._attrs:
            raise KeyError(mid)
        return [{'id': k} for k in self._attrs[mid].keys()]

    def getMetaobjAttr(self, mid, aid):
        return self._attrs[mid][aid]


class MockContext:
    def __init__(self, root):
        self._root = root

    def getRootElement(self):
        return self._root


class MockConnector:
    def __init__(self, config=None):
        self._config = config or {}

    def getConfProperty(self, key, default=None):
        return self._config.get(key, default)


def test_get_available_llmtools_profiles_filters_by_suffix_and_type():
    root = MockRoot(metaobjs={
        'core_llmtools': {'id': 'core_llmtools', 'type': 'ZMSLibrary', 'package': 'com.zms.llm'},
        'ignored_connector': {'id': 'ignored_connector', 'type': 'ZMSLibrary', 'package': 'com.zms.catalog'},
        'bad_llmtools': {'id': 'bad_llmtools', 'type': 'ZMSDocument', 'package': 'com.zms.llm'},
    })
    context = MockContext(root)
    profiles = llmtools.get_available_llmtools_profiles(context)
    assert [p['id'] for p in profiles] == ['core_llmtools']


def test_adapter_returns_builtin_tools_when_no_profile_is_set():
    root = MockRoot()
    context = MockContext(root)
    connector = MockConnector({'llm.llmtools.id': ''})
    adapter = llmtools.ZMSLLMToolsAdapter(connector, context)
    tools = adapter.get_llmtools()
    assert isinstance(tools, list)
    assert tools[0]['type'] == 'function'


def test_adapter_loads_custom_profile_manifest():
    expected_tools = [{
        'type': 'function',
        'function': {
            'name': 'ping',
            'description': 'Ping tool',
            'parameters': {'type': 'object', 'properties': {}, 'required': []},
        },
    }]
    attrs = {
        'custom_llmtools': {
            'get_llmtools': {
                'id': 'get_llmtools',
                'type': 'Script (Python)',
                'ob': lambda connector, context: expected_tools,
            }
        }
    }
    root = MockRoot(
        metaobjs={'custom_llmtools': {'id': 'custom_llmtools', 'type': 'ZMSLibrary'}},
        attrs=attrs
    )
    context = MockContext(root)
    connector = MockConnector({'llm.llmtools.id': 'custom_llmtools'})
    adapter = llmtools.ZMSLLMToolsAdapter(connector, context)
    tools = adapter.get_llmtools()
    assert tools == expected_tools


def test_adapter_executes_custom_llmtool_action():
    attrs = {
        'custom_llmtools': {
            'get_llmtools': {
                'id': 'get_llmtools',
                'type': 'py',
                'ob': lambda connector, context: [{
                    'type': 'function',
                    'function': {
                        'name': 'ping',
                        'description': 'Ping tool',
                        'parameters': {'type': 'object', 'properties': {}, 'required': []},
                    },
                }],
            },
            'llmtool_ping': {
                'id': 'llmtool_ping',
                'type': 'py',
                'ob': lambda connector, context, args: {'pong': args.get('value', '')},
            }
        }
    }
    root = MockRoot(
        metaobjs={'custom_llmtools': {'id': 'custom_llmtools', 'type': 'ZMSLibrary'}},
        attrs=attrs
    )
    context = MockContext(root)
    connector = MockConnector({'llm.llmtools.id': 'custom_llmtools'})
    adapter = llmtools.ZMSLLMToolsAdapter(connector, context)
    result = adapter.execute_llmtool('ping', {'value': 'ok'})
    assert result == {'pong': 'ok'}
