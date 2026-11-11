"""
_cachemanager.py - Request-local caching helpers used across ZMS managers.

This module provides a tiny request buffer abstraction to avoid recomputing
expensive values multiple times during a single HTTP request.

Key concepts:
  - C{Buff}: A minimal attribute container stored on C{REQUEST['__buff__']}.
  - C{ReqBuff}: Mixin-style helper with methods to create, read, and clear
    namespaced cache entries.

Namespacing strategy:
  - Buffer keys are prefixed with the object's physical path
    (see C{ReqBuff.getReqBuffId}) to avoid collisions between different
    objects using the same logical key.

Typical usage pattern:
  1. Try C{fetchReqBuff('some.key')}.
  2. On cache miss, compute the value.
  3. Persist it with C{storeReqBuff('some.key', value)}.
  4. Invalidate with C{clearReqBuff('some')} when related state changes.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
from Products.zms import standard
from zope.globalrequest import getRequest

class Buff(object):
  """Lightweight attribute container used for request-local buffering."""
  pass

class ReqBuff(object):
    """Request-scoped buffer helpers for expensive values computed during one request."""


    def getReqBuffId(self, key):
      """
      Return a stable request-buffer key namespaced by the object's physical path.
      
      @param key: Buffer key (namespaced by physical path).
      @type key: C{str}
      @return: Namespaced buffer key.
      @rtype: C{str}
      """
      return '%s_%s'%('_'.join(self.getPhysicalPath()[2:]), key)


    def clearReqBuff(self, prefix='', REQUEST=None):
      """
      Remove buffered entries from the current request, optionally filtered by prefix.

      @param prefix: Optional prefix to filter buffer keys.
      @type prefix: C{str}
      @param REQUEST: Optional request object.
      @type REQUEST: C{object}
      """
      request = getattr(self, 'REQUEST', getRequest())
      buff = request.get('__buff__', Buff())
      reqBuffId = self.getReqBuffId(prefix)
      if len(prefix) > 0:
        reqBuffId += '.'
      for key in list(buff.__dict__):
        if key.startswith(reqBuffId):
          delattr(buff, key)
 

    def fetchReqBuff(self, key=None, REQUEST=None):
      """
      Fetch one buffered value from the current request (raises if missing).

      @param key: Buffer key (namespaced by physical path).
      @type key: C{str}
      @return: The buffered value.
      @rtype: C{object}
      """
      request = getattr(self, 'REQUEST', getRequest())
      if key is None: # For debugging purposes, return whole buffer.
        return None   # request.get('__buff__',{})
      buff = request['__buff__']
      reqBuffId = self.getReqBuffId(key)
      return getattr(buff, reqBuffId)


    def storeReqBuff(self, key, value, REQUEST=None):
      """
      Store and return a value in the current request buffer.
      The value is stored under a key namespaced by the object's 
      physical path to avoid conflicts with other objects.

      @param key: Buffer key (namespaced by physical path).
      @type key: C{str}
      @param value: Value to store in the buffer.
      @type value: C{object}
      @return: The value that was stored.
      @rtype: C{object}
      """
      request = getattr(self, 'REQUEST', getRequest())
      buff = request.get('__buff__', None)
      if buff is None:
        buff = Buff()
      reqBuffId = self.getReqBuffId(key)
      setattr(buff, reqBuffId, value)
      request.set('__buff__', buff)
      return value
