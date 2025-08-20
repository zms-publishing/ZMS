class ontology_node:
	"""
	python-representation of ontology_node
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
	id = "ontology_node"

	# Name
	name = "Ontology-Node"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "0.2.1"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"py"}

		key = {"default":""
			,"id":"key"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Key"
			,"repetitive":0
			,"type":"string"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Description"
			,"repetitive":0
			,"type":"attr_dc_description"}

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

		get_ontology_skos = {"default":""
			,"id":"get_ontology_skos"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get SKOS Ontology"
			,"repetitive":0
			,"type":"External Method"}

		icon_clazz = {"custom":"fas fa-tags"
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
			,"name":"README.md"
			,"repetitive":0
			,"type":"resource"}

		e = {"default":""
			,"id":"e"
			,"keys":["ontology_node"]
			,"mandatory":0
			,"multilang":0
			,"name":"Nodes"
			,"repetitive":1
			,"type":"*"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Ontology-Node"
			,"repetitive":0
			,"type":"zpt"}
