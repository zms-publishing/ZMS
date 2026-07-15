import os
from Products.zms import _fileutil 

def manage_exportZodbNative2LocalFS( self):
	request = self.REQUEST
	request.set('lang',request.get('lang',self.getPrimaryLanguage()))
	zope_objects = {'DTML Method':'.dtml','Page Template':'.zpt','File':'','Image':'','Script (Python)':'.py','Z SQL Method':'.zsql'}


	# ------------------------------------------------------------
	# Helper functions
	# ------------------------------------------------------------
	def normalize(path):
		path = path.replace('\\', '/')
		if path != '/':
			path = path.rstrip('/')
		return path or '/'

	def find_node_by_physical_path(node, target_path):
		path = '/'.join(node.getPhysicalPath())
		if path == target_path:
			return node
		if node.meta_type in ['Folder','ZMS','ZMSMetacmdProvider','ZMSMetamodelProvider','ZMSWorkflowProvider']:
			for child in node.objectValues():
				found = find_node_by_physical_path(child, target_path)
				if found is not None:
					return found
		return None

	def build_export_filepath(node, start_node, target_base_path, replicate_path_segments):
		node_path = normalize('/'.join(node.getPhysicalPath()))
		start_path = normalize('/'.join(start_node.getPhysicalPath()))

		if replicate_path_segments:
			rel_path = node_path
		elif node_path == start_path:
			rel_path = ''
		elif node_path.startswith(start_path + '/'):
			rel_path = node_path[len(start_path):]
		else:
			rel_path = node_path

		return (target_base_path + rel_path + zope_objects[node.meta_type]).replace('\\','/')
	
	def traverse(node,execute):
		rtn = []
		meta_type = node.meta_type
		if meta_type in zope_objects.keys():
			i = {}
			i['node'] = node
			i['status'] = []
			if execute and '/'.join(node.getPhysicalPath()) in request.get('ids',[]):
				filepath = build_export_filepath(node, start_node, target_path, replicate_path_segments)
				_fileutil.exportObj(node,filepath)
				i['status'].append('<span class="badge badge-success">Done</span> <span class="text-truncate">'+filepath+'</span>')
			rtn.append(i)
		if node.meta_type in ['Folder','ZMS','ZMSMetacmdProvider','ZMSMetamodelProvider','ZMSWorkflowProvider']:
			for childNode in node.objectValues():
				rtn.extend(traverse(childNode,execute))
		return rtn
	# ------------------------------------------------------------
	

	# ------------------------------------------------------------
	# Main
	# ------------------------------------------------------------

	# Basic parameter handling
	execute = request.get('btn')=='execute'
	zodb_path = request.get('zodb_path','/'.join(self.getHome().getPhysicalPath()))
	target_path = normalize(request.get('path',self.getINSTANCE_HOME()+'/var'))
	replicate_path_segments = str(request.get('replicate_path_segments', '1')).lower() in ['1','true','on','yes']
	start_node = find_node_by_physical_path(self.getHome(), normalize(zodb_path))

	if start_node is None:
		if execute:
			return self.str_json([['Error: Source ZODB path not found: %s' % zodb_path]])
		t = []
	else:
		t = traverse(start_node,execute)

	if execute:
		return self.str_json([x['status'] for x in t if x['status']])


	# ------------------------------------------------------------
	# HTML generation
	# ------------------------------------------------------------

	html_style = '''<style>
		#zmi-tab table.table td {
			max-width: 50vw;
			white-space: nowrap;
		}
		#zmi-tab table.table td .text-truncate {
			display: inline-block;
			max-width: calc(50vw - 10rem);
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
			vertical-align: bottom;
		}
		#zmi-tab table.table th.text-center,
		#zmi-tab table.table td.text-center {
			text-align: center !important;
		}
		</style>
		'''

	html_script = """<script>
		function btn_refresh_click() {
			var form = document.createElement('form');
			form.method = 'post';
			form.action = 'manage_exportZodbNative2LocalFS';

			var pathInput = document.createElement('input');
			pathInput.type = 'hidden';
			pathInput.name = 'path';
			pathInput.value = $("input[name=path]").val();
			form.appendChild(pathInput);

			var zodbPathInput = document.createElement('input');
			zodbPathInput.type = 'hidden';
			zodbPathInput.name = 'zodb_path';
			zodbPathInput.value = $("input[name=zodb_path]").val();
			form.appendChild(zodbPathInput);

			document.body.appendChild(form);
			form.submit();
			return false;
		};

		function btn_execute_click() {
			var replicate_path_segments = $("input[name='replicate_path_segments']").is(':checked') ? '1' : '0';
			$("input[name='ids:list']:checked").each( function() {
				var v = $(this).attr("value");
				var $td = $("td:last",$(this).parents("tr")[0]);
				var p = {'btn':'execute','ids:list':v,'path':$("input[name=path]").val(),'zodb_path':$("input[name=zodb_path]").val(),'replicate_path_segments':replicate_path_segments};
				$.ajax({
					url:'manage_exportZodbNative2LocalFS',
					data:p,
					timeout:30000,
					error: function (xhr, ajaxOptions, thrownError) {
						$td.html(''
							+ '<span class="badge badge-danger">' + getZMILangStr('CAPTION_ERROR')+'</span> '
							+ '<code>' + xhr.status + ': ' + thrownError + '</code>');
					},
					success:function(response) {
						var l = eval('('+response+')');
						$td.html(l.join('<br>'));
					}
				});
			});
			return false;
		}
		</script>
		"""
	
	# Generate result rows with export status for each relevant ZODB object
	table_rows = '\n'.join([
		'''
			<tr>
				<td class="text-center bg-light"><input type="checkbox" name="ids:list" value="%s" checked="checked"/></td>
				<td><a href="%s/manage_main" target="_blank" class="text-truncate">%s%s</a> (%s)</td>
				<td>%s</td>
			</tr>
		'''%(
			'/'.join(x['node'].getPhysicalPath()),
			'/'.join(x['node'].getPhysicalPath()),
			'/'.join(x['node'].getPhysicalPath()),
			zope_objects[x['node'].meta_type],
			x['node'].meta_type,
			'<br>'.join(x['status']),
			) for x in t])


	# Build HTML structure with form and table containing export results
	html = f'''<!DOCTYPE html>
		<html lang="en">
		{self.zmi_html_head(self,request)}
		{html_script}
		{html_style}
		<body class="{' '.join(['zmi',request['lang'],self.meta_id])}">
		{self.zmi_body_header(self,request,options=[{'action':'#','label':'Export ZODB to LocalFS...'}])}
			<div id="zmi-tab">
				{self.zmi_breadcrumbs(self,request)}
				<form class="form-horizontal" method="post" enctype="multipart/form-data">
					<div class="card">
						<legend>Export ZODB Objects to Local Filesystem</legend>
						<div class="form-group row card-body pb-0">
							<label class="col-sm-2 control-label mandatory">
								<span>Source ZODB Path</span>
							</label>
							<div class="col-sm-10">
								<input class="form-control zmi-code text-primary" id="zodb_path" name="zodb_path" value="{zodb_path}">
							</div>
						</div>
						<div class="form-group row card-body pt-0">
							<label class="col-sm-2 control-label">
								<span>Path Handling</span>
							</label>
							<div class="col-sm-10">
								<div class="form-check">
									<input class="form-check-input" type="checkbox" id="replicate_path_segments" name="replicate_path_segments" value="1" {['', 'checked="checked"'][int(replicate_path_segments)]}>
									<label class="form-check-label" for="replicate_path_segments">Replicate source ZODB path segments in target filesystem path</label>
								</div>
								<small class="form-text text-muted">Unchecked: selected source node becomes filesystem export root.</small>
							</div>
						</div>
						<div class="form-group row card-body">
							<label class="col-sm-2 control-label mandatory"><span>Target Filesystem Path</span></label>
							<div class="col-sm-10">
								<input class="form-control zmi-code" id="path" name="path" value="{target_path}">
							</div>
						</div>
						<div class="form-row">
							<div class="controls save">
								<button type="button" name="btn" class="btn btn-secondary" value="BTN_REFRESH" 
									onclick="return btn_refresh_click()">
									{self.getZMILangStr('BTN_REFRESH')}
								</button>
								<button type="button" name="btn" class="btn btn-danger" value="BTN_EXECUTE" 
									onclick="btn_execute_click()">
									{self.getZMILangStr('BTN_EXECUTE')}
								</button>
							</div>
						</div>
						<table class="table">
							<tr>
								<th class="text-center" style="width: 5rem;">
									<div class="btn-group">
										<span class="btn btn-secondary" 
											title="{self.getZMILangStr('BTN_SLCTALL')}/{self.getZMILangStr('BTN_SLCTNONE')}" 
											onclick="zmiToggleSelectionButtonClick(this)">
											<i class="fas fa-check-square"></i>
										</span>
									</div>
								</th>
								<th class="align-middle" style="max-width: calc(50% - 5rem)">Objekt</th>
								<th class="align-middle" style="max-width: calc(50% - 5rem)">Status</th>
							</tr>
							{table_rows}
						</table>
					</div>
				</form>
			</div>
			{self.zmi_body_footer(self,request)}
		</body>
		</html>'''

	# Assemble and return the complete HTML
	return html