class ontology_collection:
	"""
	python-representation of ontology_collection
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
	id = "ontology_collection"

	# Name
	name = "Ontology-Collection"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "0.0.6"

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

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface"
			,"repetitive":0
			,"type":"interface"}

		queryinput = {"default":"1"
			,"id":"queryinput"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"GUI: Textinput"
			,"repetitive":0
			,"type":"boolean"}

		filtertype = {"default":""
			,"id":"filtertype"
			,"keys":["##"
				,"return ["
				,"(None,'No Filter shown'),"
				,"('parallel','Parallel Facet-Filtering'),"
				,"('sequential','Sequential Facet-Filtering'),"
				,"]"]
			,"mandatory":0
			,"multilang":0
			,"name":"GUI: Filter"
			,"repetitive":0
			,"type":"select"}

		navigationtype = {"default":""
			,"id":"navigationtype"
			,"keys":["##"
				,"return ["
				,"(None,'No Navigation shown'),"
				,"('pagination','Paginaton'),"
				,"('load','Load more...'),"
				,"]"]
			,"mandatory":0
			,"multilang":0
			,"name":"GUI: Navigation"
			,"repetitive":0
			,"type":"select"}

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

		new12 = {"default":""
			,"id":"new12"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"new12"
			,"repetitive":0
			,"type":""}
