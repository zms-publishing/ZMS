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
  p = '<a (.*?)href="(.*?)"(.*?)>(.*?)<\\/a>'
  r = re.compile(p)
  for f in r.findall(text):
    ref = None
    attr = f[0]+f[2]
    if attr.find('data-id=') >= 0:
      data_id = attr[attr.find('data-id='):]
      data_id = data_id[data_id.find('"')+1:]
      data_id = data_id[:data_id.find('"')]
      l.append('{$%s}'%data_id)
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
  def getRefByObjs(self):
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
                for iv in getInlineRefs(v):
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
    p = '<a (.*?)data-id="(.*?)"(.*?)>(.*?)<\\/a>'
    r = re.compile(p)
    for f in r.findall(text):
      data_id = f[1]
      d0 = dict(re.findall('(\\w*?)="(.*?)"',f[0]))
      d1 = dict(re.findall('(\\w*?)="(.*?)"',f[2]))
      d = dict(d0,**d1)
      old = (p.replace('\\','').replace('(.*?)','%s'))%tuple(f)
      href = self.getLinkUrl(url='{$%s}'%data_id)
      d['data-id'] = data_id
      d['href'] = href
      title = f[3]
      new = '<a %s>%s</a>'%(' '.join(map(lambda x:'%s="%s"'%(x,d[x]),d.keys())),title)
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
      ob = self.evalExtensionPoint('ExtensionPoint.ZReferableItem.getLinkObj',default,url=url)
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
