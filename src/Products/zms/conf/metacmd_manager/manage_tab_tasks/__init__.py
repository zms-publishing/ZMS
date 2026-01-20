class manage_tab_tasks:
	"""
	python-representation of manage_tab_tasks
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_tasks"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_tab_tasks"

	# Meta_types
	meta_types = ["type(ZMSDocument)"]

	# Name
	name = "TAB_TASKS"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.metacmd.tabs"

	# Revision
	revision = "5.0.4"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "TAB_TASKS"

	# Impl
	class Impl:
		manage_tab_tasks = {"id":"manage_tab_tasks"
			,"type":"Page Template"}
