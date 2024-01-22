class manage_zmsindex_reindex_paged:
	"""
	python-representation of manage_zmsindex_reindex_paged
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zmsindex_reindex_paged"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_zmsindex_reindex_paged"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Reindex paged..."

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.index"

	# Revision
	revision = "1.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Reindex paged"

	# Impl
	class Impl:
		manage_zmsindex_reindex_paged = {"id":"manage_zmsindex_reindex_paged"
			,"type":"External Method"}
