class ZMSTeaserContainer:
	"""
	python-representation of ZMSTeaserContainer
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
	id = "ZMSTeaserContainer"

	# Name
	name = "ZMSTeaserContainer"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

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

		e = {"default":""
			,"id":"e"
			,"keys":["ZMSNote"
				,"ZMSFile"
				,"type(ZMSTeaserElement)"]
			,"mandatory":0
			,"multilang":0
			,"name":"Teaser-Elements"
			,"repetitive":1
			,"type":"*"}

		getteaserelements = {"default":""
			,"id":"getTeaserElements"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Function: Teaser-Elements"
			,"repetitive":0
			,"type":"Script (Python)"}

		pageelement_teaser = {"default":""
			,"id":"pageelement_Teaser"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Teaser"
			,"repetitive":0
			,"type":"Script (Python)"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ZMI: Render short"
			,"repetitive":0
			,"type":"zpt"}
