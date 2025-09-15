class ZMSGraphic:
	"""
	python-representation of ZMSGraphic
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
	id = "ZMSGraphic"

	# Name
	name = "ZMSGraphic"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.2.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-image"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		f_css_defaults = {"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"name":"CSS: Default"
			,"type":"resource"}

		displaytype = {"default":"2"
			,"id":"displaytype"
			,"keys":[]
			,"mandatory":1
			,"name":"Display-Type"
			,"type":"int"}

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Image"
			,"type":"image"}

		imghires = {"default":""
			,"id":"imghires"
			,"keys":[]
			,"multilang":1
			,"name":"Image (Hires)"
			,"type":"image"}

		imgsuperres = {"default":""
			,"id":"imgsuperres"
			,"keys":[]
			,"multilang":1
			,"name":"Image (Superres)"
			,"type":"image"}

		img_attrs_spec = {"default":"alt=\"\""
			,"id":"img_attrs_spec"
			,"keys":[]
			,"name":"WAI-Attributes"
			,"type":"string"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"multilang":1
			,"name":"Image (URL)"
			,"type":"url"}

		align = {"default":""
			,"id":"align"
			,"keys":["LEFT"
				,"LEFT_FLOAT"
				,"RIGHT"
				,"RIGHT_FLOAT"
				,"CENTER"]
			,"mandatory":1
			,"name":"Align"
			,"type":"select"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"multilang":1
			,"name":"Text"
			,"type":"richtext"}

		format = {"default":"##\r\nreturn context.getTextFormatDefault()"
			,"id":"format"
			,"keys":[]
			,"mandatory":1
			,"name":"Format"
			,"type":"string"}

		textalign = {"default":""
			,"id":"textalign"
			,"keys":["LEFT"
				,"RIGHT"
				,"CENTER"]
			,"mandatory":1
			,"name":"Text-Align"
			,"type":"select"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"name":"DC.Title.Alt"
			,"type":"py"}

		gethref2indexhtml = {"default":""
			,"id":"getHref2IndexHtml"
			,"keys":[]
			,"name":"Function: index_html"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSGraphic"
			,"type":"zpt"}

		standard_json_docx = {"default":""
			,"id":"standard_json_docx"
			,"keys":[]
			,"name":"DOCX-JSON Template: ZMSGraphic"
			,"type":"py"}
