# -*- coding: utf-8 -*-

def get_ontology_attropts(self):
	request = self.REQUEST
	lang = request.get('lang', self.getPrimaryLanguage())
	langs = self.getLanguages(request)
	# Get ontology records by acquisition along the breadcrumb path.
	ontology = self.get_ontology()
	# If function get_ontology returns a string as warning message.
	if isinstance(ontology, str):
		return [('', ontology)]
	# Create a list of attribute options for each facet key.
	attropts = []
	for facet_key in list(ontology.keys()):
		for k, v in ontology[facet_key].items():
			if k not in langs and k!='sortid':
				if facet_key == 'default':
					v  = v[lang]
				else:
					try:
						# Attempt to translate the facet key using the ontology dictionary.
						facet_key_lang = ontology[facet_key].get(lang, facet_key)
					except:
						facet_key_lang = facet_key
					v  = '%s &#x25BA; %s'%(facet_key_lang, v[lang])
				attropts.append([k, v])

	return attropts

