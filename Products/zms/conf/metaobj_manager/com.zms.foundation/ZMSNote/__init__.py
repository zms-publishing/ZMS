class ZMSNote:
	"""
	python-representation of ZMSNote
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
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
	revision = "5.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-comment-alt"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Memotext"
			,"repetitive":0
			,"type":"text"}

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface"
			,"repetitive":0
			,"type":"interface"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ZMI: Render short"
			,"repetitive":0
			,"type":"zpt"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onChangeObj"
			,"repetitive":0
			,"type":"py"}
