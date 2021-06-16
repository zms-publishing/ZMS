class bt_jumbotron:
	"""
	python-representation of bt_jumbotron
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
	id = "bt_jumbotron"

	# Name
	name = "Jumbotron"

	# Package
	package = "com.zms.foundation.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-republican"
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

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
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
			,"type":"richtext"}

		links = {"default":""
			,"id":"links"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Links"
			,"repetitive":0
			,"type":"bt_link_list"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Jumbotron"
			,"repetitive":0
			,"type":"zpt"}
