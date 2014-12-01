################################################################################
# _pathhandler.py
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
from OFS.CopySupport import absattr
import copy
# Product Imports.
import _blobfields
import _confmanager
import _fileutil
import _globals


# ------------------------------------------------------------------------------
#  _pathhandler.validateId:
#
#  Validates id against list of possible declarative id.
# ------------------------------------------------------------------------------
def validateId(self, id, REQUEST):
  langs = []
  lang = REQUEST.get( 'lang')
  if lang is None:
    for lang in self.getLanguages():
      req={ 'lang': lang, 'preview': REQUEST.get('preview','')}
      decl_id = self.getDeclId( req)
      if id == decl_id:
        langs.append( lang)
    if len( langs) == 1:
      self.REQUEST.set( 'lang', langs[0])
  else:
    decl_id = self.getDeclId( REQUEST)
    if id == decl_id:
      langs.append( lang)
  if len( langs) > 0:
    return True
  return False


# ------------------------------------------------------------------------------
#  _pathhandler.filterId:
#
#  Filters object by id.
# ------------------------------------------------------------------------------
def filterId(self, id, REQUEST):
  obs = self.objectValues( self.dGlobalAttrs.keys())
  filtered_obs = filter( lambda x: x.id == id, obs)
  if len( filtered_obs) > 0:
    return filtered_obs[0]
  elif self.getConfProperty( 'ZMS.pathhandler', 0) != 0:
    req = { 'lang': REQUEST.get('lang'), 'preview': REQUEST.get('preview')}
    filtered_obs = filter( lambda x: x.isVisible( req) and x.isPage() and validateId( x, id, req), obs)
    if len( filtered_obs) > 0:
      return filtered_obs[0]
  return None


# ------------------------------------------------------------------------------
#  _pathhandler.handleBlobAttrs:
#
#  If the object has blob-fields find by filename and display data.
# ------------------------------------------------------------------------------
def handleBlobAttrs(self, name, REQUEST):
  langs = self.getLangIds()
  name_without_lang_suffix = name
  if len(langs) == 1 and name.find('_%s.'%langs[0]) > 0:
    name_without_lang_suffix = name.replace('_%s.'%langs[0],'.')
  for ob in [self]+self.filteredChildNodes(REQUEST,['ZMSFile']):
    for key in ob.getObjAttrs().keys():
      obj_attr = ob.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype in _globals.DT_BLOBS:
        lang = ob.getLanguageFromName( REQUEST['URL'])
        REQUEST.set( 'lang', lang)
        value = ob.getObjProperty( key, REQUEST)
        if value is not None:
          href = value.getHref( REQUEST)
          langfilename = href.split( '/')[ -1]
          if langfilename.find( '?') > 0:
            langfilename = langfilename[ :langfilename.find( '?')]
          if langfilename == name or \
             langfilename == _globals.url_encode(name) or \
             langfilename == name_without_lang_suffix or \
             langfilename == _globals.url_encode(name_without_lang_suffix):
            return value
  return None



################################################################################
################################################################################
###
###   class PathHandler:
###
###   Based on the Zope-Product PathHandler
###   http://www.zope.org/Members/NIP/PathHandler).
###
################################################################################
################################################################################
class PathHandler: 

    # --------------------------------------------------------------------------
    #  PathHandler.base_url
    # --------------------------------------------------------------------------
    def base_url(self):
      if  self.getConfProperty( 'ZMS.pathcoherence', 1) == 1:
        # return self.REQUEST.get('BASE0') + '/'.join( list( self.getPhysicalPath()))
        return '/'.join( list( self.getPhysicalPath()))
      else:
        return self.absolute_url()


    # --------------------------------------------------------------------------
    #  PathHandler.__bobo_traverse__
    # --------------------------------------------------------------------------
    def __bobo_traverse__(self, TraversalRequest, name):
      # If this is the first time this __bob_traverse__ method has been called
      # in handling this traversal request, store the path_to_handle
      req = self.REQUEST
      url = self.REQUEST.get('URL','')
      zmi = url.find('/manage') >= 0
      
      if not TraversalRequest.has_key('path_to_handle'):
      
          # Make a reversed copy of the TraversalRequestNameStack
          TraversalRequestNameStackReversed=copy.copy(TraversalRequest['TraversalRequestNameStack'])
          TraversalRequestNameStackReversed.reverse()
          
          # Set path_to_handle in the TraversalRequest.
          TraversalRequest['path_to_handle']=[name]+TraversalRequestNameStackReversed
          
          # Set path_to_handle for VirtualHosts.
          if '/' in TraversalRequest[ 'path_to_handle']:
            path_physical = req.get( 'path_physical', list( self.getDocumentElement().getPhysicalPath())[1:])
            if len( path_physical) > 1:
              b = TraversalRequest[ 'path_to_handle'].index( '/')
              TraversalRequest[ 'path_to_handle'] = TraversalRequest[ 'path_to_handle'][ b+1:]
              for i in range( 1, len( path_physical)):
                TraversalRequest[ 'path_to_handle'].insert( i-1, path_physical[ i])
      
      # Set language.
      lang = req.get( 'lang')
      if lang is None:
        lang = self.getLanguageFromName( TraversalRequest['path_to_handle'][-1])
      if lang is not None:
        req.set( 'lang', lang)
     
      # If the name is in the list of attributes, call it.
      ob = getattr( self, name, None)
      if ob is None or getattr(ob,'meta_type',None) == 'Folder':
        obContext = filterId( self, name, req)
        if obContext is not None:
          ob = obContext
      if ob is not None:
        meta_type = getattr(ob,'meta_type','?')
        if not zmi and TraversalRequest['path_to_handle'][-1] == name:
          lang = req.get( 'lang')
          if lang is None:
            lang = self.getHttpAcceptLanguage( self.REQUEST)
          if lang is not None:
            self.REQUEST.set( 'lang', lang)
        
        return ob
      
      # otherwise do some 'magic'
      else:
        _globals.writeLog( self, '[__bobo_traverse__]: otherwise do some magic')
        
        # Package-Home.
        if name == '$ZMS_HOME':
          i = TraversalRequest['path_to_handle'].index(name)
          filepath = self.localfs_package_home()+'/'+'/'.join(TraversalRequest['path_to_handle'][i+1:])
          data, mt, enc, size = _fileutil.readFile(filepath)
          filename = TraversalRequest['path_to_handle'][-1]
          f = self.FileFromData( data, filename, mt)
          f.aq_parent = self
          f.key = name
          f.lang = req.get('lang', self.getPrimaryLanguage())
          return f
        
        # Pathhandler-Hook.
        if 'pathhandler' in self.getMetaobjAttrIds( self.meta_id, types=['method','py']):
          if name == TraversalRequest['path_to_handle'][-1]:
            req.set( 'path_', '/'.join(req.get('path_',[])+[name]))
            return self.getObjProperty('pathhandler',req)
          else:
            req.set( 'path_', req.get('path_',[])+[name])
            return self
        
        if not zmi or req.get( 'ZMS_PATH_HANDLER', False):
          
          # Recursive inclusions.
          thisOb = _globals.nvl( filterId( self, name, req), self)
          if thisOb.meta_type == 'ZMSLinkElement':
            recursive = thisOb.isEmbeddedRecursive( req)
            if recursive:
              ob = thisOb.getRefObj()
              proxy = thisOb.initProxy( thisOb.aq_parent, thisOb.absolute_url(), ob, recursive)
              c = 0
              l = TraversalRequest[ 'path_to_handle']
              if thisOb.id in l:
                i = l.index( thisOb.id) + 1
              elif thisOb.getDeclId( req) in l:
                i = l.index( thisOb.getDeclId( req)) + 1
              for k in range( i, len(l)):
                newOb = None
                obs = ob.getChildNodes( req)
                filtered_obs = filter( lambda x: ( x.id == l[k] or x.getDeclId( req) == l[k]), obs)
                if len( filtered_obs) == 1:
                  newOb = filtered_obs[0]
                try:
                  if newOb.meta_type not in self.dGlobalAttrs.keys():
                    newOb = None
                except:
                  pass
                if newOb is None:
                  break
                ob = newOb
                proxy = thisOb.initProxy( proxy, proxy.absolute_url()+'/'+ob.id, ob, recursive)
                c += 1
              if c > 0:
                req.set( 'ZMS_PROXY_%s'%self.id, proxy)
            if req.get( 'ZMS_PROXY_%s'%self.id) and req.get( 'ZMS_PROXY_%s'%self.id).id != TraversalRequest[ 'path_to_handle'][-1]:
              v = handleBlobAttrs( req.get( 'ZMS_PROXY_%s'%self.id).proxy, TraversalRequest[ 'path_to_handle'][-1], req)
              if v is not None: 
                return v
            return thisOb
        
        # Declarative Urls.
        ob = self.pathob([name],self.REQUEST)
        if ob is not None:
          return ob
        
        # If the object is record-set and has blob-fields find by filename and 
        # display data.
        if name.find( '@') == 0:
          if self.getType()=='ZMSRecordSet':
            try:
              i = int( name[1:])
              r = self.getObjProperty( self.getMetaobj( self.meta_id)['attrs'][0]['id'], self.REQUEST)
              d = r[i]
              for key in d.keys():
                value = d[key]
                if isinstance(value,_blobfields.MyImage) or isinstance(value,_blobfields.MyFile):
                  value = value._getCopy()
                  value.aq_parent = self
                  value.key = key
                  value.lang = req.get('lang', self.getPrimaryLanguage())
                  langfilename = value.getHref( req).split( '/')[ -1]
                  if langfilename.find( '?') > 0:
                    langfilename = langfilename[ :langfilename.find( '?')]
                  if langfilename == TraversalRequest['path_to_handle'][-1]:
                    return value
            except:
              _globals.writeError( self, '[__bobo_traverse__]')
          else:
            try:
              i = int( name[1:])
              obj_attrs = self.getObjAttrs()
              for key in self.getObjAttrs().keys():
                obj_attr = obj_attrs[ key]
                if obj_attr['datatype_key'] == _globals.DT_LIST and \
                   obj_attr['repetitive']:
                  lp = [ self.REQUEST.get('preview')]
                  if lp[ 0] != 'preview':
                    lp.append( 'preview')
                  par = None
                  for ip in lp:
                    try:
                      self.REQUEST.set( 'preview', ip)
                      r = self.getObjProperty( key, self.REQUEST, par)
                      value = r[i]
                      value = value._getCopy()
                      value.aq_parent = self
                      value.key = key
                      value.lang = req.get('lang', self.getPrimaryLanguage())
                      langfilename = value.getHref( req).split( '/')[ -1]
                      if langfilename.find( '?') > 0:
                        langfilename = langfilename[ :langfilename.find( '?')]
                      if langfilename == TraversalRequest['path_to_handle'][-1]:
                        return value
                    except:
                      _globals.writeError( self, '[__bobo_traverse__]: ip=%s'%str(ip))
                    par = {'fetchReqBuff':0}
                  self.REQUEST.set( 'preview', lp[ 0])
            except:
              _globals.writeError( self, '[__bobo_traverse__]')
        
        # If the object has blob-fields find by filename and display data.
        v = handleBlobAttrs( self, name, req)
        if v is not None: return v
        
        # If the object has executable-fields find by name and display data.
        if name in self.getMetaobjAttrIds( self.meta_id, types=['method','py']):
          v = self.attr(name)
          if v is not None:
            if type(v) is str:
              v = self.FileFromData( v, content_type='text/plain;charset=utf-8')
              v.aq_parent = self
              v.key = name
              v.lang = req.get('lang', self.getPrimaryLanguage())
            return v
        
        # Skins
        if name == TraversalRequest['path_to_handle'][-1]:
          l = name
          i = l.rfind('_')
          j = l.rfind('.')
          if i > 0 and j > 0:
            lang = l[i+1:j]
            if lang in self.getLangIds():
              auth_user = self.REQUEST.get('AUTHENTICATED_USER')
              zms_skin = l[:i]
              zms_ext = l[j+1:]
              if zms_skin in map(lambda x:x.strip(),self.getConfProperty('ZMS.skins','index,search,sitemap,mobile').split(',')) and \
                 zms_ext == self.getPageExt(self.REQUEST)[1:]:
                access = True
                #--access = (auth_user is None and self.hasPublicAccess()) or \
                #--         (auth_user is not None and auth_user.has_permission( 'View', self) in [ 1, True])
                if access:
                  self.REQUEST.set('ZMS_SKIN',zms_skin)
                  self.REQUEST.set('ZMS_EXT',zms_ext)
                  self.REQUEST.set('lang',lang)
                  return self
        
        # If there's no more names left to handle, return the path handling 
        # method to the traversal machinery so it gets called next
        exc_value='<h2>Site-Error</h2><b>Sorry, there is no web page matching your request.</b> It is possible you typed the address incorrectly, or that the page no longer exists.<hr><b>Resource<b> <i>'+name+'</i> '+''.join(map(lambda x: x+'/',TraversalRequest['path_to_handle']))+' GET'
        return self.standard_error_message( self, 
          exc_type='Resource not found', 
          exc_value=exc_value, 
          REQUEST=self.REQUEST)


    # --------------------------------------------------------------------------
    #  PathHandler.pathob
    # --------------------------------------------------------------------------
    def pathob(self, path_to_handle, REQUEST):
      path_ob = self
      path_index = 0
      while True:
        if path_index == len(path_to_handle):
          return path_ob
        path_item = path_to_handle[path_index]
        obs = path_ob.objectValues( self.dGlobalAttrs.keys())
        path_ob = filterId( path_ob, path_item, REQUEST)
        if path_ob is None: 
          return path_ob
        path_index += 1

################################################################################
