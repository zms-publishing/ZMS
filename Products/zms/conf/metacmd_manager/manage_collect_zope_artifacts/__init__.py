class manage_collect_zope_artifacts:
	"""
	python-representation of manage_collect_zope_artifacts
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_collect_zope_artifacts"

	# Description
	description = ""

	# Execution
	execution = 0

	# Icon_clazz
	icon_clazz = "fas fa-briefcase"

	# Id
	id = "manage_collect_zope_artifacts"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Collect Zope Artifacts..."

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.0.2"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Transfer Zope Artifacts to a ZMS Content-Object Library"

	# Impl
	class Impl:
		manage_collect_zope_artifacts = {"id":"manage_collect_zope_artifacts"
			,"type":"External Method"}
