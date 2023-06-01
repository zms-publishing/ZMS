class opensearch:
	"""
	python-representation of opensearch
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
	id = "opensearch"

	# Name
	name = "Opensearch"

	# Package
	package = "com.zms.foundation.zcatalog.opensearch"

	# Revision
	revision = "0.1.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-search text-danger"
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

		get_breadcrumbs_by_uuid = {"default":""
			,"id":"get_breadcrumbs_by_uuid"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Object Path from ZMSIndex as HTML"
			,"repetitive":0
			,"type":"Script (Python)"}

		add_docmt_to_opensearch_index = {"default":""
			,"id":"add_docmt_to_opensearch_index"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"(Re-)Index an ZMS node by given UUID"
			,"repetitive":0
			,"type":"External Method"}

		beforeCommitObjChangesEvt = {"default":""
			,"id":"beforeCommitObjChangesEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Calling Global Change-Event Handler for (Re-)Indexing a Document"
			,"repetitive":0
			,"type":"Script (Python)"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Opensearch"
			,"repetitive":0
			,"type":"zpt"}
