################################################################################
# _cachemanager.py
#
# $Id: _cachemanager.py,v 1.7 2004/11/24 21:02:52 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.7 $
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


# ------------------------------------------------------------------------------
#  _cachemanager.clearCachePage
# ------------------------------------------------------------------------------
def _clearCachePage(self, id):
  count = 0
  if not self.isPage():
    return _clearCachePage(self.getParentNode(),id)
  if id in self.objectIds():
    self.writeLog( "[_clearCachePage]: Removing ID=%s"%id)
    self.manage_delObjects(ids=[id])
    count += 1
  return count


# ------------------------------------------------------------------------------
#  _refreshCachePage
# ------------------------------------------------------------------------------
def _refreshCachePage(self, id, REQUEST):
  if not self.isPage():
    return _refreshCachePage(self.getParentNode(),id,REQUEST)
  _clearCachePage(self,id)
  self.writeLog( "[_refreshCachePage]: Generating ID=%s"%id)
  REQUEST.set('ZMS_CACHE',1)
  title = '*** CACHE [%s] ***'%str(self.getObjProperty( 'attr_cacheable', REQUEST))
  raw = self.index_html(self,REQUEST)
  self.manage_addDTMLDocument(id,title,raw)
  if self.getObjProperty( 'attr_cacheable', REQUEST) in [ 2, '2']:
    raw = self.dt_html( raw, REQUEST)
  return raw


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
      url = REQUEST.get('URL','/manage')
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
################################################################################
###
###   Class CacheableObject:
###
################################################################################
################################################################################
class CacheableObject(ReqBuff):

    # --------------------------------------------------------------------------
    # CacheableObject.clearCachePage: 
    # --------------------------------------------------------------------------
    def clearCachePage(self):
      count = 0
      for s_lang in self.getLangIds():
        for s_op in dct_op.keys():
          id = _getCacheId('%s_%s'%(s_op,s_lang))
          count += _clearCachePage(self,id)
      return count


    # --------------------------------------------------------------------------
    # CacheableObject.clearCachePages: 
    # --------------------------------------------------------------------------
    def clearCachePages(self, max_depth=999, cur_depth=0):
      count = 0
      if self.isPage():
        count += self.clearCachePage()
        if cur_depth < max_depth:
          for ob in self.getChildNodes():
            count += ob.clearCachePages( max_depth, cur_depth+1)
      return count


    # --------------------------------------------------------------------------
    #  CacheableObject.synchronizeCachePage: 
    # --------------------------------------------------------------------------
    def synchronizeCachePage(self, REQUEST):
      if self.getConfProperty('ZMS.cache.active')==1:
        s_lang = REQUEST.get('lang',self.getPrimaryLanguage())
        if self.isPageElement():
          _clearCachePage(self,_getCacheId('index_%s'%s_lang))
          _clearCachePage(self,_getCacheId('index_print_%s'%s_lang))
        elif self.isPage():
          _clearCachePage(self,_getCacheId('index_%s'%s_lang))
          _clearCachePage(self,_getCacheId('index_print_%s'%s_lang))
          _clearCachePage(self,_getCacheId('sitemap_%s'%s_lang))
        else:
          self.getParentNode().synchronizeCachePage(REQUEST)


    # --------------------------------------------------------------------------
    # CacheableObject.getCachedPages:
    # --------------------------------------------------------------------------
    def getCachedPages(self, REQUEST, max_depth=999, cur_depth=0):
      count = 0
      if self.isPage():
        if self.isCachedPage( REQUEST):
          self.getCachedPage( REQUEST)
        count += 1
        if cur_depth < max_depth:
          for ob in self.filteredChildNodes( REQUEST, self.PAGES):
            count += ob.getCachedPages( REQUEST, max_depth, cur_depth+1)
      return count


    # --------------------------------------------------------------------------
    #  CacheableObject.isCachedPage:
    # --------------------------------------------------------------------------
    def isCachedPage(self, REQUEST):
      rtn = True
      # URL-Params?
      try: rtn = rtn and not len(filter( lambda x: x != '-C', REQUEST.form.keys())) > 0
      except: pass
      if not rtn:
        return False
      # Page exists?
      id = _getIdFromUrl(REQUEST)
      if id in self.objectIds(['DTML Document']):
        return True
      # Page cacheable?
      if not self.isPage():
        parent = self.getParentNode()
        if parent is not None and isinstance( parent, CacheableObject):
          return parent.isCachedPage(REQUEST)
      # Page can be cached?
      found = False
      for s_lang in self.getLangIds():
        for s_op in dct_op.keys():
          if id == _getCacheId('%s_%s'%(s_op,s_lang)):
            found = True
      rtn = rtn and found
      rtn = rtn and self.getConfProperty('ZMS.cache.active')
      rtn = rtn and self.getObjProperty('attr_cacheable',REQUEST) in [ 1, '1', 2, '2', True]
      rtn = rtn and not REQUEST.get('preview','')=='preview'
      rtn = rtn and not REQUEST.get('ZMS_CACHE',0) in [ 1, True]
      return rtn


    # --------------------------------------------------------------------------
    # CacheableObject.getCachedPage:
    # --------------------------------------------------------------------------
    def getCachedPage(self, REQUEST):
      if not self.isPage():
        return self.getParentNode().getCachedPage( REQUEST)
      id = _getIdFromUrl( REQUEST)
      for ob in self.objectValues( [ 'DTML Document']):
        if ob.id() == id:
          raw = ob.raw
          if self.getObjProperty( 'attr_cacheable', REQUEST) in [ 2, '2']:
            raw = self.dt_html( raw, REQUEST)
          return raw
      return _refreshCachePage( self, id, REQUEST)


    ############################################################################
    #  CacheableObject.manage_getCachedPages:
    #
    #  Get cached pages.
    ############################################################################
    def manage_getCachedPages(self, lang, REQUEST, RESPONSE): 
      """ CacheableObject.manage_getCachedPages """
      
      message = ''
      t0 = time.time()
      max_depth = REQUEST.get('attr_cacheable_levels',999)
      
      ##### Clear cached pages ####
      count = self.clearCachePages( max_depth)
      message += self.getZMILangStr('MSG_DELETED')%count
      
      ##### Get cached pages ####
      REQUEST.set( 'URL', REQUEST['URL1'] + '/index_%s.html'%lang)
      count = self.getCachedPages( REQUEST, max_depth)
      message += '<br/>' + self.getZMILangStr('MSG_INSERTED')%(str(count)+' '+self.getZMILangStr('ATTR_OBJECTS'))
      
      # Return with message.
      message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      target = REQUEST.get('manage_target','manage_properties')
      return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))


    ############################################################################
    #  CacheableObject.manage_clearCachePages:
    #
    #  Clear cached pages.
    ############################################################################
    def manage_clearCachePages(self, lang, REQUEST, RESPONSE): 
      """ CacheableObject.manage_clearCachePages """
      
      message = ''
      t0 = time.time()
      max_depth = REQUEST.get('attr_cacheable_levels',999)
      
      ##### Clear cached pages ####
      count = self.clearCachePages( max_depth)
      message += self.getZMILangStr('MSG_DELETED')%count
      
      # Return with message.
      message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      target = REQUEST.get('manage_target','manage_properties')
      return RESPONSE.redirect('%s?preview=preview&lang=%s&manage_tabs_message=%s'%(target,lang,urllib.quote(message)))
      
################################################################################
