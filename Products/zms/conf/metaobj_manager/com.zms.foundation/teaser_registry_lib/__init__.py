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
	package = "com.zms.foundation"

	# Revision
	revision = "0.0.3"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		readme = {"custom":"First insert a ZSQLiteDA object named 'teasers' \r\nconnected to $INSTANCE_HOME/var/sqlite/teasers.sqlite'.\r\nThen add a python attribute-method onChangeObjEvt to\r\nthe teaser content model:\r\n##############################\r\n# --// onChangeObjEvt //--\r\nfrom Products.zms import standard\r\nrequest = container.REQUEST\r\nRESPONSE =  request.RESPONSE\r\ntry:\r\n    zmscontext.register_teaser()\r\nexcept:\r\n    pass\r\nreturn None\r\n# --// /onChangeObjEvt //--\r\n##############################"
			,"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"readme"
			,"repetitive":0
			,"type":"constant"}

		icon_clazz = {"custom":"fas fa-flask text-success"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		teaser_registry_sqlite_db_create = {"default":""
			,"id":"teaser_registry/sqlite_db_create"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sqlite_db_create"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sqlite_db_upsert_sql = {"default":""
			,"id":"teaser_registry/sqlite_db_upsert_sql"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sqlite_db_upsert_sql"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sqlite_db_select_sql = {"default":""
			,"id":"teaser_registry/sqlite_db_select_sql"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sqlite_db_select_sql"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sqlite_db_update_datetime_sql = {"default":""
			,"id":"teaser_registry/sqlite_db_update_datetime_sql"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sqlite_db_update_datetime_sql"
			,"repetitive":0
			,"type":"Z SQL Method"}

		teaser_registry_sqlite_db_delete_sql = {"default":""
			,"id":"teaser_registry/sqlite_db_delete_sql"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"teaser_registry/sqlite_db_delete_sql"
			,"repetitive":0
			,"type":"Z SQL Method"}

		register_teaser = {"default":""
			,"id":"register_teaser"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Execute Teaser Registration"
			,"repetitive":0
			,"type":"External Method"}

		register_teaser_test = {"default":""
			,"id":"register_teaser_test"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"TEST"
			,"repetitive":0
			,"type":"Script (Python)"}

		teaser_registry_index_html = {"default":""
			,"id":"teaser_registry/index_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Preview"
			,"repetitive":0
			,"type":"Page Template"}
