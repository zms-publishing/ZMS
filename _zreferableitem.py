################################################################################
# _zreferableitem.py
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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
import operator
import re
import time
import urllib
# Product Imports.
import _confmanager
import _globals
import _objattrs

# ------------------------------------------------------------------------------
#  _zreferableitem.isMailLink:
# ------------------------------------------------------------------------------
def isMailLink(url):
  rtn = type(url) is str and url.lower().startswith('mailto:')
  return rtn

# ------------------------------------------------------------------------------
#  _zreferableitem.isInternalLink:
# ------------------------------------------------------------------------------
def isInternalLink(url):
  rtn = type(url) is str and url.startswith('{$') and url.endswith('}')
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
		'manage_RefForm', 'manage_browse_iframe',
		)
  __ac_permissions__=(
		('ZMS Author', __authorPermissions__),
		)

  # Management Interface.
  # ---------------------
  manage_RefForm = PageTemplateFile('zpt/ZMSLinkElement/manage_refform',globals())
  manage_browse_iframe = PageTemplateFile('zpt/ZMSLinkElement/manage_browse_iframe',globals()) 


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRelativeUrl:
  # ----------------------------------------------------------------------------
  def getRelativeUrl(self, path, url, sep='/'):
    ref = '.'
    SERVER_URL = self.REQUEST['SERVER_URL']
    currntPath = path
    if currntPath.startswith(SERVER_URL):
      currntPath = currntPath[len(SERVER_URL)+1:]
    elif currntPath.startswith(sep):
      currntPath = currntPath[1:]
    targetPath = url;
    if targetPath.startswith(SERVER_URL):
      targetPath = targetPath[len(SERVER_URL)+1:]
    elif targetPath.startswith(sep):
      targetPath = targetPath[1:]
    currntElmnts = currntPath.split(sep)
    targetElmnts = targetPath.split(sep)
    i = 0
    while i < len( currntElmnts) and \
          i < len( targetElmnts) and \
          currntElmnts[ i] == targetElmnts[ i]:
      i = i + 1
    currntElmnts = currntElmnts[ i:]
    targetElmnts = targetElmnts[ i:]
    for currntElmnt in currntElmnts:
      ref = ref + sep + '..'
    for targetElmnt in targetElmnts:
      ref = ref + sep + targetElmnt
    return ref


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRelObjPath:
  # ----------------------------------------------------------------------------
  def getRelObjPath(self, ob):
    ref = '.'
    currntElmnts = self.getVersionContainer().getPhysicalPath()
    targetElmnts = ob.getSelf( ).getPhysicalPath()
    i = 0
    while i < min(len( currntElmnts),len( targetElmnts)) and \
          currntElmnts[ i] == targetElmnts[ i]:
      i = i + 1
    currntElmnts = currntElmnts[ i:]
    targetElmnts = targetElmnts[ i:]
    ref += ''.join(map(lambda x: '/..',currntElmnts))
    ref += ''.join(map(lambda x: '/'+x,targetElmnts))
    return ref


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefObjPath:
  # ----------------------------------------------------------------------------
  def getRefObjPath(self, ob, anchor=''):
    ref = ''
    if ob is not None:
      ob_path = ob.breadcrumbs_obj_path()
      homeIds = map(lambda x:x.getHome().id,filter(lambda x:x.meta_id=='ZMS',ob_path))
      pathIds = map(lambda x:x.id,filter(lambda x:x.meta_id!='ZMS',ob_path))
      path = '/'.join(homeIds) + '@' + '/'.join(pathIds)
      ref = '{$' + path + anchor + '}'
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
    key = 'ref_by'
    if key in self.__dict__.keys():
      ref_by = getattr(self,key,[])
      ref_by = list(set(ref_by))
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
      if ob is not None and ob.meta_type.startswith('ZMS'):
        has_ref = False
        for key in ob.getObjAttrs().keys():
          obj_attr = ob.getObjAttr( key)
          if obj_attr['datatype_key'] in _globals.DT_STRINGS:
            for lang in self.getLangIds():
              req = {'lang':lang,'preview':'preview'}
              obj_vers = ob.getObjVersion(req)
              value = ob._getObjAttrValue(obj_attr,obj_vers,lang)
              svalue = ob.str_item(value)
              lvalue = []
              for exp in ['"(.*?)/%s"','{\$%s}','{\$(.*?)/%s}']:
                lvalue.extend( ob.re_search( exp%self.id, svalue))
              if len(lvalue) > 0 and obj_attr['datatype_key'] == _globals.DT_URL:
                has_ref = True
                new_value = ob.getRefObjPath(self)
                if value != new_value:
                  _objattrs.setobjattr(self, obj_vers, obj_attr, new_value, lang)
        if has_ref:
          ob_path = self.getRefObjPath(ob)
          if not ob_path in ref_by:
            ref_by.append(ob_path)
    ref_by = list(set(ref_by))
    ref_by.sort()
    if ref_by != v:
      setattr(self,key,ref_by)


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
    _globals.writeLog( self, "[registerRefObj]: %s(%s) - add %s"%(ob.id,ob.meta_type,ref))
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
    _globals.writeLog( self, "[unregisterRefObj]: %s(%s)"%(ob.id,ob.meta_type))
    ref_by = self.getRefByObjs(REQUEST)
    ref_by = filter( lambda x: x[2:-1].split('/')[-1]!=ob.id,ref_by)
    ##### Set Attribute ####
    setattr(self,'ref_by',ref_by)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.refreshRefObj:
  #
  #  Refreshs referencing object.
  # ----------------------------------------------------------------------------
  def refreshRefObj(self, ob, REQUEST):
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
    _globals.writeLog( self, '[synchronizeRefToObjs]')
    for key in self.getObjAttrs().keys():
      obj_attr = self.getObjAttr(key)
      datatype = obj_attr['datatype_key']
      if datatype == _globals.DT_URL:
        for lang in self.getLangIds():
          req = { 'lang':lang, 'preview':'preview'}
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
    _globals.writeLog( self, '[refreshRefToObj]: %s -> dest_obj=%s(%s)'%(self.id,dest_obj.absolute_url(),dest_obj.meta_type))
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
  #  ZReferableItem.validateInlineLinkObj:
  #
  #  Validates internal links.
  # ----------------------------------------------------------------------------
  def validateInlineLinkObj(self, text):
    if bool(self.getConfProperty('ZMS.InternalLinks.autocorrection',0)):
      p = '<a data-id="(.*?)" href="(.*?)">(.*?)<\\/a>'
      r = re.compile(p)
      for f in r.findall(text):
        old = (p.replace('\\','').replace('(.*?)','%s'))%tuple(f)
        data_id = f[0]
        href = f[1]
        title = f[2]
        ob = self.getLinkObj(url='{$%s}'%data_id)
        if ob is not None:
          new = (p.replace('\\','').replace('(.*?)','%s'))%(data_id,self.getRelObjPath(ob),title)
          if old != new:
            print old, new
            text = text.replace(old,new)
    return text


  # ----------------------------------------------------------------------------
  #  ZReferableItem.validateLinkObj:
  #
  #  Validates internal links.
  # ----------------------------------------------------------------------------
  def validateLinkObj(self, url):
    if bool(self.getConfProperty('ZMS.InternalLinks.autocorrection',0)) and url.startswith('{$') and not url.startswith('{$__'):
      ref_obj = self.getLinkObj(url)
      ref_anchor = ''
      if url.find('#') > 0:
        ref_anchor = url[url.find('#'):-1]
      if ref_obj is not None:
        # Repair link.
        url = self.getRefObjPath( ref_obj, ref_anchor)
      else:
        # Broken link.
        url = '{$__' + url[2:-1] + '__}'
    return url


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkObj:
  #
  #  Resolves internal/external links and returns Object.
  # ----------------------------------------------------------------------------
  def getLinkObj(self, url, REQUEST={}):
    ob = None
    if isInternalLink(url):
      _globals.writeBlock(self,'[getLinkObj]: url='+url) 
      # Extension Point
      ep = self.getConfProperty('ZReferableItem.getLinkObj','')
      if ep != '':
        ob = self.evalMetaobjAttr(ep,url=url)
      # Default
      elif not url.startswith('{$__'):
        # Find document-element.
        docElmnt = None
        path = url[2:-1]
        i = path.find('#')
        if i > 0:
          path = path[:i]
        i = path.find('@')
        if i > 0:
          clientIds = path[:i].split('/')
          path = path[i+1:]
          clientHome = self.getHome()
          for clientId in clientIds:
            clientHome = getattr(clientHome,clientId,None)
            if clientHome is None:
              break
          if clientHome is not None:
            obs = clientHome.objectValues(['ZMS'])
            if obs:
              docElmnt = obs[0]
        else:
          docElmnt = self.getDocumentElement()
        ob = docElmnt
        # Find object.
        if ob is not None and len(path) > 0:
          _globals.writeLog( self, '[getLinkObj]: path=%s'%path)
          ids = path.split( '/')
          for id in ids:
            ob = getattr(ob,id,None)
            if ob is None:
              if self.getConfProperty('ZMS.InternalLinks.autocorrection',0)==1:
                ob_id = self.getHome().id+'@'+ids[-1]
                _globals.writeBlock(self,'[getLinkObj]: ob_id='+ob_id) 
                ob = self.synchronizeRefs( ob_id)
              break
    return ob


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkUrl:
  #
  #  Resolves internal/external links and returns URL.
  # ----------------------------------------------------------------------------
  def getLinkUrl( self, url, REQUEST=None):
    REQUEST = _globals.nvl( REQUEST, self.REQUEST)
    if isInternalLink(url):
      ref_anchor = ''
      if url.find('#') > 0:
        ref_anchor = url[url.find('#'):-1]
      ob = self.getLinkObj(url,REQUEST)
      if ob is None:
        index_html = './index_%s.html?op=not_found&url=%s'%(REQUEST.get('lang',self.getPrimaryLanguage()),url)
      else:
        index_html = ob.getObjProperty('getHref2IndexHtml',REQUEST)
        if not index_html:
          index_html = ob.getHref2IndexHtmlInContext(self,REQUEST)
      return index_html + ref_anchor
    elif isMailLink (url): 
      prefix = 'mailto:'
      return prefix + self.encrypt_ordtype(url[len(prefix):])
    return url

  # ----------------------------------------------------------------------------
  #  ZReferableItem.tal_anchor:
  #  
  #  @param
  #  @return
  # ----------------------------------------------------------------------------
  def tal_anchor(self, href, target='', attrs={}, content=''):
    filtered_attrs_keys = filter(lambda x: len(x)>0, attrs.keys())
    str_attrs = ' '.join( map(lambda x:str(x)+'=\042'+str(attrs[x]+'\042'), filtered_attrs_keys) )
    return '<a href="%s" %s%s>%s</a>'%(href,['',' target="%s"'%target][int(len(target)>0)],str_attrs,content)

  # ----------------------------------------------------------------------------
  #  ZReferableItem.synchronizeRefs:
  #  
  #  @param
  #  @return
  # ----------------------------------------------------------------------------
  def synchronizeRefs( self, ob_id=None, clients=False, unify_ids=False):
    _globals.writeBlock(self,'[synchronizeRefs]')
    
    # Extend object-tree.
    def extendObjectTree(home, home_path):
      message = ''
      if home not in homes:
        homes.append( home)
        home_ob = self
        for home_id in home_path:
          if home_ob is not None:
            home_ob = getattr( home_ob, home_id, None)
        if home_ob is not None:
          t1 = time.time()
          map( lambda x: operator.setitem(obs, x.base_url(), x), _globals.objectTree( home_ob))
          message += '[INFO] Load object-tree for '+home+' (in '+str(int((time.time()-t1)*100.0)/100.0)+' secs.)<br/>'
        else:
          message += '[ERROR] Can\'t load object-tree for '+home+': not found!<br/>'
        _globals.writeBlock(self,'[synchronizeRefs]: '+message)
      return message
    
    # Handle internal references.
    def handleInternalRefs(k,v):
      message = ''
      sp = '{$'
      l = v.split(sp)
      if len(l) > 1:
        m = [l[0]]
        for i in l[1:]:
          ref = i[:i.find('}')]
          if ref.startswith('__') and ref.endswith('__'):
            ref = ref[2:-2]
          if len( ref.split('@')) == 1:
            home_path = [ob.getHome().id]
            home = home_path[-1]
          else:
            home_path = ref.split('@')[0].split('/')
            home = home_path[-1]
          id = ref.split('@')[-1].split('/')[-1]
          if len( id) == 0:
            id = 'content'
          
          # Extend object-tree.
          message += extendObjectTree(home, home_path)
          
          f = filter( lambda x: x.find('/%s/content'%home) >= 0 and x.endswith('/%s'%id), obs.keys())
          if len( f) == 0:
            ref = '__%s__'%ref
          else:
            if len( f) > 1:
              if ref.find('@') > 0:
                ref = ref[ ref.find('@')+1:]
              g = filter( lambda x: x.find('/%s/content'%home) >= 0 and x.endswith('/%s'%ref), obs.keys())
              if len( g) == 1:
                f = g
              else:
                message += '[WARNING] %s: Ambigous reference ref=%s in f=%s'%(ob.absolute_url(),ref,str(f))
            else:
              target = obs[f[0]]
              ref = ob.getRefObjPath( target)[2:-1]
              if ob.version_live_id == obj_vers.id:
                target_ref = target.getRefObjPath( ob)
                target_ref_by = getattr( target, 'ref_by', [])
                if target_ref not in target_ref_by:
                  setattr( target, 'ref_by', target_ref_by + [ target_ref])
          if ref.startswith('__') and ref.endswith('__'):
            message += '<a href="%s/manage_main" target="_blank">%s(%s)%s=%s</a><br/>'%(ob.absolute_url(),ob.absolute_url(),ob.meta_type,k,ref)
          m.append(ref+i[i.find('}'):])
        v = sp.join(m)
      return v, message
    
    # Handle relative references.
    def handleRelativeRefs(k,v):
      message = ''
      for sp in ['href="./','src="./']:
        l = v.split(sp)
        if len(l) > 1:
          m = [l[0]]
          for i in l[1:]:
            if i.find('"') > 0:
              ref = i[:i.find('"')]
              if ref.endswith('/'):
                ref = ref[:-1]
              decl_id = ref.split('/')[-1]
              if getattr(ob.getHome(),decl_id,None) is None: # must not exist as Zope resource
                filtered_did = filter(lambda x: x['decl_id']==decl_id,did)
                if len(filtered_did) == 1: # simplest case: decl_id is unique!
                  found = filtered_did[0]
                  req = REQUEST={'lang':found['lang']}
                  target_url = found['abs_url']
                  target_ref = obs[target_url].getDeclUrl(REQUEST=req)
                  ob_ref = ob.getSelf(ob.PAGES).getDeclUrl(REQUEST=req)
                  ref = self.getRelativeUrl(ob_ref,target_ref)
                  i = ref + i[i.find('"'):]
            m.append(i)
          v = sp.join(m)
      return v, message
    
    # Initialize.
    message = ''
    t0 = time.time()
    obs = {}
    clients = clients or (not self.getPortalMaster() and not self.getPortalClients())
    
    # Initialize object-tree.
    map( lambda x: operator.setitem(obs, x.base_url(), x), _globals.objectTree( self, clients))
    homes = obs.keys()
    homes = map( lambda x: x[:x.find('/content')], homes)
    homes = map( lambda x: x[x.rfind('/')+1:], homes)
    homes = dict.fromkeys(homes).keys()
    message += 'Load object-tree ['+str(len(obs.keys()))+ '] for '+str(homes)+' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)<br/>'
    _globals.writeBlock(self,'[synchronizeRefs]: '+message)
    
    abs_urls = obs.keys()
    abs_urls.sort()
    
    did = []
    if self.getConfProperty('ZMS.pathhandler',0) != 0:
      for x in obs.keys():
        ob = obs[x]
        for lang in self.getLangIds():
          did.append({'decl_id':ob.getDeclId(REQUEST={'lang':lang}),'lang':lang,'abs_url':x})
    
    # Unify object-ids.
    if unify_ids:
      did = {}
      map( lambda x: operator.setitem( did, x.id, did.get(x.id,0)+1), obs.values())
      for id in filter( lambda x: did.get(x) > 1 and x[-1] in ['0','1','2','3','4','5','6','7','8','9'], did.keys()):
        prefix = None
        keys = map( lambda x: (x.find('/content'),x), filter( lambda x: x.endswith('/'+id), obs.keys()))
        keys.sort()
        keys = map( lambda x: x[1], keys)
        for key in keys:
          ob = obs[key]
          if prefix is None:
            prefix = _globals.id_prefix( id)
            message += '[INFO] %s: Keep unique object-id \'%s\'<br/>'%(key,id)
          else:
            new_id = self.getNewId(prefix)
            try:
              ob.getParentNode().manage_renameObject( id=id, new_id=new_id)
              obs[ ob.base_url()] = ob
              message += '[INFO] %s: Rename to unique object-id \'%s\'<br/>'%(key,new_id)
            except:
              message += _globals.writeError( ob, '%s: Can\'t rename to unique object-id \'%s\'<br/>'%(key,new_id))
    
    # Clear 'ref_by' (reference-by) attributes.
    for x in filter( lambda x: hasattr( obs[x], 'ref_by'), abs_urls):
      if clients or True:
        try:
          setattr( obs[x], 'ref_by', [])
        except: pass
      else:
        try:
          ref_by = getattr( obs[x], 'ref_by')
          ref_by = filter( lambda x: x.find('@')<0, ref_by)
          setattr( obs[x], 'ref_by', ref_by)
        except: pass
    
    langs = self.getLangIds()
    for abs_url in abs_urls:
      ob = obs[ abs_url]
      
      # Process recordset.
      if ob.meta_id!='ZMSLinkElement' and ob.getType()=='ZMSRecordSet':
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
                  v, m = handleInternalRefs('%s.%s[%i]'%(key,k,c),v)
                  message += m
                  v, m = handleRelativeRefs('%s.%s[%i]'%(key,k,c),v)
                  message += m
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
                  v, m = handleInternalRefs(key,v)
                  message += m
                  v, m = handleRelativeRefs(key,v)
                  message += m
                  if v != o:
                    _objattrs.setobjattr(ob,obj_vers,obj_attr,v,lang)
    
    message += ' (in '+str(int((time.time()-t0)*100.0)/100.0)+' secs.)'
    _globals.writeBlock(self,'[synchronizeRefs]: '+message)
    
    # Return with desired object.
    if ob_id is not None:
      if type( ob_id) is str:
        home = ob_id.split('@')[0]
        id = ob_id.split('@')[1]
        f = filter( lambda x: x.find('/%s/content'%home) > 0 and x.endswith('/%s'%id), abs_urls)
        if len( f) > 0:
          return obs[f[0]]
      return None
    
    # Return with message.
    else:
      return message

################################################################################
