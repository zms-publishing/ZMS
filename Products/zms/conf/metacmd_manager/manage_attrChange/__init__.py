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
	execution = False

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

	# Revision
	revision = "5.2.0"

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
