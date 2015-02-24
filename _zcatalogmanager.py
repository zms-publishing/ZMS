################################################################################
# _zcatalogmanager.py
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
from Products.ZCatalog import CatalogAwareness
import re
import sys
import zope.interface
# Product Imports.
import _globals
import IZMSCatalogAdapter


# ------------------------------------------------------------------------------
#  _zcatalogmanager.search_string:
#
#  Search string of given value.
# ------------------------------------------------------------------------------
def search_string(v):
  s = ''
  if v is not None:
    if type(v) is str and len(v) > 0:
      s += v + ' '
    elif type(v) is list:
      for i in v:
        s += search_string(i) + ' '
    elif type(v) is dict:
      for k in v.keys():
        i = v[k]
        s += search_string(i) + ' '
  return s


# ------------------------------------------------------------------------------
#  _zcatalogmanager.search_quote:
#
#  Remove HTML-Tags from given string.
# ------------------------------------------------------------------------------
def search_quote(s, maxlen=255, tag='&middot;'):
  # remove all tags.
  s = re.sub( '<script((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</script>', '', s)
  s = re.sub( '<style((.|\n|\r|\t)*?)>((.|\n|\r|\t)*?)</style>', '', s)
  s = re.sub( '<((.|\n|\r|\t)*?)>', '', s)
  # limit characters.
  if len(s) > maxlen:
    if s[:maxlen].rfind('&') >= 0 and not s[:maxlen].rfind('&') < s[:maxlen].rfind(';') and \
       s[maxlen:].find(';') >= 0 and not s[maxlen:].find(';') > s[maxlen:].find('&'):
      maxlen = maxlen + s[maxlen:].find(';')
    if s[:maxlen].endswith(chr(195)) and maxlen < len(s):
      maxlen += 1
    s = s[:maxlen] + tag * 3
  # return quoted search string.
  return s


################################################################################
################################################################################
###
###   class ZCatalogItem
###
################################################################################
################################################################################
class ZCatalogItem(CatalogAwareness.CatalogAware):

    # --------------------------------------------------------------------------
    #  ZCatalogItem.search_quote:
    #
    #  Remove HTML-Tags.
    # --------------------------------------------------------------------------
    def search_quote(self, s, maxlen=255, tag='&middot;'):
      return search_quote(s,maxlen,tag)


    # --------------------------------------------------------------------------
    #  ZCatalogItem.search_encode:
    #
    #  Encodes given string.
    # --------------------------------------------------------------------------
    def search_encode(self, s):
      return _globals.umlaut_quote(self, s)


    # --------------------------------------------------------------------------
    #  ZCatalogItem.getCatalogNavUrl:
    #
    #  Returns catalog-navigation url.
    # --------------------------------------------------------------------------
    def getCatalogNavUrl(self, REQUEST):
      return self.url_inherit_params(REQUEST['URL'],REQUEST,['qs'])


    ############################################################################
    ###
    ###  Metadate: Indices / Columns
    ###
    ############################################################################

    # --------------------------------------------------------------------------
    #  ZCatalogItem.zcat_custom:
    # --------------------------------------------------------------------------
    def zcat_custom( self, lang=None):
      request = self.REQUEST
      if lang is None:
        lang = request.get('lang',self.getPrimaryLanguage())
      req = {'lang':lang}
      xml = ''
      xml += '<breadcrumbs>'
      for breadcrumb in self.breadcrumbs_obj_path():
        xml += '<breadcrumb>'
        xml += '<loc>%s</loc>'%breadcrumb.getHref2IndexHtml(request)
        xml += '<title>%s</title>'%breadcrumb.getTitlealt(request)
        xml += '</breadcrumb>'
      xml += '</breadcrumbs>'
      return xml

    # --------------------------------------------------------------------------
    #  ZCatalogItem.synchronizeSearch:
    # --------------------------------------------------------------------------
    def synchronizeSearch(self, REQUEST, forced=0):
      if self.getConfProperty('ZMS.CatalogAwareness.active',1) or forced:
        _globals.writeLog( self, '[synchronizeSearch]')
        for ref_by in self.getRefByObjs(REQUEST):
          ref_ob = self.getLinkObj(ref_by,REQUEST)
          if ref_ob is not None and \
             ref_ob. meta_type == 'ZMSLinkElement' and \
             ref_ob.isEmbedded( REQUEST) and not \
             ref_ob.isEmbeddedRecursive( REQUEST):
            if not forced or ref_ob.getHome().id != self.getHome().id:
              ref_ob.synchronizeSearch( REQUEST=REQUEST, forced=forced)
        lang = REQUEST.get( 'lang', self.getPrimaryLanguage())
        # Reindex object.
        ob = self.getCatalogItem()
        if ob is not None:
          ob.default_catalog = 'catalog_%s'%lang
          ob.reindex_object()


    # --------------------------------------------------------------------------
    #  ZCatalogItem.isCatalogItem:
    #
    #  Returns true if this is a catalog item.
    # --------------------------------------------------------------------------
    def isCatalogItem(self):
      return True


    # --------------------------------------------------------------------------
    #  ZCatalogItem.getCatalogItem:
    # --------------------------------------------------------------------------
    def getCatalogItem(self):
      ob = self
      while ob is not None:
        if ob.isCatalogItem():
          break
        ob = ob.getParentNode()
      return ob


    # --------------------------------------------------------------------------
    #  ZCatalogItem.reindexCatalogItem:
    #
    #  Reindex catalog item.
    # --------------------------------------------------------------------------
    def reindexCatalogItem(self, REQUEST):
      message = ''
      # Process catalog-item.
      if self.isCatalogItem():
        self.synchronizeSearch(REQUEST=REQUEST,forced=1)
      # Recurse.
      for ob in filter( lambda x: x.isActive(REQUEST), self.filteredChildNodes(REQUEST)):
        ob.reindexCatalogItem(REQUEST)
      # Return with message.
      return message


################################################################################
################################################################################
###
###   class ZCatalogManager
###
################################################################################
################################################################################
class ZCatalogManager:

    # --------------------------------------------------------------------------
    #  ZCatalogManager.getCatalogQueryString:
    # --------------------------------------------------------------------------
    def getCatalogQueryString(self, raw, option='AND', only_words=False):
      qs = []
      i = 0
      for si in raw.split('"'):
        si = si.strip()
        if si:
          if i % 2 == 0:
            for raw_item in si.split(' '):
              raw_item = raw_item.strip()
              if len(raw_item) > 1 and not raw_item.upper() in ['AND','OR']:
                raw_item = raw_item.replace('-','* AND *')
                if not only_words and not raw_item.endswith('*'):
                  raw_item += '*'
                if raw_item not in qs:
                  qs.append( raw_item)
          else:
            raw_item = '"%s"'%si
            if raw_item not in qs:
              qs.append( raw_item)
        i += 1
      return (' %s '%option).join(filter( lambda x: len(x.strip())>0, qs))


    # --------------------------------------------------------------------------
    #  ZCatalogManager.getCatalogPathObject:
    #
    #  Returns object from catalog-path.
    # --------------------------------------------------------------------------
    def getCatalogPathObject(self, path):
      ob = self.getHome()
      l = path.split( '/')
      if ob.id not in l:
        docElmnt = self.getDocumentElement()
        if docElmnt.id not in l:
          ob = docElmnt
      else:
        l = l[ l.index(ob.id)+1:]
      for id in l:
         if len( id) > 0 and ob is not None:
          ob = getattr(ob,id,None)
      return ob


    # --------------------------------------------------------------------------
    #  ZCatalogManager.submitCatalogQuery:
    #
    #  Submits query to catalog.
    # --------------------------------------------------------------------------
    def submitCatalogQuery(self, search_query, search_order_by, search_meta_types=[], search_clients=False, REQUEST=None):
      rtn = []
      
      # delegate to adapters
      for ob in self.getDocumentElement().objectValues():
        if IZMSCatalogAdapter.IZMSCatalogAdapter in list(zope.interface.providedBy(ob)):
          rtn.extend(ob.search(search_query, search_order_by))
      
      return rtn

################################################################################
