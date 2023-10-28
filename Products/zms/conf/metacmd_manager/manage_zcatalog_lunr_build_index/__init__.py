class manage_zcatalog_lunr_build_index:
	"""
	python-representation of manage_zcatalog_lunr_build_index
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zcatalog_lunr_build_index"

	# Description
	description = "Build search_index.json"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-sitemap"

	# Id
	id = "manage_zcatalog_lunr_build_index"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "Build search_index.json"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.zcatalog.lunr"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "zcatalog"

	# Title
	title = "Build search_index.json"

	# Impl
	class Impl:
		manage_zcatalog_lunr_build_index = {"id":"manage_zcatalog_lunr_build_index"
			,"type":"External Method"}
