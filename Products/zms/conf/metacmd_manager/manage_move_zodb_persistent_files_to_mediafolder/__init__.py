class manage_move_zodb_persistent_files_to_mediafolder:
	"""
	python-representation of manage_move_zodb_persistent_files_to_mediafolder
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_move_zodb_persistent_files_to_mediafolder"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_move_zodb_persistent_files_to_mediafolder"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Re-Index All Clients"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.mediafolder"

	# Revision
	revision = "0.0.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Move ZODB Persistent Files to Media Folder"

	# Impl
	class Impl:
		manage_zmsindex_reindex = {"id":"manage_move_zodb_persistent_files_to_mediafolder"
			,"type":"External Method"}
