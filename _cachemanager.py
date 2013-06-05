################################################################################
# _cachemanager.py
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

# Imports.
import time
import urllib
import zExceptions


dct_op = {'index':'','sitemap':'sitemap','index_print':'print'}


# ------------------------------------------------------------------------------
#  _cachemanager.Empty
# ------------------------------------------------------------------------------
class Empty: pass


################################################################################
#
#   STATIC CACHE
#
################################################################################

# ------------------------------------------------------------------------------
#  _cachemanager._getIdFromUrl
# ------------------------------------------------------------------------------
def _getIdFromUrl(REQUEST):
  id = REQUEST['URL']
  id = id[:-5]
  id = id[id.rfind('/')+1:]
  if id.find('_') < 0 and REQUEST.has_key('lang'):
    id = '%s_%s'%(id,REQUEST['lang'])
  return _getCacheId(id)


# ------------------------------------------------------------------------------
#  _cachemanager._getCacheId
# ------------------------------------------------------------------------------
def _getCacheId(id):
  return 'cache_%s_html'%id


################################################################################
#
#   REQUEST BUFFER
#
################################################################################

# ------------------------------------------------------------------------------
#  getReqBuffId:
#
#  Gets buffer-id in Http-Request.
#
#  @throws Exception
# ------------------------------------------------------------------------------
def getReqBuffId(self, key, REQUEST):
  id = '%s#%s.%s'%( '/'.join(self.getPhysicalPath()),key,REQUEST.get('lang','*'))
  return id


# ------------------------------------------------------------------------------
#  getReqBuff:
#
#  Gets buffer from Http-Request.
#
#  @throws Exception
# ------------------------------------------------------------------------------
def getReqBuff(self, REQUEST):
  buff = REQUEST.get('__buff__',None)
  if buff == None:
    buff = Empty()
  return buff


################################################################################
#
# ReqBuff
#
################################################################################
class ReqBuff:

    # --------------------------------------------------------------------------
    #  fetchReqBuff:
    #
    #  Fetch buffered value from Http-Request.
    #
    #  @throws Exception
    # --------------------------------------------------------------------------
    def fetchReqBuff(self, key, REQUEST, forced=False):
      if REQUEST.get('ZMS_FETCH_REQ_BUFF',True):
        url = REQUEST.get('PSEUDOURL',REQUEST.get('URL','/manage'))
        url = url[url.rfind('/'):]
        if forced or not url.find('/manage') >= 0:
          buff = getReqBuff(self,REQUEST)
          reqBuffId = getReqBuffId(self,key,REQUEST)
          try:
            value = getattr(buff,reqBuffId)
            return value
          except:
            raise zExceptions.InternalError('%s not found in ReqBuff!'%reqBuffId)
      raise zExceptions.InternalError('ReqBuff is inactive!')

    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST):
      try:
        buff = getReqBuff(self,REQUEST)
        reqBuffId = getReqBuffId(self,key,REQUEST)
        setattr(buff,reqBuffId,value)
        REQUEST.set('__buff__',buff)
      except:
        pass
      return value

    # --------------------------------------------------------------------------
    #  clearReqBuff:
    #
    #  Clears key from buffer of Http-Request.
    # --------------------------------------------------------------------------
    def clearReqBuff(self, key, REQUEST):
      try:
        buff = getReqBuff(self,REQUEST)
        reqBuffId = getReqBuffId(self,key,REQUEST)
        delattr(buff,reqBuffId)
        REQUEST.set('__buff__',buff)
      except:
        pass

################################################################################
