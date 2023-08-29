## Script (Python) "get_object_by_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='e1758'
##title=Getting an ZMS-Object by Requesting an UID/ID on ZMSIndex
##
request = container.REQUEST
response =  request.response
zmscontext = context.content
cat_attr_name = id.startswith('uid') and 'get_uid' or 'id'
catalog = zmscontext.getZMSIndex().get_catalog()
q = catalog({ cat_attr_name : str(id) })
for r in q:
    uid = r['get_uid']
    pth = r['getPath']
    zms_data_id = '{$%s}'%uid
    # Return 1st catalog hit
    return zmscontext.getLinkObj(zms_data_id) #.get_uid()

return 'No Valid Document ID'
