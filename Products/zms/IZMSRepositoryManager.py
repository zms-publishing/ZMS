"""
IZMSRepositoryManager.py

Defines IZMSRepositoryManager for ZMS plugin interfaces.
It establishes contracts for provider implementations, ensuring loose coupling and extensibility.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from zope.interface import Interface

class IZMSRepositoryManager(Interface):

  def exec_auto_commit(self, provider, id):
    """
    Execute auto-commit.
    @rtype: C{Bool}
    """

  def exec_auto_update(self):
    """
    Execute auto-update.
    @rtype: C{Bool}
    """
