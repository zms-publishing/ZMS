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
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"titlealt"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		attr_cacheable = {"custom":"0"
			,"default":""
			,"id":"attr_cacheable"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Cacheable"
			,"repetitive":0
			,"type":"constant"}

		tab_metadata = {"default":""
			,"id":"TAB_METADATA"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"TAB_METADATA"
			,"repetitive":0
			,"type":"delimiter"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Description"
			,"repetitive":0
			,"type":"attr_dc_description"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}
