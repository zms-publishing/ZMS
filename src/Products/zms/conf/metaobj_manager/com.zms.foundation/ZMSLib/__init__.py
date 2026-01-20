class ZMSLib:
	"""
	python-representation of ZMSLib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "ZMSLib"

	# Name
	name = "ZMSLib"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		bodycontentzmslib_page = {"default":""
			,"id":"bodyContentZMSLib_page"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Page"
			,"repetitive":0
			,"type":"Page Template"}

		uploadmedia = {"default":""
			,"id":"uploadMedia"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Upload: Media"
			,"repetitive":0
			,"type":"py"}

		show_version = {"default":""
			,"id":"show_version"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Show version"
			,"repetitive":0
			,"type":"zpt"}

		index_html = {"default":""
			,"id":"index_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Index-Html"
			,"repetitive":0
			,"type":"Script (Python)"}
