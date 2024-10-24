class url_extract_lib:
	"""
	python-representation of url_extract_lib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "url_extract_lib"

	# Name
	name = "URL-Extract Lib"

	# Package
	package = "com.zms.mirroring"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		url_extract_sql_create = {"default":""
			,"id":"url_extract/sql_create"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_extract/sql_create"
			,"repetitive":0
			,"type":"Z SQL Method"}

		url_extract_sql_upsert = {"default":""
			,"id":"url_extract/sql_upsert"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_extract/sql_upsert"
			,"repetitive":0
			,"type":"Z SQL Method"}

		url_extract_sql_select = {"default":""
			,"id":"url_extract/sql_select"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_extract/sql_select"
			,"repetitive":0
			,"type":"Z SQL Method"}

		url_extract_sql_update_datetime = {"default":""
			,"id":"url_extract/sql_update_datetime"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_extract/sql_update_datetime"
			,"repetitive":0
			,"type":"Z SQL Method"}

		url_extract_tryout = {"default":""
			,"id":"url_extract/tryout"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Try Out"
			,"repetitive":0
			,"type":"Page Template"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"readme"
			,"repetitive":0
			,"type":"resource"}
