# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
from Products.zms import standard

def get_ontology_skos(self):
	"""
	Returns a SKOS-conformant list of terms from the ontology.
	Each term is a dict with 'id', 'prefLabel', and optionally 'broader' (parent key).
	Ref: https://www.w3.org/TR/skos-reference/
	The 'id' is derived from the ZMS-node ID, converting 'e123' to 123,
	so that it can be used as a primary key when migrating to a SQL database.
	"""
	zmscontext = self
	request = self.REQUEST
	request_lang = request.get('lang', zmscontext.getLanguage(request))

	ontology_obj = standard.operator_getattr(zmscontext, 'ontology')
	if not ontology_obj:
		return "WARNING: No ontology found."

	skos_terms = []
	languages = zmscontext.getLanguages(request)
	is_multilang = len(languages) > 1

	# Recursive function to collect terms from the ontology
	# Each term is a dict with 'id', 'prefLabel', and optionally 'broader' (parent key).
	# The 'id' is derived from the node ID, converting 'e123' to 123.
	# The 'prefLabel' is the title of the node.
	# The 'broader' is the parent term's ID if applicable.
	def collect_terms(node, parent_id=None):
		id = node.getId()
		key = node.attr('key')
		label = node.attr('title')

		if parent_id == None:
			id = 0  # Root node
		else:
			# Use the node ID as the term ID, converting 'e123' to 123
			if id.startswith('e'):
				id = int(id[1:]) # Convert 'e123' to 123

		if is_multilang:
			label = {}
			for lang in languages:
				request.set('lang', lang)
				label[lang] = node.attr('title')
			request.set('lang', request_lang)

		term = {
			'id': id,
			'url': node.absolute_url_path(),
			'altLabel': key,
			'prefLabel': label
		}

		# If the node has a description, add it as definition to the term.
		if is_multilang:
			definition = {}
			for lang in languages:
				request.set('lang', lang)
				if  node.attr('attr_dc_description'):
					definition[lang] = node.attr('attr_dc_description')
			request.set('lang', request_lang)
		elif node.attr('attr_dc_description'):
			definition = node.attr('attr_dc_description')
		if definition:
			term['definition'] = definition

		# If the node has a parent, add it as broader term.
		if parent_id or parent_id == 0:
			term['broader'] = parent_id
		skos_terms.append(term)
		for child in node.getChildNodes(request, meta_types=['ontology_node']):
			collect_terms(child, id)

	collect_terms(ontology_obj)

	# For debugging purposes, return as JSON if called directly
	if request.get('URL0').endswith('/get_ontology_skos'):
		return json.dumps(skos_terms, ensure_ascii=False, indent=2)