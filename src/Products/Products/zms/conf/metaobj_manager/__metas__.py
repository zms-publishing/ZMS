class __metas__:
	"""
	python-representation of __metas__
	"""

	# Id
	id = "__metas__"

	# Metas
	class Metas:
		titlealt = {"custom":""
			,"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"string"}

		title = {"custom":""
			,"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"repetitive":0
			,"type":"string"}

		levelnfc = {"custom":""
			,"default":""
			,"id":"levelnfc"
			,"keys":["##"
				,"return [(x,context.getZMILangStr('OPT_L_%i'%x)) for x in range(3)]"]
			,"mandatory":0
			,"multilang":0
			,"name":"Level"
			,"repetitive":0
			,"type":"select"}

		attr_dc_description = {"custom":""
			,"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Description"
			,"repetitive":0
			,"type":"text"}

		attr_dc_subject = {"custom":""
			,"default":""
			,"id":"attr_dc_subject"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Subject"
			,"repetitive":0
			,"type":"text"}

		attr_dc_type = {"custom":""
			,"default":""
			,"id":"attr_dc_type"
			,"keys":["Home"
				,"Artikel"
				,"Forum"
				,"News"
				,"Resource"]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Type"
			,"repetitive":0
			,"type":"select"}

		attr_dc_creator = {"custom":""
			,"default":""
			,"id":"attr_dc_creator"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Creator"
			,"repetitive":0
			,"type":"string"}

		attr_logo = {"custom":""
			,"default":""
			,"id":"attr_logo"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Logo"
			,"repetitive":0
			,"type":"image"}

		attr_navigation = {"custom":""
			,"default":""
			,"id":"attr_navigation"
			,"keys":["1"
				,"2"
				,"3"
				,"4"]
			,"mandatory":0
			,"multilang":0
			,"name":"Navigation"
			,"repetitive":0
			,"type":"select"}

		attr_dc_accessrights_restricted = {"custom":""
			,"default":"0"
			,"id":"attr_dc_accessrights_restricted"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Restricted"
			,"repetitive":0
			,"type":"boolean"}
