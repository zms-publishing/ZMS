class ZMSTextarea:
	"""
	python-representation of ZMSTextarea
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""]}

	# Enabled
	enabled = 1

	# Id
	id = "ZMSTextarea"

	# Name
	name = "ZMSTextarea"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-align-left"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		readme = {"custom":"# ZMSTextarea\r\nZMSTextarea is the standard element for text blocks. It offers two kind of input fields:\r\n\r\n1. plain text\r\n2. rich-text (wysiswyg)\r\n\r\nThe ZMSTextarea-GUI is customzied by text-format definitions for:\r\n\r\n1. paragraphs (block formats like h1, h2, p)\r\n2. characters (inline formats like bold, italic)\r\n\r\nA paragraph format is declared for the whole text block, whereas character formats can nest any text string inline.\r\nBoth plain text and richt-text editors provide a list of the configured block formats. But inly the plan text editor \r\ncan be customizd by the configured character formats, because the rich-text editor frontends integrate a set of inline \r\nformat by themselves.\r\nFor the plain text editor a helper funcion for valifdating the html/XML wellformedness by setting a configuration parameter:\r\n`ZMS.ZMSTextarea.show_htmlcheck`: 1\r\n\r\n## Rich Text / WYSIWYG Exitors\r\n\r\nBy default ZMS comes with three types of richt text editors (RTE)\r\n\r\n1. CKEditor (HTML)\r\n2. TinyMCE (HTML)\r\n3. SimpleMDE (Markdown)\r\n\r\nThe list of RTE can be extendes by adding a TAL-based template `manage_form` as a plugins to the plugin-rte-folder:\r\n`Products/zms/plugins/rte/`.  \r\nThe editor's JS/GUI-asset files can be placed in the as `++resource++zms_` registred resource folder\r\n`Products/zms/plugins/www`\r\nTo tell the ZMS client which one of the RTEs should be applied, a configuration parameter has to be set:\r\n`ZMS.richtext.plugin` (ckeditor, tinymce, simplemde etc.)\r\n\r\n## Using Markdown\r\nThe SimpleMDE-editor is a minimal markdown editor using the Python module *markdown*. This module will be installed \r\nby default (if code base is fresh), see on [github](https://github.com/zms-publishing/ZMS/blob/main/requirements-full.txt).\r\n\r\nAfter setting ZMS configuration parameter \r\n`ZMS.richtext.plugin`: `simplemde`\r\nat least a paragraph format named `markdown` is needed. ZMS provides a suitable set of paragraph formats named \r\n`markdown-0.0.1` for one-click-import: it contains the markdown format as the standard format and a typical set \r\nof several html block elements. "
			,"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Readme.md"
			,"repetitive":0
			,"type":"constant"}

		format = {"default":"##\r\nreturn context.getTextFormatDefault()"
			,"id":"format"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Format"
			,"repetitive":0
			,"type":"string"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Text"
			,"repetitive":0
			,"type":"richtext"}

		check_constraints = {"default":""
			,"id":"check_constraints"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Hook: check constraints"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSTextarea"
			,"repetitive":0
			,"type":"zpt"}
