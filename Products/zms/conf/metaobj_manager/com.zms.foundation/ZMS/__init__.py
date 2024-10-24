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
	revision = "5.0.3"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-home"
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

		titleimage = {"default":""
			,"id":"titleimage"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Titleimage"
			,"repetitive":0
			,"type":"image"}

		levelnfc = {"default":""
			,"id":"levelnfc"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Level"
			,"repetitive":0
			,"type":"levelnfc"}

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

		attr_dc_subject = {"default":""
			,"id":"attr_dc_subject"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Subject"
			,"repetitive":0
			,"type":"attr_dc_subject"}

		attr_dc_type = {"default":""
			,"id":"attr_dc_type"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Type"
			,"repetitive":0
			,"type":"attr_dc_type"}

		attr_dc_creator = {"default":""
			,"id":"attr_dc_creator"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Creator"
			,"repetitive":0
			,"type":"attr_dc_creator"}

		delimiter_permalinks = {"default":""
			,"id":"delimiter_permalinks"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Permalinks"
			,"repetitive":0
			,"type":"delimiter"}

		interface_permalinks = {"default":""
			,"id":"interface_permalinks"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface_permalinks"
			,"repetitive":0
			,"type":"interface"}

		e = {"default":""
			,"id":"e"
			,"keys":["type(ZMSDocument)"
				,"type(ZMSObject)"
				,"type(ZMSRecordSet)"
				,"type(ZMSReference)"
				,"type(ZMSModule)"]
			,"mandatory":0
			,"multilang":0
			,"name":"Objects"
			,"repetitive":1
			,"type":"*"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onChange"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMS"
			,"repetitive":0
			,"type":"zpt"}
