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
			,"mandatory":0
			,"multilang":0
			,"name":"Info-Text"
			,"repetitive":0
			,"type":"string"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Code"
			,"repetitive":0
			,"type":"text"}

		codeeditor = {"default":""
			,"id":"codeeditor"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"codeeditor"
			,"repetitive":0
			,"type":"interface"}

		display = {"default":""
			,"id":"display"
			,"keys":["rendered"
				,"rendered_preview_only"
				,"as_raw_code"]
			,"mandatory":0
			,"multilang":0
			,"name":"Display-Mode"
			,"repetitive":0
			,"type":"select"}

		attr_dc_accessrights_restrictededitors = {"default":""
			,"id":"attr_dc_accessrights_restrictedEditors"
			,"keys":["ZMSAdministrator"
				,"ZMSEditor"]
			,"mandatory":0
			,"multilang":0
			,"name":"Access"
			,"repetitive":0
			,"type":"multiselect"}

		icon_clazz = {"custom":"fas fa-code"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		omit_div_container = {"default":"0"
			,"id":"omit_div_container"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Omit DIV-Container"
			,"repetitive":0
			,"type":"boolean"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: HTML-Block"
			,"repetitive":0
			,"type":"zpt"}
