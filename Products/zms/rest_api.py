################################################################################
# rest_api.py
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
import copy
import json
# Product Imports.
from Products.zms import _blobfields
from Products.zms import standard

class api(object):

    def __init__(self, **kwargs):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        #--print("Inside __init__()", kwargs)
        self.kwargs = kwargs

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        #--print("Inside __call__()")
        def wrapped_f(*args):
            #--print("Inside wrapped_f()")
            #--print("Decorator arguments:", self.kwargs)
            data = f(*args)
            #--print("After f(*args)")
            return self.kwargs['content_type'], data
        return wrapped_f


def get_lang_context(context):
    langs = context.getLangIds()
    monolang = context.REQUEST.get('lang') in langs
    langs = [context.REQUEST.get('lang')] if monolang else langs
    return monolang, langs


def get_meta_data(node):
    data = {}
    data['id'] = node.id
    data['meta_id'] = node.meta_id
    data['uid'] = node.get_uid()
    data['getPath'] = '/'.join(node.getPhysicalPath())
    return data


def get_rest_api_url(url):
    if '/content' in url:
        i = url.find('/content')+len('/content')
    elif '://' in url:
        i = url.find('://')+len('://')
        i = i+url[i:].find('/')
    return '%s/++rest_api%s'%(url[:i],url[i:])


def get_attr(node, id):
    value = node.attr(id)
    if isinstance(value,_blobfields.MyBlob):
        REQUEST = node.REQUEST
        d = {}
        d['href'] = value.getHref(REQUEST)
        d['filename'] = value.getFilename()
        d['content_type'] = value.getContentType()
        d['size'] = value.get_size()
        d['icon'] = standard.getMimeTypeIconSrc(value.getContentType())
        value = d
    return value


def get_attrs(self, node, REQUEST):
    monolang, langs = get_lang_context(node)
    data = get_meta_data(node)
    for lang in langs:
        REQUEST.set('lang',lang)
        id = 'active'
        data[id if monolang else '%s_%s'%(id,lang)] = node.isActive(REQUEST)
        id = 'title'
        data[id if monolang else '%s_%s'%(id,lang)] = node.getTitle(REQUEST)
        id = 'titlealt'
        data[id if monolang else '%s_%s'%(id,lang)] = node.getTitlealt(REQUEST)
    data['is_page'] = node.isPage()
    data['is_page_element'] = node.isPageElement()
    data['index_html'] = node.getHref2IndexHtmlInContext(node,REQUEST=REQUEST)
    data['parent_uid'] = node.breadcrumbs_obj_path()[-2].get_uid() if len(node.breadcrumbs_obj_path()) > 1 else None
    data['home_id'] = node.getHome().id
    data['level'] = node.getLevel()
    data['restricted'] = node.hasRestrictedAccess()
    obj_attrs = node.getObjAttrs()
    metaobj_attrs = node.getMetaobjManager().getMetaobjAttrs(node.meta_id)
    for metaobj_attr in metaobj_attrs:
        id = metaobj_attr['id']
        if id in obj_attrs:
            if metaobj_attr['multilang']:
                for lang in langs:
                    REQUEST.set('lang',lang)
                    data[id if monolang else '%s_%s'%(id,lang)] = get_attr(node,id)
            else:
                data[id] = get_attr(node,id)
    return data


class RestApiController(object):
    """
    RestApiController
    """

    def __init__(self, context, TraversalRequest):
        self.context = context
        self.method = TraversalRequest['REQUEST_METHOD']
        self.ids = copy.copy(TraversalRequest['path_to_handle'][1:])
        while self.ids:
            id = self.ids[0]
            if id.startswith('uid:'):
              context = context.getLinkObj('{$%s}'%id)
            elif id not in context.getPhysicalPath():
              context = getattr(self.context, id, None)
            if context is None:
                break
            self.context = context
            self.ids.remove(id)

    def __bobo_traverse__(self, TraversalRequest, name):
        return self

    __call____roles__ = None
    def __call__(self, REQUEST=None, **kw):
        """"""
        if self.method == 'GET':
            content_type, data = 'text/plain', {}
            if self.context.meta_type == 'ZMSIndex':
                content_type, data = self.zmsindex(self.context, REQUEST)
            elif self.context.meta_type == 'ZMSMetamodelProvider':
                content_type, data = self.metaobj_manager(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'get_body_content':
                content_type, self.get_body_content(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'list_parent_nodes':
                content_type, data = self.list_parent_nodes(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'list_child_nodes':
                content_type, data = self.list_child_nodes(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'list_tree_nodes':
                content_type, data = self.list_tree_nodes(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'get_parent_nodes':
                content_type, data = self.get_parent_nodes(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'get_child_nodes':
                content_type, data = self.get_child_nodes(self.context, REQUEST)
            elif self.ids and self.ids[0] == 'get_tree_nodes':
                content_type, data = self.get_tree_nodes(self.context, REQUEST)
            else:
                content_type, data = self.get(self.context, REQUEST)
            REQUEST.RESPONSE.setHeader('Content-Type',content_type)
            return json.dumps(data)
        return None
    
    @api(tag="zmsindex", pattern="/zmsindex", content_type="application/json")
    def zmsindex(self, context, REQUEST):
        catalog = context.get_catalog()
        q = {k:v for k,v in REQUEST.form.items() if v != ''}
        l = catalog(q)
        return [{item_name:r[item_name] for item_name in catalog.schema()} for r in l]

    @api(tag="metamodel", pattern="/metaobj_manager", content_type="application/json")
    def metaobj_manager(self, context, REQUEST):
        data = {}
        for id in context.getMetaobjIds():
            d = {}
            d['icon_clazz'] = context.aq_parent.zmi_icon(id)
            data[id] = d
        return data

    @api(tag="content", pattern="/{path}", method="GET", content_type="application/json")
    def get(self, context, REQUEST):
        return get_attrs(self, context, REQUEST)

    @api(tag="content", pattern="/{path}/get_body_content", method="GET", content_type="text/html")
    def get_body_content(self, context, REQUEST):
        return context.getBodyContent(REQUEST,forced=False)

    @api(tag="navigation", pattern="/{path}/list_parent_nodes", method="GET", content_type="application/json")
    def list_parent_nodes(self, context, REQUEST):
        nodes = context.breadcrumbs_obj_path()
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/list_child_nodes", method="GET", content_type="application/json")
    def list_child_nodes(self, context, REQUEST):
        id_prefix = REQUEST.get('id_prefix','e')
        meta_types = [context.PAGES if str(x)==str(context.PAGES) else context.PAGEELEMENTS if str(x)==str(context.PAGEELEMENTS) else x for x in REQUEST.get('meta_types').split(',')] if REQUEST.get('meta_types') else None
        nodes = context.getObjChildren(id_prefix, REQUEST, meta_types)
        if context.meta_type == 'ZMS':
            nodes.extend(context.getPortalClients())
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/list_tree_nodes", method="GET", content_type="application/json")
    def list_tree_nodes(self, context, REQUEST):
        nodes = context.getTreeNodes(REQUEST)
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_parent_nodes", method="GET", content_type="application/json")
    def get_parent_nodes(self, context, REQUEST):
        nodes = context.breadcrumbs_obj_path()
        return [get_attrs(self, x, REQUEST) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_child_nodes", method="GET", content_type="application/json")
    def get_child_nodes(self, context, REQUEST):
        id_prefix = REQUEST.get('id_prefix','e')
        meta_types = [context.PAGES if str(x)==str(context.PAGES) else context.PAGEELEMENTS if str(x)==str(context.PAGEELEMENTS) else x for x in REQUEST.get('meta_types').split(',')] if REQUEST.get('meta_types') else None
        nodes = context.getObjChildren(id_prefix, REQUEST, meta_types)
        if context.meta_type == 'ZMS':
            nodes.extend(context.getPortalClients())
        return [get_attrs(self, x, REQUEST) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_tree_nodes", method="GET", content_type="application/json")
    def get_tree_nodes(self, context, REQUEST):
        nodes = context.getTreeNodes(REQUEST)
        return [get_attrs(self, x, REQUEST) for x in nodes]