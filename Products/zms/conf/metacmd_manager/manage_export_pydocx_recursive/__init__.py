class manage_export_pydocx_recursive:
	"""
	python-representation of manage_export_pydocx_recursive
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_export_pydocx_recursive"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-download text-danger"

	# Id
	id = "manage_export_pydocx_recursive"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "Py-DOCX Export (Recursive)"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.export"

	# Revision
	revision = "5.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Py-DOCX Export (Recursive)"

	# Impl
	class Impl:
		manage_export_pydocx_recursive = {"id":"manage_export_pydocx_recursive"
			,"type":"External Method"}
