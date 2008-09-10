################################################################################
# _zreferableitem.py
#
# $Id: _zreferableitem.py,v 1.9 2004/11/30 20:03:17 zmsdev Exp $
# $Name:$
# $Author: zmsdev $
# $Revision: 1.9 $
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
from Globals import HTML, HTMLFile
import copy
import operator
import time
import urllib
# Product Imports.
import _globals
import _objattrs

# ------------------------------------------------------------------------------
#  _zreferableitem.getMedlineLink:
# ------------------------------------------------------------------------------
def getMedlineLink(url):
  try:
    http_prefix = 'http://'
    if url.find(http_prefix) == 0:
      url = url[len(http_prefix):]
    url = 'http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=PubMed&list_uids=%i&dopt=Abstract'%int(url)
  except:
    pass
  return url

# ------------------------------------------------------------------------------
#  _zreferableitem.isMailLink:
# ------------------------------------------------------------------------------
def isMailLink(url):
  rtn = type(url) is str and url.lower().find('mailto:') == 0
  return rtn

# ------------------------------------------------------------------------------
#  _zreferableitem.isInternalLink:
# ------------------------------------------------------------------------------
def isInternalLink(url):
  rtn = type(url) is str and url.startswith('{$') and url.endswith('}')
  return rtn

# ------------------------------------------------------------------------------
#  _zreferableitem.absolute_home:
# ------------------------------------------------------------------------------
def absolute_home(ob):
  rtn = ''.join( map( lambda x: x+'/', list(ob.getVirtualRootPhysicalPath( ob.getHome()))))[:-1]
  return rtn


################################################################################
################################################################################
###
###   class ZReferableItem
###
################################################################################
################################################################################
class ZReferableItem: 

  # Management Permissions.
  # -----------------------
  __authorPermissions__ = (
		'manage_RefForm', 'manage_browse_objs',
		)
  __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)

  # Management Interface.
  # ---------------------
  manage_RefForm = HTMLFile('dtml/ZMSLinkElement/manage_refform', globals())
  manage_browse_objs = f_browse_objs = HTMLFile('dtml/ZMSLinkElement/f_browse_objs', globals()) 


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRelObjPath:
  # ----------------------------------------------------------------------------
  def getRelObjPath(self, ob):
    ref = '.'
    currntPath = self.getSelf( self.PAGES).absolute_url()
    targetPath = ob.absolute_url()
    currntElmnts = currntPath.split( '/')
    targetElmnts = targetPath.split( '/')
    i = 0
    while i < len( currntElmnts) and \
          i < len( targetElmnts) and \
          currntElmnts[ i] == targetElmnts[ i]:
      i = i + 1
    currntElmnts = currntElmnts[ i:]
    targetElmnts = targetElmnts[ i:]
    for currntElmnt in currntElmnts:
      ref = ref + '/..'
    for targetElmnt in targetElmnts:
      ref = ref + '/' + targetElmnt
    return ref


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefObjPath:
  # ----------------------------------------------------------------------------
  def getRefObjPath(self, ob):
    ref = ''
    if ob is not None:
      path = ob.relative_obj_path()
      clientIds = absolute_home(ob).split('/')
      thisIds = absolute_home(self).split('/')
      if clientIds[-1] != thisIds[-1]:
        if len(clientIds) <= len(thisIds):
          path = clientIds[-1] + '@' + path
        else:
          while len(clientIds) > 0 and \
                len(thisIds) > 0 and \
                clientIds[0] == thisIds[0]:
            del thisIds[0]
            del clientIds[0]
          s = ''
          for clientId in clientIds:
            if len(s) > 0: s = s + '/'
            s += clientId
          path = s + '@' + path
      ref = '{$' + path + '}'
    return ref


  """
  ##############################################################################
  ###  
  ###  Links FROM other objects.
  ### 
  ##############################################################################
  """

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefByObjs:
  #
  #  Returns references BY other objects.
  # ----------------------------------------------------------------------------
  def getRefByObjs(self, REQUEST={}):
    ref_by = []
    if _objattrs.hasobjattr(self,'ref_by'):
      ref_by = getattr(self,'ref_by',[])
      ref_by = copy.deepcopy(ref_by)
    if _globals.debug( self): 
      _globals.writeLog( self, "[getRefByObjs]: ref_by=%s"%str(ref_by))
    return ref_by


  # ----------------------------------------------------------------------------
  #  ZReferableItem.delRefByObjs:
  #
  #  Deletes references BY other objects.
  # ----------------------------------------------------------------------------
  def delRefByObjs(self, ids=[]):
    key = 'ref_by'
    v = getattr(self,key,[])
    ref_by = []
    for i in v:
      l = i
      l = l[2:-1]
      l = l.split('/')
      b = len(filter(lambda x: x in l, ids)) > 0
      if not b:
        ref_by.append(i)
    if len(ref_by) < len(v):
      setattr(self,'ref_by',ref_by)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.synchronizeRefByObjs:
  #
  #  Synchronizes references BY other objects.
  # ----------------------------------------------------------------------------
  def synchronizeRefByObjs(self, strict=1):
    key = 'ref_by'
    v = getattr(self,key,[])
    ref_by = []
    for i in v:
      ob = self.getLinkObj(i)
      if ob is not None and ob.meta_type[:3] == 'ZMS':
        ob_path = self.getRefObjPath(ob)
        if not ob_path in ref_by:
          ref_by.append(ob_path)
        if ob.meta_type == 'ZMSLinkElement' and ob.isEmbedded( self.REQUEST):
          ob.synchronizePublicAccess()
    if strict or len(ref_by) < len(v):
      setattr(self,'ref_by',ref_by)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.clearRegisteredRefObjs:
  #
  #  Clears registered referencing objects.
  # ----------------------------------------------------------------------------
  def clearRegisteredRefObjs(self, REQUEST):
    ref_by = []
    setattr(self,'ref_by',ref_by)

    
  # ----------------------------------------------------------------------------
  #  ZReferableItem.registerRefObj:
  #
  #  Registers referencing object.
  # ----------------------------------------------------------------------------
  def registerRefObj(self, ob, REQUEST):
    ref = self.getRefObjPath(ob)
    if _globals.debug( self): 
      _globals.writeLog( self, "[registerRefObj]: %s(%s): %s"%(ob.id,ob.meta_type,ref))
    ref_by = self.getRefByObjs(REQUEST)
    if not ref in ref_by:
      ref_by.append(ref)
    ##### Set Attribute ####
    setattr(self,'ref_by',ref_by)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.unregisterRefObj:
  #
  #  Unregisters referencing object.
  # ----------------------------------------------------------------------------
  def unregisterRefObj(self, ob, REQUEST):
    if _globals.debug( self): 
      _globals.writeLog( self, "[unregisterRefObj]: %s(%s)"%(ob.id,ob.meta_type))
    ref_by = self.getRefByObjs(REQUEST)
    ref = self.getRefObjPath( ob)
    id = ref[2:-1].split( '/')[-1]
    for url in ref_by:
      if id in url[2:-1].split( '/'):
        if ref == url:
          del ref_by[ref_by.index(url)]
        else:
          ref_obj = self.getLinkObj( url)
          if ref == self.getRefObjPath( ref_obj):
            del ref_by[ref_by.index(url)]
    ##### Set Attribute ####
    setattr(self,'ref_by',ref_by)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.refreshRefObj:
  #
  #  Refreshs referencing object.
  # ----------------------------------------------------------------------------
  def refreshRefObj(self, ob, REQUEST):
    if _globals.debug( self): 
      _globals.writeLog( self, "[refreshRefObj]: %s(%s) -> %s(%s)"%(self.id,self.meta_type,ob.id,ob.meta_type))
    self.unregisterRefObj(ob,REQUEST)
    self.registerRefObj(ob,REQUEST)

    
  """
  ##############################################################################
  ###  
  ###  References TO other objects.
  ### 
  ##############################################################################
  """

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefToObjs:
  #
  #  Returns list of references TO other objects.
  # ----------------------------------------------------------------------------
  def getRefToObjs(self, REQUEST):
    ref_to =  []
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype == _globals.DT_URL:
        ref = self.getObjProperty(key,REQUEST)
        if not ref in ref_to:
          ref_to.append(ref)
    return ref_to


  # ----------------------------------------------------------------------------
  #  ZReferableItem.synchronizeRefToObjs:
  #
  #  Synchronizes references TO other objects.
  # ----------------------------------------------------------------------------
  def synchronizeRefToObjs(self):
    if _globals.debug( self): 
      _globals.writeLog( self, "[synchronizeRefToObjs]")
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype == _globals.DT_URL:
        for s_lang in self.getLangIds():
          req = {'lang':s_lang,'preview':'preview'}
          ref = self.getObjProperty(key,req)
          ref_obj = self.getLinkObj(ref)
          if ref_obj is not None:
            ref_obj.refreshRefObj(self,req)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.refreshRefToObj:
  #
  #  Refreshs reference TO given destination.
  # ----------------------------------------------------------------------------
  def refreshRefToObj(self, dest_obj, REQUEST):
    if _globals.debug( self): 
      _globals.writeLog( self, "[refreshRefToObj]: %s -> dest_obj=%s(%s)"%(self.id,dest_obj.absolute_url(),dest_obj.meta_type))
    ref_to =  []
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype == _globals.DT_URL:
        ref = self.getObjProperty(key,REQUEST)
        ref_obj = self.getLinkObj(ref)
        if ref_obj is not None:
          if dest_obj.id == ref_obj.id:
            ##### Set Property ####
            dest_obj_path = self.getRefObjPath(dest_obj)
            self.setObjProperty(key,dest_obj_path,REQUEST['lang'],1)


  """
  ##############################################################################
  ###  
  ###  Process Events 
  ### 
  ##############################################################################
  """

  # ----------------------------------------------------------------------------
  #  ZReferableItem.onMoveRefObj:
  #
  #  This method is executed after an object has been moved.
  # ----------------------------------------------------------------------------
  def onMoveRefObj(self, REQUEST, deep=0):
    if _globals.debug( self): 
      _globals.writeLog( self, "[onMoveRefObj]")

    ##### Update references TO other objects ####
    for ref in self.getRefToObjs(REQUEST):
      ob = self.getLinkObj(ref)
      if ob is not None:
        ob.refreshRefObj(self,REQUEST)

    ##### Update references FROM other objects ####
    for ref in self.getRefByObjs(REQUEST):
      ob = self.getLinkObj(ref)
      if ob is not None:
        ob.refreshRefToObj(self,REQUEST)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.onCopyRefObj:
  #
  #  This method is executed after an object has been copied.
  # ----------------------------------------------------------------------------
  def onCopyRefObj(self, REQUEST, deep=0):
    if _globals.debug( self): 
      _globals.writeLog( self, "[onCopyRefObj]")

    ##### Register copy in references TO other objects ####
    for ref in self.getRefToObjs(REQUEST):
      ob = self.getLinkObj(ref)
      if ob is not None:
        ob.registerRefObj(self,REQUEST)

    ##### Clear references FROM other objects ####
    self.clearRegisteredRefObjs(REQUEST)


  """
  ##############################################################################
  ###  
  ###  Resolve Links 
  ### 
  ##############################################################################
  """

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkObj:
  #
  #  Resolves internal/external links and returns Object.
  # ----------------------------------------------------------------------------
  def getLinkObj(self, url, REQUEST={}):
    ob = None
    if isInternalLink(url):
      if url.find('{$__') != 0:
        docElmnt = None
        path = url[2:-1]
        i = path.find('@')
        if i > 0:
          clientIds = path[:i].split('/')
          path = path[i+1:]
          thisHome = self.getHome()
          clientHome = None
          if thisHome.aq_parent.id == clientIds[-1]:
            clientHome = thisHome
            for j in range(len(clientIds)):
              if clientHome.aq_parent.id == clientIds[-(j+1)]:
                clientHome = clientHome.aq_parent
          elif hasattr(thisHome,clientIds[0]):
            clientHome = thisHome
            for j in range(len(clientIds)):
              clientHome = getattr(clientHome,clientIds[j],None)
          if clientHome is not None:
            obs = clientHome.objectValues(['ZMS'])
            if obs:
              docElmnt = obs[0]
        else:
          docElmnt = self.getDocumentElement()
        if docElmnt is not None:
          ob = docElmnt.findObjId(path,REQUEST)
    return ob

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkUrl:
  #
  #  Resolves internal/external links and returns URL.
  # ----------------------------------------------------------------------------
  def getLinkUrl( self, url, REQUEST=None):
    REQUEST = _globals.nvl( REQUEST, self.REQUEST)
    if isInternalLink(url):
      ob = self.getLinkObj(url,REQUEST)
      if ob is None:
        index_html = './index_%s.html?op=not_found&url=%s'%(REQUEST.get('lang',self.getPrimaryLanguage()),url)
      else:
        index_html = ob.getObjProperty('getHref2IndexHtml',REQUEST)
        if index_html == '':
          index_html = ob.getHref2IndexHtml(REQUEST)
      return index_html
    elif isMailLink (url): 
      prefix = 'mailto:'
      return prefix + self.encrypt_ordtype(url[len(prefix):])
    return url

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkHtml:
  #
  #  Resolves internal/external links and returns Html.
  # ----------------------------------------------------------------------------
  def getLinkHtml( self, url, html='<a href="%s">&raquo;</a>', REQUEST=None):
    REQUEST = _globals.nvl( REQUEST, self.REQUEST)
    s = ''
    ob = self
    while ob is not None:
      if html in ob.getMetaobjIds( sort=0):
        metaObj = ob.getMetaobj( html) 
        for metaObjAttr in metaObj['attrs']:
          if metaObjAttr['type'] == 'method' and \
             metaObjAttr['id'] == 'getLinkHtml':
            REQUEST.set( 'ref_id', url)
            return self.dt_html( metaObjAttr['custom'], REQUEST)
      ob = self.getPortalMaster()
    ob = self.getLinkObj(url,REQUEST)
    if ob is not None:
      if ob.isActive(REQUEST) and \
         ob.isVisible(REQUEST):
        url = ob.getHref2IndexHtml(REQUEST)
        s = html%url
    return s

  # ----------------------------------------------------------------------------
  #  ZReferableItem.synchronizeRefs:
  #  
  #  @param
  #  @return
  # ----------------------------------------------------------------------------
  def synchronizeRefs( self, ob_id=None):
    portalMaster = self.getPortalMaster()
    if portalMaster is not None:
      return portalMaster.synchronizeRefs()
    
    message = ''
    t0 = time.time()
    
    obs = {}
    map( lambda x: operator.setitem(obs, x.base_url(), x), _globals.objectTree( self, True))
    message += 'Load object-tree (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)<br/>'
    abs_urls = obs.keys()
    abs_urls.sort()
    map( lambda x: delattr( obs[x], 'ref_by'), filter( lambda x: hasattr( obs[x], 'ref_by'), abs_urls))
    langs = self.getLangIds()
    for abs_url in abs_urls:
      ob = obs[ abs_url]
      
      # Process recordset.
      if ob.getType()=='ZMSRecordSet':
        key = ob.getMetaobjAttrIds(ob.meta_id)[0]
        obj_attr = ob.getObjAttr(key)
        for lang in langs:
          for obj_vers in ob.getObjVersions():
            v = _objattrs.getobjattr(ob,obj_vers,obj_attr,lang)
            c = 0
            for r in v:
              for k in r.keys():
                v = r[k]
                o = v
                if type(v) is str:
                  l = v.split('{$')
                  if l > 1:
                    m = [l[0]]
                    for i in l[1:]:
                      ref = i[:i.find('}')]
                      if ref.startswith('__') and ref.endswith('__'):
                        ref = ref[2:-2]
                      if len( ref.split('@')) == 1:
                        home = ob.getHome().id
                      else:
                        home = ref.split('@')[0].split('/')[-1]
                      id = ref.split('@')[-1].split('/')[-1]
                      if len( id) == 0:
                        id = 'content'
                      f = filter( lambda x: x.find('/%s/content'%home) > 0 and x.endswith('/%s'%id), abs_urls)
                      if len( f) == 0:
                        ref = '__%s__'%ref
                      else:
                        target = obs[f[0]]
                        ref = ob.getRefObjPath( target)[2:-1]
                        setattr( target, 'ref_by', getattr( target, 'ref_by', []) + [ target.getRefObjPath( ob)])
                      if ref.startswith('__') and ref.endswith('__'):
                        message += '<a href="%s/manage_main" target="_blank">%s(%s).%s[%i]=%s</a><br/>'%(ob.absolute_url(),ob.absolute_url(),ob.meta_type,k,c,ref)
                      m.append(ref+i[i.find('}'):])
                    v = '{$'.join(m)
                    if v != o:
                      r[k] = v
              c += 1
      
      # Process object.
      else:
        for key in ob.getObjAttrs().keys():
          obj_attr = ob.getObjAttr(key)
          datatype = obj_attr['datatype_key']
          if datatype in _globals.DT_STRINGS:
            for lang in langs:
              for obj_vers in ob.getObjVersions():
                v = _objattrs.getobjattr(ob,obj_vers,obj_attr,lang)
                o = v
                if type(v) is str:
                  l = v.split('{$')
                  if l > 1:
                    m = [l[0]]
                    for i in l[1:]:
                      ref = i[:i.find('}')]
                      if ref.startswith('__') and ref.endswith('__'):
                        ref = ref[2:-2]
                      if len( ref.split('@')) == 1:
                        home = ob.getHome().id
                      else:
                        home = ref.split('@')[0].split('/')[-1]
                      id = ref.split('@')[-1].split('/')[-1]
                      if len( id) == 0:
                        id = 'content'
                      f = filter( lambda x: x.find('/%s/content'%home) > 0 and x.endswith('/%s'%id), abs_urls)
                      if len( f) == 0:
                        ref = '__%s__'%ref
                      else:
                        target = obs[f[0]]
                        ref = ob.getRefObjPath( target)[2:-1]
                        setattr( target, 'ref_by', getattr( target, 'ref_by', []) + [ target.getRefObjPath( ob)])
                      if ref.startswith('__') and ref.endswith('__'):
                        message += '<a href="%s/manage_main" target="_blank">%s(%s).%s=%s</a><br/>'%(ob.absolute_url(),ob.absolute_url(),ob.meta_type,key,ref)
                      m.append(ref+i[i.find('}'):])
                    v = '{$'.join(m)
                    if v != o:
                      _objattrs.setobjattr(ob,obj_vers,obj_attr,v,lang)
    
    if ob_id is not None:
      # Return with desired object.
      home = ob_id.split('@')[0]
      id = ob_id.split('@')[1]
      f = filter( lambda x: x.find('/%s/content'%home) > 0 and x.endswith('/%s'%id), abs_urls)
      if len( f) == 0:
        return None
      else:
        return obs[f[0]]
    
    else:
      # Return with message.
      message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
      return message

################################################################################
