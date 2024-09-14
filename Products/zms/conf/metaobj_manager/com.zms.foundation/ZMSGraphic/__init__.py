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
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		f_css_defaults = {"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS: Default"
			,"repetitive":0
			,"type":"resource"}

		displaytype = {"default":"2"
			,"id":"displaytype"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Display-Type"
			,"repetitive":0
			,"type":"int"}

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Image"
			,"repetitive":0
			,"type":"image"}

		imghires = {"default":""
			,"id":"imghires"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Image (Hires)"
			,"repetitive":0
			,"type":"image"}

		imgsuperres = {"default":""
			,"id":"imgsuperres"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Image (Superres)"
			,"repetitive":0
			,"type":"image"}

		img_attrs_spec = {"default":"alt=\"\""
			,"id":"img_attrs_spec"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"WAI-Attributes"
			,"repetitive":0
			,"type":"string"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Image (URL)"
			,"repetitive":0
			,"type":"url"}

		align = {"default":""
			,"id":"align"
			,"keys":["LEFT"
				,"LEFT_FLOAT"
				,"RIGHT"
				,"RIGHT_FLOAT"
				,"CENTER"]
			,"mandatory":1
			,"multilang":0
			,"name":"Align"
			,"repetitive":0
			,"type":"select"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Text"
			,"repetitive":0
			,"type":"richtext"}

		format = {"default":"##\r\nreturn context.getTextFormatDefault()"
			,"id":"format"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Format"
			,"repetitive":0
			,"type":"string"}

		textalign = {"default":""
			,"id":"textalign"
			,"keys":["LEFT"
				,"RIGHT"
				,"CENTER"]
			,"mandatory":1
			,"multilang":0
			,"name":"Text-Align"
			,"repetitive":0
			,"type":"select"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"py"}

		gethref2indexhtml = {"default":""
			,"id":"getHref2IndexHtml"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Function: index_html"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSGraphic"
			,"repetitive":0
			,"type":"zpt"}

		standard_json_docx = {"default":""
			,"id":"standard_json_docx"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DOCX-JSON Template: ZMSGraphic"
			,"repetitive":0
			,"type":"py"}
