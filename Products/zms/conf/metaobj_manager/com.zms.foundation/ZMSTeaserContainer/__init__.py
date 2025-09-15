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
			,"name":"Icon (Class)"
			,"type":"constant"}

		f_css_defaults = {"default":""
			,"id":"f_css_defaults"
			,"keys":[]
			,"name":"CSS: Default"
			,"type":"resource"}

		e = {"default":""
			,"id":"e"
			,"keys":["ZMSNote"
				,"ZMSFile"
				,"type(ZMSTeaserElement)"]
			,"name":"Teaser-Elements"
			,"repetitive":1
			,"type":"*"}

		getteaserelements = {"default":""
			,"id":"getTeaserElements"
			,"keys":[]
			,"name":"Function: Teaser-Elements"
			,"type":"Script (Python)"}

		pageelement_teaser = {"default":""
			,"id":"pageelement_Teaser"
			,"keys":[]
			,"name":"Template: Teaser"
			,"type":"Script (Python)"}

		rendershort = {"default":""
			,"id":"renderShort"
			,"keys":[]
			,"name":"ZMI: Render short"
			,"type":"zpt"}
