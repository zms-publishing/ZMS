class zms_formulator_lib:
	"""
	python-representation of zms.formulator.lib
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[]
		,"insert_custom":""
		,"insert_deny":[]}

	# Enabled
	enabled = 0

	# Id
	id = "zms.formulator.lib"

	# Lang_dict
	lang_dict = {"zms.formulator.lib.BUTTON_RESTORE":{"eng":"Restore"
			,"fra":"Restaurer"
			,"ger":"Zurücksetzen"}
		,"zms.formulator.lib.BUTTON_SUBMIT":{"eng":"Submit"
			,"fra":"Soumettre"
			,"ger":"Absenden"}
		,"zms.formulator.lib.ERROR_ADDITIONALITEMS":{"eng":"No additional items allowed in this array"
			,"fra":"No additional items allowed in this array"
			,"ger":"Keine weiteren Elemente in diesem Array erlaubt!"}
		,"zms.formulator.lib.ERROR_ADDITIONAL_PROPERTIES":{"eng":"No additional properties allowed, but property {{0}} is set"
			,"fra":"No additional properties allowed, but property {{0}} is set"
			,"ger":"Keine weiteren Eigenschaften sind erlaubt; die Eigenschaft {{0}} ist gesetzt"}
		,"zms.formulator.lib.ERROR_ANYOF":{"eng":"Value must validate against at least one of the provided schemas"
			,"fra":"Value must validate against at least one of the provided schemas"
			,"ger":"Value must validate against at least one of the provided schemas"}
		,"zms.formulator.lib.ERROR_DEPENDENCY":{"eng":"Must have property {{0}}"
			,"fra":"Must have property {{0}}"
			,"ger":"Muss die Eigenschaft {{0}} haben"}
		,"zms.formulator.lib.ERROR_DISALLOW":{"eng":"Value must not be of type {{0}}"
			,"fra":"Value must not be of type {{0}}"
			,"ger":"Der Wert darf nicht dem Typen {{0}} entsprechen"}
		,"zms.formulator.lib.ERROR_DISALLOW_UNION":{"eng":"Value must not be one of the provided disallowed types"
			,"fra":"Value must not be one of the provided disallowed types"
			,"ger":"Der Wert darf nicht einem der unerlaubten Typen entsprechen"}
		,"zms.formulator.lib.ERROR_ENUM":{"eng":"Value must be one of the enumerated values"
			,"fra":"Value must be one of the enumerated values"
			,"ger":"Der Wert muss einem der aufgezählten Werte entsprechen"}
		,"zms.formulator.lib.ERROR_MANDATORY":{"eng":"Value is mandatory"
			,"fra":"Value is mandatory"
			,"ger":"Der Wert ist eine Pflichtangabe"}
		,"zms.formulator.lib.ERROR_MAXIMUM_EXCL":{"eng":"Value must be less than {{0}}"
			,"fra":"Value must be less than {{0}}"
			,"ger":"Der Wert muss kleiner sein als {{0}}"}
		,"zms.formulator.lib.ERROR_MAXIMUM_INCL":{"eng":"Value must be at most {{0}}"
			,"fra":"Value must be at most {{0}}"
			,"ger":"Der Wert muss maximal {{0}} sein"}
		,"zms.formulator.lib.ERROR_MAXITEMS":{"eng":"Value must have at most {{0}} items"
			,"fra":"Value must have at most {{0}} items"
			,"ger":"Der Wert darf maximal {{0}} Elemente enthalten"}
		,"zms.formulator.lib.ERROR_MAXLENGTH":{"eng":"Value must be at most {{0}} characters long"
			,"fra":"Value must be at most {{0}} characters long"
			,"ger":"Der Wert darf maximal {{0}} Zeichen lang sein"}
		,"zms.formulator.lib.ERROR_MAXPROPERTIES":{"eng":"Object must have at most {{0}} properties"
			,"fra":"Object must have at most {{0}} properties"
			,"ger":"Das Objekt darf maximal {{0}} Eigenschaften haben"}
		,"zms.formulator.lib.ERROR_MINIMUM_EXCL":{"eng":"Value must be greater than {{0}}"
			,"fra":"Value must be greater than {{0}}"
			,"ger":"Der Wert muss grösser sein als {{0}}"}
		,"zms.formulator.lib.ERROR_MINIMUM_INCL":{"eng":"Value must be at least {{0}}"
			,"fra":"Value must be at least {{0}}"
			,"ger":"Der Wert muss mindestens {{0}} sein"}
		,"zms.formulator.lib.ERROR_MINITEMS":{"eng":"Value must have at least {{0}} items"
			,"fra":"Value must have at least {{0}} items"
			,"ger":"Der Wert muss mindestens {{0}} Elemente enthalten"}
		,"zms.formulator.lib.ERROR_MINLENGTH":{"eng":"Value must be at least {{0}} characters long"
			,"fra":"Value must be at least {{0}} characters long"
			,"ger":"Der Wert muss mindestens {{0}} Zeichen lang sein"}
		,"zms.formulator.lib.ERROR_MINPROPERTIES":{"eng":"Object must have at least {{0}} properties"
			,"fra":"Object must have at least {{0}} properties"
			,"ger":"Das Objekt muss mindestens {{0}} Eigenschaften haben"}
		,"zms.formulator.lib.ERROR_MULTIPLEOF":{"eng":"Value must be a multiple of {{0}}"
			,"fra":"Value must be a multiple of {{0}}"
			,"ger":"Der Wert muss ein Vielfaches von {{0}} sein"}
		,"zms.formulator.lib.ERROR_NOT":{"eng":"Value must not validate against the provided schema"
			,"fra":"Value must not validate against the provided schema"
			,"ger":"Value must not validate against the provided schema"}
		,"zms.formulator.lib.ERROR_NOTEMPTY":{"eng":"Value required"
			,"fra":"Value required"
			,"ger":"Es wird ein Wert benötigt"}
		,"zms.formulator.lib.ERROR_NOTSET":{"eng":"Property must be set"
			,"fra":"Property must be set"
			,"ger":"Eigenschaft muss angegeben werden"}
		,"zms.formulator.lib.ERROR_ONEOF":{"eng":"Value must validate against exactly one of the provided schemas. It currently validates against {{0}} of the schemas."
			,"fra":"Value must validate against exactly one of the provided schemas. It currently validates against {{0}} of the schemas."
			,"ger":"Value must validate against exactly one of the provided schemas. It currently validates against {{0}} of the schemas."}
		,"zms.formulator.lib.ERROR_PATTERN":{"eng":"Value must match the provided pattern"
			,"fra":"Value must match the provided pattern"
			,"ger":"Der Wert muss dem vorgegebenen Muster entsprechen"}
		,"zms.formulator.lib.ERROR_REQUIRED":{"eng":"Object is missing the required property '{{0}}'"
			,"fra":"Object is missing the required property '{{0}}'"
			,"ger":"Dem Objekt fehlt die benötigte Eigenschaft '{{0}}'"}
		,"zms.formulator.lib.ERROR_TYPE":{"eng":"Value must be of type {{0}}"
			,"fra":"Value must be of type {{0}}"
			,"ger":"Der Wert muss dem Typen {{0}} entsprechen"}
		,"zms.formulator.lib.ERROR_TYPE_UNION":{"eng":"Value must be one of the provided types"
			,"fra":"Value must be one of the provided types"
			,"ger":"Der Wert muss dem vorgegebenen Typen entsprechen"}
		,"zms.formulator.lib.ERROR_UNIQUEITEMS":{"eng":"Array must have unique items"
			,"fra":"Array must have unique items"
			,"ger":"Das Feld darf nur eindeutige Elemente enthalten!"}
		,"zms.formulator.lib.FEEDBACK_MSG":{"eng":"Thank you, we have received the data."
			,"fra":"Thank you, we have received the data."
			,"ger":"Vielen Dank, die Daten sind bei uns eingegangen."}
		,"zms.formulator.lib.HINT_CHECKINPUT":{"eng":"Please check your input!"
			,"fra":"Please check your input!"
			,"ger":"Bitte überprüfen Sie Ihre Eingabe!"}
		,"zms.formulator.lib.HINT_DATANOTSENT":{"eng":"Data was not sent. Are you a robot?"
			,"fra":"Data was not sent. Are you a robot?"
			,"ger":"Daten wurden nicht übertragen! Bist du etwa ein Roboter?"}
		,"zms.formulator.lib.HINT_DATASENT":{"eng":"Data was sent."
			,"fra":"Data was sent."
			,"ger":"Die Daten wurden übertragen."}
		,"zms.formulator.lib.HINT_EMAILSYNTAX":{"eng":"E-Mails expect a format like \\\"user@domain.tld\\\""
			,"fra":"E-Mails expect a format like \\\"user@domain.tld\\\""
			,"ger":"E-Mails erwarten ein Format wie \\\"user@domain.tld\\\""}
		,"zms.formulator.lib.HINT_ERROROCCURED":{"eng":"An Error occurred!"
			,"fra":"An Error occurred!"
			,"ger":"Es ist ein Fehler aufgetreten!"}
		,"zms.formulator.lib.HINT_FILESIZE":{"eng":"File size:"
			,"fra":"File size:"
			,"ger":"Dateigröße:"}
		,"zms.formulator.lib.HINT_FILETYPE":{"eng":"File type:"
			,"fra":"File type:"
			,"ger":"Dateityp:"}
		,"zms.formulator.lib.HINT_MULTISELECT":{"eng":"Hint: Select multiple entries by holding cmd- or Ctrl-key."
			,"fra":"Hint: Select multiple entries by holding cmd- or Ctrl-key."
			,"ger":"Tipp: Sie können mehrere Einträge durch das Halten der cmd- bzw. Strg-Taste auswählen."}}

	# Name
	name = "zms.formulator.lib"

	# Package
	package = "zms.formulator"

	# Revision
	revision = "5.0.1"

	# Type
	type = "ZMSLibrary"

	# Attrs
	class Attrs:
		jsoneditorminjs = {"default":""
			,"id":"jsoneditor.min.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JSONEditor-1.3.5"
			,"repetitive":0
			,"type":"resource"}

		jsoneditorcustomjs = {"default":""
			,"id":"jsoneditor.custom.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JSONEditor-custom"
			,"repetitive":0
			,"type":"resource"}

		jsoneditor = {"default":""
			,"id":"JSONEditor"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"JSONEditor"
			,"repetitive":0
			,"type":"External Method"}

		zmsformulator = {"default":""
			,"id":"ZMSFormulator"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"ZMSFormulator"
			,"repetitive":0
			,"type":"External Method"}

		getjsoneditor = {"default":""
			,"id":"getJSONEditor"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"getJSONEditor"
			,"repetitive":0
			,"type":"External Method"}

		getjsonschema = {"default":""
			,"id":"getJSONSchema"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"getJSONSchema"
			,"repetitive":0
			,"type":"External Method"}

		printdata = {"default":""
			,"id":"printData"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"printData"
			,"repetitive":0
			,"type":"External Method"}

		putdata = {"default":""
			,"id":"putData"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"putData"
			,"repetitive":0
			,"type":"External Method"}

		resetdata = {"default":""
			,"id":"resetData"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"resetData"
			,"repetitive":0
			,"type":"External Method"}

		downloaddata = {"default":""
			,"id":"downloadData"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"downloadData"
			,"repetitive":0
			,"type":"External Method"}

		readmemd = {"default":""
			,"id":"readme.md"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Readme"
			,"repetitive":0
			,"type":"zpt"}
