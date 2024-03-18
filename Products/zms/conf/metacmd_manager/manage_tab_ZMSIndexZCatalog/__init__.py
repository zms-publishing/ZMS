class manage_tab_ZMSIndexZCatalog:
	"""
	python-representation of manage_tab_ZMSIndexZCatalog
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_ZMSIndexZCatalog"

	# Description
	description = "ZMSIndex"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_tab_ZMSIndexZCatalog"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "ZMSIndex"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.index"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "ZMSIndex"

	# Impl
	class Impl:
		manage_tab_zmsindexzcatalog = {"id":"manage_tab_ZMSIndexZCatalog"
			,"type":"External Method"}
