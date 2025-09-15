class ZMS:
	"""
	python-representation of ZMS
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
	enabled = 0

	# Id
	id = "ZMS"

	# Name
	name = "ZMS"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.4"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-home"
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

		delimiter_permalinks = {"default":""
			,"id":"delimiter_permalinks"
			,"keys":[]
			,"multilang":1
			,"name":"Permalinks"
			,"type":"delimiter"}

		interface_permalinks = {"default":""
			,"id":"interface_permalinks"
			,"keys":[]
			,"name":"interface_permalinks"
			,"type":"interface"}

		e = {"default":""
			,"id":"e"
			,"keys":["type(ZMSDocument)"
				,"type(ZMSObject)"
				,"type(ZMSRecordSet)"
				,"type(ZMSReference)"
				,"type(ZMSModule)"]
			,"name":"Objects"
			,"repetitive":1
			,"type":"*"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"name":"Event: onChange"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMS"
			,"type":"zpt"}
