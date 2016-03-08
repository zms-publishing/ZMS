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
#  isMailLink:
# ------------------------------------------------------------------------------
def isMailLink(url):
  rtn = type(url) is str and url.lower().startswith('mailto:')
  return rtn

# ------------------------------------------------------------------------------
#  isInternalLink:
# ------------------------------------------------------------------------------
def isInternalLink(url):
  rtn = type(url) is str and url.startswith('{$') and url.endswith('}')
  return rtn

# ----------------------------------------------------------------------------
#  getInlineRefs:
#
#  Parses internal links.
# ----------------------------------------------------------------------------
def getInlineRefs(text):
  l = []
  p = '<a(.*?)>(.*?)<\\/a>'
  r = re.compile(p)
  for f in r.findall(str(text)):
    d = dict(re.findall('\\s(.*?)="(.*?)"',f[0]))
    if d.has_key('data-id'):
      l.append(d['data-id'])
  return l

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
  def getRelativeUrl(self, path, url):
    import urlparse
    import posixpath
    u_dest = urlparse.urlsplit(url)
    u_src = urlparse.urlsplit(path)
    _uc1 = urlparse.urlunsplit(u_dest[:2]+tuple('' for i in range(3)))
    _uc2 = urlparse.urlunsplit(u_src[:2]+tuple('' for i in range(3)))
    if _uc1 != _uc2:
        ## This is a different domain
        return url
    _relpath = posixpath.relpath(u_dest.path, posixpath.dirname(u_src.path))
    return './%s'%urlparse.urlunsplit(('', '', _relpath, u_dest.query, u_dest.fragment))

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefObjPath:
  # ----------------------------------------------------------------------------
  def getRefObjPath(self, ob, anchor=''):
    ref = ''
    if ob is not None:
      def default(*args, **kwargs):
        self = args[0]
        ob = args[1]['ob']
        anchor = args[1]['anchor']
        ob_path = ob.breadcrumbs_obj_path()
        homeIds = map(lambda x:x.getHome().id,filter(lambda x:x.meta_id=='ZMS',ob_path))
        pathIds = map(lambda x:x.id,filter(lambda x:x.meta_id!='ZMS',ob_path))
        path = '/'.join(homeIds) + '@' + '/'.join(pathIds)
        return '{$' + path + anchor + '}'
      ref = self.evalExtensionPoint('ExtensionPoint.ZReferableItem.getRefObjPath',default,ob=ob,anchor=anchor)
    return ref


  """
  ##############################################################################
  ###  
  ###  References FROM other objects.
  ### 
  ##############################################################################
  """

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefByObjs:
  #
  #  Returns references FROM other objects.
  # ----------------------------------------------------------------------------
  def getRefByObjs(self, REQUEST=None):
    ref_by = []
    if 'ref_by' in self.__dict__.keys():
      ref_by = self.ref_by
      ref_by = list(set(ref_by))
    return ref_by


  # ----------------------------------------------------------------------------
  #  ZReferableItem.synchronizeRefByObjs:
  #
  #  Synchronizes references FROM other objects.
  # ----------------------------------------------------------------------------
  def synchronizeRefByObjs(self, strict=1):
    v = self.getRefByObjs()
    ref_by = []
    for i in v:
      ob = self.getLinkObj(i)
      if ob is not None:
        for ref_to in ob.getRefToObjs():
          ref_ob = self.getLinkObj(ref_to)
          if self == ref_ob:
            ref = self.getRefObjPath(ob)
            ref_by.append(ref)
            break
    ref_by = list(set(ref_by))
    ref_by.sort()
    if ref_by != v:
      self.ref_by = ref_by
    return ref_by


  # ----------------------------------------------------------------------------
  #  ZReferableItem.registerRefObj:
  #
  #  Registers reference FROM other object.
  # ----------------------------------------------------------------------------
  def registerRefObj(self, ob):
    ref = self.getRefObjPath(ob)
    _globals.writeLog(self,'[registerRefObj]: ref='+ref)
    ref_by = self.synchronizeRefByObjs()
    if ref not in ref_by:
      ref_by.append(ref)
      self.ref_by = ref_by


  # ----------------------------------------------------------------------------
  #  ZReferableItem.unregisterRefObj:
  #
  #  Unregisters reference FROM other object.
  # ----------------------------------------------------------------------------
  def unregisterRefObj(self, ob):
    ref = self.getRefObjPath(ob)
    _globals.writeLog(self,'[unregisterRefObj]: ref='+ref)
    ref_by = self.synchronizeRefByObjs()
    if ref in ref_by:
      ref_by = filter( lambda x: x!=ref,ref_by)
      self.ref_by = ref_by


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
  def getRefToObjs(self):
    d = {}
    for key in self.getObjAttrs().keys():
      objAttr = self.getObjAttr(key)
      datatype = objAttr['datatype']
      if datatype in ['richtext','string','text','url']:
        lang_suffixes = ['']
        if objAttr['multilang']:
          lang_suffixes = map(lambda x:'_%s'%x,self.getLangIds())
        for lang_suffix in lang_suffixes:
          for obj_vers in self.getObjVersions():
            v = getattr(obj_vers,'%s%s'%(key,lang_suffix),None)
            if v is not None:
              if datatype in ['richtext','string','text']:
                for iv in getInlineRefs(str(v)):
                  ref_ob = self.getLinkObj(iv)
                  if ref_ob is not None:
                    ref = self.getRefObjPath(ref_ob)
                    d[ref] = 1
              elif datatype in ['url']:
                ref_ob = self.getLinkObj(v)
                if ref_ob is not None:
                  ref = self.getRefObjPath(ref_ob)
                  d[ref] = 1
    return d.keys()


  # ----------------------------------------------------------------------------
  #  ZReferableItem.prepareRefreshRefToObjs:
  #
  #  Prepare refresh of references TO other objects.
  # ----------------------------------------------------------------------------
  def prepareRefreshRefToObjs(self):
    _globals.writeBlock( self, '[prepareRefreshRefToObjs]')
    if 'ref_to' not in self.__dict__.keys():
      self.ref_to = self.getRefToObjs()


  # ----------------------------------------------------------------------------
  #  ZReferableItem.refreshRefToObjs:
  #
  #  Synchronizes references TO other objects.
  # ----------------------------------------------------------------------------
  def refreshRefToObjs(self):
    _globals.writeBlock( self, '[refreshRefToObjs]')
    if 'ref_to' in self.__dict__.keys():
      old_ref_to = self.ref_to
      _globals.writeBlock( self, '[refreshRefToObjs]: old=%s'%str(old_ref_to))
      new_ref_to = self.getRefToObjs()
      _globals.writeBlock( self, '[refreshRefToObjs] new=%s'%str(old_ref_to))
      delattr(self,'ref_to')
      for ref in old_ref_to:
        ref_ob = self.getLinkObj(ref)
        if ref_ob is not None:
          self_ref = ref_ob.getRefObjPath(self)
          if ref not in new_ref_to and self_ref in ref_ob.synchronizeRefByObjs():
            ref_ob.unregisterRefObj(self)
      for ref in new_ref_to:
        ref_ob = self.getLinkObj(ref)
        if ref_ob is not None:
          self_ref = ref_ob.getRefObjPath(self)
          if ref not in old_ref_to or self_ref not in ref_ob.synchronizeRefByObjs():
            ref_ob.registerRefObj(self)


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
    for pq in [('<a(.*?)>','href'),('<img(.*?)>','src')]:
      p = pq[0]
      q = pq[1]
      r = re.compile(p)
      for f in r.findall(str(text)):
        d = dict(re.findall('\\s(.*?)="(.*?)"',f))
        if d.has_key('data-id'):
          old = p.replace('(.*?)',f)
          url = d['data-id']
          ob = self.getLinkObj(url)
          if ob is not None:
            REQUEST = self.REQUEST
            d[q] = self.getLinkUrl(url)
            if not ob.isActive(REQUEST):
              d['data-target'] = "inactive"
            elif self.getTrashcan().isAncestor(ob):
              d['data-target'] = 'trashcan'
          else:
            d['data-target'] = "missing"
          new = p.replace('(.*?)',' '.join(['']+map(lambda x:'%s="%s"'%(x,d[x]),d.keys())))
          if old != new:
            text = text.replace(old,new)
    return text


  # ----------------------------------------------------------------------------
  #  ZReferableItem.validateLinkObj:
  #
  #  Validates internal links.
  # ----------------------------------------------------------------------------
  def validateLinkObj(self, url):
    if isInternalLink(url):
      if not url.startswith('{$__'):
        # Params.
        ref_params = ''
        if url.find(';') > 0:
          ref_params = url[url.find(';'):-1]
          url = '{$%s}'%url[2:url.find(';')]
        ref_obj = self.getLinkObj(url)
        # Anchor.
        ref_anchor = ''
        if url.find('#') > 0:
          ref_anchor = url[url.find('#'):-1]
        if ref_obj is not None:
          # Repair link.
          url = '{$%s%s}'%(self.getRefObjPath( ref_obj, ref_anchor)[2:-1],ref_params)
        else:
          # Broken link.
          url = '{$__' + url[2:-1] + '__}'
    return url


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkObj:
  #
  #  Resolves internal/external links and returns Object.
  # ----------------------------------------------------------------------------
  def getLinkObj(self, url, REQUEST=None):
    ob = None
    if isInternalLink(url):
      def default(*args, **kwargs):
        self = args[0]
        url = args[1]['url']
        ob = None
        if not url.startswith('{$__'):
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
            ids = path.split( '/')
            for id in ids:
              ob = getattr(ob,id,None)
              if ob is None:
                break
        return ob
      # Params.
      ref_params = {}
      if url.find(';') > 0:
        ref_params = dict(re.findall(';(\w*)=(\w*)',url[url.find(';'):-1]))
        url = '{$%s}'%url[2:url.find(';')]
      # Get object.
      ob = self.evalExtensionPoint('ExtensionPoint.ZReferableItem.getLinkObj',default,url=url)
      # Prepare request
      if ob is not None:
        request = self.REQUEST
        ob.set_request_context(request,ref_params)
    return ob


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkUrl:
  #
  #  Resolves internal/external links and returns URL.
  # ----------------------------------------------------------------------------
  def getLinkUrl( self, url, REQUEST=None):
    REQUEST = _globals.nvl( REQUEST, self.REQUEST)
    if isInternalLink(url):
      # Params.
      ref_params = {}
      if url.find(';') > 0:
        ref_params = dict(re.findall(';(\w*)=(\w*)',url[url.find(';'):-1]))
        url = '{$%s}'%url[2:url.find(';')]
      # Anchor.
      ref_anchor = ''
      if url.find('#') > 0:
        ref_anchor = url[url.find('#'):-1]
      # Prepare request.
      bak_params = {}
      for key in ref_params.keys():
        bak_params[key] = REQUEST.get(key,None)
        REQUEST.set(key,ref_params[key])
      # Get index_html.
      ob = self.getLinkObj(url,REQUEST)
      if ob is None:
        index_html = './index_%s.html?op=not_found&url=%s'%(REQUEST.get('lang',self.getPrimaryLanguage()),url)
      else:
        index_html = ob.getObjProperty('getHref2IndexHtml',REQUEST)
        if not index_html:
          index_html = ob.getHref2IndexHtml(REQUEST)
        context = REQUEST.get('ZMS_THIS',self)
        index_html = ob.getHref2IndexHtmlInContext(context,index_html,REQUEST)
      # Unprepare request.
      for key in bak_params.keys():
        REQUEST.set(key,bak_params[key])
      # Return index_html.
      return index_html + ref_anchor
    elif isMailLink (url): 
      prefix = 'mailto:'
      return prefix + self.encrypt_ordtype(url[len(prefix):])
    return url

  # ----------------------------------------------------------------------------
  #  ZReferableItem.tal_anchor:
  #  
  #  @param href
  #  @param target
  #  @param attrs
  #  @param content
  #  @return
  # ----------------------------------------------------------------------------
  def tal_anchor(self, href, target='', attrs={}, content=''):
    filtered_attrs_keys = filter(lambda x: len(x)>0, attrs.keys())
    str_attrs = ' '.join( map(lambda x:str(x)+'=\042'+str(attrs[x]+'\042'), filtered_attrs_keys) )
    return '<a href="%s" %s %s>%s</a>'%(href,['',' target="%s"'%target][int(len(target)>0)],str_attrs,content)

################################################################################
