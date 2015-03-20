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
      page_index = int(page_index)
      page_size = int(page_size)
      REQUEST.set('lang',REQUEST.get('lang',self.getPrimaryLanguage()))
      RESPONSE = REQUEST.RESPONSE
      content_type = 'text/xml; charset=utf-8'
      RESPONSE.setHeader('Content-Type',content_type)
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Pragma', 'no-cache')
      # Execute query.
      p = {}
      p['q'] = q
      p['wt'] = 'xml'
      p['start'] = page_index
      p['rows'] = page_size
      p['hl'] = 'true'
      p['hl.fragsize']  = self.getConfProperty('solr.select.hl.fragsize',200)
      p['hl.fl'] = self.getConfProperty('solr.select.hl.fl','title,body')
      p['hl.simple.pre'] = self.getConfProperty('solr.select.hl.simple.pre','<span class="highlight">')
      p['hl.simple.post'] = self.getConfProperty('solr.select.hl.simple.post','</span>')
      solr_url = self.getConfProperty('solr.url')
      url = '%s/%s/select'%(solr_url,self.getAbsoluteHome().id)
      url = self.url_append_params(url,p,sep='&')
      result = self.http_import(url,method='GET')
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
      solr_url = self.getConfProperty('solr.url')
      url = '%s/%s/suggest'%(solr_url,self.getAbsoluteHome().id)
      url = self.url_append_params(url,p,sep='&')
      result = self.http_import(url,method='GET')
      return result


    def __get_xml(self, node, recursive, attrs={}):
      zcm = self.getCatalogAdapter()
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<add'+' '.join(['']+map(lambda x:'%s="%s"'%(x,str(attrs[x])),attrs))+'>')
      def cb(node,d):
        xml.append('<doc>')
        for k in d.keys():
          xml.append('<field name="%s">%s</field>'%(k,d[k]))
        xml.append('</doc>')
      zcm.get_sitemap(cb,node,recursive)
      xml.append('</add>')
      return '\n'.join(xml)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector._update:
    # --------------------------------------------------------------------------
    def _update(self, xml):
      solr_url = self.getConfProperty('solr.url')
      url = '%s/%s/update'%(solr_url,self.getAbsoluteHome().id)
      url = '%s?%s'%(url,xml)
      result = self.http_import(url,method='POST',headers={'Content-Type':'text/xml;charset=UTF-8'})


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self):
      xml =  self.__get_xml(self.getDocumentElement(),recursive=True,attrs={'commitWithin':1000,'overwrite':'true'})
      self._update(xml)


    # --------------------------------------------------------------------------
    #  ZMSZCatalogSolrConnector.reindex_node:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      xml =  self.__get_xml(node,recursive=False,attrs={'commitWithin':1,'overwrite':'true'})
      self._update(xml)


    def get_sitemap(self):
      """
      Returns sitemap.
      @rtype: C{str}
      """
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
      xml =  self.__get_xml(self.getDocumentElement(),recursive=True)
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
        
        return message

################################################################################
