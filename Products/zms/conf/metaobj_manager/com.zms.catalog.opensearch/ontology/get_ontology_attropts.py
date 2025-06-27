# -*- coding: utf-8 -*-

def get_ontology_attropts(self):
	request = self.REQUEST
	lang = request.get('lang', self.getPrimaryLanguage())
	langs = self.getLanguages(request)
	# Get ontology records by acquisition along the breadcrumb path.
	ontology = self.get_ontology()
	# Create a list of attribute options for each facet key.
	attropts = []
	for facet_key in list(ontology.keys()):
		for k, v in ontology[facet_key].items():
			if k not in langs:
				if facet_key == 'default':
					v  = v[lang]
				else:
					v  = '%s &#x25BA; %s'%(facet_key, v[lang])
				attropts.append([k, v])

	return attropts

