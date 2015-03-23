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
import urllib
import zope.interface
# Product Imports.
import _globals
import _xmllib
import IZMSCatalogConnector
import ZMSZCatalogAdapter
import ZMSItem


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
class ZMSZCatalogSolrConnector(
        ZMSItem.ZMSItem):
    zope.interface.implements(
        IZMSCatalogConnector.IZMSCatalogConnector)

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogSolrConnector'
    icon = "/++resource++zms_/img/solr.png"

    # Management Interface.
    # ---------------------
    manage_input_form = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_solr_connector',globals())

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
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang',REQUEST.get('lang',self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      attrs = zcm.getAttrs()
      # Execute query.
      p = {}
      p['q'] = q
      p['wt'] = 'xml'
      p['start'] = page_index
      p['rows'] = page_size
      p['defType'] = 'edismax'
      p['qf'] = ' '.join(map(lambda x:'%s_t^%s'%(x,str(attrs[x].get('boost',1.0))),attrs.keys()))
      p['hl'] = 'true'
      p['hl.fragsize']  = self.getConfProperty('solr.select.hl.fragsize',200)
      p['hl.fl'] = self.getConfProperty('solr.select.hl.fl',','.join(map(lambda x:'%s_t'%x,attrs.keys())))
      p['hl.simple.pre'] = self.getConfProperty('solr.select.hl.simple.pre','<span class="highlight">')
      p['hl.simple.post'] = self.getConfProperty('solr.select.hl.simple.post','</span>')
      solr_url = self.getConfProperty('solr.url','http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core',self.getAbsoluteHome().id)
      url = '%s/%s/select'%(solr_url,solr_core)
      url = self.url_append_params(url,p,sep='&')
      result = self.http_import(url,method='GET')
      result = self.re_sub('name="(.*?)_t"','name="\\1"',result)
      return result


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.suggest_xml:
    # --------------------------------------------------------------------------
    def suggest_xml(self, q, REQUEST=None, RESPONSE=None):
      """ ZMSZCatalogSolrConnector.suggest_xml """
      # Check constraints.
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      p = {}
      p['q'] = q
      solr_url = self.getConfProperty('solr.url','http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core',self.getAbsoluteHome().id)
      url = '%s/%s/suggest'%(solr_url,solr_core)
      url = self.url_append_params(url,p,sep='&')
      result = self.http_import(url,method='GET')
      return result


    def __get_delete_xml(self, query='*:*', attrs={}):
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<delete'+' '.join(['']+map(lambda x:'%s="%s"'%(x,str(attrs[x])),attrs))+'>')
      xml.append('<query>%s</query>'%query)
      xml.append('</delete>')
      return '\n'.join(xml)


    def __get_command_xml(self, command):
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<%s/>'%command)
      return '\n'.join(xml)


    def __get_add_xml(self, node, recursive, attrs={}):
      zcm = self.getCatalogAdapter()
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<add'+' '.join(['']+map(lambda x:'%s="%s"'%(x,str(attrs[x])),attrs))+'>')
      def cb(node,d):
        xml.append('<doc>')
        for k in d.keys():
          v = d[k]
          if k not in ['id']:
            if type(v) in (str,unicode):
              k = '%s_t'%k
          xml.append('<field name="%s">%s</field>'%(k,v))
        xml.append('</doc>')
      zcm.get_sitemap(cb,node,recursive)
      xml.append('</add>')
      return '\n'.join(xml)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector._update:
    # --------------------------------------------------------------------------
    def _update(self, xml):
      solr_url = self.getConfProperty('solr.url','http://localhost:8983/solr')
      solr_core = self.getConfProperty('solr.core',self.getAbsoluteHome().id)
      url = '%s/%s/update'%(solr_url,solr_core)
      url = '%s?%s'%(url,xml)
      result = self.http_import(url,method='POST',headers={'Content-Type':'text/xml;charset=UTF-8'})
      self.writeLog("[ZMSZCatalogSolrConnector._update]: %s"%str(result))
      return result


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self):
      self._update(self.__get_delete_xml())
      xml =  self.__get_add_xml(self.getDocumentElement(),recursive=True)
      result = self._update(xml)
      self._update(self.__get_command_xml('commit'))
      self._update(self.__get_command_xml('optimize'))
      return result


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_node:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      xml =  self.__get_add_xml(node,recursive=False,attrs={'overwrite':'true'})
      return self._update(xml)


    def get_sitemap(self):
      """
      Returns sitemap.
      @rtype: C{str}
      """
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
      xml =  self.__get_add_xml(self.getDocumentElement(),recursive=True)
      return xml


    ############################################################################
    #  ZMSZCatalogSolrConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, selected, btn, lang, REQUEST):
        message = ''
        
        # Reindex.
        # --------
        if btn == 'Reindex' and selected:
          reindex = self.reindex_all()
          message += '%s reindexed (%s)\n'%(self.id,str(reindex))
          
        # Save.
        # -----
        elif btn == 'Save':
          self.setConfProperty('solr.url',REQUEST['solr_url'])
          self.setConfProperty('solr.core',REQUEST['solr_core'])
        
        return message

################################################################################
