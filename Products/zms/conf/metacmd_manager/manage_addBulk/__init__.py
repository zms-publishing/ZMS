class manage_addBulk:
	"""
	python-representation of manage_addBulk
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_addBulk"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-home"

	# Id
	id = "manage_addBulk"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "ZMS-Bulk test-data..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "1.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "insert"

	# Title
	title = "Insert new ZMS-Bulk test-data"

	# Impl
	class Impl:
		manage_addbulk = {"id":"manage_addBulk"
			,"type":"External Method"}
