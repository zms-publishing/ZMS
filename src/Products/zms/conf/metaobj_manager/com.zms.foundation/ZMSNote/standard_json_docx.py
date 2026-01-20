## Script (Python) "ZMSNote.standard_json_docx"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: JSON-DOCX Template
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
text = zmscontext.attr('text')
author = zmscontext.attr('change_uid')
# date = '2024-01-01T00:00:00Z'
date = '%sZ'%standard.format_datetime_iso(zmscontext.attr('change_dt'))[0:-6]
zmsnote_langstr = zmscontext.getZMILangStr('TYPE_ZMSNOTE')

blocks = []

text = '%s: %s, %s\n%s'%(zmsnote_langstr, author, date, text)

blocks.append(
	{
		'id': id,
		'meta_id': zmscontext.meta_id,
		'parent_id': zmscontext.getParentNode().id,
		'parent_meta_id': zmscontext.getParentNode().meta_id,
		'docx_format': 'ZMSNotiz',
		'content': text
	}
)

return blocks
# --// /standard_json_docx //--

