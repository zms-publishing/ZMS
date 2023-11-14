class manage_zcatalog_afterDeleteObjsEvt:
	"""
	python-representation of manage_zcatalog_afterDeleteObjsEvt
	"""

	# Acquired
	acquired = 0

	# Action
	action = "javascript:%%smanage_zcatalog_afterDeleteObjsEvt"

	# Description
	description = ""

	# Execution
	execution = 2

	# Icon_clazz
	icon_clazz = "fas fa-cogs"

	# Id
	id = "manage_zcatalog_afterDeleteObjsEvt"

	# Meta_types
	meta_types = []

	# Name
	name = "ZCatalog: uncatalog objects"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.foundation.zcatalog.opensearch"

	# Revision
	revision = "0.0.0"

	# Roles
	roles = []

	# Stereotype
	stereotype = "zcatalog"

	# Title
	title = "ZCatalog: uncatalog objects"

	# Impl
	class Impl:
		manage_zcatalog_afterdeleteobjsevt = {"id":"manage_zcatalog_afterDeleteObjsEvt"
			,"type":"External Method"}
