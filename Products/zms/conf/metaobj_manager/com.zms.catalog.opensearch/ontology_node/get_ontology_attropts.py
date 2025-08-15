# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
from Products.zms import standard

def get_ontology_attropts(self):
	request = self.REQUEST
	ontology = self.get_ontology()

	# Create a list of attribute options for each facet key.
	attropts = []
	if not ontology.keys():
		return ["NO DATA FOUND"]

	# Aggregate the hierarchy to key/value set where the key is
	# the last element in the hierarchy path and the value is
	# a concatenatination of all titles of the path.
	# Do not append an element if it has sub-nodes.
	def aggregate_hierarchy(ontology, parent_title=''):
		for key, value in ontology.items():
			if isinstance(value, dict):
				title = value.get('title', key)
				if parent_title:
					title = f"{parent_title} &#x2005;&rsaquo; {title}"
				if 'nodes' not in value.keys():
					attropts.append({
						'key': key,
						'title': title
					})
				else:
					aggregate_hierarchy(value['nodes'], title)
			else:
				title = value

	aggregate_hierarchy(ontology)

	# Sort the attribute options by title
	attropts.sort(key=lambda x: x['title'])

	# Convert the dict to a ZMI-like list of tuples
	attropts = [(opt['key'], opt['title']) for opt in attropts]


	# If the request is for JSON, return the attribute options as JSON.
	if request.get('URL0').endswith('/get_ontology_attropts'):
		return json.dumps(attropts, indent=2)
	else:
		# Otherwise, return the attribute options directly.
		return attropts
