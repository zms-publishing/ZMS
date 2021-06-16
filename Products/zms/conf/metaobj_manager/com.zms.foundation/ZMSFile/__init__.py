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
	revision = "3.4.0"

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

		f_css_defaults = {"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS: Default"
			,"repetitive":0
			,"type":"resource"}

		file = {"default":""
			,"id":"file"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"File"
			,"repetitive":0
			,"type":"file"}

		align = {"default":""
			,"id":"align"
			,"keys":["LEFT"
				,"LEFT_FLOAT"
				,"RIGHT"
				,"RIGHT_FLOAT"
				,"NONE"]
			,"mandatory":1
			,"multilang":0
			,"name":"Align"
			,"repetitive":0
			,"type":"select"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

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

		icon_clazz = {"custom":"fas fa-download"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		attr_img_src = {"default":""
			,"id":"attr_img_src"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Teaser.Image"
			,"repetitive":0
			,"type":"py"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Teaser.Url"
			,"repetitive":0
			,"type":"py"}

		attr_abstract = {"default":""
			,"id":"attr_abstract"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Teaser.Abstract"
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
			,"name":"Template: ZMSFile"
			,"repetitive":0
			,"type":"zpt"}
