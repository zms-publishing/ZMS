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
	revision = "0.0.5"

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

		default_css = {"custom":".calendar nav {\r\n	display:flex;\r\n	flex-direction: row;\r\n	align-content: center;\r\n	justify-content: space-between;\r\n	margin:0 0 -3.5em 0;\r\n	padding:0 1em 0 1em;\r\n	z-index:100;\r\n	line-height:1;\r\n}\r\n.calendar nav a,\r\n.calendar nav a:hover {\r\n	text-decoration:none;\r\n	display:block;\r\n	padding-top:.5em;\r\n}\r\n.calendar nav i {\r\n	color:#b1d8de;\r\n	font-size:2em;\r\n	border:0px solid white;\r\n	line-height:1;\r\n	width:1.5em;\r\n	height:1.5em;\r\n	text-align:center;\r\n	padding-top:.275em;\r\n	border-radius:50%;\r\n	background:#00000033;\r\n}\r\n.calendar nav i.fa-chevron-left {\r\n	padding-right:.15em;\r\n}\r\n.calendar nav i.fa-chevron-right {\r\n	padding-left:.15em;\r\n}\r\n.calendar nav i:hover {\r\n	border-radius:50%;\r\n	background:#00000066;\r\n	color:white;\r\n}\r\n.calendar table th.month-head {\r\n	background-color:#17a2b8;\r\n	color:white;\r\n	font-size:2em;\r\n	padding: .2em .75rem;\r\n	font-weight:normal\r\n}\r\n.calendar table th.month-head:before {\r\n	content:\"\\f073\";\r\n	font-family: 'Font Awesome 5 Free';\r\n	font-weight: normal;\r\n	margin: 0 .5em 0 0;\r\n	-moz-osx-font-smoothing: grayscale;\r\n	-webkit-font-smoothing: antialiased;\r\n	display: inline-block;\r\n	font-style: normal;\r\n	font-variant: normal;\r\n	text-rendering: auto;\r\n	line-height: 1;\r\n	box-sizing: border-box;\r\n	display:inline-block;\r\n}\r\n.bs3 th.month-head:before {\r\n	content: \"\\e109\";\r\n	font-family \"Glyphicons Halflings\";\r\n}\r\n.calendar table td {\r\n	vertical-align:top;\r\n	width:6rem;\r\n}\r\n.calendar tr.hilight {\r\n    background:#d1ecf1 !important;\r\n}\r\n.calendar table td[data-toggle=\"tooltip\"]:hover {\r\n	background-color:#eee;\r\n	cursor:pointer;\r\n}\r\n.calendar table td span.day {\r\n	color:#aaa;\r\n}\r\n.calendar table td p {\r\n	width:6rem;\r\n	width: calc(842px / 7);\r\n	white-space:nowrap;\r\n	overflow:hidden;\r\n	text-overflow:ellipsis;\r\n	margin-top:.5em;\r\n}"
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
