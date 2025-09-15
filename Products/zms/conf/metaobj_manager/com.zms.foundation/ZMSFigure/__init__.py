class ZMSFigure:
	"""
	python-representation of ZMSFigure
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,"ZMSAuthor"
			,"ZMSEditor"]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,"ZMSAuthor"
			,"ZMSEditor"]}

	# Enabled
	enabled = 1

	# Id
	id = "ZMSFigure"

	# Name
	name = "ZMSFigure"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"name":"DC.Title.Alt"
			,"type":"py"}

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Image"
			,"type":"image"}

		_img = {"default":""
			,"id":"_img"
			,"keys":[]
			,"multilang":1
			,"name":"Image (Preview)"
			,"type":"image"}

		figcaption = {"default":""
			,"id":"figcaption"
			,"keys":[]
			,"multilang":1
			,"name":"Legende"
			,"type":"text"}

		icon_clazz = {"custom":"icon-picture fas fa-image"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon-Class (CSS)"
			,"type":"constant"}

		gethref2indexhtml = {"default":""
			,"id":"getHref2IndexHtml"
			,"keys":[]
			,"name":"Function: index_html"
			,"type":"py"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"name":"Event: onChange"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: Simple-Bild"
			,"type":"zpt"}
