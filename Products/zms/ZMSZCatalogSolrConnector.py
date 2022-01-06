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
from Products.zms import ZMSZCatalogAdapter
from Products.zms import ZMSItem
from Products.zms import standard
from Products.zms import _xmllib


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
    def search_xml(self, q, page_index=0, page_size=10, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogSolrConnector.search_xml """
      # Check constraints.
      zcm = self.getCatalogAdapter()
      attrs = zcm.getAttrs()
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang', REQUEST.get('lang', self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
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
      url = self.url_append_params(url, p, sep='&')
      result = self.http_import(url, method='GET')
      result = standard.re_sub('name="(.*?)_[ist]"', 'name="\\1"', result)
      return result


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.suggest_xml:
    # --------------------------------------------------------------------------
    def suggest_xml(self, q, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogSolrConnector.suggest_xml """
      # Check constraints.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      RESPONSE.setHeader('Content-Type', content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      p = {}
      solr_url = self.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core', self.getAbsoluteHome().id)
      SOLR_SUGGEST_SELECT = 'select?q=*:*&rows=0&facet=true&facet.field=text&facet.prefix=%s&facet.limit=5'
      SOLR_SUGGEST_SUGGEST = 'suggest?q=%s'
      solr_suggest = self.getConfProperty('solr.suggest', SOLR_SUGGEST_SELECT)%q
      url = '%s/%s/%s'%(solr_url, solr_core, solr_suggest)
      result = self.http_import(url, method='GET')
      return result


    def __get_delete_xml(self, query='*:*', attrs={}):
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<delete'+' '.join(['']+['%s="%s"'%(x, str(attrs[x])) for x in attrs])+'>')
      xml.append('<query>%s</query>'%query)
      xml.append('</delete>')
      return '\n'.join(xml)


    def __get_command_xml(self, command):
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<%s/>'%command)
      return '\n'.join(xml)


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


    def __get_add_xml(self, node, recursive, xmlattrs={}, update=False):
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
          if update:
            xml.insert(0, '<?xml version="1.0"?>')
            xml.insert(1, '<add'+' '.join(['']+['%s="%s"'%(x, str(xmlattrs[x])) for x in xmlattrs])+'>')
            xml.append('</add>')
            results.append(self._update('update', '\n'.join(xml)))
          else:
            results.extend(xml)
        except:
          standard.writeError(node,"can't cb")
      zcm.get_sitemap(cb, node, recursive)
      if not update:
        results.insert(0, '<?xml version="1.0"?>')
        results.insert(1, '<add'+' '.join(['']+['%s="%s"'%(x, str(xmlattrs[x])) for x in xmlattrs])+'>')
        results.append('</add>')
      return ['\n',','][int(update)].join(results)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector._update:
    # --------------------------------------------------------------------------
    def _update(self, action, xml):
      solr_url = self.getConfProperty('solr.url', 'http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core', self.getAbsoluteHome().id)
      url = '%s/%s/update'%(solr_url, solr_core)
      url = '%s?%s'%(url, xml)
      result = standard.pystr(standard.http_import(self, url, method='POST', headers={'Content-Type':'text/xml;charset=UTF-8'}))
      standard.writeLog(self, "[ZMSZCatalogSolrConnector._update]: %s=%s"%(action,result))
      return '%s=%s'%(action,result)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self, container=None):
      result = []
      if container is None:
        container = self.getDocumentElement()
      home_id = container.getHome().id
      result.append(self._update('delete', self.__get_delete_xml(query='home_id_s:%s'%home_id)))
      result.append(self.__get_add_xml(container, recursive=True, update=True))
      result.append(self._update('commit', self.__get_command_xml('commit')))
      result.append(self._update('optimize', self.__get_command_xml('optimize')))
      for portalClient in self.getPortalClients():
        result.append(self.reindex_all(portalClient))
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_self(self, uid):
      result = []
      container = self.getLinkObj(uid)
      home_id = container.getHome().id
      result.append(self._update('delete', self.__get_delete_xml(query='home_id_s:%s'%home_id)))
      result.append(self.__get_add_xml(container, recursive=True, update=True))
      result.append(self._update('commit', self.__get_command_xml('commit')))
      result.append(self._update('optimize', self.__get_command_xml('optimize')))
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_node:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      xml =  self.__get_add_xml(node, recursive=False, xmlattrs={'overwrite':'true'})
      return self._update(xml)


    def get_sitemap(self):
      """
      Returns sitemap.
      @rtype: C{str}
      """
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      RESPONSE.setHeader('Content-Type', 'text/xml; charset=utf-8')
      xml =  self.__get_add_xml(self.getDocumentElement(), recursive=True)
      return xml


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
