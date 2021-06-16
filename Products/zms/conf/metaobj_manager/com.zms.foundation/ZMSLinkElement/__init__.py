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
	revision = "3.1.20"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-link"
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

		inferface0 = {"default":""
			,"id":"inferface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"inferface0"
			,"repetitive":0
			,"type":"interface"}

		attr_ref = {"default":""
			,"id":"attr_ref"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Reference"
			,"repetitive":0
			,"type":"url"}

		ref_lang = {"default":""
			,"id":"ref_lang"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Reference (lang)"
			,"repetitive":0
			,"type":"string"}

		attr_type = {"default":""
			,"id":"attr_type"
			,"keys":["replace"
				,"new"
				,"embed"
				,"recursive"
				,"remote"
				,"iframe"]
			,"mandatory":1
			,"multilang":0
			,"name":"Type"
			,"repetitive":0
			,"type":"select"}

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

		attr_dc_creator = {"default":""
			,"id":"attr_dc_creator"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Creator"
			,"repetitive":0
			,"type":"attr_dc_creator"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Url"
			,"repetitive":0
			,"type":"py"}

		attr_abstract = {"default":""
			,"id":"attr_abstract"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Abstract"
			,"repetitive":0
			,"type":"py"}

		check_constraints = {"default":""
			,"id":"check_constraints"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Hook: Check constraints"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSLinkElement"
			,"repetitive":0
			,"type":"zpt"}
