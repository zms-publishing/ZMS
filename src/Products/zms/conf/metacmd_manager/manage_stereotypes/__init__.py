class manage_stereotypes:
	"""
	python-representation of manage_stereotypes
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_stereotypes"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-cubes"

	# Id
	id = "manage_tab_stereotypes"

	# Meta_types
	meta_types = ["type(ZMSDocument)"
		,"type(ZMSObject)"
		,"type(ZMSTeaserElement)"
		,"type(ZMSRecordSet)"
		,"type(ZMSResource)"
		,"type(ZMSReference)"
		,"type(ZMSLibrary)"
		,"type(ZMSPackage)"
		,"type(ZMSModule)"]

	# Name
	name = "Stereotypes"

	# Nodes
	nodes = "{$}"

	# Package
	package = "ch.unibe.maintenance"

	# Revision
	revision = "4.0.3"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = "tab"

	# Title
	title = "Change stereotype"

	# Impl
	class Impl:
		manage_tab_stereotypes = {"id":"manage_stereotypes"
			,"type":"Script (Python)"}
