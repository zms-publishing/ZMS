"""
_cachemanager.py

Internal helpers for cachemanager in ZMS.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
# Imports.
from Products.zms import standard
from zope.globalrequest import getRequest

class Buff(object):
  pass

################################################################################
#
# ReqBuff
#
################################################################################
class ReqBuff(object):

    # ------------------------------------------------------------------------------
    #  getReqBuffId:
    #
    #  Gets buffer-id in Http-Request.
    # ------------------------------------------------------------------------------
    def getReqBuffId(self, key):
      return '%s_%s'%('_'.join(self.getPhysicalPath()[2:]), key)

    # --------------------------------------------------------------------------
    #  clearReqBuff:
    #
    #  Clear buffered values from Http-Request.
    # --------------------------------------------------------------------------
    def clearReqBuff(self, prefix='', REQUEST=None):
      request = getattr(self, 'REQUEST', getRequest())
      buff = request.get('__buff__', Buff())
      reqBuffId = self.getReqBuffId(prefix)
      if len(prefix) > 0:
        reqBuffId += '.'
      for key in list(buff.__dict__):
        if key.startswith(reqBuffId):
          delattr(buff, key)
 
    # --------------------------------------------------------------------------
    #  fetchReqBuff:
    #
    #  Fetch buffered value from Http-Request.
    #
    #  @throws Exception
    # --------------------------------------------------------------------------
    def fetchReqBuff(self, key=None, REQUEST=None):
      request = getattr(self, 'REQUEST', getRequest())
      if key is None: # For debugging purposes, return whole buffer.
        return None   # request.get('__buff__',{})
      buff = request['__buff__']
      reqBuffId = self.getReqBuffId(key)
      return getattr(buff, reqBuffId)

    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST=None):
      request = getattr(self, 'REQUEST', getRequest())
      buff = request.get('__buff__', None)
      if buff is None:
        buff = Buff()
      reqBuffId = self.getReqBuffId(key)
      setattr(buff, reqBuffId, value)
      request.set('__buff__', buff)
      return value
