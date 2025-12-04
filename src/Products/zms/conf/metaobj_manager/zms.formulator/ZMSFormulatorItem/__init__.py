class ZMSFormulatorItem:
	"""
	python-representation of ZMSFormulatorItem
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
	enabled = 0

	# Id
	id = "ZMSFormulatorItem"

	# Name
	name = "ZMSFormulatorItem"

	# Package
	package = "zms.formulator"

	# Revision
	revision = "5.0.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-tasks"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		identifier = {"default":""
			,"id":"identifier"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"ID"
			,"repetitive":0
			,"type":"identifier"}

		mandatoryfield = {"default":"0"
			,"id":"mandatoryField"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Mandatory?"
			,"repetitive":0
			,"type":"boolean"}

		hiddenfield = {"default":"0"
			,"id":"hiddenField"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Hidden?"
			,"repetitive":0
			,"type":"boolean"}

		replytofield = {"default":"0"
			,"id":"replyToField"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Use as Reply-To?"
			,"repetitive":0
			,"type":"boolean"}

		hint_mail = {"default":""
			,"id":"HINT_mail"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"HINT_mail"
			,"repetitive":0
			,"type":"interface"}

		copytofield = {"default":"0"
			,"id":"copyToField"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Send confirmation mail?"
			,"repetitive":0
			,"type":"boolean"}

		maildataincluded = {"default":"1"
			,"id":"mailDataIncluded"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Include Form Data?"
			,"repetitive":0
			,"type":"boolean"}

		mailtextcc = {"default":""
			,"id":"mailTextCc"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Mail Text"
			,"repetitive":0
			,"type":"text"}

		type = {"default":""
			,"id":"type"
			,"keys":["string"
				,"email"
				,"mailattachment"
				,"textarea"
				,"date"
				,"select"
				,"multiselect"
				,"checkbox"
				,"integer"
				,"float"
				,"custom"]
			,"mandatory":1
			,"multilang":0
			,"name":"Type"
			,"repetitive":0
			,"type":"select"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"string"}

		hint_titlealt = {"default":""
			,"id":"HINT_titlealt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"HINT_titlealt"
			,"repetitive":0
			,"type":"interface"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"title"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Description"
			,"repetitive":0
			,"type":"attr_dc_description"}

		valuedefault = {"default":""
			,"id":"valueDefault"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Default"
			,"repetitive":0
			,"type":"string"}

		valueminimum = {"default":""
			,"id":"valueMinimum"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Minimum"
			,"repetitive":0
			,"type":"int"}

		valuemaximum = {"default":""
			,"id":"valueMaximum"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Maximum"
			,"repetitive":0
			,"type":"int"}

		valueselect = {"default":""
			,"id":"valueSelect"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Auswahlwerte"
			,"repetitive":0
			,"type":"text"}

		rawjson = {"default":"{}"
			,"id":"rawJSON"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"JSON-Schema"
			,"repetitive":0
			,"type":"text"}

		ace_rawjson = {"default":""
			,"id":"ACE_rawJSON"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ACE_rawJSON"
			,"repetitive":0
			,"type":"interface"}

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface"
			,"repetitive":0
			,"type":"interface"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSFormulatorItem"
			,"repetitive":0
			,"type":"zpt"}
