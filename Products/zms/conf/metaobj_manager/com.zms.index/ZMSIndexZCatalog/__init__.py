class ZMSIndexZCatalog:
	"""
	python-representation of ZMSIndexZCatalog
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""
			,""]}

	# Enabled
	enabled = 0

	# Id
	id = "ZMSIndexZCatalog"

	# Name
	name = "ZMSIndexZCatalog"

	# Package
	package = "com.zms.index"

	# Revision
	revision = "2.1.3"

	# Type
	type = "ZMSResource"

	# Attrs
	class Attrs:
		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		zmsindexzcatalog_func_ = {"default":""
			,"id":"ZMSIndexZCatalog_func_"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Trusted functions"
			,"repetitive":0
			,"type":"External Method"}

		getlinkobj = {"default":""
			,"id":"getLinkObj"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Extension-Point: Get link object"
			,"repetitive":0
			,"type":"py"}

		getrefobjpath = {"default":""
			,"id":"getRefObjPath"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Extension-Point: Get ref object path"
			,"repetitive":0
			,"type":"py"}

		get_uid = {"default":""
			,"id":"get_uid"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Extension-Point: Get uid"
			,"repetitive":0
			,"type":"py"}

		oncreateobjevt = {"default":""
			,"id":"onCreateObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onCreateObj"
			,"repetitive":0
			,"type":"py"}

		onimportobjevt = {"default":""
			,"id":"onImportObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onCreateObj"
			,"repetitive":0
			,"type":"py"}

		objectadded = {"default":""
			,"id":"ObjectAdded"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: object added"
			,"repetitive":0
			,"type":"py"}

		objectmoved = {"default":""
			,"id":"ObjectMoved"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: object moved"
			,"repetitive":0
			,"type":"py"}

		objectremoved = {"default":""
			,"id":"ObjectRemoved"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: object removed"
			,"repetitive":0
			,"type":"py"}

		doi = {"default":""
			,"id":"doi"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DOI-Redirect"
			,"repetitive":0
			,"type":"Script (Python)"}
