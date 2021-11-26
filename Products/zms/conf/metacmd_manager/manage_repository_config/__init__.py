class manage_repository_config:
	"""
	python-representation of manage_repository_config
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_repository_config"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_repository_config"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "TAB_CONFIGURATION"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "4.9.9"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "repository"

	# Title
	title = "Git-Configuration"

	# Impl
	class Impl:
		manage_repository_config = {"id":"manage_repository_config"
			,"type":"External Method"}
