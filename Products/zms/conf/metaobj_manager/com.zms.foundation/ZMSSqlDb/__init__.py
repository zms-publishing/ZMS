class ZMSSqlDb:
	"""
	python-representation of ZMSSqlDb
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
	id = "ZMSSqlDb"

	# Name
	name = "ZMSSqlDb"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-database"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"name":"ZMI: Render short"
			,"type":"zpt"}
