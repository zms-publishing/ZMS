class manage_tab_search:
	"""
	python-representation of manage_tab_search
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_search"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_tab_search"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "TAB_SEARCH"

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "TAB_SEARCH"

	# Impl
	class Impl:
		manage_tab_search = {"id":"manage_tab_search"
			,"type":"Page Template"}
