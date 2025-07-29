class url_extract_page:
	"""
	python-representation of url_extract_page
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
	id = "url_extract_page"

	# Name
	name = "URL-Extract Page"

	# Package
	package = "com.zms.mirroring"

	# Revision
	revision = "5.1.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-file-import text-primary"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"titlealt"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		content_url = {"default":"https://www.uniklinikum-jena.de/Uniklinikum+Jena/Wir+%C3%BCber+uns/Portrait/Geschichte.html"
			,"id":"content_url"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Absolute URL"
			,"repetitive":0
			,"type":"url"}

		content_node = {"default":"div.content-bottom"
			,"id":"content_node"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Node-Selector"
			,"repetitive":0
			,"type":"string"}

		css_custom = {"default":".media {\n    float: left;\n    margin: .5rem 2rem 0 0;\n    max-width:30%;\n}\n.media img {\n    max-width: 100%;\n}\np {\n    text-align: left !important;\n}\nh1.maintitle {\n    display: none;\n}\nbody.zmi h1.maintitle {\n    display: block;\n}"
			,"id":"css_custom"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Custom-CSS"
			,"repetitive":0
			,"type":"text"}

		url_extracting = {"default":""
			,"id":"url_extracting"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"URL Content Extaction"
			,"repetitive":0
			,"type":"External Method"}

		content_preview = {"default":""
			,"id":"content_preview"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"content_preview"
			,"repetitive":0
			,"type":"interface"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: URL-Extract"
			,"repetitive":0
			,"type":"zpt"}
