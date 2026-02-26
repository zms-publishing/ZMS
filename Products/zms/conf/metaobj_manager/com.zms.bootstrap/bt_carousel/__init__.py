class bt_carousel:
	"""
	python-representation of bt_carousel
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
	id = "bt_carousel"

	# Name
	name = "Carousel"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-images"
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

		interval = {"default":"5000"
			,"id":"interval"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Interval"
			,"repetitive":0
			,"type":"int"}

		indicators = {"default":"1"
			,"id":"indicators"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Show indicators"
			,"repetitive":0
			,"type":"boolean"}

		controls = {"default":"1"
			,"id":"controls"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Show controls (prev/next)"
			,"repetitive":0
			,"type":"boolean"}

		captions = {"default":"1"
			,"id":"captions"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Show captions"
			,"repetitive":0
			,"type":"boolean"}

		slides = {"default":""
			,"id":"slides"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Slides"
			,"repetitive":1
			,"type":"bt_slide"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Carousel"
			,"repetitive":0
			,"type":"zpt"}

		standard_json_docx = {"default":""
			,"id":"standard_json_docx"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JSON-DOCX Template"
			,"repetitive":0
			,"type":"py"}
