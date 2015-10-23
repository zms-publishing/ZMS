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
    #  fetchReqBuff:
    #
    #  Fetch buffered value from Http-Request.
    #
    #  @throws Exception
    # --------------------------------------------------------------------------
    def fetchReqBuff(self, key, REQUEST, forced=False):
      buff = None
      if forced or not REQUEST.get('URL','/manage').find('/manage') >= 0:
        reqBuffId = self.getReqBuffId(key)
        buff = REQUEST.get('__buff__',Buff())
      return getattr(buff,reqBuffId)

    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST):
      reqBuffId = self.getReqBuffId(key)
      buff = REQUEST.get('__buff__',Buff())
      setattr(buff,reqBuffId,value)
      REQUEST.set('__buff__',buff)
      return value

################################################################################
