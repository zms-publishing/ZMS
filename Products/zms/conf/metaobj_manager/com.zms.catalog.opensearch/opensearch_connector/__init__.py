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
			,"ger":"Index löschen"}
		,"opensearch_connector.BTN_SCHEMATIZE":{"eng":"Create Schema (JSON)"
			,"ger":"Schema erzeugen (JSON)"}}

	# Name
	name = "Opensearch-Connector"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "1.10.2"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\r\n  {\r\n    \"id\": \"opensearch.url\",\r\n    \"type\": \"string\",\r\n    \"label\": \"URL(s)\",\r\n    \"default_value\": \"https://localhost:9200\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.url.timeout\",\r\n    \"type\": \"number\",\r\n    \"label\": \"URL-Timeout\",\r\n    \"default_value\": \"5\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.username\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Username\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.password\",\r\n    \"type\": \"password\",\r\n    \"label\": \"Password\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.schema\",\r\n    \"type\": \"text\",\r\n    \"label\": \"Schema\",\r\n    \"default_value\": \"{}\",\r\n    \"is_target_of\": \"schematize\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.parser\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Parser\",\r\n    \"default_value\": \"http://localhost:9998/tika\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.score_script\",\r\n    \"type\": \"text\",\r\n    \"label\": \"Score-Script (Painless)\",\r\n    \"default_value\": \"return _score;\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.suggest.fields.unibe\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Suggest-Fields: unibe\",\r\n    \"default_value\": \"['title', 'attr_dc_description']\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.suggest.fields.unitel\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Suggest-Fields: unitel\",\r\n    \"default_value\": \"['Vorname', 'Nachname']\",\r\n    \"is_target_of\": \"\"\r\n  }\r\n]"
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
