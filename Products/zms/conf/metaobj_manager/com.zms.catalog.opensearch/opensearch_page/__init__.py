class opensearch_page:
	"""
	python-representation of opensearch_page
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
	id = "opensearch_page"

	# Lang_dict
	lang_dict = {"opensearch_page.BTN_SEARCH":{"eng":"Search"
			,"fra":"Recherche"
			,"ger":"Suchen"
			,"ita":"Ricerca"}
		,"opensearch_page.INFO_KEYWORD":{"eng":"Keyword"
			,"fra":"Mot-clé"
			,"ger":"Stichwort"
			,"ita":"Parola chiave"}
		,"opensearch_page.INFO_LOADING":{"eng":"Is loading ..."
			,"fra":"En attendant ..."
			,"ger":"Wird geladen..."
			,"ita":"In attesa ..."}
		,"opensearch_page.INFO_RESULTS":{"eng":"Hits"
			,"fra":"Résultats"
			,"ger":"Treffer"
			,"ita":"Colpi"}
		,"opensearch_page.INFO_RESULTS_FOR":{"eng":"Hits for"
			,"fra":"Les hits pour"
			,"ger":"Treffer für"
			,"ita":"Colpi per"}
		,"opensearch_page.INFO_SEARCH":{"eng":"Search for Keywords"
			,"fra":"Recherche de mots-clés"
			,"ger":"Suche nach Stichworten"
			,"ita":"Ricerca per parole chiave"}
		,"opensearch_page.INFO_UNIBE":{"eng":"Content"
			,"fra":"Contenu"
			,"ger":"Inhalte"
			,"ita":"Contenuto"}
		,"opensearch_page.INFO_UNITEL":{"eng":"Persons"
			,"fra":"Personnes"
			,"ger":"Personen"
			,"ita":"Persone"}
		,"opensearch_page.SEARCH_FOR":{"eng":"Search for"
			,"fra":"Recherche de"
			,"ger":"Suche nach"
			,"ita":"Ricerca di"}
		,"opensearch_page.TOP_RESULTS":{"eng":"Top Hits"
			,"fra":"Meilleurs résultats"
			,"ger":"Top-Treffer"
			,"ita":"Colpo di punta"}
		,"opensearch_page.UNITEL_KEY_EMail":{"eng":"E-Mail"
			,"fra":"E-Mail"
			,"ger":"E-Mail"
			,"ita":"E-Mail"}
		,"opensearch_page.UNITEL_KEY_Institution":{"eng":"Institution"
			,"fra":"Institution"
			,"ger":"Institution"
			,"ita":"Istituzione"}
		,"opensearch_page.UNITEL_KEY_Institutionstelefon":{"eng":"Institution phone"
			,"fra":"Téléphone de l'institution"
			,"ger":"Institutionstelefon"
			,"ita":"Telefono dell'istituzione"}
		,"opensearch_page.UNITEL_KEY_Land":{"eng":"Country"
			,"fra":"Pays"
			,"ger":"Land"
			,"ita":"Paese"}
		,"opensearch_page.UNITEL_KEY_Ort":{"eng":"City"
			,"fra":"Ville"
			,"ger":"Ort"
			,"ita":"Città"}
		,"opensearch_page.UNITEL_KEY_PLZ":{"eng":"ZIP"
			,"fra":"Code postal"
			,"ger":"PLZ"
			,"ita":"CAP"}
		,"opensearch_page.UNITEL_KEY_StrassePostfach":{"eng":"Street / P.O. Box"
			,"fra":"Rue / Boîte postale"
			,"ger":"Strasse / Postfach"
			,"ita":"Strada / Casella postale"}
		,"opensearch_page.UNITEL_KEY_Telefondirekt1":{"eng":"Phone direct"
			,"fra":"Téléphone direct"
			,"ger":"Telefon direkt"
			,"ita":"Telefono diretto"}
		,"opensearch_page.UNITEL_KEY_WWWInstitution":{"eng":"Internet"
			,"fra":"Internet"
			,"ger":"Internet"
			,"ita":"Internet"}}

	# Name
	name = "Opensearch-Page"

	# Package
	package = "com.zms.catalog.opensearch"

	# Revision
	revision = "1.8.17"

	# Type
	type = "ZMSDocument"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-search text-primary"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

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

		multisite_search = {"default":"1"
			,"id":"multisite_search"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Multisite-Search"
			,"repetitive":0
			,"type":"boolean"}

		multisite_exclusions = {"default":""
			,"id":"multisite_exclusions"
			,"keys":["##"
				,"master = context.unibe.content"
				,"zmsclientids = []"
				,"def getZMSPortalClients(zmsclient):"
				,"  zmsclientids.append(zmsclient.getHome().id)"
				,"  for zmsclientid in zmsclient.getPortalClients():"
				,"    getZMSPortalClients(zmsclientid)"
				,"  zmsclientids.sort()"
				,"  return list(zmsclientids)"
				,"return [(id,id) for id in getZMSPortalClients(zmsclient=master)]"]
			,"mandatory":0
			,"multilang":0
			,"name":"Multisite-Exclusions"
			,"repetitive":0
			,"type":"multiautocomplete"}

		adwords_linked = {"default":""
			,"id":"adwords_linked"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Linked Adwords"
			,"repetitive":0
			,"type":"url"}

		scriptjs = {"default":""
			,"id":"script.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Script (JS)"
			,"repetitive":0
			,"type":"resource"}

		stylecss = {"default":""
			,"id":"style.css"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Style (CSS)"
			,"repetitive":0
			,"type":"resource"}

		handlebarsjs = {"default":""
			,"id":"handlebars.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Handlebars: JS 4.7.7"
			,"repetitive":0
			,"type":"resource"}

		adwords = {"default":""
			,"id":"adwords"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Adwords (Toptreffer)"
			,"repetitive":0
			,"type":"adwords"}

		opensearch_breadcrumbs_obj_path = {"default":""
			,"id":"opensearch_breadcrumbs_obj_path"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Get Object Path from ZMSIndex as HTML"
			,"repetitive":0
			,"type":"Script (Python)"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: Opensearch"
			,"repetitive":0
			,"type":"zpt"}
