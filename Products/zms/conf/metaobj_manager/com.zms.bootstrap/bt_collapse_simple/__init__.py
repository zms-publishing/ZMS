class bt_collapse_simple:
	"""
	python-representation of bt_collapse_simple
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
	id = "bt_collapse_simple"

	# Name
	name = "Collapse Item (Simple)"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-grip-lines"
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
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Body"
			,"repetitive":0
			,"type":"richtext"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Simple-Item"
			,"repetitive":0
			,"type":"zpt"}
