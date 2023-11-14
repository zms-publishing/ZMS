class zcatalog_interface:
	"""
	python-representation of zcatalog_interface
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "zcatalog_interface"

	# Name
	name = "ZCatalog-Interface"

	# Package
	package = "com.zms.foundation.catalog.zcatalog"

	# Revision
	revision = "0.0.0"

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

		manage_zcatalog_object_add = {"default":""
			,"id":"manage_zcatalog_object_add"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Object: Catalog to ZCatalog"
			,"repetitive":0
			,"type":"External Method"}

		manage_zcatalog_object_remove = {"default":""
			,"id":"manage_zcatalog_object_remove"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Object: Uncatalog from ZCatalog"
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
