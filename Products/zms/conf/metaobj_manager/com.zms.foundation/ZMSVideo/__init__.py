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
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

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

		img = {"default":""
			,"id":"img"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Preview-Screen"
			,"repetitive":0
			,"type":"image"}

		videodata = {"default":""
			,"id":"videodata"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"MP4 File Upload"
			,"repetitive":0
			,"type":"file"}

		provider = {"default":""
			,"id":"provider"
			,"keys":["fileupload"
				,"vimeo"
				,"youtube"
				,"switch"]
			,"mandatory":0
			,"multilang":0
			,"name":"Video Provider"
			,"repetitive":0
			,"type":"select"}

		videoid = {"default":""
			,"id":"videoId"
			,"keys":[]
			,"mandatory":1
			,"multilang":0
			,"name":"Video-ID"
			,"repetitive":0
			,"type":"string"}

		videohint = {"default":""
			,"id":"videoHint"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"<div id=\"tr_videoHint\" class=\"form-group row\"><label class=\"col-sm-2 control-label\" for=\"videoHint\"><span>Hinweise</span></label><div id=\"videoHint\" class=\"col-sm-10\">Der Kurztitel ist nur für die interne Darstellung/Referenzierung.<br />WICHTIG: Die Option \"Einbetten auf Anfrage\" des YouTube Videos darf nicht deaktiviert sein!<br />Die YouTube ID kann aus der URL des Browsers beim Betrachten des Videos entnommen werden:<ol><li>http://www.youtube.com/watch?v=<strong style=\"color:darkred\">7nxwgSxLA68</strong></li><li>http://youtu.be/<strong style=\"color:darkred\">7nxwgSxLA68</strong></li></ol></div></div>"
			,"repetitive":0
			,"type":"hint"}

		videowidth = {"default":""
			,"id":"videoWidth"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Breite"
			,"repetitive":0
			,"type":"int"}

		videoheight = {"default":""
			,"id":"videoHeight"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Höhe"
			,"repetitive":0
			,"type":"int"}

		titlealt = {"default":""
			,"id":"titlealt"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Title.Alt"
			,"repetitive":0
			,"type":"py"}

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
			,"name":"Template: YouTube Video"
			,"repetitive":0
			,"type":"zpt"}
