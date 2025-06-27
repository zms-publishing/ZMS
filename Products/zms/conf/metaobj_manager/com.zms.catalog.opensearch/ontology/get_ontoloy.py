## Script (Python) "ontology.get_ontoloy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=zmscontext=None,options=None
##title=py: Get Facetted Ontology
##
# --// get_ontoloy //--
from Products.zms import standard
request = container.REQUEST
langs = context.content.getLanguages(request)

res = context.content.getChildNodes(request,'ontology')[0].attr('records')
if not res:
	return "No ontology records found."

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

# Return JSON representation of the ontology.
return context.content.str_json(facet_groups)
# --// /get_ontoloy //--
