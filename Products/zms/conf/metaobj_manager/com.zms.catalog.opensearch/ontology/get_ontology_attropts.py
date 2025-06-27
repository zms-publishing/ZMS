# -*- coding: utf-8 -*-

def get_ontology_attropts(self):
	request = self.REQUEST
	lang = request.get('lang', self.getPrimaryLanguage())
	langs = self.getLanguages(request)
	# Get ontology records by acquisition along the breadcrumb path.
	ontology = self.get_ontology()
	# Create a list of attribute options for each facet key.
	attropts = []
	for facet_key in [k for k in ontology.keys() if k != 'default']:
		for k, v in ontology[facet_key].items():
			if k not in langs:
				attropts.append([k, '%s / %s'%(k, v[lang])])
	return attropts

