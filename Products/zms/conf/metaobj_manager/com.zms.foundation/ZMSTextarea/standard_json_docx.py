## Script (Python) "ZMSTextarea.standard_json_docx"
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
format = zmscontext.attr('format')
text = zmscontext.attr('text')

format_docx_map = {
	"body" : "Normal",
	"blockquote" : "Quote",
	"caption" : "Caption",
	"headline_1" : "Heading 1",
	"headline_2" : "Heading 2",
	"headline_3" : "Heading 3",
	"headline_4" : "Heading 4",
	"headline_5" : "Heading 5",
	"headline_6" : "Heading 6",
	"headline_7" : "Heading 7",
	"headline_8" : "Heading 8",
	"ordered_list" : "ListBullet",
	"unordered_list" : "ListBullet",
	"plain_html": "html",
	"wysiwyg" : "html",
}

blocks = [
	{
		'id':id, 
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		"docx_format":format_docx_map.get(format,'Normal'), 
		'content':text
	}
]

return blocks
# --// standard_json_docx //--
