class manage_setObjState:
	"""
	python-representation of manage_setObjState
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_setObjState"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-hammer"

	# Id
	id = "manage_setObjState"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "Set object-state..."

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.metacmd.maintenance"

	# Revision
	revision = "0.0.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Set object-state..."

	# Impl
	class Impl:
		manage_setobjstate = {"id":"manage_setObjState"
			,"type":"Script (Python)"}
