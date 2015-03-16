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
import copy
import urllib
import zope.interface
# Product Imports.
import _confmanager
import _globals
import IZMSCatalogConnector
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


    def __get_xml(self, attrs={}):
      xml =  []
      xml.append('<?xml version="1.0"?>')
      xml.append('<add'+' '.join(['']+map(lambda x:'%s="%s"'%(x,str(attrs[x])),attrs))+'>')
      def cb(node,d):
        xml.append('<doc>')
        for k in d.keys():
          xml.append('<field name="%s">%s</field>'%(k,d[k]))
        xml.append('</doc>')
      self.aq_parent.get_sitemap(cb)
      xml.append('</add>')
      return '\n'.join(xml)


    def reindex(self):
      xml =  self.__get_xml({'commitWithin':1000,'overwrite':'true'})
      solr_url = self.getConfProperty('solr.url')
      url = '%s/%s/update'%(solr_url,self.getAbsoluteHome().id)
      url = '%s?%s'%(url,xml)
      result = self.http_import(url,method='POST',headers={'Content-Type':'text/xml;charset=UTF-8'})
      print result


    def get_sitemap(self):
      """
      Returns sitemap.
      @rtype: C{str}
      """
      request = self.REQUEST
      RESPONSE = request.RESPONSE
      RESPONSE.setHeader('Content-Type','text/xml; charset=utf-8')
      xml =  self.__get_xml()
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
          reindex = self.reindex()
          message += '%s reindexed (%s)\n'%(self.id,reindex)
          
        # Save.
        # -----
        elif btn == 'Save':
          self.setConfProperty('solr.url',REQUEST['solr_url'])
        
        return message

################################################################################
