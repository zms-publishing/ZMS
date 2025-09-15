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
	revision = "5.2.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-align-left"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"name":"interface0"
			,"type":"interface"}

		format = {"default":"##\r\nreturn context.getTextFormatDefault()"
			,"id":"format"
			,"keys":[]
			,"mandatory":1
			,"name":"Format"
			,"type":"string"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"multilang":1
			,"name":"Text"
			,"type":"richtext"}

		check_constraints = {"default":""
			,"id":"check_constraints"
			,"keys":[]
			,"name":"Hook: check constraints"
			,"type":"py"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"name":"Readme (text/markdown)"
			,"type":"resource"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSTextarea"
			,"type":"zpt"}

		standard_json_docx = {"default":""
			,"id":"standard_json_docx"
			,"keys":[]
			,"name":"DOCX-JSON Template: ZMSTextarea"
			,"type":"py"}
