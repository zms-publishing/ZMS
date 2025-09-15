class ZMSSysFolder:
	"""
	python-representation of ZMSSysFolder
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
	id = "ZMSSysFolder"

	# Name
	name = "ZMSSysFolder"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-folder"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title.Alt"
			,"type":"titlealt"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"type":"title"}

		attr_cacheable = {"custom":"0"
			,"default":""
			,"id":"attr_cacheable"
			,"keys":[]
			,"name":"Cacheable"
			,"type":"constant"}

		tab_metadata = {"default":""
			,"id":"TAB_METADATA"
			,"keys":[]
			,"name":"TAB_METADATA"
			,"type":"delimiter"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Description"
			,"type":"attr_dc_description"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"name":"interface0"
			,"type":"interface"}
