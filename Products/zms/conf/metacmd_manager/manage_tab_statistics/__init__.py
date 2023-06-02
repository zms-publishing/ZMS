class manage_tab_statistics:
	"""
	python-representation of manage_tab_statistics
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_statistics"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "icon-cogs fas fa-chart-bar"

	# Id
	id = "manage_tab_statistics"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Statistics"

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.5"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "Content object usage statistics"

	# Impl
	class Impl:
		manage_tab_statistics = {"id":"manage_tab_statistics"
			,"type":"Page Template"}
