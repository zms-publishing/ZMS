class manage_cachepurge:
	"""
	python-representation of manage_cachepurge
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_cachepurge"

	# Description
	description = ""

	# Execution
	execution = 1

	# Icon_clazz
	icon_clazz = "fas fa-sync"

	# Id
	id = "manage_cachepurge"

	# Meta_types
	meta_types = ["ZMSDocument"
		,"ZMSFolder"
		,"ZMS"
		,"type(ZMSDocument)"]

	# Name
	name = "Cache-Purge"

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
	title = "Löscht den Cache Eintrag dieses Dokument-Knotens"

	# Impl
	class Impl:
		manage_cachepurge = {"id":"manage_cachepurge"
			,"type":"Script (Python)"}
