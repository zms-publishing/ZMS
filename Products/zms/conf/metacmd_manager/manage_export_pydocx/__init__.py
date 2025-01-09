class manage_export_pydocx:
	"""
	python-representation of manage_export_pydocx
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_export_pydocx"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-download text-primary"

	# Id
	id = "manage_export_pydocx"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "Py-DOCX Export"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.export"

	# Revision
	revision = "5.0.2"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Py-DOCX Export"

	# Impl
	class Impl:
		manage_export_pydocx = {"id":"manage_export_pydocx"
			,"type":"External Method"}
