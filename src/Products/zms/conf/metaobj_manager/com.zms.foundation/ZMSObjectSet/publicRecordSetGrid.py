## Script (Python) "ZMSObjectSet.publicRecordSetGrid"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Grid record-set.
##
# --// publicRecordSetGrid //--

request = container.REQUEST
RESPONSE =  request.RESPONSE
zmscontext.zmi_page_request(zmscontext,request)
url = request['HTTP_REFERER']+'?'
url = url[:url.find('?')]
request.set('URL',url)

attr_ids = zmscontext.attr('record_attrs')
metaObjAttrs =[{'id':'objectset','name':'','type':'html'}] \
		+attr_ids \
		+[{'id':'change_uid','name':zmscontext.getZMILangStr('BY'),'type':'string'}] \
		+[{'id':'change_dt','name':zmscontext.getZMILangStr('ON'),'type':'datetime'}]
metaObjAttrIds = ['__id__']+[x['id'] for x in metaObjAttrs]
zmscontext.attr('recordSet_Prepare')
# hook: objectset-filter
for record_meta_id in zmscontext.attr('record_meta_ids'):
	if 'objectset_interface' in zmscontext.getMetaobjAttrIds(record_meta_id):
		zmscontext.evalMetaobjAttr('%s.objectset_filter'%record_meta_id)

return zmscontext.metaobj_recordset_main_grid( \
		metaObjAttrIds=metaObjAttrIds, \
		metaObjAttrs=metaObjAttrs, \
		record_handler=zmscontext.attr('record_handler'), \
		records=request['res'], \
		filtered_records=request['res'], \
		actions=['insert','update','delete','cut','copy','paste'], \
		insert='[[INSERT]]', \
		update='[[UPDATE]]', \
		delete='zmiObjectSetDelete(this)', \
		cut='zmiObjectSetCut(this)', \
		copy='zmiObjectSetCopy(this)', \
		paste='zmiObjectSetPaste(this)', \
		)

# --// /publicRecordSetGrid //--
