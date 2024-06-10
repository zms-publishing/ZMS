class zcatalog_connector:
	"""
	python-representation of zcatalog_connector
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "zcatalog_connector"

	# Lang_dict
	lang_dict = {"zcatalog_connector.BTN_DESTROY":{"eng":"Delete ZCatalog"
			,"ger":"ZCatalog löschen"}}

	# Name
	name = "ZCatalog-Connector"

	# Package
	package = "com.zms.catalog.zcatalog"

	# Revision
	revision = "1.0.3"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[\r\n]"
			,"default":""
			,"id":"properties"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Property-Definitions (JSON)"
			,"repetitive":0
			,"type":"constant"}

		manage_zcatalog_init = {"default":""
			,"id":"manage_zcatalog_init"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Init: Create ZCatalog(s)"
			,"repetitive":0
			,"type":"External Method"}

		manage_zcatalog_objects_add = {"default":""
			,"id":"manage_zcatalog_objects_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Catalog to ZCatalog"
			,"repetitive":0
			,"type":"External Method"}

		manage_zcatalog_objects_remove = {"default":""
			,"id":"manage_zcatalog_objects_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Uncatalog from ZCatalog"
			,"repetitive":0
			,"type":"External Method"}

		manage_zcatalog_objects_clear = {"default":""
			,"id":"manage_zcatalog_objects_clear"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects: Clear Client from ZCatalog"
			,"repetitive":0
			,"type":"External Method"}

		manage_zcatalog_destroy = {"default":""
			,"id":"manage_zcatalog_destroy"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Destroy: Delete ZCatalog(s)"
			,"repetitive":0
			,"type":"External Method"}

		zcatalog_query = {"default":""
			,"id":"zcatalog_query"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Query"
			,"repetitive":0
			,"type":"External Method"}

		zcatalog_suggest = {"default":""
			,"id":"zcatalog_suggest"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Suggest"
			,"repetitive":0
			,"type":"External Method"}
