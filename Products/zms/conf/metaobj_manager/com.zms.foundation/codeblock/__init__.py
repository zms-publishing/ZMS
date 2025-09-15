class codeblock:
	"""
	python-representation of codeblock
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
	id = "codeblock"

	# Name
	name = "Code-Block"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		info = {"default":"HINT: This object contains programming code."
			,"id":"info"
			,"keys":[]
			,"name":"Info-Text"
			,"type":"string"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Code"
			,"type":"text"}

		codeeditor = {"default":""
			,"id":"codeeditor"
			,"keys":[]
			,"name":"codeeditor"
			,"type":"interface"}

		display = {"default":""
			,"id":"display"
			,"keys":["rendered"
				,"rendered_preview_only"
				,"as_raw_code"]
			,"name":"Display-Mode"
			,"type":"select"}

		attr_dc_accessrights_restrictededitors = {"default":""
			,"id":"attr_dc_accessrights_restrictedEditors"
			,"keys":["ZMSAdministrator"
				,"ZMSEditor"]
			,"name":"Access"
			,"type":"multiselect"}

		icon_clazz = {"custom":"fas fa-code"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		omit_div_container = {"default":"0"
			,"id":"omit_div_container"
			,"keys":[]
			,"name":"Omit DIV-Container"
			,"type":"boolean"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: HTML-Block"
			,"type":"zpt"}
