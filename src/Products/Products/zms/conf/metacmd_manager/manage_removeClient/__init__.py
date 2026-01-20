class manage_removeClient:
	"""
	python-representation of manage_removeClient
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_removeClient"

	# Description
	description = "Do you really want to remove ZMS-Client?"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-times text-danger"

	# Id
	id = "manage_removeClient"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Remove ZMS-Client..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.2"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Remove ZMS-Client..."

	# Impl
	class Impl:
		manage_removeclient = {"id":"manage_removeClient"
			,"type":"Script (Python)"}
