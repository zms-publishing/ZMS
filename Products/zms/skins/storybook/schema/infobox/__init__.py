class infobox:
	"""
	python-representation of infobox
	"""

	# Access
	access = {"delete_custom": ""
		,"delete_deny": "[]"
		,"insert_custom": "{$}"
		,"insert_deny": "[]"}

	# Enabled
	enabled = 1

	# Id
	id = "infobox"

	# Name
	name = "Infobox"

	# Package
	package = "com.zms.infobox"

	# Revision
	revision = "0.0.1"

	# Type
	type = "ZMSObject"

	class Attrs:
		title = {"id": "title"
			,"type": "string"
			,"name": "Title"
			,"mandatory": "0"
			,"multilang": "1"
			,"repetitive": "0"
			,"default": ""
			,"keys": "[]"}

		attr_dc_description = {"id": "attr_dc_description"
			,"type": "text"
			,"name": "Description"
			,"mandatory": "0"
			,"multilang": "1"
			,"repetitive": "0"
			,"default": ""
			,"keys": "[]"}

		url = {"id": "url"
			,"type": "url"
			,"name": "Url"
			,"mandatory": "0"
			,"multilang": "1"
			,"repetitive": "0"
			,"default": ""
			,"keys": "[]"}

		linktext = {"id": "linktext"
			,"type": "string"
			,"name": "Linktext"
			,"mandatory": "0"
			,"multilang": "1"
			,"repetitive": "0"
			,"default": "Read more..."
			,"keys": "[]"}

