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

	# Package
	package = "com.zms.foundation.metacmd.gitbridge"

	# Revision
	revision = "5.1.1"

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
