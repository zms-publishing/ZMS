class bt_collapse:
	"""
	python-representation of bt_collapse
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
	id = "bt_collapse"

	# Name
	name = "Collapsible Content"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-align-justify"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
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

		stereotype = {"default":""
			,"id":"stereotype"
			,"keys":["Accordion"
				,"Tabs"]
			,"mandatory":0
			,"multilang":1
			,"name":"Stereotype"
			,"repetitive":0
			,"type":"select"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Title"
			,"repetitive":0
			,"type":"string"}

		items = {"default":""
			,"id":"items"
			,"keys":["bt_collapse_simple"
				,"bt_collapse_complex"]
			,"mandatory":0
			,"multilang":0
			,"name":"Items"
			,"repetitive":1
			,"type":"*"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Accordion"
			,"repetitive":0
			,"type":"zpt"}
