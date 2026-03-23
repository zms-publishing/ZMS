class manage_cachepurge_list:
	"""
	python-representation of manage_cachepurge_list
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_cachepurge_list"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-sync"

	# Id
	id = "manage_cachepurge_list"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Cache-Purge (List)"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.cache"

	# Revision
	revision = "5.0.0"

	# Roles
	roles = ["ZMSAdministrator"
		,"ZMSEditor"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Liste von URLs aus dem Cache löschen"

	# Impl
	class Impl:
		manage_cachepurge_list = {"id":"manage_cachepurge_list"
			,"type":"Page Template"}
