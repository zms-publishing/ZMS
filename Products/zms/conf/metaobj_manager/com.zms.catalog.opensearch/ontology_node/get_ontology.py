# -*- coding: utf-8 -*-
from collections import OrderedDict
import json
from Products.zms import standard

def get_ontology(self):

	zmscontext = self
	request = self.REQUEST

	# Get ontology records by acquisition along the breadcrumb path.
	ontology_obj = standard.operator_getattr(zmscontext, 'ontology')

	if not ontology_obj:
		return "WARNING: No ontology found."

	def get_ontology_dict(self, request):
		ontology_dict = {}
		for ob in self.getChildNodes(request, meta_types=['ontology_node']):
			ontology_dict[ob.attr('key')] = {}
			ontology_dict[ob.attr('key')]['title'] = ob.attr('title')
			if get_ontology_dict(ob, request):
				ontology_dict[ob.attr('key')]['nodes'] = get_ontology_dict(ob, request)
		return ontology_dict

	ontology_dict = OrderedDict(get_ontology_dict(ontology_obj, request))	

	# For debugging purposes, return the facet groups 
	# as JSON representation.
	if request.get('URL0').endswith('/get_ontology'):
		return json.dumps(ontology_dict)
	# For production return the facet groups directly.
	return ontology_dict
