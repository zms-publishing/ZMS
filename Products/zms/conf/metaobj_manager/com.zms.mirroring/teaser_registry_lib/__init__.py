class teaser_registry_lib:
	"""
	python-representation of teaser_registry_lib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "teaser_registry_lib"

	# Name
	name = "Teaser Registry Lib"

	# Package
	package = "com.zms.mirroring"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		register_teaser = {"default":""
			,"id":"register_teaser"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Execute Teaser Registration"
			,"repetitive":0
			,"type":"External Method"}

		teaser_registry_sql_create = {"default":""
			,"id":"teaser_registry/sql_create"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sql_create"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sql_upsert = {"default":""
			,"id":"teaser_registry/sql_upsert"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sql_upsert"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sql_select = {"default":""
			,"id":"teaser_registry/sql_select"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sql_select"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sql_update_datetime = {"default":""
			,"id":"teaser_registry/sql_update_datetime"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sql_update_datetime"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sql_delete = {"default":""
			,"id":"teaser_registry/sql_delete"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sql_delete"
			,"repetitive":0
			,"type":"Z SQL Method"}

		icon_clazz = {"custom":"fas fa-flask text-success"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		teaser_registry_tryout = {"default":""
			,"id":"teaser_registry/tryout"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Try Out (Test)"
			,"repetitive":0
			,"type":"Script (Python)"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"README.md"
			,"repetitive":0
			,"type":"resource"}

		teaser_registry_index_html = {"default":""
			,"id":"teaser_registry/index_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Preview"
			,"repetitive":0
			,"type":"Page Template"}
