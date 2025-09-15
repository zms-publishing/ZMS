class ZMSRichtext:
	"""
	python-representation of ZMSRichtext
	"""

	# Access
	access = {"delete":["ZMSAdministrator"
			,"ZMSAuthor"
			,"ZMSEditor"]
		,"delete_custom":""
		,"insert":["ZMSAdministrator"
			,"ZMSAuthor"
			,"ZMSEditor"]
		,"insert_custom":"{$}"}

	# Enabled
	enabled = 0

	# Id
	id = "ZMSRichtext"

	# Name
	name = "ZMSRichtext"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-file-word"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"name":"interface0"
			,"type":"interface"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"multilang":1
			,"name":"Text"
			,"type":"richtext"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"name":"Event: onChange-Object"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSRichtext"
			,"type":"zpt"}
