class bt_card_layout:
	"""
	python-representation of bt_card_layout
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
	id = "bt_card_layout"

	# Name
	name = "Card-Layout"

	# Package
	package = "com.zms.bootstrap"

	# Revision
	revision = "4.1.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-address-card"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		layout = {"default":""
			,"id":"layout"
			,"keys":["##"
				,"return ["
				,"('card-group','Group'),"
				,"('card-deck','Deck'),"
				,"('card-columms','Columns'),"
				,"]"]
			,"mandatory":1
			,"multilang":0
			,"name":"Layout"
			,"repetitive":0
			,"type":"select"}

		cards = {"default":""
			,"id":"cards"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Cards"
			,"repetitive":1
			,"type":"bt_card"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Card-Columns"
			,"repetitive":0
			,"type":"zpt"}
