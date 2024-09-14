## Script (Python) "bt_carousel.standard_json_docx"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: JSON-DOCX Template
##
# --// standard_json_docx //--
from Products.zms import standard
request = zmscontext.REQUEST
url_base = request.get('BASE0','')

blocks = []

for slide in zmscontext.filteredObjChildren('slides',request):
	id = slide.id
	title = slide.attr('title')
	text = slide.attr('text')
	url = slide.attr('url')
	img = slide.attr('image')
	src = img.getHref(request)

	docxml = f'''
		<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
			<w:bookmarkStart w:id="{id}" w:name="{id}"></w:bookmarkStart>
			<w:bookmarkEnd w:id="{id}"></w:bookmarkEnd>
			{f'<w:r><w:rPr><w:rStyle w:val="Bold"/></w:rPr><w:t>{title}</w:t><w:br/></w:r>' if title else ''}
			<w:r><w:t>{text}</w:t></w:r>
			{f'<w:r><w:br/><w:t>{url}</w:t></w:r>' if url else ''}
		</w:p>
	'''
	blocks.append( {
		'id': id,
		'meta_id': slide.meta_id,
		'parent_id': slide.getParentNode().id,
		'parent_meta_id': slide.getParentNode().meta_id,
		'docx_format': 'xml',
		'content': docxml
	} )

	blocks.append( {
		'id': '%s_1'%(id),
		'meta_id': slide.meta_id,
		'parent_id': slide.getParentNode().id,
		'parent_meta_id': slide.getParentNode().meta_id,
		'docx_format': 'image',
		'content': '//' in src and src or '%s%s'%(url_base, src)
	} )

return blocks

# --// /standard_json_docx //--
