class manage_export_pdf_recursive:
	"""
	python-representation of manage_export_pdf_recursive
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_export_pdf_recursive"

	# Description
	description = "Export current document tree as one PDF (weasyprint)"

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-file-pdf text-danger"

	# Id
	id = "manage_export_pdf_recursive"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "PDF Export (Recursive)"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.export"

	# Revision
	revision = "1.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "PDF Export (Recursive)"

	# Impl
	class Impl:
		manage_export_pdf_recursive = {"id":"manage_export_pdf_recursive"
			,"type":"External Method"}
