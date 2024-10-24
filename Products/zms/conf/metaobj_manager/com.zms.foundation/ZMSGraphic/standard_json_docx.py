## Script (Python) "ZMSGraphic.standard_json_docx"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=JSON
##
# --// standard_json_docx //--
from Products.zms import standard
request = zmscontext.REQUEST

id = zmscontext.id
meta_id = zmscontext.meta_id
parent_id = zmscontext.getParentNode().id 
parent_meta_id = zmscontext.getParentNode().meta_id 
text = zmscontext.attr('text')
img = zmscontext.attr('imghires') or zmscontext.attr('img')
img_url = img.getHref(request) 
imgwidth = img and int(img.getWidth()) or 0;
imgheight = img and int(img.getHeight()) or 0;

blocks = [
	{
		'id':id, 
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'docx_format':'Caption',
		'content':text
	},
	{
		'id':'%s_1'%(id), 
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'docx_format':'html',
		'content':'<img src="%s" width="%s" height="%s" />'%(img_url, imgwidth, imgheight)
	}
]

return blocks
# --// standard_json_docx //--
