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
