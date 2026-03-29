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
from AccessControl import ClassSecurityInfo
from Products.zms import standard
from zope.globalrequest import getRequest

class Buff(object):
  """Lightweight attribute container used for request-local buffering."""
  pass

class SharedBuff(object):
    """
    Shared buffer helpers using a multi-user cache (RAM or Memcache).
    This allows data persistence across different requests and users.
    """

    security = ClassSecurityInfo()

    security.declarePublic('get_cache_manager')
    def get_cache_manager(self, cache_id='zms_cache'):
        """
        Fetch the configured Zope Cache Manager.
        Expects a configuration property 'ZMS.cache.path' pointing to the 
        manager (e.g., '/zms/my_ram_cache').
        """
        cache_path = self.getConfProperty('ZMS.cache.path', None)
        if cache_path:
            try:
                manager = self.unrestrictedTraverse(cache_path)
                return manager.ZCacheManager_getCache()
            except:
                pass
        return None

    security.declarePublic('fetchSharedBuff')
    def fetchSharedBuff(self, key):
        """Fetch a value from the shared global cache."""
        doc_element = self.getPortalMaster() or self.getDocumentElement()
        cache = doc_element.get_cache_manager()
        if cache:
            # Note: keywords/view_name can be used for namespacing if needed.
            return cache.ZCache_get(doc_element, view_name='shared', keywords={'key': key})
        return None

    security.declarePublic('storeSharedBuff')
    def storeSharedBuff(self, key, value):
        """Store a value in the shared global cache."""
        doc_element = self.getPortalMaster() or self.getDocumentElement()
        cache = doc_element.get_cache_manager()
        if cache:
            # We use the DocumentElement (ZMS site root) as the context 
            # to ensure the cache is shared globally across the entire site.
            cache.ZCache_set(doc_element, value, view_name='shared', keywords={'key': key})
        return value

    security.declarePublic('getSharedBuffJSON')
    def getSharedBuffJSON(self):
        """
        Return the contents of the shared cache as a JSON-formatted string.
        Leverages the internal tracking mechanism of mcdutils using the 
        DocumentElement as the global context.
        """
        import json
        cache = self.get_cache_manager()
        data = {}
        if cache:
            # Always look at the DocumentElement's path for the global cache
            doc_element = self.getPortalMaster() or self.getDocumentElement()
            path = '/'.join(doc_element.getPhysicalPath())
            tracked_keys = cache.proxy.get(path)
            
            if tracked_keys:
                for k in tracked_keys.keys():
                    val = cache.proxy.get(k)
                    data[str(k)] = str(val) if val is not None else "EXPIRED/NONE"
            
            if not data:
                data = {
                    'info': 'Global cache is empty.',
                    'path_searched': path,
                    'manager': str(cache)
                }
        else:
            data = {'error': 'No cache manager found.'}
            
        return json.dumps(data, indent=2)


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
