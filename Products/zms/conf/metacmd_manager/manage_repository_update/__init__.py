class manage_repository_update:
	"""
	python-representation of manage_repository_update
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_repository_update"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-backward"

	# Id
	id = "manage_repository_update"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "BTN_UPDATE"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "4.9.9"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "repository"

	# Title
	title = "Git Pull"

	# Impl
	class Impl:
		manage_repository_update = {"id":"manage_repository_update"
			,"type":"External Method"}
