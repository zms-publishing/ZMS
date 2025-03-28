class captcha_lib:
	"""
	python-representation of captcha_lib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "captcha_lib"

	# Lang_dict
	lang_dict = {"captcha_lib.captcha_hint":{"ger":"Bitte geben Sie nun abschliessend folgende vier-stellige Prüfziffer zum Schutz vor Spam in das weisse Feld ein; beachten Sie, dass sich die Prüfziffer alle zwei Minuten erneuert. Durch Klick auf das blaue Stoppuhr-Symbol \"Reload\" können Sie jederzeit eine erneut zwei Minuten gütige Prüfziffer anfordern."}
		,"captcha_lib.captcha_input":{"ger":"Bitte Prüfziffer eingeben und absenden."}
		,"captcha_lib.captcha_invalid":{"ger":"Leider ist die Eingabe der Prüfziffer nicht korrekt; bitte betätigen Sie die \"Zurück\"-Taste des Webbrowsers und versuchen Sie es bitte nochmals."}
		,"captcha_lib.captcha_reload":{"ger":"Erneuern"}
		,"captcha_lib.captcha_valid":{"ger":"Prüfziffer korrekt."}}

	# Name
	name = "Captcha-Lib"

	# Package
	package = ""

	# Revision
	revision = "0.5.0"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		readme = {"default":""
			,"id":"readme"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"README.md"
			,"repetitive":0
			,"type":"resource"}

		captchaipynb = {"default":""
			,"id":"captcha.ipynb"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Jupyter Notebook"
			,"repetitive":0
			,"type":"resource"}

		captcha_js = {"default":""
			,"id":"captcha_js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Captcha JS"
			,"repetitive":0
			,"type":"resource"}

		captcha_css = {"default":""
			,"id":"captcha_css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Captcha CSS"
			,"repetitive":0
			,"type":"resource"}

		captcha_func = {"default":""
			,"id":"captcha_func"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"captcha_func"
			,"repetitive":0
			,"type":"External Method"}

		captcha_create = {"default":""
			,"id":"captcha_create"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Create Captcha"
			,"repetitive":0
			,"type":"Script (Python)"}

		captcha_validate = {"default":""
			,"id":"captcha_validate"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Validate Captcha"
			,"repetitive":0
			,"type":"Script (Python)"}

		captcha_html = {"default":""
			,"id":"captcha_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Captcha HTML"
			,"repetitive":0
			,"type":"Page Template"}
