################################################################################
# ZMSZCatalogOpensearchConnector.py
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


################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSCatalogConnector.IZMSCatalogConnector)
class ZMSZCatalogOpensearchConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogOpensearchConnector'
    icon = "++resource++zms_/img/solr.png"

    # Management Interface.
    # ---------------------
    manage_input_form = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_opensearch_connector', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
      'manage_changeProperties', 'manage_main',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
    )

    ############################################################################
    #  ZMSZCatalogOpensearchConnector.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self):
      self.id = 'zcatalog_opensearch_connector'


    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.search_json:
    # --------------------------------------------------------------------------
    def search_json(self, q, REQUEST, RESPONSE=None):
      """ ZMSZCatalogOpensearchConnector.search_json """
      import requests
      from requests.auth import HTTPBasicAuth
      import json

      qpage_index = REQUEST.get('pageIndex',0)
      qsize = REQUEST.get('size', 10)
      qfrom = REQUEST.get('from', qpage_index*qsize)

      d = {
        "size": qsize,
        "from":qfrom,
        "query":{
          "query_string":{"query":q}
        },
        "highlight": {
          "fields": {
            "title": { "type": "plain"},
            "standard_html": { "type": "plain"}
          }
        },
        "aggs": {
          "response_codes": {
            "terms": {
              "field": "meta_id",
              "size": 5
            }
          }
        }
      }

      url = self.getConfProperty('opensearch.url', 'https://localhost:9200')
      # ID of opensearch index is ZMS multisite root node id or explicitly given by request variable 'opensearch_index_id'
      root_id = self.getRootElement().getHome().id
      index_id = REQUEST.get('opensearch_index_id',root_id)
      username = self.getConfProperty('opensearch.username', 'admin')
      password = self.getConfProperty('opensearch.password', 'admin')
      verify = bool(self.getConfProperty('opensearch.ssl.verify', ''))
      auth = HTTPBasicAuth(username,password)
      response = requests.get('%s/%s/_search?pretty=true'%(url,index_id),auth=auth,json=d,verify=verify)
      response.raise_for_status()
      json_obj = response.json()
      data = json.dumps(json_obj, separators=(",", ":"), indent=4)
      REQUEST.RESPONSE.setHeader('Content-Type','text/json; charset=utf-8')
      return data


    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.reindex_all:
    # --------------------------------------------------------------------------
    def reindex_all(self, container=None):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_self(self, uid):
      result = []
      return ', '.join([x for x in result if x])


    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.reindex_self:
    # --------------------------------------------------------------------------
    def reindex_node(self, node):
      pass


    ############################################################################
    #  ZMSZCatalogOpensearchConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, selected, btn, lang, REQUEST):
        message = ''
        
        # Save.
        # -----
        if btn == 'Save':
          self.setConfProperty('opensearch.url', REQUEST['opensearch_url'])
          if REQUEST.get('opensearch_password','********') != '********':
            self.setConfProperty('opensearch.username', REQUEST['opensearch_username'])
            self.setConfProperty('opensearch.password', REQUEST['opensearch_password'])
        
        return message

################################################################################
