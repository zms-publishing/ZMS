class manage_addMultiUpload:
	"""
	python-representation of manage_addMultiUpload
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_addMultiUpload"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fas fa-upload text-danger"

	# Id
	id = "manage_addMultiUpload"

	# Meta_types
	meta_types = ["ZMSDocument"
		,"ZMSFolder"
		,"ZMS"]

	# Name
	name = "Multi-Upload"

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.1.0"

	# Roles
	roles = ["ZMSAdministrator"
		,"ZMSEditor"
		,"ZMSAuthor"]

	# Stereotype
	stereotype = "insert"

	# Title
	title = "Upload via Multi-Selection of Files"

	# Impl
	class Impl:
		manage_addmultiupload = {"id":"manage_addMultiUpload"
			,"type":"External Method"}
