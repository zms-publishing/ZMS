## Script (Python) "ZMSTextarea.standard_json"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=JSON
##
# --// standard_json //--
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
	"headline_1" : "Heading1",
	"headline_2" : "Heading2",
	"headline_3" : "Heading3",
	"headline_4" : "Heading4",
	"headline_5" : "Heading5",
	"headline_6" : "Heading6",
	"ordered_list" : "ListBullet",
	"unordered_list" : "ListBullet",
	"plain_html": "html",
	"wysiwyg" : "html",
}

block_seq = []

block1 = dict({
	'id':id, 
	'meta_id':meta_id,
	'parent_id':parent_id,
	'parent_meta_id':parent_meta_id,
	"docx_format":format_docx_map.get(format,'Normal'), 
	'content':text
})

block_seq.append(block1)

return block_seq
# --// standard_json //--
