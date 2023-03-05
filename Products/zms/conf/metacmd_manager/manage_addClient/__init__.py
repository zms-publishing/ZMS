class manage_addClient:
	"""
	python-representation of manage_addClient
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_addClient"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-home"

	# Id
	id = "manage_addClient"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "ZMS-Client..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "insert"

	# Title
	title = "Insert new ZMS-Client"

	# Impl
	class Impl:
		manage_addclient = {"id":"manage_addClient"
			,"type":"External Method"}
