class manage_zcatalog_update_documents:
	"""
	python-representation of manage_zcatalog_update_documents
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_zcatalog_update_documents"

	# Description
	description = "Step 2: Update Solr Document Index based on a fresh XML Sitemap"

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-sync"

	# Id
	id = "manage_zcatalog_update_documents"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "Update Solr Document Index"

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
	title = "Update documents"

	# Impl
	class Impl:
		manage_zcatalog_update_documents = {"id":"manage_zcatalog_update_documents"
			,"type":"External Method"}
