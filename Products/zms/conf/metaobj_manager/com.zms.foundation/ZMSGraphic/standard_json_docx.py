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
# This Python script is used to generate a normalized JSON representation 
# of the object's content, which is then used by ZMS-action manage_export_pydocx 
# for exporting its content to a Word file.
# For further details, please refer to the docstring of 
# manage_export_pydocx.apply_standard_json_docx().
#
from Products.zms import standard
request = zmscontext.REQUEST

id = zmscontext.id
meta_id = zmscontext.meta_id
parent_id = zmscontext.getParentNode().id 
parent_meta_id = zmscontext.getParentNode().meta_id 
text = zmscontext.attr('text')
img = zmscontext.attr('imghires') or zmscontext.attr('img')
img_url = '%s/%s'%(zmscontext.absolute_url(),img.getHref(request).split('/')[-1])
imgwidth = img and int(img.getWidth()) or 0;
imgheight = img and int(img.getHeight()) or 0;

blocks = [
	{
		'id':'%s_img'%(id), 
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'docx_format':'image',
		'imgwidth':imgwidth,
		'imgheight':imgheight,
		'content':img_url
	},
	{
		'id':id,
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'docx_format':'Caption',
		'content':'[Abb. %s] %s'%(id, text)
	},
]

return blocks
# --// standard_json_docx //--
