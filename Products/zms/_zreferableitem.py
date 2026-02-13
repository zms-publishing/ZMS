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
import base64
import re
# Product Imports.
from Products.zms import standard
from zope.globalrequest import getRequest
# FOR DEBUGGING PURPOSES ONLY: import traceback to log the call stack of getLinkObj calls
import traceback


# ------------------------------------------------------------------------------
#  isMailLink:
# ------------------------------------------------------------------------------
def isMailLink(url):
  rtn = isinstance(url, str) and url.lower().startswith('mailto:')
  return rtn

# ------------------------------------------------------------------------------
#  isInternalLink:
# ------------------------------------------------------------------------------
def isInternalLink(url):
  rtn = isinstance(url, str) and url.startswith('{$') and url.endswith('}')
  return rtn

# ------------------------------------------------------------------------------
#  getInternalLinkDict:
# ------------------------------------------------------------------------------
def getInternalLinkDict(self, url):
  #-- [ReqBuff]: Fetch buffered value from Http-Request.
  docelmnt = self.getDocumentElement()
  reqBuffId = 'getInternalLinkDict.%s'%url
  try: return docelmnt.fetchReqBuff(reqBuffId)
  except: pass
  request = getattr(self, 'REQUEST', getRequest())
  d = {}
  # Params.
  anchor = ''
  ref_params = {}
  if url.find(';') > 0:
    anchor = url[url.find(';'):-1]
    ref_params = dict(re.findall(r';(\w*)=(\w*)', anchor))
    url = '{$%s}'%url[2:url.find(';')]
  # Anchor.
  ref_anchor = ''
  if url.find('#') > 0:
    ref_anchor = url[url.find('#'):-1]
  # Get index_html.
  ref_obj = self.getLinkObj(url)
  if ref_obj is not None:
    # Prepare request.
    bak_params = {}
    for key in ref_params:
      bak_params[key] = request.get(key, None)
      request.set(key, ref_params[key])
    url = '{$%s%s}'%(self.getRefObjPath( ref_obj)[2:-1], anchor)
    d['data-id'] = url
    d['data-url'] = getInternalLinkUrl(self, url, ref_obj)
    if not ref_obj.isActive(request):
      d['data-target'] = "inactive"
    elif self.getTrashcan().isAncestor(ref_obj):
      d['data-target'] = 'trashcan'
    # Unprepare request.
    for key in bak_params:
      request.set(key, bak_params[key])
  else:
    d['data-id'] = "{$__%s__}"%url[2:-1]
    d['data-target'] = "missing"
  #-- [ReqBuff]: Returns value and stores it in buffer of Http-Request.
  return docelmnt.storeReqBuff( reqBuffId, d)

# ------------------------------------------------------------------------------
#  getInternalLinkUrl:
# ------------------------------------------------------------------------------
def getInternalLinkUrl(self, url, ob):
  request = getattr(self, 'REQUEST', getRequest())
  if ob is None:
    index_html = './index_%s.html?error_type=NotFound&op=not_found&url=%s'%(request.get('lang', self.getPrimaryLanguage()), str(url))
  else:
    # Contextualized index_html.
    context = request.get('ZMS_THIS', self)
    index_html = ob.getHref2IndexHtmlInContext(context, REQUEST=request)
  return index_html

# ----------------------------------------------------------------------------
#  getInlineRefs:
#
#  Parses internal links.
# ----------------------------------------------------------------------------
def getInlineRefs(text):
  l = []
  p = r'<a(.*?)>(.*?)</a>'
  r = re.compile(p)
  for f in r.findall(str(text)):
    d = dict(re.findall(r'\s(.*?)="(.*?)"', f[0]))
    if 'data-id' in d:
      l.append(d['data-id'])
  return l

################################################################################
################################################################################
###
###   class ZReferableItem
###
################################################################################
################################################################################
class ZReferableItem(object): 

  # Management Permissions.
  # -----------------------
  __authorPermissions__ = (
    'manage_RefForm', 'manage_browse_iframe',
  )
  __administratorPermissions__ = (
    'manage_change_refs',
  )
  __ac_permissions__=(
    ('ZMS Author', __authorPermissions__),
    ('ZMS Administrator', __administratorPermissions__),
  )

  # Management Interface.
  # ---------------------
  manage_RefForm = PageTemplateFile('zpt/ZMSLinkElement/manage_refform', globals())
  manage_browse_iframe = PageTemplateFile('zpt/ZMSLinkElement/manage_browse_iframe', globals())
  manage_change_refs = PageTemplateFile('zpt/ZMSLinkElement/manage_changeRefsToObj', globals())


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRelativeUrl:
  # ----------------------------------------------------------------------------
  def getRelativeUrl(self, path, url):
    import posixpath
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
    u_dest = urlsplit(url)
    u_src = urlsplit(path)
    _uc1 = urlunsplit(u_dest[:2]+tuple('' for i in range(3)))
    _uc2 = urlunsplit(u_src[:2]+tuple('' for i in range(3)))
    if _uc1 != _uc2:
        ## This is a different domain
        return url
    _relpath = posixpath.relpath(u_dest.path, posixpath.dirname(u_src.path))
    return './%s'%urlunsplit(('', '', _relpath, u_dest.query, u_dest.fragment))

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getRefObjPath:
  # ----------------------------------------------------------------------------
  def getRefObjPath(self, ob, anchor=''):
    ref = ob.get_uid()
    if anchor:
      ref += '#'+anchor
    return '{$%s}'%ref


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
    if 'ref_by' in self.__dict__:
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
    ref_by = sorted(set(ref_by))
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
    standard.writeLog(self, '[registerRefObj]: ref='+ref)
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
    standard.writeLog(self, '[unregisterRefObj]: ref='+ref)
    ref_by = self.synchronizeRefByObjs()
    if ref in ref_by:
      ref_by = [x for x in ref_by if x!=ref]
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
    for key in self.getObjAttrs():
      objAttr = self.getObjAttr(key)
      datatype = objAttr['datatype']
      if datatype in ['richtext', 'string', 'text', 'url']:
        lang_suffixes = ['']
        if objAttr['multilang']:
          lang_suffixes = ['_%s'%x for x in self.getLangIds()]
        for lang_suffix in lang_suffixes:
          for obj_vers in self.getObjVersions():
            v = getattr(obj_vers, '%s%s'%(key, lang_suffix), None)
            if v is not None:
              if datatype in ['richtext', 'string', 'text']:
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
    return list(set(d))


  # ----------------------------------------------------------------------------
  # ZReferableItem.changeRefsToObj:
  #
  # Change all internal references to a new target object.
  # @param ref_to: The target object to which all references should point
  # @return: Dictionary with counts of changed references
  # ----------------------------------------------------------------------------
  def changeRefsToObj(self, ref_to):
    standard.writeLog(self, '[changeRefToObjs]')
    result = {'changed': [], 'unchanged': [], 'ref_to': None}
    request = self.REQUEST
    req_lang = request.get('lang', self.getPrimaryLanguage())
    # Get the link of the current object
    this_ref = str(self.getRefObjPath(self))
    # Get selected references to change
    # refByObjs = self.getRefByObjs() # from object
    if 'refByObjs' in request.form: # from form
      refByObjs = request.form.get('refByObjs', [])
      if isinstance(refByObjs, str):
        refByObjs = [refByObjs]
    if not refByObjs or not ref_to:
      # Break if there are no references or the target object is not specified
      standard.writeLog(self, '[changeRefsToObj] No references or target object specified.')
      return None
    else:
      result['ref_to'] = '%s/manage_RefForm'%(self.getLinkObj(ref_to).absolute_url())

    for ref in refByObjs:
      ref_obj = self.getLinkObj(ref,request)
      if ref_obj is not None:
        ref_ob_changed = False
        # Find the attribute that is linking to the current object
        for key in [k for k in list(ref_obj.getObjAttrs()) if ref_obj.getObjAttrs()[k]['datatype'] in ['richtext', 'string', 'text', 'url']]:
          objAttr = ref_obj.getObjAttr(key)
          datatype = objAttr['datatype']
          langs = list(objAttr.get('multilang') and self.getLangs().keys() or [self.getPrimaryLanguage()])
          for lang in langs:
            request.set('lang', lang)
            if datatype in ['richtext', 'string', 'text']:
              # Reset obsolete ZMSLinkElement.ref_lang attribute if exists
              if ref_obj.meta_id == 'ZMSLinkElement' and key=='ref_lang':
                ref_obj.attr('ref_lang', None)
                continue
              # Get the value of the attribute
              v = ref_obj.attr(key)
              if v is not None and isinstance(v, str):
                if str(this_ref[:-1]) in str(v):
                  try:
                    ref_obj.setObjStateModified(request)
                    ref_obj.attr(key,str(v).replace(this_ref, ref_to))
                    # Register the new reference at the target object
                    ref_to_ob = self.getLinkObj(ref_to)
                    if ref_to_ob is not None:
                      ref_to_ob.registerRefObj(ref_obj)
                    if not ref_ob_changed:
                      result['changed'].append(ref)
                      # Register the language change
                      ref_ob_changed = True
                  except Exception as e:
                    # Handle the exception if the replacement fails
                    standard.writeLog(self, '[changeRefsToObj] Error: %s'%str(e))
                    result['unchanged'].append(ref)
            elif datatype in ['url']:
              v = ref_obj.attr(key)
              if v is not None:
                if str(this_ref[:-1]) in str(v):
                  try:
                    ref_obj.setObjStateModified(request)
                    ref_obj.attr(key, ref_to)
                    # Register the new reference at the target object
                    ref_to_ob = self.getLinkObj(ref_to)
                    if ref_to_ob is not None:
                      ref_to_ob.registerRefObj(ref_obj)
                    if not ref_ob_changed:
                      result['changed'].append(ref)
                      # Register the language change
                      ref_ob_changed = True
                  except Exception as e:
                    # Handle the exception if the replacement fails
                    standard.writeLog(self, '[changeRefsToObj] Error: %s'%str(e))
                    result['unchanged'].append(ref)
          # Reset the request-language
          request.set('lang', req_lang)
        # If any url in the object has changed, trigger onChangeObj
        if ref_ob_changed:
          ref_obj.onChangeObj(request,forced=True)
          # If Workflow is active and reference object is part of a page-container:
          if not self.getAutocommit() and not ref_obj.isPage():
            ref_obj_page = [ ob for ob in ref_obj.breadcrumbs_obj_path() if ob.isPage() ][-1]
            ref_obj_page.setObjStateModified(request)
            ref_obj_page.onChangeObj(request,forced=True)
    return result

  # ----------------------------------------------------------------------------
  #  ZReferableItem.prepareRefreshRefToObjs:
  #
  #  Prepare refresh of references TO other objects.
  # ----------------------------------------------------------------------------
  def prepareRefreshRefToObjs(self):
    standard.writeLog( self, '[prepareRefreshRefToObjs]')
    if 'ref_to' not in self.__dict__:
      self.ref_to = self.getRefToObjs()


  # ----------------------------------------------------------------------------
  #  ZReferableItem.refreshRefToObjs:
  #
  #  Synchronizes references TO other objects.
  # ----------------------------------------------------------------------------
  def refreshRefToObjs(self):
    standard.writeLog( self, '[refreshRefToObjs]')
    if 'ref_to' in self.__dict__:
      old_ref_to = self.ref_to
      standard.writeLog( self, '[refreshRefToObjs]: old=%s'%str(old_ref_to))
      new_ref_to = self.getRefToObjs()
      standard.writeLog( self, '[refreshRefToObjs] new=%s'%str(old_ref_to))
      delattr(self, 'ref_to')
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
    if not bool(self.getConfProperty('ZReferableItem.validateInlineLinkObj', 1)): return text
    for pq in [('<a(.*?)>', 'href'), ('<img(.*?)>', 'src')]:
      p = pq[0]
      q = pq[1]
      r = re.compile(p)
      for f in r.findall(str(text)):
        d = dict(re.findall(r'\s(.*?)="(.*?)"', f))
        if 'data-id' in d:
          old = p.replace('(.*?)', f)
          url = d['data-id']
          ild = getInternalLinkDict(self, url)
          for k in ild:
            d[{'data-url':q}.get(k, k)] = ild[k]
          new = p.replace('(.*?)', ' '.join(['']+['%s="%s"'%(x,d[x]) for x in d]))
          if old != new:
            # @FIXME UnicodeDecodeError: 'ascii' codec can't decode byte 0x## in position ###: ordinal not in range(128)
            text = text.replace(old, new)
    return text

  # ----------------------------------------------------------------------------
  #  ZReferableItem.validateLinkObj:
  #
  #  Validates internal links.
  # ----------------------------------------------------------------------------
  def validateLinkObj(self, url):
    if not bool(self.getConfProperty('ZReferableItem.validateLinkObj', 1)): return url
    if isInternalLink(url):
      if not url.startswith('{$__'):
        ild = getInternalLinkDict(self, url)
        url = ild['data-id']
    return url

  # ----------------------------------------------------------------------------
  # Validates internal object-references.
  #
  # @param s: String to validate
  # ----------------------------------------------------------------------------
  def validateRefObj(self, s):
    if isInternalLink(s):
      return self.validateLinkObj(s)
    return self.validateInlineLinkObj(s)


  # ----------------------------------------------------------------------------
  #  ZReferableItem.findObject:
  #
  #  Find object.
  #  Fast access to object of what we know that it must exist,
  #  since we have just calculated the url a short period before.
  # ----------------------------------------------------------------------------
  def findObject(self, url):
    url = url[2:-1]
    if url.find('id:') >= 0:
      catalog = self.getZMSIndex().get_catalog()
      q = catalog({'get_uid':url})
      for r in q:
        path  = '%s/'%r['getPath']
        break
    else:
      path = url.replace('@','/content/')
    ob = self
    l = [x for x in path.split('/') if x] 
    for id in l:
      ob = getattr(ob,id,None)
    return ob

  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkObj:
  #
  #  Resolves internal/external links and returns Object.
  # ----------------------------------------------------------------------------
  def getLinkObj(self, url, REQUEST=None):
    request = getattr(self, 'REQUEST', getRequest())
    was_buffered = True
    ob = None
    if isInternalLink(url):
      # Params.
      ref_params = {}
      if url.find(';') > 0:
        ref_params = dict(re.findall(r';(\w*)=(\w*)', url[url.find(';'):-1]))
        url = '{$%s}'%url[2:url.find(';')]
      # Get object.
      if url.startswith('{$') and url.endswith('}'):
        url = url[2:-1]
        # Strip suffixes
        i = max(url.find('#'),url.find(','))
        if i > 0:
          url = url[:i]
        #-- [ReqBuff]: Fetch buffered value from Http-Request.
        reqBuffId = 'getLinkObj.%s'%url
        try:
          ob = self.getDocumentElement().fetchReqBuff(reqBuffId)
        except:
          was_buffered = False
          if url.find('id:') >= 0:
            catalog = self.getZMSIndex().get_catalog()
            q = catalog({'get_uid':url})
            for r in q:
              path  = '%s/'%r['getPath']
              l = [x for x in path.split('/') if x] 
              ob = self.getRootElement()
              if l:
                [l.pop(0) for x in ob.getPhysicalPath() if l[0] == x]
                for id in l:
                  ob = getattr(ob,id,None)
              break
          elif not url.startswith('__'):
            path = url.replace('@','/content/')
            l = [x for x in path.split('/') if x] 
            ob = self.getDocumentElement()
            if l:
              [l.pop(0) for x in ob.getPhysicalPath() if l[0] == x]
              for id in l:
                ob = getattr(ob,id,None)
          #-- [ReqBuff]: Store value in buffer of Http-Request.
          self.getDocumentElement().storeReqBuff(reqBuffId, ob)
      # Prepare request (only if ref_params are provided)
      if ob is not None and ref_params:
        ids = self.getPhysicalPath()
        if ob.id not in ids:
          ob.set_request_context(request, ref_params)
      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      # DEBUG: logging/counting getLinkObj calls
      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      request.set('getLinkObj_counter', request.get('getLinkObj_counter', 0) + 1)
      # show traceback in debugging output to identify which function is  calling getLinkObj and causing multiple calls
      traceback_stack = []
      for frame in reversed(traceback.extract_stack()[-5:-2]):
        traceback_stack.append('%s:%s:%s' % (str(frame.filename).split('/')[-1], frame.lineno, frame.name))
      request.set('count_buffered_getLinkObj_calls', request.get('count_buffered_getLinkObj_calls', 0) + int(was_buffered))
      standard.writeStdout(self, '%d. [%s:getLinkObj] %s, Target-ID=%s (%s), URL=%s, was_buffered=%s (%s), ref_params=%s\n...was called from:\n\t%s\n'%(
        request.get('getLinkObj_counter', 0),
        self.meta_id,
        url, 
        ob.id if ob is not None else None,
        ob.meta_id if ob is not None else None,
        ob.absolute_url(relative=1) if ob is not None else None,
        was_buffered,
        request.get('count_buffered_getLinkObj_calls', 0),
        ref_params,
        '\n\t'.join(traceback_stack)
        )
      )
      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    return ob


  # ----------------------------------------------------------------------------
  #  ZReferableItem.getLinkUrl:
  #
  #  Resolves internal/external links and returns URL.
  # ----------------------------------------------------------------------------
  def getLinkUrl( self, url, REQUEST=None):
    request = self.REQUEST
    if isInternalLink(url):
      # Params.
      ref_params = {}
      if url.find(';') > 0:
        ref_params = dict(re.findall(r';(\w*)=(\w*)', url[url.find(';'):-1]))
        url = '{$%s}'%url[2:url.find(';')]
      # Anchor.
      ref_anchor = ''
      if url.find('#') > 0:
        ref_anchor = url[url.find('#'):-1]
      # Prepare request.
      bak_params = {}
      for key in ref_params:
        bak_params[key] = request.get(key, None)
        request.set(key, ref_params[key])
      # Get index_html.
      ref_obj = self.getLinkObj(url)
      index_html = getInternalLinkUrl(self, url, ref_obj)
      # Unprepare request.
      for key in bak_params:
        request.set(key, bak_params[key])
      # Return index_html.
      url = index_html + ref_anchor
    elif isMailLink (url):
      prefix = 'mailto:'
      url = 'javascript:void(location.href=\'%s\'+String.fromCharCode(%s))'%(prefix,','.join([str(ord(x)) for x in url[len(prefix):]]))
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
    filtered_attrs_keys = [x for x in attrs if x]
    str_attrs = ' '.join(['%s=\042%s\042'%(str(x),str(attrs[x])) for x in filtered_attrs_keys])
    return '<a href="%s" %s %s>%s</a>'%(href, ['', ' target="%s"'%target][int(len(target)>0)], str_attrs, content)

################################################################################
