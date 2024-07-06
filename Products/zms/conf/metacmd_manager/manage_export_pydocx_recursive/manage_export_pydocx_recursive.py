#!/usr/bin/python
# -*- coding: utf-8 -*-

def manage_export_pydocx_recursive(self):
	request = self.REQUEST
	filename = self.id_quote(self.getTitlealt(request))
	zmsdocs = []
	zmsdocs.append(self)
	zmsdocs.extend(self.filteredTreeNodes(request, self.PAGES))
	docx_data = None
	for zmsdoc in zmsdocs:
		# Do return data on last zmsdoc
		do_return = zmsdoc == zmsdocs[-1]
		docx_data = zmsdoc.manage_export_pydocx(do_return = do_return, filename = filename)            
	return docx_data