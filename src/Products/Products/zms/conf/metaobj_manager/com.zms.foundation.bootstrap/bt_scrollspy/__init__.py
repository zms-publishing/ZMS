class bt_scrollspy:
	"""
	python-representation of bt_scrollspy
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
	id = "bt_scrollspy"

	# Name
	name = "Scrollspy"

	# Package
	package = "com.zms.foundation.bootstrap"

	# Revision
	revision = "0.0.0"

	# Type
	type = "ZMSRecordSet"

	# Attrs
	class Attrs:
		records = {"default":""
			,"id":"records"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Datensätze"
			,"repetitive":0
			,"type":"list"}

		bt_id = {"default":""
			,"id":"bt_id"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Id"
			,"repetitive":0
			,"type":"identifier"}

		title = {"custom":1
			,"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Title"
			,"repetitive":0
			,"type":"string"}

		body = {"custom":1
			,"default":""
			,"id":"body"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Body"
			,"repetitive":0
			,"type":"text"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Scrollspy"
			,"repetitive":0
			,"type":"zpt"}
