"""
IZMSLLMConnector.py

Defines IZMSLLMConnector for ZMS LLM integration.
Establishes contracts for the AI/LLM connector object, ensuring loose coupling
between ZMS core and LLM provider implementations.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface


class IZMSLLMConnector(Interface):

    def chat(self, messages, **kwargs):
        """
        Send messages to the configured LLM provider and get a response.

        @param messages: List of message dicts [{"role": "user", "content": "..."}]
                         or a plain string for simple single-turn conversations.
        @type messages: list or str
        @param kwargs: Additional provider-specific parameters (temperature, top_p, etc.)
        @return: Response dict in OpenAI /v1/chat/completions format, or error dict.
        @rtype: dict
        """

    def get_provider_info(self):
        """
        Get information about the currently configured LLM provider.

        @return: Dict with keys: provider, model, endpoint, has_api_key, etc.
        @rtype: dict
        """

    def getConfProperty(self, key, default=None):
        """
        Return a connector configuration property.

        @param key: Property key (e.g. 'llm.provider', 'llm.api.key')
        @type key: str
        @param default: Default value if key is not set.
        @return: Property value or default.
        """
