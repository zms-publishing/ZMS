class bt_card:
	"""
	python-representation of bt_card
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
	id = "bt_card"

	# Name
	name = "Card"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		header = {"default":""
			,"id":"header"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Header (Optional)"
			,"repetitive":0
			,"type":"string"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		image = {"default":""
			,"id":"image"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Image (286x180)"
			,"repetitive":0
			,"type":"image"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Title"
			,"repetitive":0
			,"type":"string"}

		subtitle = {"default":""
			,"id":"subtitle"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Subtitle"
			,"repetitive":0
			,"type":"string"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Text"
			,"repetitive":0
			,"type":"text"}

		footer = {"default":""
			,"id":"footer"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Footer (Optional)"
			,"repetitive":0
			,"type":"string"}

		links = {"default":""
			,"id":"links"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Links"
			,"repetitive":0
			,"type":"bt_link_list"}

		icon_clazz = {"custom":"far fa-address-card"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Card"
			,"repetitive":0
			,"type":"zpt"}
