#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# openapi.py
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

"""ZMS OpenAPI utility module

This module provides helpful functions and classes for use in Python
Scripts.  It can be accessed from Python with the statement
"import Products.zms.openapi"
"""

# Imports.
from AccessControl.SecurityInfo import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.zms.openapi')

security.declarePublic('chat_with_gpt')
def chat_with_gpt(context, message):
    """
    Sends a message to the OpenAI GPT API and retrieves the AI-generated response.
    Args:
        message (str): The input message to send to the GPT model.
    Returns:
        str: The AI-generated reply from the GPT model.
    Notes:
        - The OpenAI API key is retrieved from the attribute 'openai.api.key'.
        - The GPT model to use is specified by the attribute 'openai.api.model', 
          defaulting to 'gpt-4o-mini' if not provided.
        - The API endpoint for chat completions is retrieved from the attribute 
          'openai.chat.completions', defaulting to 'https://api.openai.com/v1/chat/completions'.
        - Ensure that the API key and other required attributes are properly configured 
          before calling this method.
    """
    import requests
    OPENAI_API_KEY = context.getConfProperty('openai.api.key')
    OPENAI_API_MODEL = context.getConfProperty('openai.api.model', 'gpt-4o-mini')
    OPENAI_API_CHAT_COMPLETIONS = context.getConfProperty('openai.chat.completions', 'https://api.openai.com/v1/chat/completions')
    
    response = requests.post(OPENAI_API_CHAT_COMPLETIONS,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": OPENAI_API_MODEL,
            "messages": [{"role": "user", "content": message}],
        },
     )

    result = response.json()
    if result['error']:
        reply = {'error': {'code': result['error']['code'], 'message': result['error']['message']}}
    else:
        reply = result["choices"][0]
    return reply

security.apply(globals())