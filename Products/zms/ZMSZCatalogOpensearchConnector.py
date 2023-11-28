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
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem
from Products.zms import standard
import json
from urllib.parse import urlparse
import opensearchpy
from opensearchpy import OpenSearch



################################################################################
################################################################################
###
###   Class
###
################################################################################
################################################################################
@implementer(
        IZMSCatalogConnector.IZMSCatalogConnector,
        IZMSRepositoryProvider.IZMSRepositoryProvider,)
class ZMSZCatalogOpensearchConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogOpensearchConnector'
    zmi_icon = "fas fa-search"

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


    ############################################################################
    #
    #  IRepositoryProvider
    #
    ############################################################################

    """
    @see IRepositoryProvider
    """
    def provideRepository(self, r, ids=None):
      standard.writeBlock(self, "[provideRepository]: ids=%s"%str(ids))
      r = {}
      id = self.id
      d = {'id':id,'revision':'0.0.0','__filename__':['__init__.py']}
      r[id] = d
      r[id]['Opensearch'] = [{
        'id':'schema',
        'ob': {
          'filename':'schema.json',
          'data':self.getConfProperty('opensearch.schema','{}'),
          'version':'0.0.0',
          'meta_type':'File',
        }
      }]
      return r

    """
    @see IRepositoryProvider
    """
    def updateRepository(self, r):
      id = r['id']
      [self.setConfProperty('opensearch.schema',x['data']) for x in r['Opensearch'] if x['id'] == 'schema']
      return id

    """
    @see IRepositoryProvider
    """
    def translateRepositoryModel(self, r):
      d = {}
      return d

    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.get_client:
    # --------------------------------------------------------------------------
    def get_client(self):
      # ${opensearch.url:https://localhost:9200}
      # ${opensearch.username:admin}
      # ${opensearch.password:admin}
      # ${opensearch.ssl.verify:}
      url = self.getConfProperty('opensearch.url')
      if not url:
        return None
      host = urlparse(url).hostname
      port = urlparse(url).port
      ssl = urlparse(url).scheme=='https' and True or False
      verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
      username = self.getConfProperty('opensearch.username', 'admin')
      password = self.getConfProperty('opensearch.password', 'admin')
      auth = (username,password)
      
      client = OpenSearch(
        hosts = [{'host': host, 'port': port}],
        http_compress = False, # enables gzip compression for request bodies
        http_auth = auth,
        use_ssl = ssl,
        verify_certs = verify,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
      )
      return client


    # --------------------------------------------------------------------------
    #  ZMSZCatalogOpensearchConnector.search_json:
    # --------------------------------------------------------------------------
    def search_json(self, q, REQUEST, RESPONSE=None):
      """ ZMSZCatalogOpensearchConnector.search_json """

      qpage_index = REQUEST.get('pageIndex',0)
      qsize = REQUEST.get('size', 10)
      qfrom = REQUEST.get('from', qpage_index*qsize)
      index_name = self.getRootElement().getHome().id
      resp_text = ''

      query = {
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

      client = self.get_client()
      if not client:
        return '{"error":"No client"}'

      try:
        response = client.search(body = json.dumps(query), index = index_name)
        resp_text = json.dumps(response)
      except opensearchpy.exceptions.RequestError as e:
        resp_text = '//%s'%(e.error)

      REQUEST.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
      return resp_text


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
          self.setConfProperty('opensearch.schema', REQUEST['opensearch_schema'])
          self.setConfProperty('opensearch.parser', REQUEST['opensearch_parser'])
        return message

################################################################################
