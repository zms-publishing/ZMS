class ZMSFile:
	"""
	python-representation of ZMSFile
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
	id = "ZMSFile"

	# Name
	name = "ZMSFile"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.1"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
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

		f_css_defaults = {"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"name":"CSS: Default"
			,"type":"resource"}

		file = {"default":""
			,"id":"file"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"File"
			,"type":"file"}

		align = {"default":""
			,"id":"align"
			,"keys":["LEFT"
				,"LEFT_FLOAT"
				,"RIGHT"
				,"RIGHT_FLOAT"
				,"NONE"]
			,"mandatory":1
			,"name":"Align"
			,"type":"select"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"name":"interface0"
			,"type":"interface"}

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

		icon_clazz = {"custom":"fas fa-download"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (Class)"
			,"type":"constant"}

		attr_img_src = {"default":""
			,"id":"attr_img_src"
			,"keys":[]
			,"name":"Alias: Teaser.Image"
			,"type":"py"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"name":"Alias: Teaser.Url"
			,"type":"py"}

		attr_abstract = {"default":""
			,"id":"attr_abstract"
			,"keys":[]
			,"name":"Alias: Teaser.Abstract"
			,"type":"py"}

		gethref2indexhtml = {"default":""
			,"id":"getHref2IndexHtml"
			,"keys":[]
			,"name":"Function: index_html"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSFile"
			,"type":"zpt"}
