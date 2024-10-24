class manage_translate:
	"""
	python-representation of manage_translate
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_translate"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-globe text-success"

	# Id
	id = "manage_translate"

	# Meta_types
	meta_types = ["ZMSDocument"
		,"ZMSFolder"
		,"ZMS"]

	# Name
	name = "Translate..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.1"

	# Roles
	roles = ["ZMSEditor"
		,"ZMSAuthor"
		,"ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Translate Node-Content"

	# Impl
	class Impl:
		manage_translate = {"id":"manage_translate"
			,"type":"DTML Method"}
