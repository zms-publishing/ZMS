class ZMSNote:
	"""
	python-representation of ZMSNote
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
	enabled = 1

	# Id
	id = "ZMSNote"

	# Name
	name = "ZMSNote"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "3.0.2"

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

		zmsnote_bggif = {"default":""
			,"id":"zmsnote_bg.gif"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Resource: Background"
			,"repetitive":0
			,"type":"resource"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
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

		catalogtext = {"custom":""
			,"default":""
			,"id":"catalogText"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Hook: Catalog-Text"
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

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onChangeObj"
			,"repetitive":0
			,"type":"py"}
