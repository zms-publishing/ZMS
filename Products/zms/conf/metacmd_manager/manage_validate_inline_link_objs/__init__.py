class manage_validate_inline_link_objs:
	"""
	python-representation of manage_validate_inline_link_objs
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_validate_inline_link_objs"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_validate_inline_link_objs"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Validate Inline-Link-Objects..."

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.metacmd"

	# Revision
	revision = "0.0.2"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Validate Inline-Link-Objects..."

	# Impl
	class Impl:
		manage_zmsindex_reindex = {"id":"manage_validate_inline_link_objs"
			,"type":"External Method"}
