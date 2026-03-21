"""
ZMSMetamodelProvider.py - ZMS Metamodel Provider

Defines ZMSMetamodelProvider for central management of ZMS meta-objects and meta-dictionaries.
The provider serves as a repository for meta-model definitions, including schema and constraint data,
and offers ZMI interfaces for editing and synchronizing these definitions. It supports acquisition
from a portal master and provides repository import/export functionality for content synchronization.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

# Imports.
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import copy
from zope.interface import implementer
# Product Imports.
from Products.zms import standard
from Products.zms import IZMSConfigurationProvider, IZMSRepositoryProvider
from Products.zms import IZMSMetamodelProvider, ZMSMetaobjManager, ZMSMetadictManager
from Products.zms import ZMSItem


@implementer(
        IZMSConfigurationProvider.IZMSConfigurationProvider,
        IZMSMetamodelProvider.IZMSMetamodelProvider,
        IZMSRepositoryProvider.IZMSRepositoryProvider,)
class ZMSMetamodelProvider(
        ZMSItem.ZMSItem,
        ZMSMetaobjManager.ZMSMetaobjManager,
        ZMSMetadictManager.ZMSMetadictManager):
    """
    Central provider for ZMS object-model definitions (meta-objects and
    meta-dictionaries), including ZMI management and repository I/O.
    """

    meta_type = 'ZMSMetamodelProvider'
    zmi_icon = "fas fa-briefcase"
    icon_clazz = zmi_icon

    # Management Options.
    manage_options_default_action = '../manage_customize'
    def manage_options(self):
      return [self.operator_setitem( x, 'action', '../'+x['action']) for x in copy.deepcopy(self.aq_parent.manage_options())]

    manage_sub_options__roles__ = None
    def manage_sub_options(self):
      return (
        {'label': 'TAB_METADATA','action': 'manage_metas'},
        {'label': 'TAB_METAOBJ','action': 'manage_main'},
        )

    # Management Interface.
    manage = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main', globals())
    manage_main = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main', globals())
    manage_main_import = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main_import', globals())
    manage_main_acquire = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_main_acquire', globals())
    manage_bigpicture = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_bigpicture', globals())
    manage_analyze = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_analyze', globals())
    manage_metas = PageTemplateFile('zpt/ZMSMetamodelProvider/manage_metas', globals())

    # Management Permissions.
    __administratorPermissions__ = (
      'manage_changeProperties', 'manage_ajaxChangeProperties', 'manage_main', 'manage_main_import', 'manage_bigpicture',
      'manage_changeMetaProperties', 'manage_metas',
    )
    __authorPermissions__ = (
        'manage_bigpicture',
        'metaobj_readme',
    )
    __ac_permissions__=(
      ('ZMS Administrator', __administratorPermissions__),
      ('ZMS Author', __authorPermissions__),
    )

    # --------------------------------------------------------------------------
    #  ZMSMetamodelProvider.metaobj_readme:
    #  Serve a metaobj's readme resource as rendered HTML.
    # --------------------------------------------------------------------------
    def metaobj_readme(self, REQUEST):
      """Returns a metaobj's readme resource rendered as HTML."""
      meta_id = REQUEST.get('id', '')
      attr = self.getMetaobjAttr(meta_id, 'readme')
      if attr and 'ob' in attr:
        readme_txt = attr['ob'].data.decode('utf-8')
        html = self.renderText('markdown', 'text', readme_txt, REQUEST, meta_id)
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/html;charset=utf-8')
        return '<article class="zmi-readme">%s</article>'%html
      return ''


    def __init__(self, model={}, metas=[]):
      """Initialise the metaobj/metadict manager with an optional model dict and metas list."""
      self.id = 'metaobj_manager'
      self.model = model.copy()
      self.metas = copy.deepcopy(metas)


    def getConfProperty(self, key, default=None):
      """Return configuration property from the root content object, or default."""
      v = default
      try:
        if self.content is not None:
          v = self.content.getConfProperty(key, default)
      except:
        pass
      return v


    def __bobo_traverse__(self, TraversalRequest, name):
      """
      Custom traversal hook that resolves attributes and delegates upward
      through portal hierarchy when not found locally.
      """
      attr = getattr( self, name, None)
      if attr is not None:
        return attr
      
      # otherwise do some 'magic'
      else:
        standard.writeLog(self, "[ZMSMetamodelProvider.__bobo_traverse__]: otherwise do some 'magic'")
        ob = self.getHome().aq_parent
        while ob is not None:
          content = getattr( ob, 'content', None)
          if content is not None:
            metaobj_manager = getattr( content, self.id, None)
            if metaobj_manager is not None:
              # If the name is in the list of attributes, call it.
              attr = getattr( metaobj_manager, name, None)
              if attr is not None:
                return attr
          ob = getattr( ob, 'aq_parent', None)
        return None


    def provideRepository(self, ids=None):
      """
      Export all local model and meta-dictionary records into a repository dict.

      @param ids: Optional subset of record ids to include.
      @type ids: C{list} | C{None}
      @return: Repository payload keyed by record id.
      @rtype: C{dict}
      """
      standard.writeBlock(self, "[provideRepository]: ids=%s"%str(ids))
      r = {}
      self.provideRepositoryMetas(r, ids)
      self.provideRepositoryModel(r, ids)
      return r


    def updateRepository(self, r):
      """
      Import one record from a repository payload into the local model.

      @param r: Repository record mapping.
      @type r: C{dict}
      @return: Imported record id.
      @rtype: C{str}
      """
      id = r['id']
      self.updateRepositoryMetas(r)
      self.updateRepositoryModel(r)
      return id
