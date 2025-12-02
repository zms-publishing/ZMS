class urlmap:
	"""
	python-representation of urlmap
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""
			,""
			,""]}

	# Enabled
	enabled = 0

	# Id
	id = "urlmap"

	# Name
	name = "URL-Map"

	# Package
	package = "com.zms.routing"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSRecordSet"

	# Attrs
	class Attrs:
		records = {"default":""
			,"id":"records"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Datasets"
			,"repetitive":0
			,"type":"list"}

		key = {"custom":1
			,"default":""
			,"id":"key"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Key"
			,"repetitive":0
			,"type":"string"}

		url = {"custom":1
			,"default":""
			,"id":"url"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"URL"
			,"repetitive":0
			,"type":"url"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Standard-Template"
			,"repetitive":0
			,"type":"zpt"}

		standard_error_message = {"default":""
			,"id":"standard_error_message"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"standard_error_message"
			,"repetitive":0
			,"type":"Script (Python)"}

		doi = {"default":""
			,"id":"doi"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"doi"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_get_urlmap = {"default":""
			,"id":"url_mapping/get_urlmap"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/get_urlmap"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_get_urlmap_test = {"default":""
			,"id":"url_mapping/get_urlmap_test"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/get_urlmap_test"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_get_path_by_id = {"default":""
			,"id":"url_mapping/get_path_by_id"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/get_path_by_id"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_get_object_by_id = {"default":""
			,"id":"url_mapping/get_object_by_id"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/get_object_by_id"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_get_url_by_key = {"default":""
			,"id":"url_mapping/get_url_by_key"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/get_url_by_key"
			,"repetitive":0
			,"type":"Script (Python)"}

		url_mapping_error_404 = {"default":""
			,"id":"url_mapping/error_404"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"url_mapping/error_404"
			,"repetitive":0
			,"type":"Page Template"}
