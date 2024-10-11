class lunr_connector:
	"""
	python-representation of lunr_connector
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "lunr_connector"

	# Lang_dict
	lang_dict = {"lunr_connector.BTN_BUILD":{"eng":"Build Index"
			,"ger":"Index erzeugen"}}

	# Name
	name = "Lunr-Connector"

	# Package
	package = "com.zms.catalog.lunr"

	# Revision
	revision = "1.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		properties = {"custom":"[]"
			,"default":""
			,"id":"properties"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Property-Definitions (JSON)"
			,"repetitive":0
			,"type":"constant"}

		manage_lunr_build_index = {"default":""
			,"id":"manage_lunr_build_index"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Build: search_index.json"
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
