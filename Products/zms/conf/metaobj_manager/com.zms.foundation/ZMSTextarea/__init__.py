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

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Readme (text/markdown)"
			,"repetitive":0
			,"type":"resource"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSTextarea"
			,"repetitive":0
			,"type":"zpt"}

		standard_json = {"default":""
			,"id":"standard_json"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JSON"
			,"repetitive":0
			,"type":"py"}
