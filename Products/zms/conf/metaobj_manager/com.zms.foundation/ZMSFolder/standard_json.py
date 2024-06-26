## Script (Python) "ZMSFolder.standard_json"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: JSON Template: ZMSFolder
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
url = zmscontext.getHref2IndexHtml(request)

# 1st block is container meta data
blocks = [
	{
		'id':id,
		'url':url,
		'meta_id':meta_id,
		'parent_id':parent_id,
		'parent_meta_id':parent_meta_id,
		'title':title,
		'descripton':descripton,
		'last_change_dt':last_change_dt
	}
]

# Sequence all pageelements
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
			html = '<table>'
			html += '<caption>Rendering Error: %s</caption>' % pageelement.meta_id
			attrs = [d['id'] for d in zmscontext.getMetaobjAttrs(pageelement.meta_id) if d['type'] not in ['dtml','zpt','py','constant','resource','interface']]
			for attr in attrs:
				html += '<tr><td>%s</td><td>%s</td></tr>' % (attr, pageelement.attr(attr))
			html += '</table>'
		# Create a json block
		json_block = [{
			'id': pageelement.id,
			'meta_id': pageelement.meta_id,
			'parent_id': pageelement.getParentNode().id,
			'parent_meta_id': pageelement.getParentNode().meta_id,
			'docx_format': 'html',
			'content': html
		}]
	blocks.extend(json_block)

# Update last_change_dt
blocks[0]['last_change_dt'] = last_change_dt

return blocks

# --// /standard_json //--
