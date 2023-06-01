class manage_zcatalog_export_data:
	"""
	python-representation of manage_zcatalog_export_data
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zcatalog_export_data"

	# Description
	description = "Export JSON data?"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_zcatalog_export_data"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "#2 Export data"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.zcatalog.opensearch"

	# Revision
	revision = "0.0.1"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "zcatalog"

	# Title
	title = "Export JSON data"

	# Impl
	class Impl:
		manage_zcatalog_export_data = {"id":"manage_zcatalog_export_data"
			,"type":"External Method"}
