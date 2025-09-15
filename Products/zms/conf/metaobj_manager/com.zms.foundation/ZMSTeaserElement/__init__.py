class ZMSTeaserElement:
	"""
	python-representation of ZMSTeaserElement
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
	id = "ZMSTeaserElement"

	# Name
	name = "ZMSTeaserElement"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSTeaserElement"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-bullhorn"
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

		attr_penetrance = {"default":""
			,"id":"attr_penetrance"
			,"keys":["this"
				,"sub_nav"
				,"sub_all"]
			,"mandatory":1
			,"name":"Penetrance"
			,"type":"select"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"multilang":1
			,"name":"Url"
			,"type":"url"}

		attr_img = {"default":""
			,"id":"attr_img"
			,"keys":[]
			,"multilang":1
			,"name":"Image"
			,"type":"image"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"type":"title"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"multilang":1
			,"name":"Text"
			,"type":"richtext"}

		attr_img_src = {"default":""
			,"id":"attr_img_src"
			,"keys":[]
			,"name":"Alias: Image"
			,"type":"py"}

		attr_abstract = {"default":""
			,"id":"attr_abstract"
			,"keys":[]
			,"name":"Alias: Abstract"
			,"type":"py"}

		pageelement_teaserelement = {"default":""
			,"id":"pageelement_TeaserElement"
			,"keys":[]
			,"name":"Template: Teaser-Element"
			,"type":"Page Template"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSTeaserElement"
			,"type":"zpt"}
