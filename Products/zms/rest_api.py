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
from Products.zms import mock_http
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
        def wrapped_f(*args, **kwargs):
            #--print("Inside wrapped_f()", args, kwargs)
            #--print("Decorator arguments:", self.kwargs)
            data = f(*args)
            #--print("After f(*args)")
            decoration = {x for x in kwargs if kwargs.get(x)}
            if decoration:
                return {x:self.kwargs.get(x) for x in decoration}, data
            return data
        return wrapped_f


def _get_request(context):
    request = getattr(context,'REQUEST',mock_http.MockHTTPRequest())
    return request


def _get_context(context):
    request = _get_request(context)
    lang_ids = context.getLangIds()
    lang = request.get('lang',None)
    monolang = lang is not None
    langs = [lang] if monolang else lang_ids
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


def get_attrs(node):
    request = _get_request(node)
    monolang, langs = _get_context(node)
    data = get_meta_data(node)
    for lang in langs:
        request.set('lang',lang)
        id = 'active'
        data[id if monolang else '%s_%s'%(id,lang)] = node.isActive(request)
        id = 'title'
        data[id if monolang else '%s_%s'%(id,lang)] = node.getTitle(request)
        id = 'titlealt'
        data[id if monolang else '%s_%s'%(id,lang)] = node.getTitlealt(request)
    data['is_page'] = node.isPage()
    data['is_page_element'] = node.isPageElement()
    data['index_html'] = node.getHref2IndexHtmlInContext(node,REQUEST=request)
    data['parent_uid'] = node.breadcrumbs_obj_path()[-2].get_uid() if len(node.breadcrumbs_obj_path()) > 1 else None
    data['home_id'] = node.getHome().id
    data['level'] = node.getLevel()
    data['restricted'] = node.hasRestrictedAccess()
    if node.meta_id == 'ZMS':
        data['has_portal_clients'] = node.getPortalClients() != []
    general_keys = data.keys()
    obj_attrs = node.getObjAttrs()
    try:
        metaobj_attrs = node.getMetaobjManager().getMetaobjAttrs(node.meta_id)
    except:
        # In case node is a ZMSProxy object:
        metaobj_attrs = node.proxy.getMetaobjManager().getMetaobjAttrs(node.meta_id)
    for metaobj_attr in metaobj_attrs:
        id = metaobj_attr['id']
        if id in obj_attrs and not id in general_keys:
            if metaobj_attr['multilang']:
                for lang in langs:
                    request.set('lang',lang)
                    data[id if monolang else '%s_%s'%(id,lang)] = get_attr(node,id)
            else:
                data[id] = get_attr(node,id)
    # print("data",data)
    return data


class RestApiController(object):
    """
    RestApiController
    """

    def __init__(self, context=None, TraversalRequest=None):
        if context and TraversalRequest:
            self.context = context
            self.method = TraversalRequest['REQUEST_METHOD']
            self.path_to_handle = copy.copy(TraversalRequest['path_to_handle'])
            self.ids = [x for x in self.path_to_handle if x != '++rest_api'] # remove ++rest_api as first element
            while self.ids:
                id = self.ids[0]
                print(id,context)
                if id.startswith('uid:'):
                  context = context.getLinkObj('{$%s}'%id)
                elif id not in context.getPhysicalPath():
                  context = getattr(self.context, id, None)
                if context is None or not getattr(context,'meta_type',None):
                    break
                self.context = context
                self.ids.remove(id)

    def __bobo_traverse__(self, TraversalRequest, name):
        return self

    __call____roles__ = None
    def __call__(self, REQUEST=None, **kw):
        """"""
        standard.writeBlock(self.context,'__call__: %s'%str(self.ids))
        if self.method == 'GET':
            decoration, data = {'content_type':'text/plain'}, {}
            if  self.ids == [] and self.context.meta_type == 'ZMSIndex':
                decoration, data = self.zmsindex(self.context, content_type=True)
            elif self.ids == [] and self.context.meta_type == 'ZMSMetamodelProvider':
                decoration, data = self.metaobj_manager(self.context, content_type=True)
            elif self.ids == ['get_body_content']:
                decoration, data = self.get_body_content(self.context, content_type=True)
            elif self.ids == ['list_parent_nodes']:
                decoration, data = self.list_parent_nodes(self.context, content_type=True)
            elif self.ids == ['list_child_nodes']:
                decoration, data = self.list_child_nodes(self.context, content_type=True)
            elif self.ids == ['list_tree_nodes']:
                decoration, data = self.list_tree_nodes(self.context, content_type=True)
            elif self.ids == ['get_parent_nodes']:
                decoration, data = self.get_parent_nodes(self.context, content_type=True)
            elif self.ids == ['get_child_nodes']:
                decoration, data = self.get_child_nodes(self.context, content_type=True)
            elif self.ids == ['get_tree_nodes']:
                decoration, data = self.get_tree_nodes(self.context, content_type=True)
            elif self.ids == [] or self.ids == ['get']:
                decoration, data = self.get(self.context, content_type=True)
            else:
                data = {'ERROR':'Not Found','context':str(self.context),'path_to_handle':self.path_to_handle,'ids':self.ids}
            REQUEST.RESPONSE.setHeader('Content-Type',decoration['content_type'])
            return json.dumps(data)
        return None

    @api(tag="zmsindex", pattern="/zmsindex", content_type="application/json")
    def zmsindex(self, context):
        request = _get_request(context)
        catalog = context.get_catalog()
        q = {k.replace('[]',''):v for k,v in request.form.items() if v != ''}
        l = catalog(q)
        return [{item_name:(r[item_name] or '') for item_name in catalog.schema()} for r in l]

    @api(tag="metamodel", pattern="/metaobj_manager", content_type="application/json")
    def metaobj_manager(self, context):
        data = {}
        for id in context.getMetaobjIds():
            d = {}
            d['icon_clazz'] = context.aq_parent.zmi_icon(id)
            data[id] = d
        return data

    @api(tag="content", pattern="/{path}", method="GET", content_type="application/json")
    def get(self, context):
        return get_attrs(context)

    @api(tag="content", pattern="/{path}/get_body_content", method="GET", content_type="text/html")
    def get_body_content(self, context):
        request = _get_request(context)
        return context.getBodyContent(request, forced=False)

    @api(tag="navigation", pattern="/{path}/list_parent_nodes", method="GET", content_type="application/json")
    def list_parent_nodes(self, context):
        nodes = context.breadcrumbs_obj_path()
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/list_child_nodes", method="GET", content_type="application/json")
    def list_child_nodes(self, context):
        request = _get_request(context)
        id_prefix = request.get('id_prefix','')
        meta_types = [context.PAGES if str(x)==str(context.PAGES) else context.PAGEELEMENTS if str(x)==str(context.PAGEELEMENTS) else x for x in request.get('meta_types').split(',')] if request.get('meta_types') else None
        nodes = context.getObjChildren(id_prefix, request, meta_types)
        if context.meta_type == 'ZMS':
            nodes.extend(context.getPortalClients())
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/list_tree_nodes", method="GET", content_type="application/json")
    def list_tree_nodes(self, context):
        request = _get_request(context)
        nodes = context.getTreeNodes(request)
        return [get_meta_data(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_parent_nodes", method="GET", content_type="application/json")
    def get_parent_nodes(self, context):
        nodes = context.breadcrumbs_obj_path()
        return [get_attrs(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_child_nodes", method="GET", content_type="application/json")
    def get_child_nodes(self, context):
        request = _get_request(context)
        id_prefix = request.get('id_prefix','')
        meta_types = [context.PAGES if str(x)==str(context.PAGES) else context.PAGEELEMENTS if str(x)==str(context.PAGEELEMENTS) else x for x in request.get('meta_types').split(',')] if request.get('meta_types') else None
        nodes = context.getObjChildren(id_prefix, request, meta_types)
        if context.meta_type == 'ZMS':
            nodes.extend(context.getPortalClients())
        return [get_attrs(x) for x in nodes]

    @api(tag="navigation", pattern="/{path}/get_tree_nodes", method="GET", content_type="application/json")
    def get_tree_nodes(self, context):
        request = _get_request(context)
        nodes = context.getTreeNodes(request)
        return [get_attrs(x) for x in nodes]
