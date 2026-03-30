"""
_zreferableitem.py - ZMS Referable Item Mixin for Internal Reference Handling and Link Validation

Defines ZReferableItem for object persistence, Zope integration, and container protocols.
It implements Zope's ObjectManager interface, handles acquisition, and manages object lifecycle.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""
# Imports.
import time

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import base64
import re
# Product Imports.
from Products.zms import standard
from zope.globalrequest import getRequest


# ----------------------------------------------------------------------------
# Internal Link Utilities for ZMS Objects
# ----------------------------------------------------------------------------

def isMailLink(url):
  """
  Checks if the given URL is a mailto link.
  @param url: The URL to check.
  @type url: C{str}
  @return: True if the URL starts with C{mailto:}, False otherwise.
  @rtype: C{bool}
  """
  rtn = isinstance(url, str) and url.lower().startswith('mailto:')
  return rtn


def isInternalLink(url):
  """
  Checks if the given URL is an internal link.
  @param url: The URL to check.
  @type url: C{str}
  @return: True if the URL is in the internal link format C{{$...}},
      False otherwise.
  @rtype: C{bool}
  """
  rtn = isinstance(url, str) and url.startswith('{$') and url.endswith('}')
  return rtn


def getInternalLinkDict(self, url):
  """
  Resolves an internal link and returns a dictionary with link metadata.
  @param self: The object context.
  @type self: C{object}
  @param url: The internal link to resolve.
  @type url: C{str}
  @return: Metadata about the internal link such as C{data-id},
      C{data-url}, and C{data-target}.
  @rtype: C{dict}
  """
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


def getInternalLinkUrl(self, url, ob):
  """
  Resolves the internal index_html URL for a given object and internal link.
  @param self: The object context.
  @type self: C{object}
  @param url: The internal link.
  @type url: C{str}
  @param ob: The referenced object.
  @type ob: C{object}
  @return: The resolved C{index_html} URL.
  @rtype: C{str}
  """
  request = getattr(self, 'REQUEST', getRequest())
  if ob is None:
    index_html = './index_%s.html?error_type=NotFound&op=not_found&url=%s'%(request.get('lang', self.getPrimaryLanguage()), str(url))
  else:
    # Contextualized index_html.
    context = request.get('ZMS_THIS', self)
    index_html = ob.getHref2IndexHtmlInContext(context, REQUEST=request)
  return index_html


def getInlineRefs(text):
  """
  Extracts internal link references from inline HTML content.
  @param text: The HTML content.
  @type text: C{str}
  @return: Internal link identifiers found in anchor tags.
  @rtype: C{list}
  """
  l = []
  p = r'<a(.*?)>(.*?)</a>'
  r = re.compile(p)
  for f in r.findall(str(text)):
    d = dict(re.findall(r'\s(.*?)="(.*?)"', f[0]))
    if 'data-id' in d:
      l.append(d['data-id'])
  return l


class ZReferableItem(object): 
  """
  Mixin for internal reference handling in ZMS objects.

  This mixin resolves internal link tokens, collects outgoing references,
  maintains incoming backlinks in C{ref_by}, and validates stored references.
  """

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
  # ZReferableItem Functions for Getting object reference path or relative URL.
  # ----------------------------------------------------------------------------
  def getRelativeUrl(self, path, url):
    """
    Computes a relative URL from a source path to a destination URL.
    @param path: The source path.
    @type path: C{str}
    @param url: The destination URL.
    @type url: C{str}
    @return: The relative URL if both URLs share the same base, otherwise
        the original destination URL.
    @rtype: C{str}
    """
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


  def getRefObjPath(self, ob, anchor=''):
    """
    Returns the internal reference path for a given object.
    @param ob: The object to reference.
    @type ob: C{object}
    @param anchor: Anchor string to append.
    @type anchor: C{str}
    @return: The internal reference path in C{{$...}} format.
    @rtype: C{str}
    """
    ref = ob.get_uid()
    if anchor:
      ref += '#'+anchor
    return '{$%s}'%ref


  # ----------------------------------------------------------------------------
  #  FROM: ZReferableItem Functions for Referencing FROM Other Objects.
  # ----------------------------------------------------------------------------

  def getRefByObjs(self, REQUEST=None):
    """
    Returns a list of references FROM other objects to this object.
    @param REQUEST: The request object.
    @type REQUEST: C{object}
    @return: References from other objects to this object.
    @rtype: C{list}
    """
    ref_by = []
    if 'ref_by' in self.__dict__:
      ref_by = self.ref_by
      ref_by = list(set(ref_by))
    return ref_by


  def synchronizeRefByObjs(self, strict=1):
    """
    Synchronizes the list of references FROM other objects.
    @param strict: Flag kept for API compatibility.
    @type strict: C{int}
    @return: The updated list of references from other objects.
    @rtype: C{list}
    """
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


  def registerRefObj(self, ob):
    """
    Registers a reference FROM another object to this object.
    @param ob: The object referencing this object.
    @type ob: C{object}
    """
    ref = self.getRefObjPath(ob)
    standard.writeLog(self, '[registerRefObj]: ref='+ref)
    ref_by = self.synchronizeRefByObjs()
    if ref not in ref_by:
      ref_by.append(ref)
      self.ref_by = ref_by


  def unregisterRefObj(self, ob):
    """
    Unregisters a reference FROM another object to this object.
    @param ob: The object referencing this object.
    @type ob: C{object}
    """
    ref = self.getRefObjPath(ob)
    standard.writeLog(self, '[unregisterRefObj]: ref='+ref)
    ref_by = self.synchronizeRefByObjs()
    if ref in ref_by:
      ref_by = [x for x in ref_by if x!=ref]
      self.ref_by = ref_by


  # ----------------------------------------------------------------------------
  #  TO: ZReferableItem Functions for Referencing TO Other Objects.
  # ----------------------------------------------------------------------------

  def getRefToObjs(self):
    """
    Returns a list of references from this object TO other objects.
    @return: References from this object to other objects.
    @rtype: C{list}
    """
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


  def changeRefsToObj(self, ref_to):
    """
    Changes all internal references TO a new target object.
    @param ref_to: The target reference to which all selected references
      should point.
    @type ref_to: C{str}
    @return: A result dictionary with changed and unchanged references, or
      C{None} if no update could be performed.
    @rtype: C{dict} or C{None}
    """
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


  def prepareRefreshRefToObjs(self):
    """
    Prepares the refresh of references TO other objects by storing the current references.
    This method stores the current outgoing references in C{self.ref_to} for
    later comparison by L{refreshRefToObjs}.
    """
    standard.writeLog( self, '[prepareRefreshRefToObjs]')
    if 'ref_to' not in self.__dict__:
      self.ref_to = self.getRefToObjs()


  def refreshRefToObjs(self):
    """
    Synchronizes references TO other objects, updating registrations as
    needed.

    The method unregisters obsolete backlinks and registers newly created
    backlinks.
    """
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


  # ----------------------------------------------------------------------------
  #  ZReferableItem Functions for Resolving/Validating Internal Links
  # ----------------------------------------------------------------------------

  def validateInlineLinkObj(self, text):
    """
    Validates internal links within inline HTML content.
    @param text: The HTML content to validate.
    @type text: C{str}
    @return: The validated HTML content with updated internal links.
    @rtype: C{str}
    """
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


  def validateLinkObj(self, url):
    """
    Validates a single internal link.
    @param url: The internal link to validate.
    @type url: C{str}
    @return: The validated internal link.
    @rtype: C{str}
    """
    if isInternalLink(url):
      if not url.startswith('{$__'):
        ild = getInternalLinkDict(self, url)
        url = ild['data-id']
    return url


  def validateRefObj(self, s):
    """
    Validates internal object-references.
    @param s: String to validate. This can be an internal link token or an
        inline HTML fragment.
    @type s: C{str}
    @return: The validated link or HTML string.
    @rtype: C{str}
    """
    if isInternalLink(s):
      return self.validateLinkObj(s)
    return self.validateInlineLinkObj(s)


  def findObject(self, url):
    """
    Quickly finds and returns an object based on an internal URL.
    Assumes the object exists as a recently calculated uid in 
    ZMSIndex or as a object path.
    @param url: Internal URL string in the format C{{$...}}.
    @type url: C{str}
    @return: The resolved object if found, otherwise C{None}.
    @rtype: C{object} or C{None}
    """
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


  def getLinkObj(self, url, REQUEST=None):
    """
    Resolves internal or external links and returns the corresponding object.
    @param url: The link to resolve. It can be internal or external.
    @type url: C{str}
    @param REQUEST: The request object.
    @type REQUEST: C{object}
    @return: The resolved object if found, otherwise C{None}.
    @rtype: C{object} or C{None}
    """
    request = getattr(self, 'REQUEST', getRequest())
    request.set('counter_getlinkobj', float(request.get('counter_getlinkobj', 0)) + 1)
    # ///////////////////////////////////////////////////
    # MEASURING PERFORMANCE:
    start_getlinkobj = time.time()
    # ///////////////////////////////////////////////////
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
        #-- [ReqBuff/SharedBuff]: Fetch buffered value.
        reqBuffId = 'getLinkObj.%s'%url
        try:
          # Try Request-Local first.
          ob = self.fetchReqBuff(reqBuffId)
        except:
          # Try Shared Global Context if configured.
          if hasattr(self, 'fetchSharedBuff'):
            cached_path = self.fetchSharedBuff(reqBuffId)
            if cached_path:
               ob = self.unrestrictedTraverse(cached_path, None)

          if ob is None:
            # ///////////////////////////////////////////////////
            # MEASURING PERFORMANCE:
            # For summing up the time needed find object by URL via ZMSIndex:
            # add the current time to the request-parameter 'total_time_consumed_by_zmsindex_requests'/int (in ms)
            start_zmsindex_request = time.time()
            # ///////////////////////////////////////////////////
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
            
            #-- [ReqBuff/SharedBuff]: Store value.
            self.storeReqBuff(reqBuffId, ob)
            if ob and hasattr(self, 'storeSharedBuff'):
               self.storeSharedBuff(reqBuffId, '/'.join(ob.getPhysicalPath()))
            # ///////////////////////////////////////////////////
            # MEASURING PERFORMANCE: Count and time for requests to ZMSIndex to find object by URL.
            request.set('counter_zmsindex_requests', float(request.get('counter_zmsindex_requests', 0)) + 1)
            request.set('time_consumed_by_zmsindex_requests_in_ms', round(float(request.get('time_consumed_by_zmsindex_requests_in_ms', 0)) + float((time.time() - start_zmsindex_request)*1000),2))
            # ///////////////////////////////////////////////////
      # Prepare request (only if ref_params are provided)
      if ob is not None and ref_params:
        ids = self.getPhysicalPath()
        if ob.id not in ids:
          ob.set_request_context(request, ref_params)
    # ///////////////////////////////////////////////////
    # MEASURING PERFORMANCE: Count and time for getLinkObj calls.
    request.set('time_consumed_by_getlinkobj_in_ms', round(float(request.get('time_consumed_by_getlinkobj_in_ms', 0)) + float((time.time() - start_getlinkobj)*1000),2))
    time_consumed_by_getlinkobj_datalist = request.get('time_consumed_by_getlinkobj_datalist', [])
    time_consumed_by_getlinkobj_datalist.append(round(float((time.time() - start_getlinkobj)*1000),2)) # in ms
    request.set('time_consumed_by_getlinkobj_datalist', time_consumed_by_getlinkobj_datalist)
    # ///////////////////////////////////////////////////
    return ob


  def getLinkUrl(self, url, REQUEST=None):
    """
    Combines internal/external link resolution and returns the final URL string, 
    handling anchors and mailto obfuscation.
    @param url: The link to resolve. It can be internal or external.
    @type url: C{str}
    @param REQUEST: The request object.
    @type REQUEST: C{object}
    @return: The resolved URL as a string.
    @rtype: C{str}

    This method differs from L{getLinkObj}, which returns the referenced
    object, and from L{getInternalLinkUrl}, which renders an internal
    C{index_html} URL for a specific object.
    """
    request = self.REQUEST
    if isInternalLink(url):
      # Params.
      ref_params = {}
      if url.find(';') > 0:
        ref_params = dict(re.findall(r';(\w*)=(\w*)', url[url.find(';'):-1]))
        url = '{$%s}'%(url[2:url.find(';')])
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
    elif isMailLink(url):
      prefix = 'mailto:'
      url = 'javascript:void(location.href=\'%s\'+String.fromCharCode(%s))'%(
        prefix, ','.join([str(ord(x)) for x in url[len(prefix):]])
      )
    return url


  def tal_anchor(self, href, target='', attrs={}, content=''):
    """
    Generate an HTML anchor (<a>) tag.
    @param href: The URL for the anchor's C{href} attribute.
    @type href: C{str}
    @param target: The target attribute for the anchor, for example C{_blank}.
    @type target: C{str}
    @param attrs: Additional HTML attributes for the anchor tag.
    @type attrs: C{dict}
    @param content: The inner HTML or text content of the anchor.
    @type content: C{str}
    @return: The formatted HTML anchor tag as a string.
    @rtype: C{str}
    """
    filtered_attrs_keys = [x for x in attrs if x]
    str_attrs = ' '.join(['%s=\042%s\042'%(str(x),str(attrs[x])) for x in filtered_attrs_keys])
    return '<a href="%s" %s %s>%s</a>'%(href, ['', ' target="%s"'%target][int(len(target)>0)], str_attrs, content)