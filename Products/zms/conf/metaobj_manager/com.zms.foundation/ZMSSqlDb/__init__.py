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
	revision = "5.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-database"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ZMI: Render short"
			,"repetitive":0
			,"type":"zpt"}
