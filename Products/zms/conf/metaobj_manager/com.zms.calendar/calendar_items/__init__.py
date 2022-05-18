class calendar_items:
	"""
	python-representation of calendar_items
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""
			,""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""
			,""
			,""
			,""]}

	# Enabled
	enabled = 0

	# Id
	id = "calendar_items"

	# Name
	name = "Calendar Items"

	# Package
	package = "com.zms.calendar"

	# Revision
	revision = "0.0.2"

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

		col_id = {"default":""
			,"id":"col_id"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"COL_ID"
			,"repetitive":0
			,"type":"identifier"}

		start_time = {"custom":1
			,"default":""
			,"id":"start_time"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Start Date/Time"
			,"repetitive":0
			,"type":"datetime"}

		end_time = {"custom":1
			,"default":""
			,"id":"end_time"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"End Date/Time"
			,"repetitive":0
			,"type":"datetime"}

		title = {"custom":1
			,"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Title"
			,"repetitive":0
			,"type":"string"}

		description = {"custom":1
			,"default":""
			,"id":"description"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Description"
			,"repetitive":0
			,"type":"text"}

		url = {"default":""
			,"id":"url"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Link"
			,"repetitive":0
			,"type":"url"}

		icon_clazz = {"custom":"far fa-list-alt text-info"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Calendar Data"
			,"repetitive":0
			,"type":"zpt"}
