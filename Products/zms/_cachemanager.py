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

# Kill switch for shared cache usage. Set to False to disable shared caching.
shared_cache_enabled = True

# ID of the shared cache. 
# Valid Neta-Types are 'RAM Cache Manager' and 'MemCache Cache Manager'.
shared_cache_id = 'shared_cache'

# Keys that are shared across requests and should be stored in the shared cache.
# This list can be extended with additional keys as needed.
shared_keys = ['ZMSMetaobjManager.__get_metaobjs__']

# Class that wraps an object to provide the ZCacheable interface for shared caching.
class SharedCacheable:
    def __init__(self, ob):
        self._ob = ob

    def ZCacheable_getModTime(self, *args, **kwargs):
        return 0

    def ZCacheable_getIdentifier(self):
        return "/".join(self._ob.getPhysicalPath())

    def ZCacheable_isCachingEnabled(self):
        return True

    def getPhysicalPath(self):
        return self._ob.getPhysicalPath()

# Helper function to retrieve the shared cache manager if available.
def get_cache(self):
    cache = None
    if shared_cache_enabled and hasattr(self, shared_cache_id):
        shared_cache = getattr(self, shared_cache_id)
        cache = shared_cache.ZCacheManager_getCache()
    return cache


# Request-local buffer management.
buff_key = '__buff__'

# Lightweight attribute container used for request-local buffering.
class Buff(object):
  """Lightweight attribute container used for request-local buffering."""
  pass

# Helper functions to get and set the request-local buffer.
def get_buff(request):
    buff = getattr(request, buff_key, None)
    if buff is None:
        buff = Buff()
        set_buff(request, buff)
    return buff

# Helper function to set the request-local buffer.
def set_buff(request, buff):
    setattr(request, buff_key, buff)


# Helper function to retrieve the current request object, either from the instance or globally.
def get_request(self):
    request = getattr(self, 'REQUEST', None)
    if request: 
        return request
    return getRequest()

# Request-scoped buffer helpers for expensive values computed during one request.
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
      path = self.getPhysicalPath()
      return f"{hash(path)}_{key}"


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


    def fetchSharedCache(self, key):
      # RAM cache is optional, so we ignore errors if it's not available.
      try:
        if key in shared_keys:
          cache = get_cache(self)
          if cache:
            cacheable = SharedCacheable(self)
            # Note: keywords/view_name can be used for namespacing if needed.
            return cache.ZCache_get(cacheable, view_name='shared', keywords={'key': key})
      except Exception as e:
        print("SharedCache not available:", key, e)
        pass
      return None


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
      if not hasattr(buff, reqBuffId):
        # RAM cache is optional, so we ignore errors if it's not available.
        value = self.fetchSharedCache(key)
        if value:
            # Store the value in the request buffer for future access.
            setattr(buff, reqBuffId, value)
            set_buff(request, buff)
            return value
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
      reqBuffId = self.getReqBuffId(key)
      request = get_request(self)
      buff = get_buff(request)
      setattr(buff, reqBuffId, value)
      set_buff(request, buff)
      # RAM cache is optional, so we ignore errors if it's not available.
      try:
        if key in shared_keys:
          cache = get_cache(self)
          if cache:
            cacheable = SharedCacheable(self)
            cache.ZCache_set(cacheable, value, view_name='shared', keywords={'key': key})
      except Exception as e:
        print("SharedCache not available:", key, e)
        pass
      return value
