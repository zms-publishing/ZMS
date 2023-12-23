class lunr_page:
	"""
	python-representation of lunr_page
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "lunr_page"

	# Name
	name = "Lunr-Page"

	# Package
	package = "com.zms.catalog.lunr"

	# Revision
	revision = "1.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-moon text-warning"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		lunr_page_css_picomincss = {"default":""
			,"id":"lunr_page/css/pico.min.css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"pico.min.css"
			,"repetitive":0
			,"type":"File"}

		lunr_page_js_lunrjs = {"default":""
			,"id":"lunr_page/js/lunr.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"lunr.js"
			,"repetitive":0
			,"type":"File"}

		lunr_page_js_mainjs = {"default":""
			,"id":"lunr_page/js/main.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"main.js"
			,"repetitive":0
			,"type":"File"}

		lunr_page_js_workerjs = {"default":""
			,"id":"lunr_page/js/worker.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"worker.js"
			,"repetitive":0
			,"type":"File"}

		lunr_page_index_html = {"default":""
			,"id":"lunr_page/index_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"index.html"
			,"repetitive":0
			,"type":"Page Template"}
