class calendar:
	"""
	python-representation of calendar
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
	enabled = 1

	# Id
	id = "calendar"

	# Name
	name = "Calendar"

	# Package
	package = "com.zms.calendar"

	# Revision
	revision = "0.0.3"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Title"
			,"repetitive":0
			,"type":"string"}

		icon_clazz = {"custom":"fas fa-calendar text-info"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		events = {"default":""
			,"id":"events"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Calendar-Items"
			,"repetitive":0
			,"type":"calendar_items"}

		default_css = {"custom":".calendar table th.month-head {\r\n	background-color:#17a2b8;\r\n	color:white;\r\n}\r\n.calendar table td {\r\n	vertical-align:top;\r\n	width:6rem;\r\n}\r\n.calendar table td:hover {\r\n	background-color:#eee;\r\n}\r\n.calendar table td span.day {\r\n	color:#aaa;\r\n}\r\n.calendar table td p {\r\n	width:4rem;\r\n	white-space:nowrap;\r\n	overflow:hidden;\r\n	text-overflow:ellipsis;\r\n}"
			,"default":""
			,"id":"default_css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS Defaults"
			,"repetitive":0
			,"type":"constant"}

		get_events = {"default":""
			,"id":"get_events"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Process Events Data"
			,"repetitive":0
			,"type":"py"}

		get_calendar = {"default":""
			,"id":"get_calendar"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"External Method"
			,"repetitive":0
			,"type":"External Method"}

		test__calendar__get_events = {"default":""
			,"id":"test__calendar__get_events"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"TEST get_events"
			,"repetitive":0
			,"type":"Script (Python)"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Standard-Template"
			,"repetitive":0
			,"type":"zpt"}
