class ontology_results:
	"""
	python-representation of ontology_results
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
	id = "ontology_results"

	# Name
	name = "Ontology-Results"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "0.0.1"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		attr_dc_subject = {"default":""
			,"id":"attr_dc_subject"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Subject"
			,"repetitive":0
			,"type":"attr_dc_subject"}

		icon_clazz = {"custom":"fas fa-table"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS-Icon"
			,"repetitive":0
			,"type":"constant"}

		ontology_query = {"default":""
			,"id":"ontology_query"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Query"
			,"repetitive":0
			,"type":"External Method"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Ontology-Results"
			,"repetitive":0
			,"type":"zpt"}
