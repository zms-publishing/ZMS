class ZMSDiagram:
	"""
	python-representation of ZMSDiagram
	"""

	# Access
	access = {"delete_custom":""
		,"delete_deny":[""
			,""
			,""]
		,"insert_custom":"{$}"
		,"insert_deny":[""
			,""
			,""]}

	# Enabled
	enabled = 1

	# Id
	id = "ZMSDiagram"

	# Name
	name = "ZMSDiagram"

	# Package
	package = "zms.diagrams"

	# Revision
	revision = "0.0.5"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"fas fa-project-diagram"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"icon_clazz"
			,"repetitive":0
			,"type":"constant"}

		attr_dc_type = {"default":""
			,"id":"attr_dc_type"
			,"keys":["Business Process Model and Notation"
				,"Decision Model and Notation"
				,"Entity Relationship Model"
				,"Requirement Diagram"
				,"Sequence Diagram"
				,"Class Diagram"
				,"State Diagram"
				,"User Journey"
				,"Gantt Chart"
				,"Pie Chart"
				,"Flowchart"
				,"Gitgraph"
				,"Timeline"
				,"Mindmap"]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Type"
			,"repetitive":0
			,"type":"select"}

		diagram_code = {"default":""
			,"id":"diagram_code"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Code"
			,"repetitive":0
			,"type":"text"}

		interface_mermaid = {"default":""
			,"id":"interface_mermaid"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface_mermaid"
			,"repetitive":0
			,"type":"interface"}

		diagram_file = {"default":""
			,"id":"diagram_file"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"File"
			,"repetitive":0
			,"type":"file"}

		interface_bpmn = {"default":""
			,"id":"interface_bpmn"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface_bpmn"
			,"repetitive":0
			,"type":"interface"}

		bpmn_viewerjs = {"default":""
			,"id":"bpmn-viewer.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"BPMN-Viewer-11.4.1"
			,"repetitive":0
			,"type":"resource"}

		bpmn_viewerhtml = {"default":""
			,"id":"bpmn-viewer.html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"BPMN-Viewer-11.4.1"
			,"repetitive":0
			,"type":"Page Template"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSDiagram"
			,"repetitive":0
			,"type":"zpt"}
