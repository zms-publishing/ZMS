## Script (Python) "opensearch_breadcrumbs_obj_path"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='uid:3a0e21e5-998b-42e3-9337-ede65fe96780'
##title=py: Get Object Path from ZMSIndex as HTML
##
# --// opensearch_breadcrumbs_obj_path //--
request = container.REQUEST
response =  request.response
zmscontext = context.content
cat_attr_name = id.startswith('uid') and 'get_uid' or 'id'
zmsindex = zmscontext.getZMSIndex()

# return zms_data_id
# zmscontext.getLinkObj(zms_data_id, request)

catalog =zmsindex.get_catalog()
q = catalog({ cat_attr_name : str(id) })
zmsobj = None
zmsobj_path = []
for r in q:
	uid = r['get_uid']
	pth = r['getPath']
	zms_data_id = '{$%s}'%uid
	# return '%s\n%s'%(zmsindex.getLinkObj(zms_data_id), r.getObject())
	# return zmscontext.getLinkObj(zms_data_id).attr('standard_html')
	zmsobj = zmscontext.getLinkObj(zms_data_id)
	if zmsobj:
		zmsobj_path = zmsobj.breadcrumbs_obj_path(portalMaster=False)

## Return HTML for Ajax-Requests
if len(zmsobj_path) > 2:
	zmsobj_path = zmsobj_path[:-1]
## #############################################
## A. Basic URL Generation: getHref2IndexHtml()
return '\n'.join(['<li><a href="%s">%s</a></li>'%(obj.getHref2IndexHtml(request), obj.attr('titlealt')) for obj in zmsobj_path if obj.attr('titlealt')])
## #############################################
## B. Specific URL Generation: custom function getHref2SubdomainHtml()
# return '\n'.join(['<li><a href="%s">%s</a></li>'%(zmscontext.UniBE_zeix_('getHref2SubdomainHtml',item=obj), obj.attr('titlealt')) for obj in zmsobj_path if obj.attr('titlealt')])
## #############################################

# --// /opensearch_breadcrumbs_obj_path //--
