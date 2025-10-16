class manage_change_primary_lang:
	"""
	python-representation of manage_change_primary_lang
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_change_primary_lang"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-flag text-danger"

	# Id
	id = "manage_change_primary_lang"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Change primary language..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "0.0.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Change primary language..."

	# Impl
	class Impl:
		manage_removeclient = {"id":"manage_change_primary_lang"
			,"type":"Script (Python)"}
