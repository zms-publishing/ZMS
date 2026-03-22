class manage_export_pdf:
	"""
	python-representation of manage_export_pdf
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_export_pdf"

	# Description
	description = "Export current page content as PDF (weasyprint)"

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-file-pdf text-danger"

	# Id
	id = "manage_export_pdf"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "PDF Export"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.export"

	# Revision
	revision = "1.0.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "PDF Export"

	# Impl
	class Impl:
		manage_export_pdf = {"id":"manage_export_pdf"
			,"type":"External Method"}
