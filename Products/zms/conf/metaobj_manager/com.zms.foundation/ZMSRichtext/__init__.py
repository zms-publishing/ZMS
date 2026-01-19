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
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Text"
			,"repetitive":0
			,"type":"richtext"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onChange-Object"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSRichtext"
			,"repetitive":0
			,"type":"zpt"}
