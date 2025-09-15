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
			,"name":"Template: Page"
			,"type":"Page Template"}

		uploadmedia = {"default":""
			,"id":"uploadMedia"
			,"keys":[]
			,"name":"Upload: Media"
			,"type":"py"}

		show_version = {"default":""
			,"id":"show_version"
			,"keys":[]
			,"name":"Show version"
			,"type":"zpt"}

		index_html = {"default":""
			,"id":"index_html"
			,"keys":[]
			,"name":"Index-Html"
			,"type":"Script (Python)"}
