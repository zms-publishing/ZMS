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

ram_cache_enabled = False
ram_cache_key = 'ram_cache'

def get_ram_cache(self, request, buff):
    cache = None
    if ram_cache_enabled:
        cache = getattr(buff, ram_cache_key, None)
        if cache is None:
            ram_cache = self.restrictedTraverse(ram_cache_key)
            cache = ram_cache.ZCacheManager_getCache()
            setattr(buff, ram_cache_key, cache)
            set_buff(request, buff)
    return cache

def get_request(self):
    return getattr(self, 'REQUEST', getRequest())

buff_key = '__buff__'

def get_buff(request):
    buff = getattr(request, buff_key, None)
    if buff is None:
        buff = Buff()
        setattr(request, buff_key, buff)
    return buff

def set_buff(request, buff):
    setattr(request, buff_key, buff)

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
      return '%s_%s'%('_'.join(self.getPhysicalPath()), key)


    def clearReqBuff(self, prefix='', REQUEST=None):
      """
      Remove buffered entries from the current request, optionally filtered by prefix.

      @param prefix: Optional prefix to filter buffer keys.
      @type prefix: C{str}
      @param REQUEST: Optional request object.
      @type REQUEST: C{object}
      """
      reqBuffId = self.getReqBuffId(prefix)
      request = get_request(self)
      buff = get_buff(request)
      if len(prefix) > 0:
        reqBuffId += '.'
      for key in list(buff.__dict__):
        if key.startswith(reqBuffId):
          delattr(buff, key)
      set_buff(request, buff)
      # RAM cache is optional, so we ignore errors if it's not available.
      try:
        cache = get_ram_cache(self, request, buff)
        if cache:
          #print("RAMCacheManager.clear", reqBuffId)
          value = cache.ZCache_set(self, reqBuffId, None)
      except Exception as e:
        #print("RAMCacheManager not available:", e)
        pass

    def fetchReqBuff(self, key=None, REQUEST=None):
      """
      Fetch one buffered value from the current request (raises if missing).

      @param key: Buffer key (namespaced by physical path).
      @type key: C{str}
      @return: The buffered value.
      @rtype: C{object}
      """
      reqBuffId = self.getReqBuffId(key)
      request = get_request(self)
      buff = get_buff(request)
      value = getattr(buff, reqBuffId)
      if value is None:
        # RAM cache is optional, so we ignore errors if it's not available.
        try:
          cache = get_ram_cache(self, request, buff)
          if cache:
              value = cache.ZCache_get(self, reqBuffId)
              #print("RAMCacheManager.get", reqBuffId, value is not None)
        except Exception as e:
          #print("RAMCacheManager not available:", e)
          pass
      return value


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
      reqBuffId = self.getReqBuffId(key)
      request = get_request(self)
      buff = get_buff(request)
      setattr(buff, reqBuffId, value)
      set_buff(request, buff)
      # RAM cache is optional, so we ignore errors if it's not available.
      try:
        cache = get_ram_cache(self, request, buff)
        if cache:
          value = cache.ZCache_set(self, reqBuffId, value)
      except Exception as e:
        #print("RAMCacheManager not available:", e)
        pass
      return value
