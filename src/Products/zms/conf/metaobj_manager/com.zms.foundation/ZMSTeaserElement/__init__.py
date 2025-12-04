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

		attr_penetrance = {"default":""
			,"id":"attr_penetrance"
			,"keys":["this"
				,"sub_nav"
				,"sub_all"]
			,"mandatory":1
			,"multilang":0
			,"name":"Penetrance"
			,"repetitive":0
			,"type":"select"}

		attr_url = {"default":""
			,"id":"attr_url"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Url"
			,"repetitive":0
			,"type":"url"}

		attr_img = {"default":""
			,"id":"attr_img"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Image"
			,"repetitive":0
			,"type":"image"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		text = {"default":""
			,"id":"text"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Text"
			,"repetitive":0
			,"type":"richtext"}

		attr_img_src = {"default":""
			,"id":"attr_img_src"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Alias: Image"
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

		pageelement_teaserelement = {"default":""
			,"id":"pageelement_TeaserElement"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Teaser-Element"
			,"repetitive":0
			,"type":"Page Template"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSTeaserElement"
			,"repetitive":0
			,"type":"zpt"}
