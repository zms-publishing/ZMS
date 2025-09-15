class ZMSNote:
	"""
	python-representation of ZMSNote
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
	id = "ZMSNote"

	# Name
	name = "ZMSNote"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.2.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-comment-alt"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Memotext"
			,"type":"text"}

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"name":"interface"
			,"type":"interface"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"name":"ZMI: Render short"
			,"type":"zpt"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"name":"Event: onChangeObj"
			,"type":"py"}

		standard_json_docx = {"default":""
			,"id":"standard_json_docx"
			,"keys":[]
			,"name":"JSON-DOCX Template"
			,"type":"py"}
