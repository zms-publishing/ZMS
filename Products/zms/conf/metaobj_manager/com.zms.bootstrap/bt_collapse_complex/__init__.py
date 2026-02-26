class bt_collapse_complex:
	"""
	python-representation of bt_collapse_complex
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
	enabled = 0

	# Id
	id = "bt_collapse_complex"

	# Name
	name = "Collapse Item (Complex)"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-indent"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		headline = {"default":""
			,"id":"headline"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Headline"
			,"repetitive":0
			,"type":"string"}

		body = {"default":""
			,"id":"body"
			,"keys":["type(ZMSObject)"
				,"type(ZMSRecordSet)"
				,"type(ZMSModule)"]
			,"mandatory":0
			,"multilang":0
			,"name":"Body"
			,"repetitive":1
			,"type":"*"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Complex-Item"
			,"repetitive":0
			,"type":"zpt"}
