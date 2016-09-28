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

class Buff:
  pass

################################################################################
#
# ReqBuff
#
################################################################################
class ReqBuff:

    # ------------------------------------------------------------------------------
    #  getReqBuffId:
    #
    #  Gets buffer-id in Http-Request.
    # ------------------------------------------------------------------------------
    def getReqBuffId(self, key):
      return '%s#%s'%('_'.join(self.getPhysicalPath()),key)

    # --------------------------------------------------------------------------
    #  clearReqBuff:
    #
    #  Clear buffered values from Http-Request.
    # --------------------------------------------------------------------------
    def clearReqBuff(self, prefix, REQUEST=None):
      request = self.REQUEST
      buff = request.get('__buff__',Buff())
      reqBuffId = self.getReqBuffId(prefix)+'.'
      for key in buff.__dict__.keys():
        if key.startswith(reqBuffId):
          delattr(buff,key)
 
    # --------------------------------------------------------------------------
    #  fetchReqBuff:
    #
    #  Fetch buffered value from Http-Request.
    #
    #  @throws Exception
    # --------------------------------------------------------------------------
    def fetchReqBuff(self, key, REQUEST=None):
      request = self.REQUEST
      buff = request['__buff__']
      reqBuffId = self.getReqBuffId(key)
      return getattr(buff,reqBuffId)

    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST=None):
      request = self.REQUEST
      buff = request.get('__buff__',Buff())
      reqBuffId = self.getReqBuffId(key)
      setattr(buff,reqBuffId,value)
      request.set('__buff__',buff)
      return value

################################################################################
