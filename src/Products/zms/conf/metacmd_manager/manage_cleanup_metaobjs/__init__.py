class manage_cleanup_metaobjs:
	"""
	python-representation of manage_cleanup_metaobjs
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_cleanup_metaobjs"

	# Description
	description = "Really want to remove the defined list of metaobject-classes from all portal-clients?"

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_cleanup_metaobjs"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Meta-Object Cleanup"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.metacmd.maintenance"

	# Revision
	revision = "0.0.1"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Remove Meta-Object Definitions and Artefacts from Multisite"

	# Impl
	class Impl:
		manage_cleanup_metaobjs = {"id":"manage_cleanup_metaobjs"
			,"type":"Script (Python)"}
