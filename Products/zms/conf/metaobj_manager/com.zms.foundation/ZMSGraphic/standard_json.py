## Script (Python) "ZMSGraphic.standard_json"
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
text = zmscontext.attr('text')
img = zmscontext.attr('img')
imghires = zmscontext.attr('imghires')
if img:
    img_url = img.getHref(request) 
if imghires:
    img_url = imghires.getHref(request)

blocks = [
	{
		'id':id, 
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'docx_format':'html',
		'content':'<p class="Caption">%s<p><img src="%s" />'%(text, img_url)
	}
]

return blocks
# --// standard_json //--
