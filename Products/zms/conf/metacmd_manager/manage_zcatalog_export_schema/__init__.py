class manage_zcatalog_export_schema:
	"""
	python-representation of manage_zcatalog_export_schema
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zcatalog_export_schema"

	# Description
	description = "Export JSON schema?"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_zcatalog_export_schema"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "#1 Export schema"

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
	title = "Export JSON schema"

	# Impl
	class Impl:
		manage_zcatalog_export_schema = {"id":"manage_zcatalog_export_schema"
			,"type":"External Method"}
