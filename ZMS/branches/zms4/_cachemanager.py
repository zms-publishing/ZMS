from __future__ import division
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
from builtins import object
from builtins import filter
import time
# Product Imports.
from . import standard

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
      return '%s#%s'%('_'.join(self.getPhysicalPath()[2:]), key)

    # --------------------------------------------------------------------------
    #  clearReqBuff:
    #
    #  Clear buffered values from Http-Request.
    # --------------------------------------------------------------------------
    def clearReqBuff(self, prefix='', REQUEST=None):
      request = self.REQUEST
      buff = request.get('__buff__', Buff())
      reqBuffId = self.getReqBuffId(prefix)
      if len(prefix) > 0:
        reqBuffId += '.'
      for key in buff.__dict__.keys():
        if key.startswith(reqBuffId):
          delattr(buff, key)
 
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
      return getattr(buff, reqBuffId)

    # --------------------------------------------------------------------------
    #  storeReqBuff:
    #
    #  Returns value and stores it in buffer of Http-Request.
    # --------------------------------------------------------------------------
    def storeReqBuff(self, key, value, REQUEST=None):
      request = self.REQUEST
      buff = request.get('__buff__', Buff())
      reqBuffId = self.getReqBuffId(key)
      setattr(buff, reqBuffId, value)
      request.set('__buff__', buff)
      return value

    # --------------------------------------------------------------------------
    #  clearMeasurement:
    #
    #  Clears measurement.
    # --------------------------------------------------------------------------
    def clearMeasurement(self, category=''):
      request = self.REQUEST
      if request.get('zmi-measurement'):
        buff = request.get('__buff__', Buff())
        measurements = getattr(buff, 'measurements', {})
        for key in measurements.keys():
          if key.find(category)>=0:
            del measurements[key]
        setattr(buff, 'measurements', measurements)
        request.set('__buff__', buff)

    # --------------------------------------------------------------------------
    #  startMeasurement:
    #
    #  Starts measurement.
    # --------------------------------------------------------------------------
    def startMeasurement(self, category):
      request = self.REQUEST
      if request.get('zmi-measurement'):
        buff = request.get('__buff__', Buff())
        measurements = getattr(buff, 'measurements', {})
        measurement = measurements.get(category, {}) 
        measurement['start'] = time.time()
        measurements[category] = measurement
        setattr(buff, 'measurements', measurements)
        request.set('__buff__', buff)

    # --------------------------------------------------------------------------
    #  stopMeasurement:
    #
    #  Stops measurement.
    # --------------------------------------------------------------------------
    def stopMeasurement(self, category):
      request = self.REQUEST
      if request.get('zmi-measurement'):
        buff = request.get('__buff__', Buff())
        measurements = getattr(buff, 'measurements', {})
        measurement = measurements.get(category, {})
        if 'start' in measurement:
          hotspot = '/'.join(self.getPhysicalPath()) 
          millis = time.time() - measurement['start']
          measurement['category'] = category
          measurement['count'] = measurement.get('count', 0)+1
          measurement['total'] = measurement.get('total', 0.0)+millis
          measurement['hotspot'] = [measurement.get('hotspot', hotspot), hotspot][measurement.get('max', millis)<millis] 
          measurement['min'] = [measurement.get('min', millis), millis][measurement.get('min', millis)>millis]
          measurement['max'] = [measurement.get('max', millis), millis][measurement.get('max', millis)<millis]
          measurement['avg'] = measurement['total']/measurement['count']
          del measurement['start']
          measurements[category] = measurement
          setattr(buff, 'measurements', measurements)
          request.set('__buff__', buff)

    # --------------------------------------------------------------------------
    #  getMeasurement:
    #
    #  Gets measurement.
    # --------------------------------------------------------------------------
    def getMeasurement(self, category=''):
      request = self.REQUEST
      buff = request.get('__buff__', Buff())
      measurements = getattr(buff, 'measurements', {})
      return standard.sort_list(filter(lambda x:x['category'].find(category)>=0, measurements.values()), 'total', 'desc')

################################################################################
