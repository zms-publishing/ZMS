class manage_tab_langdict:
	"""
	python-representation of manage_tab_langdict
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_langdict"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_tab_langdict"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "TAB_LANGUAGES"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "TAB_LANGUAGES"

	# Impl
	class Impl:
		manage_tab_langdict = {"id":"manage_tab_langdict"
			,"type":"Script (Python)"}
