class ZMSDocument:
	"""
	python-representation of ZMSDocument
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""]}

	# Enabled
	enabled = 1

	# Id
	id = "ZMSDocument"

	# Name
	name = "ZMSDocument"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-file-alt"
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

		titleimage = {"default":""
			,"id":"titleimage"
			,"keys":[]
			,"multilang":1
			,"name":"Titleimage"
			,"type":"image"}

		levelnfc = {"default":""
			,"id":"levelnfc"
			,"keys":[]
			,"name":"Level"
			,"type":"levelnfc"}

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

		attr_dc_subject = {"default":""
			,"id":"attr_dc_subject"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Subject"
			,"type":"attr_dc_subject"}

		attr_dc_type = {"default":""
			,"id":"attr_dc_type"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Type"
			,"type":"attr_dc_type"}

		attr_dc_creator = {"default":""
			,"id":"attr_dc_creator"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Creator"
			,"type":"attr_dc_creator"}

		e = {"default":""
			,"id":"e"
			,"keys":["type(ZMSObject)"
				,"type(ZMSRecordSet)"
				,"type(ZMSModule)"]
			,"name":"Objects"
			,"repetitive":1
			,"type":"*"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSDocument"
			,"type":"zpt"}
