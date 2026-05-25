"""
ZMSLLMConnector.py - ZMS LLM Connector for AI/LLM Integration

Provides ZMSLLMConnector as a Zope object that bridges ZMS content management
with large language model providers (OpenAI, Ollama, RAG with Qdrant).

The connector stores its own configuration as ZODB-persisted properties and is
retrieved from any ZMS context via getLLMConnector(). It can contain ZMSCustom
child objects for richer 3rd-view UI extensions.

Multiple providers are supported through llmapi.py:
  - OpenAI (gpt-4o-mini, gpt-4, gpt-3.5-turbo, ...)
  - Ollama (local LLM deployment)
  - RAG with Qdrant + Ollama (retrieval-augmented generation)

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from zope.interface import implementer
import json
# Product Imports.
from Products.zms import standard
from Products.zms import IZMSLLMConnector
from Products.zms import IZMSRepositoryProvider
from Products.zms import IZMSConfigurationProvider
from Products.zms import ZMSItem


@implementer(
    IZMSLLMConnector.IZMSLLMConnector,
    IZMSRepositoryProvider.IZMSRepositoryProvider,
    IZMSConfigurationProvider.IZMSConfigurationProvider,
)
class ZMSLLMConnector(ZMSItem.ZMSItem):
    """ZMS LLM Connector – bridges ZMS to AI/LLM provider backends."""

    # Properties.
    meta_type = 'ZMSLLMConnector'
    zmi_icon = 'fas fa-robot'

    # Management Interface.
    manage = PageTemplateFile('zpt/ZMSLLMConnector/manage_llm_connector', globals())
    manage_main = PageTemplateFile('zpt/ZMSLLMConnector/manage_llm_connector', globals())

    manage_options_default_action = '../manage_customize'

    def manage_options(self):
        """Return management options delegating to the parent ZMS object."""
        import copy
        return [self.operator_setitem(x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
        """Contribute the LLM tab to the ZMS main tab bar."""
        return (
            {'label': 'TAB_LLM', 'action': 'manage_main'},
        )

    # Management Permissions.
    __administratorPermissions__ = (
        'manage_changeProperties', 'manage_changeConfig', 'manage_changeFeatures', 'manage_main',
    )
    __ac_permissions__ = (
        ('ZMS Administrator', __administratorPermissions__),
    )

    security = ClassSecurityInfo()

    def __init__(self, id='llm_connector'):
        """Constructor."""
        self.id = id
        self._config = {}

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.getConfProperty
    # -------------------------------------------------------------------------
    def getConfProperty(self, key, default=None):
        """
        Return a configuration property for this connector.

        Reads from connector's own ``_config`` dict first; falls back to the
        ZMS root confmanager for site-wide defaults.

        @param key: Property key (e.g. 'llm.provider', 'llm.api.key').
        @param default: Value returned when key is absent.
        @return: Property value or default.
        """
        if key in self._config:
            val = self._config[key]
            # treat empty string as unset so default is returned
            if val != '':
                return val
        # Fallback: check ZMS root confmanager (for migration / site-wide overrides).
        try:
            root_val = self.aq_parent.getConfProperty(key)
            if root_val is not None and root_val != '':
                return root_val
        except Exception:
            pass
        return default

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.chat
    # -------------------------------------------------------------------------
    def chat(self, messages, **kwargs):
        """
        Send messages to the configured LLM provider.

        Delegates to ``llmapi`` provider factory using this connector as the
        configuration context so ``getConfProperty()`` resolves correctly.

        @param messages: List of ``{"role": ..., "content": ...}`` dicts or a plain string.
        @param kwargs: Optional overrides: temperature, top_p, max_tokens, etc.
        @return: Response in OpenAI /v1/chat/completions format or error dict.
        @rtype: dict
        """
        from Products.zms import llmapi
        provider = llmapi._get_provider(self)
        return provider.chat(messages, **kwargs)

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.chat_with_tools
    # -------------------------------------------------------------------------
    def chat_with_tools(self, messages, context, max_rounds=5):
        """
        Agentic chat loop with ZMS tool calling.

        Sends ``messages`` plus active tool definitions from
        ``llmtools.ZMSLLMToolsAdapter`` to the LLM. If the LLM responds with
        ``tool_calls``, each call is executed through the adapter (custom
        ``*_llmtools`` profile or built-in fallback), appended as ``tool``
        role messages, and the conversation continues until the LLM produces a
        plain text response or ``max_rounds`` is reached.

        @param messages: List of ``{"role": ..., "content": ...}`` dicts or a
          plain string (auto-wrapped as user message).
        @param context: ZMS acquisition context exposing ``metaobj_manager``.
        @param max_rounds: Maximum tool-calling iterations to prevent infinite loops.
        @return: Dict with keys:
          - ``reply`` (str): Final assistant text response.
          - ``turns`` (list): All conversation turns including tool calls/results,
            each as ``{"role", "content", "tool_calls"?}`` for UI rendering.
          - ``error`` (str): Set only on unrecoverable errors.
        @rtype: dict
        """
        from Products.zms import llmtools
        adapter = llmtools.ZMSLLMToolsAdapter(self, context)

        def _extract_latest_user_text(msgs):
            for m in reversed(msgs):
                if isinstance(m, dict) and m.get('role') == 'user':
                    return str(m.get('content') or '')
            return ''

        def _is_index_qdrant_intent(text):
            t = (text or '').lower()
            if not t:
                return False
            # Deterministic fallback for explicit site indexing requests.
            has_index_verb = ('index' in t) or ('reindex' in t) or ('re-index' in t)
            has_scope = (
                ('all content' in t) or
                ('site content' in t) or
                ('entire site' in t) or
                ('whole site' in t) or
                ('zms site' in t) or
                ('rag index' in t) or
                ('qdrant' in t)
            )
            return has_index_verb and has_scope

        # Normalise messages
        if isinstance(messages, str):
            msgs = [{'role': 'user', 'content': messages}]
        else:
            msgs = list(messages)

        turns = []  # records for UI / localStorage

        try:
            tool_schemas = adapter.get_llmtools()
        except Exception as exc:
            return {
                'error': "LLM tools profile misconfigured: %s" % str(exc),
                'turns': turns,
                'reply': '',
            }

        # Some models occasionally answer in plain text instead of issuing a tool call.
        # For explicit indexing requests, execute the indexer deterministically.
        latest_user_text = _extract_latest_user_text(msgs)
        if _is_index_qdrant_intent(latest_user_text):
            result = adapter.execute_llmtool('index_qdrant', {})
            result_str = json.dumps(result)
            turns.append({
                'role': 'assistant',
                'content': '',
                'tool_calls': [{
                    'id': 'forced-index-qdrant',
                    'type': 'function',
                    'function': {
                        'name': 'index_qdrant',
                        'arguments': '{}',
                    },
                }],
            })
            turns.append({
                'role': 'tool',
                'tool_call_id': 'forced-index-qdrant',
                'name': 'index_qdrant',
                'content': result_str,
            })
            if isinstance(result, dict) and result.get('error'):
                return {
                    'reply': f"Indexing failed: {result.get('error')}",
                    'turns': turns,
                }
            return {
                'reply': (
                    "Started and completed indexing into Qdrant. "
                    f"Pages indexed: {result.get('pages_indexed', 0)}, "
                    f"skipped: {result.get('pages_skipped', 0)}, "
                    f"total chunks: {result.get('total_chunks', 0)}, "
                    f"collection: {result.get('collection', '')}."
                ),
                'turns': turns,
            }

        def _extract_json_objects(text):
            """
            Extract all top-level JSON objects from text using balanced-brace
            scanning. Handles nested objects correctly, unlike simple regexes.
            """
            results = []
            i = 0
            while i < len(text):
                if text[i] == '{':
                    depth = 0
                    in_str = False
                    escape = False
                    start = i
                    for j in range(i, len(text)):
                        c = text[j]
                        if escape:
                            escape = False
                        elif c == '\\' and in_str:
                            escape = True
                        elif c == '"':
                            in_str = not in_str
                        elif not in_str:
                            if c == '{':
                                depth += 1
                            elif c == '}':
                                depth -= 1
                                if depth == 0:
                                    results.append(text[start:j + 1])
                                    i = j
                                    break
                i += 1
            return results

        def _parse_text_tool_calls(content, known_tools):
            """
            Fallback parser for models (e.g. qwen2.5-coder) that write tool calls
            as plain text / markdown JSON instead of issuing structured tool_calls.

            Uses balanced-brace extraction so nested argument objects like
            {"name": "get_content_type", "arguments": {"id": "..."}} are captured
            correctly, avoiding partial matches from non-greedy regexes.
            """
            if not content:
                return []
            known_names = {t.get('function', {}).get('name') for t in known_tools}
            candidates = _extract_json_objects(content)
            parsed = []
            for i, raw in enumerate(candidates):
                try:
                    obj = json.loads(raw)
                except (ValueError, TypeError):
                    continue
                name = obj.get('name') or obj.get('function', {}).get('name')
                if name not in known_names:
                    continue
                args = obj.get('arguments') or obj.get('parameters') or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except (ValueError, TypeError):
                        args = {}
                parsed.append({
                    'id': f'text_call_{i}_{name}',
                    'type': 'function',
                    'function': {
                        'name': name,
                        'arguments': json.dumps(args),
                    },
                })
            return parsed

        for _round in range(max_rounds):
            response = self.chat(msgs, tools=tool_schemas, tool_choice='auto')

            if 'error' in response:
                err = response['error']
                err_msg = err.get('message', str(err)) if isinstance(err, dict) else str(err)
                # If tools already ran in a prior round, the model can't process
                # the tool-result messages (e.g. qwen2.5-coder doesn't support
                # multi-turn tool calling). Return collected tool results as reply.
                if _round > 0 and turns:
                    tool_results = [
                        t for t in turns if t.get('role') == 'tool'
                    ]
                    if tool_results:
                        parts = []
                        for t in tool_results:
                            try:
                                data = json.loads(t.get('content', '{}'))
                                parts.append('**%s**\n```json\n%s\n```' % (
                                    t.get('name', 'tool'),
                                    json.dumps(data, indent=2, ensure_ascii=False),
                                ))
                            except (ValueError, TypeError):
                                parts.append('**%s**\n%s' % (
                                    t.get('name', 'tool'), t.get('content', ''),
                                ))
                        reply = '\n\n'.join(parts)
                        turns.append({'role': 'assistant', 'content': reply})
                        return {'reply': reply, 'turns': turns}
                return {'error': err_msg, 'turns': turns, 'reply': ''}

            message = response.get('message') or {}
            raw_content = message.get('content', '')
            tool_calls = message.get('tool_calls') or []

            # Track whether tool calls came from the text fallback parser so we
            # can degrade gracefully on execution errors without confusing the LLM.
            text_fallback_used = False
            if not tool_calls:
                tool_calls = _parse_text_tool_calls(raw_content, tool_schemas)
                text_fallback_used = bool(tool_calls)

            if not tool_calls:
                # Final plain-text response
                turns.append({'role': 'assistant', 'content': raw_content})
                return {'reply': raw_content, 'turns': turns}

            # Record assistant message with tool calls for UI
            turns.append({
                'role': 'assistant',
                'content': raw_content,
                'tool_calls': tool_calls,
            })
            msgs.append({
                'role': 'assistant',
                'content': raw_content,
                'tool_calls': tool_calls,
            })

            # Execute each tool and append results
            for tc in tool_calls:
                call_id = tc.get('id', '')
                fn = tc.get('function', {})
                tool_name = fn.get('name', '')
                try:
                    raw_args = fn.get('arguments', '{}')
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except (ValueError, TypeError):
                    args = {}

                result = adapter.execute_llmtool(tool_name, args)

                # When tool calls were parsed from plain text and the tool
                # returns an error, the model sent malformed / unencodable args.
                # Return its original text response as a formatted code block
                # instead of feeding the error back into the loop.
                if text_fallback_used and isinstance(result, dict) and result.get('error'):
                    formatted = '```json\n%s\n```' % raw_content if raw_content else str(result['error'])
                    turns.append({'role': 'assistant', 'content': formatted})
                    return {'reply': formatted, 'turns': turns}

                result_str = json.dumps(result)

                tool_turn = {
                    'role': 'tool',
                    'tool_call_id': call_id,
                    'name': tool_name,
                    'content': result_str,
                }
                turns.append(tool_turn)
                msgs.append(tool_turn)

            # Models that use plain-text tool calls (text_fallback_used) cannot
            # process tool-result messages in a second round — Ollama's template
            # parser throws an error on `tool` role messages. Return tool results
            # directly as formatted JSON without attempting another LLM call.
            if text_fallback_used:
                tool_results = [t for t in turns if t.get('role') == 'tool']
                parts = []
                for t in tool_results:
                    try:
                        data = json.loads(t.get('content', '{}'))
                        parts.append('**%s**\n```json\n%s\n```' % (
                            t.get('name', 'tool'),
                            json.dumps(data, indent=2, ensure_ascii=False),
                        ))
                    except (ValueError, TypeError):
                        parts.append('**%s**\n%s' % (t.get('name', 'tool'), t.get('content', '')))
                reply = '\n\n'.join(parts)
                turns.append({'role': 'assistant', 'content': reply})
                return {'reply': reply, 'turns': turns}

        # Exhausted max rounds without a final text reply
        return {
            'reply': 'The assistant used too many tool calls without a final answer.',
            'turns': turns,
        }


    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.get_provider_info
    # -------------------------------------------------------------------------
    def get_provider_info(self):
        """
        Return information about the currently configured LLM provider.

        @return: Dict with provider type, model name, endpoint, etc.
        @rtype: dict
        """
        from Products.zms import llmapi
        return llmapi.get_provider_info(self)

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.get_ollama_models
    # -------------------------------------------------------------------------
    def get_ollama_models(self):
        """
        Fetch the list of locally available models from the configured Ollama server.

        @return: Dict with 'models' list (name strings) or 'error'.
        @rtype: dict
        """
        from Products.zms import llmapi
        return llmapi.get_ollama_models(self)

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.getAvailableLLMToolsProfiles
    # -------------------------------------------------------------------------
    def getAvailableLLMToolsProfiles(self):
        """
        Return available ``*_llmtools`` profile meta-objects.

        Profiles are discovered from installed ZMSLibrary meta-objects and can be
        selected via ``llm.llmtools.id`` in connector config.
        """
        from Products.zms import llmtools
        return llmtools.get_available_llmtools_profiles(self)

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.getEnabledFeatures
    # -------------------------------------------------------------------------
    def getEnabledFeatures(self):
        """
        Return a dict of enabled AI feature flags.

        Keys: rte_assist, translate_assist, metadata_gen, rag_chat.
        Values: bool.

        @return: Feature flag dict.
        @rtype: dict
        """
        raw = self._config.get('llm.features', '{}')
        try:
            return json.loads(raw)
        except Exception:
            return {}

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.isFeatureEnabled
    # -------------------------------------------------------------------------
    def isFeatureEnabled(self, feature_key):
        """
        Check whether a specific AI feature is enabled.

        @param feature_key: One of 'rte_assist', 'translate_assist', 'metadata_gen', 'rag_chat'.
        @return: True if the feature is enabled.
        @rtype: bool
        """
        return bool(self.getEnabledFeatures().get(feature_key, False))

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.provideRepository
    # -------------------------------------------------------------------------
    def provideRepository(self, r, ids=None):
        """Export connector configuration for repository."""
        standard.writeBlock(self, "[provideRepository]: ids=%s" % str(ids))
        r = {}
        id = self.id
        d = {'id': id, 'revision': '0.0.0', '__filename__': ['__init__.py']}
        r[id] = d
        r[id]['LLMConnector'] = [{
            'id': 'config',
            'ob': {
                'filename': 'config.json',
                'data': json.dumps(self._config, indent=2),
                'version': '0.0.0',
                'meta_type': 'File',
            }
        }]
        return r

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.updateRepository
    # -------------------------------------------------------------------------
    def updateRepository(self, r):
        """Import connector configuration from repository."""
        id = r['id']
        self.id = id
        if 'LLMConnector' in r:
            for item in r['LLMConnector']:
                if item.get('id') == 'config':
                    try:
                        data = item.get('ob', {}).get('data', '{}')
                        self._config = json.loads(data)
                    except Exception:
                        pass
        return id

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.manage_changeConfig
    # -------------------------------------------------------------------------
    def manage_changeConfig(self, btn, lang, REQUEST, RESPONSE=None):
        """Save connector configuration fields from the Config tab form."""
        message = ''
        try:
            config_keys = [
                'llm.provider',
                'llm.api.key',
                'llm.api.model',
                'llm.api.endpoint',
                'llm.llmtools.id',
                'llm.ollama.host',
                'llm.qdrant.host',
                'llm.qdrant.collection',
                'llm.embedding.model',
                'llm.temperature',
                'llm.top_p',
                'llm.max_tokens',
                'llm.num_ctx',
                'llm.rag.top_k',
                'llm.rag.score_threshold',
                'llm.store',
                'llm.timeout',
                'llm.rag.timeout',
            ]
            config = dict(self._config)  # preserve existing values (e.g. llm.features)
            for key in config_keys:
                val = REQUEST.get(key, '').strip()
                # Never overwrite an existing API key with an empty submission
                if key == 'llm.api.key' and not val:
                    continue
                config[key] = val
            self._config = config
            self._p_changed = True
            message = self.getZMILangStr('MSG_CHANGED')
        except Exception:
            message = standard.writeError(self, "can't manage_changeConfig")
        if RESPONSE is not None:
            target = '%s/manage_main?lang=%s&manage_tabs_message=%s#panel-config' % (
                self.absolute_url(), lang, standard.url_encode(message))
            return RESPONSE.redirect(target)
        return message

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.manage_changeFeatures
    # -------------------------------------------------------------------------
    def manage_changeFeatures(self, btn, lang, REQUEST, RESPONSE=None):
        """Save feature-flag checkboxes from the Features tab form."""
        message = ''
        try:
            features = {}
            for fkey in ['rte_assist', 'translate_assist', 'metadata_gen', 'rag_chat']:
                features[fkey] = REQUEST.get('feature_%s' % fkey, '') in ('1', 'on', 'true', 'True')
            config = dict(self._config)  # preserve all other config values
            config['llm.features'] = json.dumps(features)
            self._config = config
            self._p_changed = True
            message = self.getZMILangStr('MSG_CHANGED')
        except Exception:
            message = standard.writeError(self, "can't manage_changeFeatures")
        if RESPONSE is not None:
            target = '%s/manage_main?lang=%s&manage_tabs_message=%s#panel-features' % (
                self.absolute_url(), lang, standard.url_encode(message))
            return RESPONSE.redirect(target)
        return message

    # -------------------------------------------------------------------------
    #  ZMSLLMConnector.manage_changeProperties (kept for backwards compat)
    # -------------------------------------------------------------------------
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE=None):
        """Backwards-compatible shim: delegates to manage_changeConfig."""
        return self.manage_changeConfig(btn, lang, REQUEST, RESPONSE)


# --------------------------------------------------------------------------
#  Constructor support for registerClass
# --------------------------------------------------------------------------

manage_addZMSLLMConnectorForm = PageTemplateFile(
    'zpt/ZMSLLMConnector/manage_add_llm_connector', globals())


def manage_addZMSLLMConnector(self, REQUEST, RESPONSE=None):
    """Add a ZMSLLMConnector object."""
    id = REQUEST.get('id', 'llm_connector').strip() or 'llm_connector'
    connector = ZMSLLMConnector(id)
    self._setObject(id, connector)
    if RESPONSE is not None:
        return RESPONSE.redirect('%s/manage_main' % self.absolute_url())
