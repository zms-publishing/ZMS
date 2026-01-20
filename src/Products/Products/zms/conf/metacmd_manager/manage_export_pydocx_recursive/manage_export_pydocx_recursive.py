#!/usr/bin/python
# -*- coding: utf-8 -*-

def manage_export_pydocx_recursive(self):
	request = self.REQUEST
	file_name = self.id_quote(self.getTitlealt(request))
	zmsdocs = []
	zmsdocs.append(self)
	zmsdocs.extend(self.filteredTreeNodes(request, self.PAGES))
	docx_file_data = None
	for zmsdoc in zmsdocs:
		# Do return data on last zmsdoc
		save_file = zmsdoc == zmsdocs[-1]
		docx_file_data = zmsdoc.manage_export_pydocx(save_file = save_file, file_name = file_name)
	return docx_file_data