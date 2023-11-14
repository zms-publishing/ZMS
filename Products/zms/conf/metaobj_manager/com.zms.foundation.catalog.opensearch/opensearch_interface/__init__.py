class opensearch_interface:
	"""
	python-representation of opensearch_interface
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "opensearch_interface"

	# Name
	name = "Opensearch-Interface"

	# Package
	package = "com.zms.foundation.catalog.opensearch"

	# Revision
	revision = "0.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\r\n  {\r\n    \"id\": \"opensearch.url\",\r\n    \"type\": \"string\",\r\n    \"label\": \"URL\",\r\n    \"defaultValue\": \"https://localhost:9200\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.username\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Username\",\r\n    \"defaultValue\": \"admin\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.password\",\r\n    \"type\": \"password\",\r\n    \"label\": \"Password\",\r\n    \"defaultValue\": \"admin\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.schema\",\r\n    \"type\": \"text\",\r\n    \"label\": \"Schema\",\r\n    \"defaultValue\": \"{}\"\r\n  },\r\n  {\r\n    \"id\": \"opensearch.parser\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Parser\",\r\n    \"defaultValue\": \"http://localhost:9998/tika\"\r\n  }\r\n]"
			,"default":""
			,"id":"properties"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Property-Definitions (JSON)"
			,"repetitive":0
			,"type":"constant"}

		manage_opensearch_schematize = {"default":""
			,"id":"manage_opensearch_schematize"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Schematize"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_init = {"default":""
			,"id":"manage_opensearch_init"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Init"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_object_add = {"default":""
			,"id":"manage_opensearch_object_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Object: Index Opensearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_opensearch_object_remove = {"default":""
			,"id":"manage_opensearch_object_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Object: Delete Opensearch"
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
