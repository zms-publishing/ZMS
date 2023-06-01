################################################################################
# ZMSZCatalogSolrConnector.py
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
from zope.interface import implementer
# Product Imports.
from Products.zms import IZMSCatalogConnector
from Products.zms import ZMSItem
from Products.zms import standard


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSCatalogConnector.IZMSCatalogConnector)
class ZMSZCatalogSolrConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogSolrConnector'
    icon = "++resource++zms_/img/solr.png"

    # Management Interface.
    # ---------------------
    manage_input_form = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_solr_connector', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
      'manage_changeProperties', 'manage_main',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
    )

    ############################################################################
    #  ZMSZCatalogSolrConnector.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'zcatalog_solr_connector'


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.search_xml:
    # --------------------------------------------------------------------------
    def search_xml(self, q, page_index=0, page_size=10, debug=0, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogSolrConnector.search_xml """
      # Check constraints.
      zcm = self.getCatalogAdapter()
      attrs = zcm.getAttrs()
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang', REQUEST.get('lang', self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      debug = int(debug)
      if debug:
        content_type = 'text/plain; charset=utf-8'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      RESPONSE.setHeader('Access-Control-Allow-Origin', '*')
      # Execute query.
      p = {}
      p['q'] = q
      p['wt'] = 'xml'
      p['start'] = page_index
      p['rows'] = page_size
      p['defType'] = 'edismax'
      p['qf'] = ' '.join(['%s^%s'%(self._get_field_name(x), str(attrs[x].get('boost', 1.0))) for x in attrs])
      p['hl'] = 'true'
      p['hl.fragsize']  = self.getConfProperty('solr.select.hl.fragsize', 200)
      p['hl.fl'] = self.getConfProperty('solr.select.hl.fl', ','.join([self._get_field_name(x) for x in attrs]))
      p['hl.simple.pre'] = self.getConfProperty('solr.select.hl.simple.pre', '<span class="highlight">')
      p['hl.simple.post'] = self.getConfProperty('solr.select.hl.simple.post', '</span>')
      solr_url = self.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core', self.getAbsoluteHome().id)
      url = '%s/%s/select'%(solr_url, solr_core)
      url = standard.url_append_params(url, p, sep='&')
      result = standard.http_import(self, url, method='GET', debug=debug)
      result = standard.re_sub('name="(.*?)_[ist]"', 'name="\\1"', standard.pystr(result))
      return result


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.suggest_xml:
    # --------------------------------------------------------------------------
    def suggest_xml(self, q, debug=0, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogSolrConnector.suggest_xml """
      # Check constraints.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      debug = int(debug)
      if debug:
        content_type = 'text/plain; charset=utf-8'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      p = {}
      solr_url = self.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core', self.getAbsoluteHome().id)
      SOLR_SUGGEST = 'select?q=*:*&rows=0&facet=true&facet.field=text&facet.prefix=%s&facet.limit=5' # or 'suggest?q=%s'
      solr_suggest = self.getConfProperty('solr.suggest', SOLR_SUGGEST)%(q)
      url = '%s/%s/%s'%(solr_url, solr_core, solr_suggest)
      result = standard.http_import(self, url, method='GET',debug=debug)
      return result


    def _get_field_name(self, k):
      zcm = self.getCatalogAdapter()
      attrs = zcm.getAttrs()
      if k not in ['id']:
        suffix = 's'
        if k in attrs:
          attr_type = attrs[k].get('type', 'text')
          attr_suffix = {'text':'t','string':'t','select':'s','multiselect':'s','int':'i'}
          suffix = attr_suffix.get(attr_type, suffix)
        k = '%s_%s'%(k, suffix)
      return k


    def __get_add_xml(self, node, recursive, xmlattrs={}):
      results = []
      zcm = self.getCatalogAdapter()
      attrs = zcm.getAttrs()
      def cb(node, d):
        xml =  []
        xml.append('<doc>')
        text = []
        for k in d:
          name = k
          boost = 1.0
          v = d[k]
          if k not in ['id']:
            if k in attrs:
              boost = attrs[k]['boost']
              if isinstance(v, str):
                name = '%s_t'%k
                text.append(v)
            else:
              if isinstance(v, str):
                name = '%s_s'%k
          xml.append('<field name="%s" boost="%.1f">%s</field>'%(name, boost, v))
        xml.append('<field name="text_t">%s</field>'%' '.join([x for x in text if x]))
        xml.append('</doc>')
        try:
          results.extend(xml)
        except:
          standard.writeError(node,"can't cb")
      zcm.get_sitemap(cb, node, recursive)
      results.insert(0, '<?xml version="1.0"?>')
      results.insert(1, '<add'+' '.join(['']+['%s="%s"'%(x, str(xmlattrs[x])) for x in xmlattrs])+'>')
      results.append('</add>')
      return '\n'.join(results)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self, container=None):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_self(self, uid):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      pass


    ############################################################################
    #  ZMSZCatalogSolrConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, selected, btn, lang, REQUEST):
        message = ''
        
        # Save.
        # -----
        if btn == 'Save':
          self.setConfProperty('solr.url', REQUEST['solr_url'])
          self.setConfProperty('solr.core', REQUEST['solr_core'])
        
        return message

################################################################################
