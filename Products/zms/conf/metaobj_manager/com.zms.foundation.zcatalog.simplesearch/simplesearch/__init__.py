class simplesearch:
	"""
	python-representation of simplesearch
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "simplesearch"

	# Name
	name = "SimpleSearch powered by Lunr"

	# Package
	package = "com.zms.foundation.zcatalog.simplesearch"

	# Revision
	revision = "0.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-search text-warning"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"README"
			,"repetitive":0
			,"type":"resource"}

		simplesearch_css_picomincss = {"default":""
			,"id":"simplesearch/css/pico.min.css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"pico.min.css"
			,"repetitive":0
			,"type":"File"}

		simplesearch_js_lunrjs = {"default":""
			,"id":"simplesearch/js/lunr.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"lunr.js"
			,"repetitive":0
			,"type":"File"}

		simplesearch_js_mainjs = {"default":""
			,"id":"simplesearch/js/main.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"main.js"
			,"repetitive":0
			,"type":"File"}

		simplesearch_js_workerjs = {"default":""
			,"id":"simplesearch/js/worker.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"worker.js"
			,"repetitive":0
			,"type":"File"}

		simplesearch_index_html = {"default":""
			,"id":"simplesearch/index_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"index.html"
			,"repetitive":0
			,"type":"Page Template"}
