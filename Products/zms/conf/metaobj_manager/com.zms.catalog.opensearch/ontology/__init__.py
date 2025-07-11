class ontology:
	"""
	python-representation of ontology
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
	id = "ontology"

	# Name
	name = "Ontology"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "0.0.7"

	# Type
	type = "ZMSRecordSet"

	# Attrs
	class Attrs:
		records = {"default":""
			,"id":"records"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Datensätze"
			,"repetitive":0
			,"type":"list"}

		grid = {"default":"0"
			,"id":"_grid"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Grid?"
			,"repetitive":0
			,"type":"boolean"}

		key = {"custom":1
			,"default":""
			,"id":"key"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Key"
			,"repetitive":0
			,"type":"string"}

		facet = {"custom":1
			,"default":""
			,"id":"facet"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Facet"
			,"repetitive":0
			,"type":"string"}

		ger = {"custom":1
			,"default":""
			,"id":"ger"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Deutsch"
			,"repetitive":0
			,"type":"string"}

		eng = {"custom":1
			,"default":""
			,"id":"eng"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"English"
			,"repetitive":0
			,"type":"string"}

		fra = {"custom":1
			,"default":""
			,"id":"fra"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Francais"
			,"repetitive":0
			,"type":"string"}

		get_ontology = {"default":""
			,"id":"get_ontology"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get (facetted) Ontology"
			,"repetitive":0
			,"type":"External Method"}

		get_ontology_attropts = {"default":""
			,"id":"get_ontology_attropts"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Attribute Options"
			,"repetitive":0
			,"type":"External Method"}

		icon_clazz = {"custom":"far fa-list-alt"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS-Icon"
			,"repetitive":0
			,"type":"constant"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"README.md"
			,"repetitive":0
			,"type":"resource"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Ontology"
			,"repetitive":0
			,"type":"zpt"}
