class solr_connector:
	"""
	python-representation of solr_connector
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "solr_connector"

	# Lang_dict
	lang_dict = {"solr_connector.BTN_DESTROY":{"eng":"Delete Index"
			,"ger":"Index löschen"}
		,"solr_connector.BTN_SCHEMATIZE":{"eng":"Create Schema (JSON)"
			,"ger":"Schema erzeugen (JSON)"}}

	# Name
	name = "Solr-Connector"

	# Package
	package = "com.zms.catalog.solr"

	# Revision
	revision = "1.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\r\n  {\r\n    \"id\": \"solr.url\",\r\n    \"type\": \"string\",\r\n    \"label\": \"URL\",\r\n    \"default_value\": \"http://localhost:8983/solr\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"solr.username\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Username\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"solr.password\",\r\n    \"type\": \"password\",\r\n    \"label\": \"Password\",\r\n    \"default_value\": \"admin\",\r\n    \"is_target_of\": \"\"\r\n  },\r\n  {\r\n    \"id\": \"solr.schema\",\r\n    \"type\": \"text\",\r\n    \"label\": \"Schema\",\r\n    \"default_value\": \"{}\",\r\n    \"is_target_of\": \"schematize\"\r\n  },\r\n  {\r\n    \"id\": \"solr.parser\",\r\n    \"type\": \"string\",\r\n    \"label\": \"Parser\",\r\n    \"default_value\": \"http://localhost:9998/tika\",\r\n    \"is_target_of\": \"\"\r\n  }\r\n]"
			,"default":""
			,"id":"properties"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Property-Definitions (JSON)"
			,"repetitive":0
			,"type":"constant"}

		manage_solr_schematize = {"default":""
			,"id":"manage_solr_schematize"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Schematize: Generate Schema"
			,"repetitive":0
			,"type":"External Method"}

		manage_solr_init = {"default":""
			,"id":"manage_solr_init"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Init: Put Schema"
			,"repetitive":0
			,"type":"External Method"}

		manage_solr_objects_add = {"default":""
			,"id":"manage_solr_objects_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Index Solr"
			,"repetitive":0
			,"type":"External Method"}

		manage_solr_objects_remove = {"default":""
			,"id":"manage_solr_objects_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Delete Solr"
			,"repetitive":0
			,"type":"External Method"}

		manage_solr_objects_clear = {"default":""
			,"id":"manage_solr_objects_clear"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Clear Client from Solr"
			,"repetitive":0
			,"type":"External Method"}

		manage_solr_destroy = {"default":""
			,"id":"manage_solr_destroy"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Destroy: Delete Schema"
			,"repetitive":0
			,"type":"External Method"}

		solr_query = {"default":""
			,"id":"solr_query"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Query"
			,"repetitive":0
			,"type":"External Method"}

		solr_suggest = {"default":""
			,"id":"solr_suggest"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Suggest"
			,"repetitive":0
			,"type":"External Method"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"readme.md"
			,"repetitive":0
			,"type":"resource"}
