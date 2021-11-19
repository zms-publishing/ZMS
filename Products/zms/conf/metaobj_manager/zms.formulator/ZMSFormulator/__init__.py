class ZMSFormulator:
	"""
	python-representation of ZMSFormulator
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
	enabled = 1

	# Id
	id = "ZMSFormulator"

	# Name
	name = "ZMSFormulator"

	# Package
	package = "zms.formulator"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-file-invoice"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		warnung = {"default":""
			,"id":"warnung"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"<div class=\"alert alert-danger alert-box-error\" style=\"margin:1em 0 2em;\" role=\"alert\"><b>Bitte beachten!</b> Legen Sie Formulare, sowie Formularelemente immer zuerst in der Primärsprache an. Falls Sie das Formular nur in der Sekundärsprache verwenden, dann deaktivieren Sie das Objekt in der Primärsprache.</div>"
			,"repetitive":0
			,"type":"hint"}

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

		feedbackmsg = {"default":""
			,"id":"feedbackMsg"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Feedback"
			,"repetitive":0
			,"type":"text"}

		feedbackmsg_help = {"default":""
			,"id":"feedbackMsg_help"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"<div class=\"help\" data-for=\"feedbackMsg_ger\">Im Feld <em>Feedback</em> haben Sie die Möglichkeit, eine eigene Meldung zu definieren, welche dem Absender nach dem Ausfüllen des Formulars im Browser angezeigt wird. Sie können zum Formatieren der Nachricht <a href=\"http://www.w3schools.com/tags/ref_byfunc.asp\" target=\"_blank\">HTML-Tags</a> verwenden. Wenn das Feld leer bleibt, wird eine Standardmeldung ausgegeben.</div>"
			,"repetitive":0
			,"type":"hint"}

		tab_metadata = {"default":""
			,"id":"TAB_METADATA"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
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

		attr_dc_subject = {"default":""
			,"id":"attr_dc_subject"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"DC.Subject"
			,"repetitive":0
			,"type":"text"}

		delimiter_advanced = {"default":""
			,"id":"delimiter_Advanced"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Advanced (JavaScript)"
			,"repetitive":0
			,"type":"delimiter"}

		optionsjs = {"default":"// Disable additional properties\nZMSFormulator.options.no_additional_properties = true;\n\n// Require all properties by default\nZMSFormulator.options.required_by_default = true;"
			,"id":"optionsJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Options"
			,"repetitive":0
			,"type":"text"}

		ace_optionsjs = {"default":""
			,"id":"ACE_optionsJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ACE_optionsJS"
			,"repetitive":0
			,"type":"interface"}

		onreadyjs = {"default":""
			,"id":"onReadyJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"onReady"
			,"repetitive":0
			,"type":"text"}

		ace_onreadyjs = {"default":""
			,"id":"ACE_onReadyJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ACE_onReadyJS"
			,"repetitive":0
			,"type":"interface"}

		onchangejs = {"default":""
			,"id":"onChangeJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"onChange"
			,"repetitive":0
			,"type":"text"}

		ace_onchangejs = {"default":""
			,"id":"ACE_onChangeJS"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ACE_onChangeJS"
			,"repetitive":0
			,"type":"interface"}

		zmsformulatorinterface = {"default":""
			,"id":"ZMSFORMULATORINTERFACE"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ZMSFORMULATORINTERFACE"
			,"repetitive":0
			,"type":"interface"}

		delimiter_data = {"default":""
			,"id":"delimiter_Data"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Data"
			,"repetitive":0
			,"type":"delimiter"}

		data = {"default":""
			,"id":"_data"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Data"
			,"repetitive":0
			,"type":"dictionary"}

		interface2 = {"default":""
			,"id":"interface2"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface2"
			,"repetitive":0
			,"type":"interface"}

		datastoragedisabled = {"default":"0"
			,"id":"dataStorageDisabled"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Disable Storage of Data"
			,"repetitive":0
			,"type":"boolean"}

		datastoragesql = {"default":"1"
			,"id":"dataStorageSQL"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Use SQL-Storage"
			,"repetitive":0
			,"type":"boolean"}

		sendviamail = {"default":"0"
			,"id":"sendViaMail"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Send Mail?"
			,"repetitive":0
			,"type":"boolean"}

		sendviamailfrom = {"default":""
			,"id":"sendViaMailFrom"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Mail Address [FROM]"
			,"repetitive":0
			,"type":"string"}

		hint_from = {"default":""
			,"id":"HINT_FROM"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"HINT_FROM"
			,"repetitive":0
			,"type":"interface"}

		sendviamailaddress = {"default":""
			,"id":"sendViaMailAddress"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Mail Address [TO]"
			,"repetitive":0
			,"type":"string"}

		mailtextto = {"default":""
			,"id":"mailTextTo"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Mail Text"
			,"repetitive":0
			,"type":"text"}

		mailfrmt = {"default":"0"
			,"id":"mailFrmt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"HTML formatted?"
			,"repetitive":0
			,"type":"boolean"}

		mailfrmtcss = {"default":"table { background-color:#fff; border:1px solid #000; }\nth { text-align:right; vertical-align: bottom; font-family:sans-serif; padding:0 0.5em; font-weight:normal; }\ntd { text-align:left; vertical-align: bottom; font-family:sans-serif; padding:0 0.5em; font-size:1.5em; }\nh1, h3 { font-weight:normal; }"
			,"id":"mailFrmtCSS"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Styling"
			,"repetitive":0
			,"type":"text"}

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface"
			,"repetitive":0
			,"type":"interface"}

		formulatoritems = {"default":""
			,"id":"formulatorItems"
			,"keys":["ZMSFormulatorItem"
				,"ZMSTextarea"]
			,"mandatory":0
			,"multilang":0
			,"name":"Items"
			,"repetitive":1
			,"type":"*"}

		javscriptandstyle = {"default":""
			,"id":"javscriptandstyle"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"javscriptandstyle"
			,"repetitive":0
			,"type":"interface"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSFormulator"
			,"repetitive":0
			,"type":"zpt"}
