class manage_cleanup_recursive:
	"""
	python-representation of manage_cleanup_recursive
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_cleanup_recursive"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-trash-alt text-primary"

	# Id
	id = "manage_cleanup_recursive"

	# Meta_types
	meta_types = ["ZMSFolder"
		,"ZMS"]

	# Name
	name = "Remove inactive content"

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "0.8.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Listing and removal of obsolete inactive content"

	# Impl
	class Impl:
		manage_cleanup_recursive = {"id":"manage_cleanup_recursive"
			,"type":"External Method"}
