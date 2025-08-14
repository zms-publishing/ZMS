# -*- coding: utf-8 -*-

def get_ontology_attropts(self):
	request = self.REQUEST
	ontology = self.get_ontology()

	# Create a list of attribute options for each facet key.
	attropts = []
	for facet in list(ontology.keys()):
		for term in list(ontology[facet].keys()):
			attropts.append([term, ontology[facet][term]])

	return attropts

