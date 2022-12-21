class manage_searchReplace:
	"""
	python-representation of manage_searchReplace
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_searchReplace"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-search"

	# Id
	id = "manage_searchReplace"

	# Meta_types
	meta_types = ["type(ZMSDocument)"
		,"type(ZMSObject)"]

	# Name
	name = "Search+Replace..."

	# Nodes
	nodes = "{$}"

	# Revision
	revision = "5.3.1"

	# Roles
	roles = ["ZMSAdministrator"
		,"ZMSEditor"
		,"ZMSAuthor"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Search and Replace..."

	# Impl
	class Impl:
		manage_searchreplace = {"id":"manage_searchReplace"
			,"type":"Script (Python)"}
