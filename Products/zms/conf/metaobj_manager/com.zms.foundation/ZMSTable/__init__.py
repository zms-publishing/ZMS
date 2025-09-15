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

	# Lang_dict
	lang_dict = {"ZMSTable.MSG_ZMSTABLE_EDITOR":{"eng":"<small class=\"form-text text-muted\">HINTS:\r\n	<span class=\"badge badge-dark\">Click</span> cell to edit,\r\n	<span class=\"badge badge-dark\">Double-click</span> cell to open WYSIWYG-editor,\r\n	<span class=\"badge badge-dark\">Right-click</span> to insert, move or delete cells.\r\n</small>"
			,"ger":"<small class=\"form-text text-muted\">HINWEISE:\r\n	<span class=\"badge badge-dark\">Klick</span> auf Zelle zum Editieren,\r\n	<span class=\"badge badge-dark\">Doppel-Klick</span> auf Zelle zum Öffnen des WYSIWYG-Editors,\r\n	<span class=\"badge badge-dark\">Rechts-Klick</span> zum Einfügen, Verschieben oder Löschen von Zellen.\r\n</small>"}
		,"ZMSTable.MSG_ZMSTABLE_TYPE":{"eng":"Note: Type can not be changed later"
			,"ger":"Hinweis: Tabellen-Typ kann nachträglich nicht mehr geändert werden."}}

	# Name
	name = "ZMSTable"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.1.2"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"name":"DC.Title.Alt"
			,"type":"py"}

		caption = {"default":""
			,"id":"caption"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Caption"
			,"type":"string"}

		caption_side = {"default":""
			,"id":"caption_side"
			,"keys":["bottom"
				,"top"]
			,"name":"Align"
			,"type":"select"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Description"
			,"type":"attr_dc_description"}

		sortable = {"default":"0"
			,"id":"sortable"
			,"keys":[]
			,"name":"Sortable"
			,"type":"boolean"}

		colgroup = {"default":"0"
			,"id":"colgroup"
			,"keys":[]
			,"name":"Colgroup"
			,"type":"boolean"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"name":"interface0"
			,"type":"interface"}

		type = {"default":""
			,"id":"type"
			,"keys":[]
			,"mandatory":1
			,"name":"Type"
			,"type":"int"}

		table = {"default":""
			,"id":"table"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Table"
			,"type":"list"}

		cols = {"default":""
			,"id":"cols"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"Cols"
			,"type":"list"}

		jquerytablesorterminjs = {"default":""
			,"id":"jquery.tablesorter.min.js"
			,"keys":[]
			,"name":"https://github.com/Mottie/tablesorter"
			,"type":"resource"}

		jquerytablesortercss = {"default":""
			,"id":"jquery.tablesorter.css"
			,"keys":[]
			,"name":"https://github.com/Mottie/tablesorter"
			,"type":"resource"}

		icon_clazz = {"custom":"fas fa-table"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"name":"Icon (CSS)"
			,"type":"constant"}

		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"name":"README.md"
			,"type":"resource"}

		onchangeobjevt = {"default":""
			,"id":"onChangeObjEvt"
			,"keys":[]
			,"name":"Event: onChange"
			,"type":"py"}

		widths = {"default":""
			,"id":"widths"
			,"keys":[]
			,"name":"Col-Widths [list]"
			,"type":"py"}

		zmstable_colgroup_css = {"default":""
			,"id":"zmstable_colgroup_css"
			,"keys":[]
			,"name":"CSS Colgroup"
			,"type":"zpt"}

		zmstable_sortable_js = {"default":""
			,"id":"zmstable_sortable_js"
			,"keys":[]
			,"name":"JS Sortable"
			,"type":"zpt"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: ZMSTable"
			,"type":"zpt"}
