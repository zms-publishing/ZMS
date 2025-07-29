class infobox:
	"""
	python-representation of infobox
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":"{$}"
		,"insert_deny":[]}

	# Enabled
	enabled = 1

	# Id
	id = "infobox"

	# Name
	name = "Infobox"

	# Package
	package = "com.zms.custom"

	# Revision
	revision = "0.0.1"

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

		url = {"default":""
			,"id":"url"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Url"
			,"repetitive":0
			,"type":"url"}

		linktext = {"default":"Read more..."
			,"id":"linktext"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Linktext"
			,"repetitive":0
			,"type":"string"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Description"
			,"repetitive":0
			,"type":"text"}

		icon_clazz = {"custom":"fa fa-puzzle-piece"
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon Class"
			,"repetitive":0
			,"type":"constant"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Standard-Template (ZPT)"
			,"repetitive":0
			,"type":"zpt"}

