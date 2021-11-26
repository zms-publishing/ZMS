class manage_repository_commit:
	"""
	python-representation of manage_repository_commit
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_repository_commit"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-forward"

	# Id
	id = "manage_repository_commit"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "BTN_COMMIT"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "4.9.9"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "repository"

	# Title
	title = "Git Push"

	# Impl
	class Impl:
		manage_repository_commit = {"id":"manage_repository_commit"
			,"type":"External Method"}
