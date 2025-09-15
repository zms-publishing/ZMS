class ZMSFlexbox:
	"""
	python-representation of ZMSFlexbox
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
	id = "ZMSFlexbox"

	# Name
	name = "Flexbox-Container"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"icon-columns fas fa-columns"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon-Class (CSS)"
			,"type":"constant"}

		e = {"default":""
			,"id":"e"
			,"keys":["type(ZMSObject)"]
			,"name":"Items"
			,"repetitive":1
			,"type":"*"}

		f_css_defaults = {"custom":"@media only screen and (min-width: 576px) {\n	body:not(.zmi) .ZMSFlexbox:not(.contentEditable) {\n		display: flex;\n		flex-direction: row;\n		justify-content: space-between;\n	}\n	body:not(.zmi) .ZMSFlexbox:not(.contentEditable) .ZMSFlexboxItem {\n		flex-direction: column;\n		background: rgba(0,0,0,.05);\n		padding: 1rem;\n		margin:1rem 0;\n	}\n	body:not(.zmi) .ZMSFlexbox:not(.contentEditable) .ZMSFlexboxItem > * {\n		margin:0 !important;\n		padding:0 !important;\n	}\n	body:not(.zmi) .ZMSFlexbox .ZMSFlexboxItem {\n		flex-basis:calc((100% / var(--data-itemcount)) - 3rem);\n	}\n	body:not(.zmi) .ZMSFlexbox .ZMSFlexboxItem .ZMSGraphic .graphic,\n	body:not(.zmi) .ZMSFlexbox .ZMSFlexboxItem .ZMSGraphic .graphic img {\n		width:100% !important;\n		max-width:100% !important;\n	}\n	body:not(.zmi) .ZMSFlexbox .ZMSFlexboxItem .ZMSGraphic .text {\n		padding-top:1em;\n	}\n}\n}"
			,"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"name":"CSS Default"
			,"type":"constant"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: Box-Container"
			,"type":"zpt"}
