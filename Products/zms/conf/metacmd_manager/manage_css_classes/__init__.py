class manage_css_classes:
	"""
	python-representation of manage_css_classes
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_css_classes"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fab fa-css3 text-primary"

	# Id
	id = "manage_css_classes"

	# Meta_types
	meta_types = ["ZMSTextarea"]

	# Name
	name = "CSS Specials"

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Add special CSS class names to object's internal_dict"

	# Impl
	class Impl:
		manage_css_classes = {"id":"manage_css_classes"
			,"type":"External Method"}
