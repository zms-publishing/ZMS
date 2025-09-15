class ZMSLinkElement:
	"""
	python-representation of ZMSLinkElement
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
	id = "ZMSLinkElement"

	# Name
	name = "ZMSLinkElement"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.2.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-link"
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

		inferface0 = {"default":""
			,"id":"inferface0"
			,"keys":[]
			,"name":"inferface0"
			,"type":"interface"}

		attr_ref = {"default":""
			,"id":"attr_ref"
			,"keys":[]
			,"mandatory":1
			,"name":"Reference"
			,"type":"url"}

		attr_type = {"default":""
			,"id":"attr_type"
			,"keys":["replace"
				,"new"
				,"embed"
				,"recursive"
				,"remote"
				,"iframe"]
			,"mandatory":1
			,"name":"Type"
			,"type":"select"}

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

		attr_dc_creator = {"default":""
			,"id":"attr_dc_creator"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Creator"
			,"type":"attr_dc_creator"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"name":"Alias: Url"
			,"type":"py"}

		attr_abstract = {"default":""
			,"id":"attr_abstract"
			,"keys":[]
			,"name":"Alias: Abstract"
			,"type":"py"}

		check_constraints = {"default":""
			,"id":"check_constraints"
			,"keys":[]
			,"name":"Hook: Check constraints"
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSLinkElement"
			,"type":"zpt"}
