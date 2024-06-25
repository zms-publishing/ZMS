## Script (Python) "ZMSDocument.standard_json"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: JSON Template: ZMSDocument
##
# --// standard_json //--
from Products.zms import standard
request = zmscontext.REQUEST

id = zmscontext.id
meta_id = zmscontext.meta_id
parent_id = zmscontext.getParentNode().id 
parent_meta_id = zmscontext.getParentNode().meta_id 
title = zmscontext.attr('title')
descripton = zmscontext.attr('attr_dc_descripton')
last_change_dt = zmscontext.attr('change_dt') or zmscontext.attr('created_dt')

block_seq = [{
	'id':id, 
	'meta_id':meta_id,
	'parent_id':parent_id,
	'parent_meta_id':parent_meta_id,
	'title':title,
	'descripton':descripton,
	'last_change_dt':last_change_dt
}]

# Get all pageelements
for pageelement in zmscontext.filteredChildNodes(request,zmscontext.PAGEELEMENTS):
	if pageelement.attr('change_dt') and pageelement.attr('change_dt') >= last_change_dt:
		last_change_dt = pageelement.attr('change_dt')
	json_block = []
	json_block = pageelement.attr('standard_json')
	if not json_block:
		html = ''
		try:
			html = pageelement.getBodyContent(request)
			# Clean html data
			html = standard.re_sub(r'<!--(.|\s|\n)*?-->', '', html)
			html = standard.re_sub(r'\n|\t|\s\s|\s>', '', html)
		except:
			html = 'Rendering Error: %s' % pageelement.meta_id
		# Create a json block
		json_block = [{
			'id': pageelement.id,
			'meta_id': pageelement.meta_id,
			'parent_id': pageelement.getParentNode().id,
			'parent_meta_id': pageelement.getParentNode().meta_id,
			'docx_format': 'html',
			'content': html
		}]
	block_seq.extend(json_block)

# Update last_change_dt
block_seq[0]['last_change_dt'] = last_change_dt

return block_seq

# --// /standard_json //--
