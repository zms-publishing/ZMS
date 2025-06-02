class elasticsearch_connector:
	"""
	python-representation of elasticsearch_connector
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "elasticsearch_connector"

	# Lang_dict
	lang_dict = {"elasticsearch_connector.BTN_DESTROY":{"eng":"Delete Index"
			,"ger":"Index löschen"}
		,"elasticsearch_connector.BTN_SCHEMATIZE":{"eng":"Create Schema (JSON)"
			,"ger":"Schema erzeugen (JSON)"}}

	# Name
	name = "elasticsearch-Connector"

	# Package
	package = "com.zms.catalog.elasticsearch"

	# Revision
	revision = "1.10.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\r\n  {\r\n    \"id\": \"elasticsearch.url\",\r\n    \"type\": \"string\",\r\n    \"label\": \"URL\",\r\n    \"default_value\": \"https://localhost:9200\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.url.timeout\",\r\n    \"type\": \"number\",\r\n    \"label\": \"URL-Timeout\",\r\n    \"default_value\": \"5\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.username\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Username\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.password\",\r\n    \"type\": \"password\",\r\n    \"label\": \"Password\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.index_name\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Index Name\",\r\n    \"default_value\": \"\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.schema\",\r\n    \"type\": \"text\",\r\n    \"label\": \"Schema\",\r\n    \"default_value\": \"{}\",\r\n    \"is_target_of\": \"schematize\"\r\n  },\r\n  {\r\n    \"id\": \"elasticsearch.parser\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Parser\",\r\n    \"default_value\": \"http://localhost:9998/tika\",\r\n    \"is_target_of\": \"\"\r\n  }\r\n]"
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

		manage_elasticsearch_schematize = {"default":""
			,"id":"manage_elasticsearch_schematize"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Schematize: Generate Schema"
			,"repetitive":0
			,"type":"External Method"}

		elasticsearch_get_client = {"default":""
			,"id":"elasticsearch_get_client"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Elasticsearch Client"
			,"repetitive":0
			,"type":"External Method"}

		manage_elasticsearch_init = {"default":""
			,"id":"manage_elasticsearch_init"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Init: Put Schema"
			,"repetitive":0
			,"type":"External Method"}

		manage_elasticsearch_objects_add = {"default":""
			,"id":"manage_elasticsearch_objects_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Index elasticsearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_elasticsearch_objects_remove = {"default":""
			,"id":"manage_elasticsearch_objects_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Delete elasticsearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_elasticsearch_objects_clear = {"default":""
			,"id":"manage_elasticsearch_objects_clear"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Clear Client from elasticsearch"
			,"repetitive":0
			,"type":"External Method"}

		manage_elasticsearch_destroy = {"default":""
			,"id":"manage_elasticsearch_destroy"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Destroy: Delete Schema"
			,"repetitive":0
			,"type":"External Method"}

		elasticsearch_query = {"default":""
			,"id":"elasticsearch_query"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Query"
			,"repetitive":0
			,"type":"External Method"}

		elasticsearch_suggest = {"default":""
			,"id":"elasticsearch_suggest"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Suggest"
			,"repetitive":0
			,"type":"External Method"}
