class ZMSObjectSet:
	"""
	python-representation of ZMSObjectSet
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
	enabled = 0

	# Id
	id = "ZMSObjectSet"

	# Name
	name = "ZMSObjectSet"

	# Package
	package = "com.zms.foundation"

	# Revision
	revision = "5.0.0"

	# Type
	type = "ZMSObject"

	# Attrs
	class Attrs:
		icon_clazz = {"custom":"far fa-list-alt"
			,"default":""
			,"id":"icon_clazz"
			,"keys":[]
			,"mandatory":0
			,"multilang":1
			,"name":"Icon (Class)"
			,"repetitive":0
			,"type":"constant"}

		record_meta_ids = {"default":""
			,"id":"record_meta_ids"
			,"keys":["##"
				,"l = []"
				,"request = context.REQUEST"
				,"metaobj_manager = context.getMetaobjManager()"
				,"l = [metaobj_manager.getMetaobj(x) for x in metaobj_manager.getMetaobjIds()]"
				,"l = [x for x in l if x['type'] in ['ZMSDocument','ZMSObject','ZMSRecordSet']]"
				,"l = [(x['id'],('%s %s'%(context.display_icon(meta_id=x['id']),context.display_type(meta_id=x['id']))).replace('<','<!--').replace('>','-->')) for x in l]"
				,"return l"]
			,"mandatory":1
			,"multilang":0
			,"name":"Type(s)"
			,"repetitive":0
			,"type":"multiselect"}

		record_attr_ids = {"default":""
			,"id":"record_attr_ids"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Attribute(s) [id:type,...]"
			,"repetitive":0
			,"type":"string"}

		record_order_default = {"default":""
			,"id":"record_order_default"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Sort-Order (Default) [id:asc|desc]"
			,"repetitive":0
			,"type":"string"}

		effective_standard_html = {"default":"<!-- effective_standard_html(default) -->\n\n<tal:block tal:define=\"zmscontext context\">\n\n<script src=\"/++resource++zms_/jquery/plugin/jquery.plugin.zmi_highlight.js\"></script>\n<script>\n$(function() {\n	var applyListFilter = function() {\n			var filter = $('input.filter').val().toLowerCase().trim();\n			var v = filter;\n			var regexp = new RegExp('<span class=\"highlight(.*?)\">(.*?)</span>', \"gi\");\n			$(\".card .card-header.matched\").removeClass(\"matched\").each(function() {\n					var html = $(this).html();\n					html = html.replace(regexp,'$2');\n					$(this).html(html);\n				});\n			if (v.length>0) {\n				$(\".card .card-header a\").each(function() {\n						if ($(this).text().toLowerCase().indexOf(v)>=0) {\n							htmlReplace($(this),'('+v+')','<span class=\"highlight\">$1</span>');\n							$(this).parent(\".card-header\").addClass(\"matched\");\n						}\n					});\n			}\n			$(\".card\").each(function() {\n					if ($(this).text().toLowerCase().indexOf(v)>=0) {\n						$(this).show();\n					}\n					else {\n						$(this).hide();\n					}\n				});\n			$(window).trigger('resize');\n		};\n	var t = null;\n	$('input.filter').focus().keyup(function(e) {\n		var that = this;\n		if (t != null) {\n			clearTimeout(t);\n		}\n		t = setTimeout(applyListFilter, 500);\n	});\n});\n</script>\n\n	<form class=\"form-filter\" method=\"get\" tal:attributes=\"action request/URL\">\n		<div class=\"row\">\n			<div class=\"col-md-12\">\n				<div class=\"input-group\">\n					<div class=\"input-group-prepend\">\n						<span class=\"input-group-text\"><i class=\"fas fa-filter\"></i> <span class=\"badge badge-pill badge-info\">0</span></span>\n					</div>\n					<input type=\"text\" class=\"form-control filter\" name=\"search\" placeholder=\"Filter\"/>\n				</div><!-- .input-group -->\n			</div>\n		</div><!-- .row -->\n	</form>\n\n	<div class=\"ZMSObjectSet accordion\" tal:define=\"recordSet python:zmscontext.getSelf().evalMetaobjAttr('recordSet_Prepare')\">\n		<div class=\"card\" tal:repeat=\"record recordSet\">\n			<h3 class=\"card-header\" tal:define=\"childNode python:zmscontext.operator_getattr(zmscontext,record['__id__'])\">\n				<a tal:attributes=\"href python:childNode.getHref2IndexHtml(request,deep=False); class python:childNode.meta_id;\" tal:content=\"python:childNode.getTitle(request)\">\n					the title\n				</a>\n			</h3><!-- .card-header -->\n		</div><!-- .card -->\n	</div>\n\n</tal:block>\n\n<!-- /effective_standard_html(default) -->"
			,"id":"effective_standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Standard Html"
			,"repetitive":0
			,"type":"text"}

		scriptzmijs = {"default":""
			,"id":"script.zmi.js"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Script ZMI (JS)"
			,"repetitive":0
			,"type":"resource"}

		attr_dc_identifier_doi = {"default":""
			,"id":"attr_dc_identifier_doi"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"DC.Identifier: DOI (Declarative ID)"
			,"repetitive":0
			,"type":"py"}

		interface0 = {"default":""
			,"id":"interface0"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"interface0"
			,"repetitive":0
			,"type":"interface"}

		records = {"default":""
			,"id":"records"
			,"keys":["type(ZMSObject)"
				,"type(ZMSDocument)"]
			,"mandatory":0
			,"multilang":0
			,"name":"Records"
			,"repetitive":1
			,"type":"*"}

		publicrecordsetgrid = {"default":""
			,"id":"publicRecordSetGrid"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Grid record-set."
			,"repetitive":0
			,"type":"py"}

		sortchildnodes = {"default":""
			,"id":"sortChildNodes"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Sort record-set"
			,"repetitive":0
			,"type":"py"}

		recordset_prepare = {"default":""
			,"id":"recordSet_Prepare"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Prepare record-set"
			,"repetitive":0
			,"type":"py"}

		record_attrs = {"default":""
			,"id":"record_attrs"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Record-Attrs"
			,"repetitive":0
			,"type":"py"}

		record_handler = {"default":""
			,"id":"record_handler"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Record-Handler"
			,"repetitive":0
			,"type":"py"}

		record_duplicate = {"default":""
			,"id":"record_duplicate"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Record-Duplicate"
			,"repetitive":0
			,"type":"py"}

		standard_html = {"default":""
			,"id":"standard_html"
			,"keys":[]
			,"mandatory":0
			,"multilang":0
			,"name":"Template: ZMSObjectSet"
			,"repetitive":0
			,"type":"zpt"}
