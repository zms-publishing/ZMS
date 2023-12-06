class solr:
	"""
	python-representation of solr
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
	id = "solr"

	# Name
	name = "Solr-Page"

	# Package
	package = "com.zms.foundation.catalog.solr"

	# Revision
	revision = "0.3.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-sun text-danger"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
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

		scriptjs = {"default":""
			,"id":"script.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Script (JS)"
			,"repetitive":0
			,"type":"resource"}

		stylecss = {"default":""
			,"id":"style.css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Style (CSS)"
			,"repetitive":0
			,"type":"resource"}

		handlebarsjs = {"default":""
			,"id":"handlebars.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Handlebars: JS 4.7.7"
			,"repetitive":0
			,"type":"resource"}

		solr_breadcrumbs_obj_path = {"default":""
			,"id":"solr_breadcrumbs_obj_path"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Object Path from ZMSIndex as HTML"
			,"repetitive":0
			,"type":"Script (Python)"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: solr"
			,"repetitive":0
			,"type":"zpt"}
