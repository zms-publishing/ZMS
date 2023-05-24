class bt_link_list:
	"""
	python-representation of bt_link_list
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
	id = "bt_link_list"

	# Name
	name = "Links"

	# Package
	package = "com.zms.foundation.bootstrap"

	# Revision
	revision = "5.0.4"

	# Type
	type = "ZMSResource"

	# Attrs
	class Attrs:
		links = {"default":""
			,"id":"links"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Links"
			,"repetitive":0
			,"type":"list"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}
