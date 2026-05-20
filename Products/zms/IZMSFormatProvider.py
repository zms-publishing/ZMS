"""
IZMSFormatProvider.py

Defines IZMSFormatProvider for ZMS plugin interfaces.
It establishes contracts for provider implementations, ensuring loose coupling and extensibility.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSFormatProvider(Interface):

  def getTextFormatDefault(self):
    """
    Returns id of default text-format 
    @rtype: C{string}
    """
  
  def getTextFormat(self, id, REQUEST):
    """
    Returns text-format specified by given id 
    @param REQUEST: the triggering request
    @type REQUEST: ZPublisher.HTTPRequest
    """

  def getTextFormats(self, REQUEST):
    """
    Returns list of all text-formats 
    @param REQUEST: the triggering request
    @type REQUEST: ZPublisher.HTTPRequest
    @rtype: C{list}
    """

  def getCharFormats(self):
    """
    Returns list of all character-formats 
    @rtype: C{list}
    """
