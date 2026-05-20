"""
IZMSConfigurationProvider.py

Defines IZMSConfigurationProvider for ZMS plugin interfaces.
It establishes contracts for provider implementations, ensuring loose coupling and extensibility.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSConfigurationProvider(Interface):

  def manage_sub_options(self):
    """
    Returns sub-options 
    @rtype: C{string}
    """

  def getArtefacts(self):
    """
    Returns list of artefacts.
    @rtype: C{list}
    """
  
  def setArtefacts(self, artefacts):
    """
    Applies list of artefacts.
    @param artefacts: the artefacts
    @type artefacts: C{list}
    """
