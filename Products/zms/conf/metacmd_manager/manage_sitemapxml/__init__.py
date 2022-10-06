class manage_sitemapxml:
	"""
	python-representation of manage_sitemapxml
	"""

	# Acquired
	acquired = 0

	# Action
	action = "%smanage_executeMetacmd?id=manage_sitemapxml"

	# Description
	description = ""

	# Execution
	execution = False

	# Icon_clazz
	icon_clazz = "fab fa-google"

	# Id
	id = "manage_sitemapxml"

	# Meta_types
	meta_types = ["ZMS"]

	# Name
	name = "Generate Google Sitemap"

	# Nodes
	nodes = "{$}"

	# Package
	package = ""

	# Revision
	revision = "5.1.0"

	# Roles
	roles = ["ZMSAdministrator"]

	# Stereotype
	stereotype = ""

	# Title
	title = "Generate sitemap.xml for Google"

	# Impl
	class Impl:
		manage_sitemapxml = {"id":"manage_sitemapxml"
			,"type":"External Method"}
