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
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"py"}

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Image"
			,"repetitive":0
			,"type":"image"}

		_img = {"default":""
			,"id":"_img"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Image (Preview)"
			,"repetitive":0
			,"type":"image"}

		figcaption = {"default":""
			,"id":"figcaption"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Legende"
			,"repetitive":0
			,"type":"text"}

		icon_clazz = {"custom":"icon-picture fas fa-image"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon-Class (CSS)"
			,"repetitive":0
			,"type":"constant"}

		gethref2indexhtml = {"default":""
			,"id":"getHref2IndexHtml"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Function: index_html"
			,"repetitive":0
			,"type":"py"}

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
			,"name":"Template: Simple-Bild"
			,"repetitive":0
			,"type":"zpt"}
