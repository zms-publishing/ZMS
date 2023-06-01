class manage_attrChange:
	"""
	python-representation of manage_attrChange
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_attrChange"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-exchange-alt"

	# Id
	id = "manage_attrChange"

	# Meta_types
	meta_types = ["ZMSDocument"
		,"ZMSFolder"
		,"ZMS"]

	# Name
	name = "Change Attribute Values"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.metacmd.maintenance"

	# Revision
	revision = "5.2.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Change Attribute Values"

	# Impl
	class Impl:
		manage_attrchange = {"id":"manage_attrChange"
			,"type":"Script (Python)"}
