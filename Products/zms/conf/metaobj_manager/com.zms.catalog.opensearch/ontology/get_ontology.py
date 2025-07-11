# -*- coding: utf-8 -*-
from Products.zms import standard

def get_ontology(self):
	"""
	Get (Facetted) Ontology
	This function retrieves the ontology records from the ZMS context and organizes them into facet groups based on their keys and languages.
	It returns a JSON representation of the ontology, which can be used for further processing or display.
	"""
	zmscontext = self
	request = self.REQUEST
	try:
		langs = zmscontext.getLanguages(request)
	except:
		zmscontext = self.content
		langs = zmscontext.getLanguages(request)
		pass

	# Get closed ontology records by acquisition along the breadcrumb path.
	ontology_obj = standard.operator_getattr(zmscontext, 'ontology')
	if not ontology_obj:
		return "WARNING: No ontology found."
	else:
		res =  ontology_obj.attr('records')
		if not res:
			return "WARNING: No data found."

	# Get facet-keys from the ontology records.
	facet_keys = sorted(set([r['facet'] for r in res if 'facet' in r and r['facet']!= '']))
	facet_groups = {k: {} for k in facet_keys}

	# Create facet groups in two steps:
	# --------------------------------------------------------------------
	# 1. Adding lang-dict to each facet
	# --------------------------------------------------------------------
	for r in res:
		k = r.get('key')
		if k and k.startswith('facet_') and k.replace('facet_', '') in facet_keys:
			facet_key = k.replace('facet_', '')
			for lang in langs:
				if lang in r.keys():
					if facet_key not in facet_groups:
						facet_groups[facet_key] = {}
					if lang not in facet_groups[facet_key]:
						facet_groups[facet_key][lang] = r[lang]

	#--------------------------------------------------------------------
	# 2. Adding all linked keys and its translations to each facet.
	#--------------------------------------------------------------------
	for r in res:
		if 'facet' in r and r['facet'] in facet_keys:
			facet_key = r['facet']
			# Clean up record by removing the technical keys starting with '_'.
			r = {k: v for k, v in r.items() if ( not k.startswith('_') and k != 'facet' )}
			facet_groups[facet_key][r['key']]= {}
			for lang in langs:
				if lang in r.keys():
					facet_groups[facet_key][r['key']][lang] = r[lang]
		elif not r['key'].startswith('facet_'):
		# Add not-facetted keys to the 'default' facet group.
			if 'default' not in facet_groups:
				facet_groups['default'] = {}
			facet_groups['default'][r['key']] = {}
			for lang in langs:
				if lang in r.keys():
					facet_groups['default'][r['key']][lang] = r[lang]

	# For debugging purposes, return the facet groups 
	# as JSON representation.
	if request.get('URL0').endswith('/get_ontology'):
		return standard.str_json(facet_groups)
	# For production return the facet groups directly.
	return facet_groups
