class ZMSTable:
	"""
	python-representation of ZMSTable
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
	id = "ZMSTable"

	# Name
	name = "ZMSTable"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		caption = {"default":""
			,"id":"caption"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Caption"
			,"repetitive":0
			,"type":"string"}

		caption_side = {"default":""
			,"id":"caption_side"
			,"keys":["bottom"
				,"top"]
			,"mandatory":0
			,"multilang":0
			,"name":"Align"
			,"repetitive":0
			,"type":"select"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Description"
			,"repetitive":0
			,"type":"attr_dc_description"}

		sortable = {"default":"0"
			,"id":"sortable"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Sortable"
			,"repetitive":0
			,"type":"boolean"}

		colgroup = {"default":"0"
			,"id":"colgroup"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Colgroup"
			,"repetitive":0
			,"type":"boolean"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"py"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		type = {"default":""
			,"id":"type"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Type"
			,"repetitive":0
			,"type":"int"}

		table = {"default":""
			,"id":"table"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Table"
			,"repetitive":0
			,"type":"list"}

		cols = {"default":""
			,"id":"cols"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Cols"
			,"repetitive":0
			,"type":"list"}

		jquerytablesorterminjs = {"default":""
			,"id":"jquery.tablesorter.min.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"https://github.com/Mottie/tablesorter"
			,"repetitive":0
			,"type":"resource"}

		jquerytablesortercss = {"default":""
			,"id":"jquery.tablesorter.css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"https://github.com/Mottie/tablesorter"
			,"repetitive":0
			,"type":"resource"}

		icon_clazz = {"custom":"fas fa-table"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Icon (CSS)"
			,"repetitive":0
			,"type":"constant"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Event: onChange"
			,"repetitive":0
			,"type":"py"}

		widths = {"default":""
			,"id":"widths"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Col-Widths [list]"
			,"repetitive":0
			,"type":"py"}

		zmstable_colgroup_css = {"default":""
			,"id":"zmstable_colgroup_css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"CSS Colgroup"
			,"repetitive":0
			,"type":"zpt"}

		zmstable_sortable_js = {"default":""
			,"id":"zmstable_sortable_js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JS Sortable"
			,"repetitive":0
			,"type":"zpt"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSTable"
			,"repetitive":0
			,"type":"zpt"}
