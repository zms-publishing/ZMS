## Script (Python) "solr_breadcrumbs_obj_path"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='uid:3a0e21e5-998b-42e3-9337-ede65fe96780'
##title=py: Get Object Path from ZMSIndex as HTML
##
# --// solr_breadcrumbs_obj_path //--
request = container.REQUEST
response =  request.response
zmscontext = context.content
cat_attr_name = id.startswith('uid') and 'get_uid' or 'id'
zmsindex = zmscontext.getZMSIndex()

# return zms_data_id
# zmscontext.getLinkObj(zms_data_id, request)

catalog =zmsindex.get_catalog()
q = catalog({ cat_attr_name : str(id) })
obj_path = []
for r in q:
	uid = r['get_uid']
	pth = r['getPath']
	zms_data_id = '{$%s}'%uid
	# return '%s\n%s'%(zmsindex.getLinkObj(zms_data_id), r.getObject())
	# return zmscontext.getLinkObj(zms_data_id).attr('standard_html')
	obj_path = zmscontext.getLinkObj(zms_data_id).breadcrumbs_obj_path()

# Return HTML for Ajax-Requests
if len(obj_path) > 2:
	obj_path = obj_path[:-1]
return '\n'.join(['<li><a href="%s">%s</a></li>'%(obj.getHref2IndexHtml(request), obj.attr('titlealt')) for obj in obj_path])

# --// /solr_breadcrumbs_obj_path //--
