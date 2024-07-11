################################################################################
# ZMSZCatalogConnector.py
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
import json
import re
import sys
# Product Imports.
from Products.zms import standard
from Products.zms import IZMSCatalogConnector
from Products.zms import IZMSRepositoryProvider
from Products.zms import ZMSItem


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
class ZMSZCatalogConnector(
        ZMSItem.ZMSItem):

    # Properties.
    # -----------
    meta_type = 'ZMSZCatalogConnector'
    zmi_icon = "fas fa-search"

    # Management Interface.
    # ---------------------
    manage = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_zcatalog_connector', globals())
    manage_main = PageTemplateFile('zpt/ZMSZCatalogAdapter/manage_zcatalog_connector', globals())

    # Management Permissions.
    # -----------------------
    __administratorPermissions__ = (
        'manage_changeProperties', 'manage_main',
        )
    __ac_permissions__=(
        ('ZMS Administrator', __administratorPermissions__),
        )

    ############################################################################
    #  ZMSZCatalogConnector.__init__: 
    #
    #  Constructor.
    ############################################################################
    def __init__(self, id):
      self.id = id

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
    #  ZMSZCatalogConnector.getProperties
    # --------------------------------------------------------------------------
    def getProperties(self):
      return standard.parse_json(self.evalMetaobjAttr('%s.properties'%self.id))

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.getActions
    # --------------------------------------------------------------------------
    def getActions(self, pattern=None):
      root = self.getRootElement()
      metaobjAttrs = root.getMetaobjAttrs(self.id)
      actions = [root.getMetaobjAttr(self.id, x['id']) for x in metaobjAttrs if x['type'] in ['py','External Method','Script (Python)']]
      if pattern:
        actions = [x for x in actions if re.match(pattern,x['id'])]
      return actions

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_init
    # --------------------------------------------------------------------------
    def manage_init(self):
      [x['ob'](self) for x in self.getActions(r'^manage_(.*?)_init$')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_objects_add
    #
    #  @param   objects ((node, data), (node, data), (node, data), ...)
    #  @type    objects C{list|tuple} 
    #  @return  success, failed
    #  @rtype   C{tuple}
    # --------------------------------------------------------------------------
    def manage_objects_add(self, objects):
      return [x['ob'](self, objects) for x in self.getActions(r'^manage_(.*?)_objects_add$')][0]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_objects_remove
    # 
    #  @param   nodes
    #  @type    nodes C{list|tuple} 
    #  @return  success, failed
    #  @rtype   C{tuple}
    # --------------------------------------------------------------------------
    def manage_objects_remove(self, nodes):
      return [x['ob'](self, nodes) for x in self.getActions(r'^manage_(.*?)_objects_remove$')][0]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_objects_clear
    #
    #  @param home_id
    #  @type  objects list|tuple 
    #  @return success, failed
    #  @rtype  tuple
    # --------------------------------------------------------------------------
    def manage_objects_clear(self, home_id):
      return [x['ob'](self, home_id) for x in self.getActions(r'^manage_(.*?)_objects_clear$')][0]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.manage_destroy
    # --------------------------------------------------------------------------
    def manage_destroy(self):
      [x['ob'](self) for x in self.getActions(r'^manage_(.*?)_destroy$')]

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.search_json
    # --------------------------------------------------------------------------
    def search_json(self, REQUEST, RESPONSE):
      """ search_json """
      self.ensure_zcatalog_connector_is_initialized()
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
      result = [x['ob'](self, REQUEST) for x in self.getActions(r'(.*?)_query$')][0]
      return result

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.search_xml
    # --------------------------------------------------------------------------
    def search_xml(self, REQUEST, RESPONSE):
      """ search_xml """
      self.ensure_zcatalog_connector_is_initialized()
      result = json.loads(self.search_json(REQUEST, RESPONSE))
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'text/xml; charset=utf-8')
      # Assemble xml.
      status = result['status']
      num_found = result['numFound']
      start = result['start']
      docs = result['docs']
      xml = self.getXmlHeader()
      xml += '<response>'
      xml += '<lst name="responseHeader">'
      xml += '<int name="status">%i</int>'%status
      xml += '<lst name="params">'
      for key in REQUEST.form.keys():
        xml += '<str name="%s">%s</str>'%(key, standard.html_quote(REQUEST.form[key]))
      xml += '</lst>'
      xml += '</lst>'
      xmlr = ''
      if status <= 0:
        xmlr += '<result name="response" numFound="%i" start="%i">'%(num_found, start)
        for doc in docs:
          xmlr += '<doc>'
          for k in doc:
            try:
              v = doc[k]
              if k == 'zcat_column_loc':
                k = 'loc'
              elif k == 'zcat_column_index_html':
                k = 'index_html'
              elif k == 'zcat_column_custom':
                k = 'custom'
              elif k == 'standard_html':
                v = standard.remove_tags(v)
              xmlr += '<arr name="%s">'%k
              if isinstance(v,str):
                for x in range(16):
                  v = v.replace(chr(x), '')
              if k == 'custom':
                xmlr += '<str>%s</str>'%v
              else:
                xmlr += '<str><![CDATA[%s]]></str>'%v
              xmlr += '</arr>'
            except:
              standard.writeError(self, '[search_xml]: result=%s, k=%s'%(str(result), k))
              t, v, tb = sys.exc_info()
              status = 400
              msg = v
              break
          xmlr += '</doc>'
        xmlr += '</result>'
      else:
        msg = result.get('msg','ERROR')
        xmlr = ''
        xmlr += '<lst name="error">'
        xmlr += '<str name="msg">%s</str>'%standard.html_quote(msg)
        xmlr += '<int name="code">%i</int>'%status
        xmlr += '</lst>'
      xml += str(xmlr)
      xml += '</response>'
      if standard.pybool(REQUEST.get('pretty')):
        # Prettify xml
        import minidom
        xml = minidom.parseString(xml).toprettyxml(indent='  ')
      return xml


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.suggest_json
    # --------------------------------------------------------------------------
    def suggest_json(self, REQUEST, RESPONSE):
      """ suggest_json """
      self.ensure_zcatalog_connector_is_initialized()
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
      result = [x['ob'](self, REQUEST) for x in self.getActions(r'(.*?)_suggest$')][0]
      return result

    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.suggest_xml
    # --------------------------------------------------------------------------
    def suggest_xml(self, REQUEST, RESPONSE):
      """ suggest_xml """
      self.ensure_zcatalog_connector_is_initialized()
      result = json.loads(self.suggest_json(REQUEST, RESPONSE))
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'text/xml; charset=utf-8')
      # Assemble xml.
      status = result['status']
      xml = self.getXmlHeader()
      xml += '<response>'
      xml += '<lst name="responseHeader">'
      xml += '<int name="status">%i</int>'%status
      xml += '</lst>'
      if status <= 0:
        xml += '<lst>'
        xml += '<lst name="suggestions">'
        xml += '<int name="numFound">%i</int>'%len(results)
        xml += '<arr name="suggestion">'
        for result in results:
          xml += '<str>%s</str>'%result
        xml += '</arr>'
        xml += '</lst>'
        xml += '</lst>'
      else:
        msg = result.get('msg','ERROR')
        xml += '<lst name="error">'
        xml += '<str name="msg">%s</str>'%standard.html_quote(msg)
        xml += '<int name="code">%i</int>'%status
        xml += '</lst>'
      xml += '</response>'
      if standard.pybool(REQUEST.get('pretty')):
        # Prettify xml
        import minidom
        xml = minidom.parseString(xml).toprettyxml(indent='  ')
      return xml


    # --------------------------------------------------------------------------
    #  ZMSZCatalogConnector.reindex_page
    # --------------------------------------------------------------------------
    def reindex_page(self, uid, page_size, clients=False, fileparsing=True, REQUEST=None, RESPONSE=None):
      """ reindex_page """
      adapter = self.getCatalogAdapter()
      result = {'success':0,'failed':0,'log':[],'next_node':None}
      objects = []
      log = []
      nodes, next_node = self.get_next_page(uid, page_size, clients) 
      for node in nodes:
        # Clear client.
        if node.meta_id == 'ZMS':
          cleared = 0
          home_id = node.getHome().id
          result['home_id'] = home_id
          result['cleared'] = self.manage_objects_clear(home_id)[0]
        # Get catalog objects.
        d = {}
        for lang in node.getLangIds():
          REQUEST.set('lang', lang)
          node_objects = adapter.get_catalog_objects(node, fileparsing)
          objects.extend(node_objects)
          d[lang] = len(node_objects)
        log.append({'index':nodes.index(node),
          'path':'/'.join(node.getPhysicalPath()),
          'meta_id':node.meta_id,
          'objects':d})
      # Add objects.
      result['success'], result['failed'] = self.manage_objects_add(objects)
      # Return with log and next-node.
      result['log'], result['next_node'] = log, next_node
      RESPONSE.setHeader('Cache-Control', 'no-cache')
      RESPONSE.setHeader('Content-Type', 'application/json; charset=utf-8')
      return json.dumps(result,indent=2)

    ############################################################################
    #  ZMSZCatalogConnector.manage_changeProperties:
    #
    #  Change properties.
    ############################################################################
    def manage_changeProperties(self, btn, lang, REQUEST, RESPONSE):
        """
        manage_changeProperties
        """
        message = ''
        
        # Save.
        # -----
        if btn == 'BTN_SAVE':
          properties = self.getProperties()
          for property in properties:
            id = property['id']
            default_value = property['default_value']
            value = REQUEST.get(id,default_value)
            if property.get('type','string') == 'password':
              if value:
                self.setConfProperty(id, value)
            else:
              self.setConfProperty(id, value)
          message += self.getZMILangStr('MSG_CHANGED')

        elif btn == 'BTN_CANCEL':
          pass

        # Return with message.
        message = standard.url_quote(message)
        return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s#%s'%(lang, message, REQUEST.get('tab')))

################################################################################
