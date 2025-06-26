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

# Get facets from the ontology records.
facets = sorted(set([r['facet'] for r in res if 'facet' in r and r['facet']!= '']))

# Group the records by facet and key.
facet_groups = {k: {} for k in facets}

# Reorganize the records into the facet groups.
for record in res:
	if 'facet' in record and record['facet'] in facets:
		facet = record['facet']
		# Clean up record by removing the technical keys starting with '_'.
		record = {k: v for k, v in record.items() if ( not k.startswith('_') and k != 'facet' )}
		if 'key' in record:
			facet_groups[facet][record['key']]= {}
			for lang in langs:
				if lang in record.keys():
					facet_groups[facet][record['key']][lang] = record[lang]
# Add language keys to the facet groups if they are not present.
for record in res:
	keyid = record.get('key')
	if keyid and keyid.startswith('facet_') and keyid.replace('facet_', '') in facets:
		facet_id = keyid.replace('facet_', '')
		for lang in langs:
			if lang in record.keys():
				if facet_id not in facet_groups:
					facet_groups[facet_id] = {}
				if lang not in facet_groups[facet_id]:
					facet_groups[facet_id][lang] = record[lang]

# Return JSON representation of the ontology.
return context.content.str_json(facet_groups)
# --// /get_ontoloy //--
