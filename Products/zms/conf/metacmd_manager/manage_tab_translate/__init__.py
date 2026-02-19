class manage_tab_translate:
	"""
	python-representation of manage_tab_translate
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_tab_translate"

	# Description
	description = "Translate Node-Content"

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-globe text-success"

	# Id
	id = "manage_tab_translate"

	# Meta_types
	meta_types = ["*"]

	# Name
	name = "Translate"

	# Nodes
	nodes = "{$}"

	# Package
	package = "com.zms.custom.metacmd.tabs"

	# Revision
	revision = "6.1.2"

	# Roles
	roles = ["ZMSEditor"
		,"ZMSAuthor"
		,"ZMSAdministrator"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "Translate Node-Content"

	# Impl
	class Impl:
		manage_tab_translate = {"id":"manage_tab_translate"
			,"type":"External Method"}
