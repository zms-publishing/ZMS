class opensearch_connector:
	"""
	python-representation of opensearch_connector
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "opensearch_connector"

	# Lang_dict
	lang_dict = {"opensearch_connector.BTN_DESTROY":{"eng":"Delete Index"
			,"fra":"Supprimer l'index"
			,"ger":"Index löschen"
			,"ita":"Eliminare l'indice"}
		,"opensearch_connector.BTN_SCHEMATIZE":{"eng":"Create Schema (JSON)"
			,"fra":"Créer le schéma (JSON)"
			,"ger":"Schema erzeugen (JSON)"
			,"ita":"Creare lo schema (JSON)"}}

	# Name
	name = "Opensearch-Connector"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "1.12.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\n  {\n    \"id\": \"opensearch.url\",\n    \"type\": \"string\",\n    \"label\": \"URL(s)\",\n    \"default_value\": \"https://localhost:9200\",\n    \"is_target_of\": \"\"\n  },\n  {\n    \"id\": \"opensearch.url.timeout\",\n    \"type\": \"number\",\n    \"label\": \"URL-Timeout\",\n    \"default_value\": \"5\",\n    \"is_target_of\": \"\"\n  },\n  {\n    \"id\": \"opensearch.username\",\n    \"type\": \"string\",\n    \"label\": \"Username\",\n    \"default_value\": \"admin\",\n    \"is_target_of\": \"\"\n  },\n  {\n    \"id\": \"opensearch.password\",\n    \"type\": \"password\",\n    \"label\": \"Password\",\n    \"default_value\": \"admin\",\n    \"is_target_of\": \"\"\n  },\n  {\n    \"id\": \"opensearch.schema\",\n    \"type\": \"text\",\n    \"label\": \"Schema\",\n    \"default_value\": \"{}\",\n    \"is_target_of\": \"schematize\"\n  },\n  {\n    \"id\": \"opensearch.parser\",\n    \"type\": \"string\",\n    \"label\": \"Parser\",\n    \"default_value\": \"http://localhost:9998/tika\",\n    \"is_target_of\": \"\"\n  },\n  {\n    \"id\": \"opensearch.score_script\",\n    \"type\": \"text\",\n    \"label\": \"Score-Script (Painless)\",\n    \"default_value\": \"return _score;\",\n    \"is_target_of\": \"\"\n  }\n]"
			,"default":""
			,"id":"properties"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Property-Definitions (JSON)"
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

		manage_opensearch_schematize = {"default":""
			,"id":"manage_opensearch_schematize"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Schematize: Generate Schema"
			,"repetitive":0
			,"type":"External Method"}

		opensearch_get_client = {"default":""
			,"id":"opensearch_get_client"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Opensearch Client"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_init = {"default":""
			,"id":"manage_opensearch_init"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Init: Put Schema"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_objects_add = {"default":""
			,"id":"manage_opensearch_objects_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Index Opensearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_objects_remove = {"default":""
			,"id":"manage_opensearch_objects_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Delete Opensearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_objects_clear = {"default":""
			,"id":"manage_opensearch_objects_clear"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Clear Client from Opensearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_destroy = {"default":""
			,"id":"manage_opensearch_destroy"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Destroy: Delete Schema"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_test = {"default":""
			,"id":"manage_opensearch_test"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Test: OpenSearch connection"
			,"repetitive":0
			,"type":"External Method"}

		opensearch_query = {"default":""
			,"id":"opensearch_query"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Query"
			,"repetitive":0
			,"type":"External Method"}

		opensearch_suggest = {"default":""
			,"id":"opensearch_suggest"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Suggest"
			,"repetitive":0
			,"type":"External Method"}
