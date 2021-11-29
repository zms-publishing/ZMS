class manage_repository_gitpull:
	"""
	python-representation of manage_repository_gitpull
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_repository_gitpull"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-backward"

	# Id
	id = "manage_repository_gitpull"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "BTN_GITPULL"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "5.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "repository"

	# Title
	title = "Git Pull"

	# Impl
	class Impl:
		manage_repository_gitpull = {"id":"manage_repository_gitpull"
			,"type":"External Method"}
