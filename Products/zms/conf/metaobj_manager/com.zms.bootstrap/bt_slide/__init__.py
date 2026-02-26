class bt_slide:
	"""
	python-representation of bt_slide
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
	id = "bt_slide"

	# Name
	name = "Carousel-Slide"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-image"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		image = {"default":""
			,"id":"image"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Image"
			,"repetitive":0
			,"type":"image"}

		image_filter = {"default":""
			,"id":"image_filter"
			,"keys":["##"
				,"return ["
				,"('#00000000','No Filter'),"
				,"('#00000033','12% Darker'),"
				,"('#00000066','25% Darker'),"
				,"('#00000099','40% Darker')"
				,"]"]
			,"mandatory":0
			,"multilang":0
			,"name":"Image Filter"
			,"repetitive":0
			,"type":"select"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"title"
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

		url = {"default":""
			,"id":"url"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Link"
			,"repetitive":0
			,"type":"url"}

		url_title = {"default":""
			,"id":"url_title"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Link-Titel"
			,"repetitive":0
			,"type":"string"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Slide"
			,"repetitive":0
			,"type":"zpt"}
