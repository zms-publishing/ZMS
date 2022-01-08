class manage_zcatalog_create_sitemap:
	"""
	python-representation of manage_zcatalog_create_sitemap
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zcatalog_create_sitemap"

	# Description
	description = "Step 1: Create XML Sitemap of all Documents"

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-sitemap"

	# Id
	id = "manage_zcatalog_create_sitemap"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "Create XML Sitemap"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.zcatalog.solr"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = ["*"]

	# Stereotype
	stereotype = "zcatalog"

	# Title
	title = "Create sitemap"

	# Impl
	class Impl:
		manage_zcatalog_create_sitemap = {"id":"manage_zcatalog_create_sitemap"
			,"type":"External Method"}
