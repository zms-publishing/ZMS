class manage_opensearch_export_data_paged:
	"""
	python-representation of manage_opensearch_export_data_paged
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_opensearch_export_data_paged"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_opensearch_export_data_paged"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Opensearch: Export data paged"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.zcatalog.opensearch"

	# Revision
	revision = "0.0.2"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Opensearch: Export data paged"

	# Impl
	class Impl:
		manage_opensearch_export_data_paged = {"id":"manage_opensearch_export_data_paged"
			,"type":"External Method"}
