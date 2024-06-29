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

blocks = []

for slide in zmscontext.filteredObjChildren('slides',request):
    docxml = f'''
        <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:bookmarkStart w:id="{slide.id}" w:name="{slide.id}"></w:bookmarkStart>
            <w:bookmarkEnd w:id="{slide.id}"></w:bookmarkEnd>
        	<w:r>
        		<w:t>Hello, </w:t>
        	</w:r>
        	<w:r>
        	<w:rPr>
        		<w:rStyle w:val="Emphasis"/>
        	</w:rPr>
        		<w:t>world!</w:t>
        	</w:r>
        </w:p>
    '''
    blocks.append( {
        'id': slide.id,
        'meta_id': slide.meta_id,
        'parent_id': slide.getParentNode().id,
        'parent_meta_id': slide.getParentNode().meta_id, 
        'docx_format': 'xml',
        'content': docxml
    } )

return blocks

# --// /standard_json_docx //--
