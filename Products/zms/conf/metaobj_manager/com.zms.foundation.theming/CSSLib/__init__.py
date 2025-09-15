class CSSLib:
	"""
	python-representation of CSSLib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "CSSLib"

	# Name
	name = "CSSLib"

	# Package
	package = "com.zms.foundation.theming"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		default_scss = {"custom":"/* Example SCSS Code as a Content Object Attribute */\r\n$col-h2: green;\r\n.zmi_dummy {\r\n	h1 { color:red; }\r\n	h2 { color: $col-h2; }\r\n}"
			,"default":""
			,"id":"default_scss"
			,"keys":[]
			,"name":"Example SCSS"
			,"type":"constant"}

		default_css = {"custom":"/* Example CSS Code as a Content Object Attribute */\r\n.zmi_dummy h1 { color:red; }\r\n.zmi_dummy h2 { color: green; }"
			,"default":""
			,"id":"default_css"
			,"keys":[]
			,"name":"Example CSS"
			,"type":"constant"}

		compile_scss = {"default":""
			,"id":"compile_scss"
			,"keys":[]
			,"name":"SCSS Compile"
			,"type":"External Method"}

		get_metaobj_css = {"default":""
			,"id":"get_metaobj_css"
			,"keys":[]
			,"name":"Get MetaObj CSS"
			,"type":"py"}

		all_metaobj_css = {"default":""
			,"id":"all_metaobj_css"
			,"keys":[]
			,"name":"Aggregate All Default CSS"
			,"type":"py"}

		readme = {"custom":"The CSSLib contains some helper functions to deal with default CSS or SCSS snippets that \r\nare associated as attributes to the content objects. Typically there are two kinds of attributes \r\n1. id = 'default_(s)css', type = 'constant' \r\n2. id = 'f_css_defaults', type = 'resource/file'\r\n\r\nThree functions are provided to extract the CSS code stored in content model attributes:\r\n\r\nA. Function get_metaobj_css(meta_id='CSSLib', css_attr='default_scss', syntax='scss')\r\nExtracts the CSS text by a given meta_id and its attributes name. Moreover it calls \r\na SCSS preprocessor of the attributes name contains the phrase '_scss'.\r\n\r\nB. Function all_metaobj_css()\r\nIterates the whole content model and detects all CSS containing attributes by their names\r\ncontaining the phrases 'default' and ('_css' or '_scss'). For any CSS containing attribute the \r\nfunction get_metaobj_css will be called to extract/process the CSS text. The function will\r\nreturn an concatinated CSS text stream.\r\n\r\nC. Function compile_scss(scss)\r\nThis external methods needs pyScss to be installed in your python environment. It proesses the \r\nSCSS attribute values and returns CSS text.\r\n\r\nIntegrating all the default CSS snippets into the zmi oder web CSS is simply done by a single\r\nline of CSS code:\r\n\r\n/* EXAMPLE: CSS IMPORT RULE FOR ALL DEFAULTS */\r\n@import url('/content/metaobj_manager/csslib.all_metaobj_css');\r\n \r\n/* EXAMPLE: CSS IMPORT RULE FOR A DEFAULTS */\r\n@import url('/content/metaobj_manager/CSSLib.get_metaobj_css?meta_id=CSSLib&css_attr='default_css');\r\n\r\nSee also ZMS API functions:\r\n* ZMSObject.f_css_defaults\r\n* ZMSObject.zmi_css_defaults\r\n* standard.zmi_paths\r\nand the ZMS-Action\r\n* manage_css_classes"
			,"default":""
			,"id":"readme"
			,"keys":[]
			,"name":"README.md"
			,"type":"constant"}
