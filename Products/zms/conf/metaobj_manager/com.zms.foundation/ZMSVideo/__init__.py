class ZMSVideo:
	"""
	python-representation of ZMSVideo
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
	id = "ZMSVideo"

	# Name
	name = "ZMSVideo"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-film"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"multilang":1
			,"name":"Icon (Class)"
			,"type":"constant"}

		title = {"default":""
			,"id":"title"
			,"keys":[]
			,"mandatory":1
			,"multilang":1
			,"name":"DC.Title"
			,"type":"title"}

		attr_dc_description = {"default":""
			,"id":"attr_dc_description"
			,"keys":[]
			,"multilang":1
			,"name":"DC.Description"
			,"type":"attr_dc_description"}

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"name":"Preview-Screen"
			,"type":"image"}

		videodata = {"default":""
			,"id":"videodata"
			,"keys":[]
			,"name":"MP4 File Upload"
			,"type":"file"}

		provider = {"default":""
			,"id":"provider"
			,"keys":["fileupload"
				,"vimeo"
				,"youtube"
				,"switch"]
			,"name":"Video Provider"
			,"type":"select"}

		videoid = {"default":""
			,"id":"videoId"
			,"keys":[]
			,"mandatory":1
			,"name":"Video-ID"
			,"type":"string"}

		videohint = {"default":""
			,"id":"videoHint"
			,"keys":[]
			,"name":"<div id=\"tr_videoHint\" class=\"form-group row\"><label class=\"col-sm-2 control-label\" for=\"videoHint\"><span>Hinweise</span></label><div id=\"videoHint\" class=\"col-sm-10\">Der Kurztitel ist nur für die interne Darstellung/Referenzierung.<br />WICHTIG: Die Option \"Einbetten auf Anfrage\" des YouTube Videos darf nicht deaktiviert sein!<br />Die YouTube ID kann aus der URL des Browsers beim Betrachten des Videos entnommen werden:<ol><li>http://www.youtube.com/watch?v=<strong style=\"color:darkred\">7nxwgSxLA68</strong></li><li>http://youtu.be/<strong style=\"color:darkred\">7nxwgSxLA68</strong></li></ol></div></div>"
			,"type":"hint"}

		videowidth = {"default":""
			,"id":"videoWidth"
			,"keys":[]
			,"name":"Breite"
			,"type":"int"}

		videoheight = {"default":""
			,"id":"videoHeight"
			,"keys":[]
			,"name":"Höhe"
			,"type":"int"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"name":"DC.Title.Alt"
			,"type":"py"}

		interface = {"default":""
			,"id":"interface"
			,"keys":[]
			,"name":"interface"
			,"type":"interface"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"name":"Template: YouTube Video"
			,"type":"zpt"}
