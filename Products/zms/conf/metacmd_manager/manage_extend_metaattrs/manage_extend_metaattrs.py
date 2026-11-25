from Products.zms import standard

def manage_extend_metaattrs(self, request=None):
	request = request or self.REQUEST
	RESPONSE = request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from', request.get('HTTP_REFERER', ''))
	if '?' in came_from:
		came_from = came_from[:came_from.find('?')]

	metaobj_manager = self.metaobj_manager
	attr_id = request.get('attr_id', '').strip()
	attr_name = request.get('attr_name', '').strip()
	attr_type = request.get('attr_type', '').strip()
	attr_mandatory = int(request.get('attr_mandatory:int', request.get('attr_mandatory', 0)) or 0)
	attr_multilang = int(request.get('attr_multilang:int', request.get('attr_multilang', 0)) or 0)
	attr_repetitive = int(request.get('attr_repetitive:int', request.get('attr_repetitive', 0)) or 0)
	attr_values = request.get('attr_values', '')
	selected_ids = request.get('ids', [])
	if isinstance(selected_ids, str):
		selected_ids = [selected_ids]

	status = []
	execute = btn == 'Add'
	if execute:
		if not attr_id:
			status.append('<span class="text-danger">Meta-attribute ID is required.</span>')
		elif not attr_name:
			status.append('<span class="text-danger">Meta-attribute display name is required.</span>')
		elif not attr_type:
			status.append('<span class="text-danger">Meta-attribute type is required.</span>')
		else:
			if isinstance(attr_values, str):
				attr_values = attr_values.replace('\r\n', '\n').replace('\r', '\n')
			key_types = ['autocomplete', 'multiautocomplete', 'multiselect', 'select']
			if attr_type in key_types:
				attr_keys = [key for key in attr_values.split('\n') if key]
				attr_custom = ''
				attr_default = ''
			elif attr_type in ['method', 'py', 'zpt', 'interface', 'resource', 'constant']:
				attr_keys = []
				attr_custom = attr_values
				attr_default = ''
			else:
				attr_keys = []
				attr_custom = ''
				attr_default = attr_values

			metaobj_manager.setMetadictAttr(
				None,
				attr_id,
				0,
				attr_name,
				attr_type,
				attr_mandatory,
				attr_multilang,
				attr_repetitive,
				attr_custom,
				attr_keys,
				attr_default,
			)
			status.append('Added meta-attribute <b>%s</b> to the meta-dictionary.' % attr_id)

			for metaobj_id in selected_ids:
				metaobj = metaobj_manager.getMetaobj(metaobj_id)
				if metaobj and metaobj.get('type') in ['ZMSDocument', 'ZMSObject']:
					metaobj_manager.setMetaobjAttr(
						metaobj_id,
						None,
						attr_id,
						attr_name,
						attr_mandatory,
						attr_multilang,
						attr_repetitive,
						attr_id,
						attr_keys,
						attr_custom,
						attr_default,
					)
					status.append('Added attribute to <b>%s</b>.' % metaobj_id)

	if btn in ['BTN_CANCEL', self.getZMILangStr('BTN_CANCEL')]:
		RESPONSE.redirect(standard.url_append_params(came_from, {'lang': request['lang']}))
		return ''

	metaobject_ids = [
		metaobj_id
		for metaobj_id in metaobj_manager.getMetaobjIds(sort=True)
		if metaobj_manager.getMetaobj(metaobj_id).get('type') in ['ZMSDocument', 'ZMSObject']
	]

	rtn = []
	rtn.append('<!DOCTYPE html>')
	rtn.append('<html>')
	rtn.append(self.zmi_html_head(self, request))
	rtn.append('<body class="%s">' % (' '.join(['zmi', request['lang'], self.meta_id])))
	rtn.append(self.zmi_body_header(
		self,
		request,
		options=[{'action': '#', 'label': 'Extend Model Attributes'}],
	))
	rtn.append('<div id="zmi-tab" class="p-0" style="min-height: unset;">')
	rtn.append(self.zmi_breadcrumbs(self, request))
	rtn.append('<form class="form-horizontal card" method="post" enctype="multipart/form-data">')
	rtn.append('<input type="hidden" name="lang" value="%s"/>' % request['lang'])
	rtn.append('<input type="hidden" name="came_from" value="%s"/>' % standard.html_quote(came_from))
	rtn.append('<legend>Extend Model Attributes: <span class="font-weight-normal">Define a new meta-dictionary attribute and add it to selected PAGE or PAGELEMENT meta-object classes.</span></legend>')

	if status:
		rtn.append('''
			<div class="alert alert-info m-2">%s<br/><br/>
			IMPORTANT HINT: Now switch to 
			<a href="%s/content/metaobj_manager/manage_metas" target="_blank">Meta-Attribute-Manager</a> 
			and save the new model finally.</div>'''%('<br/>'.join(status),self.getHome().absolute_url())
		)

	rtn.append('<div class="card-body table-responsive p-0">')
	rtn.append('<table class="table table-striped table-bordered table-sm mb-0"><thead><tr>')
	rtn.append('''
		<th class="pl-3">Id</th>
		<th>Display</th>
		<th>Type</th>
		<th class="text-center" title="Mandatory"><i class="fas fa-exclamation-circle"></i></th>
		<th class="text-center" title="Multilang"><i class="fas fa-globe"></i></th>
		<th class="text-center" title="Repetitive"><i class="fas fa-list-ol"></i></th>
		<th>Default values / code</th>'''
	)
	rtn.append('</tr></thead><tbody><tr>')
	rtn.append('<td><input class="form-control form-control-sm" id="attr_id" name="attr_id" value="%s" required="required"/></td>' % standard.html_quote(attr_id))
	rtn.append('<td><input class="form-control form-control-sm" id="attr_name" name="attr_name" value="%s" required="required"/></td>' % standard.html_quote(attr_name))
	rtn.append('<td><select class="form-control form-control-sm" id="attr_type" name="attr_type"><option value="">--- Type ---</option>')
	for datatype in metaobj_manager.valid_datatypes:
		rtn.append('<option value="%s"%s>%s</option>' % (
			datatype,
			' selected="selected"' if attr_type == datatype else '',
			datatype,
		))
	rtn.append('<option value="" disabled="disabled">--- Objects ---</option>')
	for metaobj_id in metaobj_manager.getMetaobjIds(sort=True, excl_ids=['ZMS']):
		rtn.append('<option value="%s"%s>%s</option>' % (
			metaobj_id,
			' selected="selected"' if attr_type == metaobj_id else '',
			metaobj_manager.display_type(meta_id=metaobj_id),
		))
	rtn.append('</select></td>')
	rtn.append('</td>')
	rtn.append('<td class="text-center"><input type="checkbox" id="attr_mandatory" name="attr_mandatory:int" value="1"%s/></td>' % (' checked="checked"' if attr_mandatory else ''))
	rtn.append('<td class="text-center"><input type="checkbox" id="attr_multilang" name="attr_multilang:int" value="1"%s/></td>' % (' checked="checked"' if attr_multilang else ''))
	rtn.append('<td class="text-center"><input type="checkbox" id="attr_repetitive" name="attr_repetitive:int" value="1"%s/></td>' % (' checked="checked"' if attr_repetitive else ''))
	rtn.append('<td><textarea class="form-control form-control-sm text-monospace mb-5" id="attr_values" name="attr_values" rows="3" title="Enter default values line-by-line or executable code">%s</textarea></td>' % standard.html_quote(attr_values))
	rtn.append('</tr></tbody></table>')
	rtn.append('</div>')

	rtn.append('<legend>Target Meta-Object Classes</legend>')
	rtn.append('<div class="card-body">')
	rtn.append('<div class="mb-3"><button type="button" class="btn btn-secondary" id="toggle-metaobjects" title="Toggle Selection"><i class="fas fa-check-square text-primary"></i></button></div>')
	rtn.append('<div class="row pl-5">')
	for metaobj_id in metaobject_ids:
		metaobj = metaobj_manager.getMetaobj(metaobj_id)
		checked = ' checked="checked"' if metaobj_id in selected_ids or (not execute and not selected_ids) else ''
		rtn.append('''
			<div class="col-md-4">
				<div class="custom-control custom-checkbox mb-2">
					<input class="custom-control-input" type="checkbox" id="meta_%s" name="ids:list" value="%s"%s/>
					<label class="custom-control-label" for="meta_%s">
						<a class="text-body" href="%s" target="_blank" 
							onmouseover="showModelPreview(event)" onmouseout="hideModelPreview()"
							data-preview-url="%s">
							%s
						</a>
					</label>
				</div>
			</div>''' % (
			standard.url_quote(metaobj_id),
			metaobj_id,
			checked,
			standard.url_quote(metaobj_id),
			'%s/manage_main?id=%s'%(metaobj_manager.absolute_url(),metaobj_id),
			'metaobj_manager/manage_bigpicture?id=%s&lang=%s&content_type=htmx'%(metaobj_id,self.REQUEST['lang']),
			standard.html_quote(metaobj.get('name', metaobj_id))
		))
	rtn.append('</div>')
	rtn.append('</div>')
	rtn.append('</div>')

	rtn.append('<div class="controls save my-3">')
	rtn.append('<button type="submit" name="btn" class="btn btn-primary" value="Add">Add</button>')
	rtn.append('<button type="submit" name="btn" class="btn btn-secondary ml-2" value="BTN_CANCEL">%s</button>' % self.getZMILangStr('BTN_CANCEL'))
	rtn.append('</div>')

	rtn.append('</form>')
	rtn.append('</div><!-- #zmi-tab -->')
	rtn.append("""
	<style>
		div.custom-checkbox a.text-body:hover {
			text-decoration: none;
			font-weight: bold;
			color: #0056b3 !important;
	</style>
	<script>
		$(function() {
			$("#toggle-metaobjects").on("click", function() {
				var checkboxes = $('input[name="ids:list"]');
				checkboxes.prop("checked", !checkboxes.filter(":checked").length);
			});
		});

		/**
		* Model Preview Popup.
		*/
		function showModelPreview(event) {
			const modelpreview = document.getElementById('modelpreview');
			// if the element is too close to the bottom edge of the viewport 
			// add extra space to the footer.
			if (event.pageY + 300 >  window.innerHeight) {
				document.querySelector('footer').style.marginTop= 300 + 'px';
			}
			modelpreview.style.display = 'block';
			modelpreview.style.left = event.pageX + 10 + 'px';
			modelpreview.style.top = event.pageY + 10 + 'px';
			// Load preview via fetch (no htmx => no history/URL change).
			const url = event.currentTarget.getAttribute('data-preview-url');
			if (window.lastModelPreviewUrl === url) return;
			window.lastModelPreviewUrl = url;
			fetch(url, {credentials: 'same-origin'})
				.then(r => r.text())
				.then(html => {
					if (window.lastModelPreviewUrl !== url) return;
					const doc = new DOMParser().parseFromString(html, 'text/html');
					const main = doc.querySelector('main');
					modelpreview.innerHTML = main ? main.innerHTML : html;
				})
				.catch(() => { window.lastModelPreviewUrl = null; });
		}
		function hideModelPreview() {
			document.getElementById('modelpreview').style.display = 'none';
		}

	</script>""")
	rtn.append('<div id="modelpreview" style="position:absolute;display:none;z-index:1000;"></div>')
	rtn.append(self.zmi_body_footer(self, request))
	rtn.append('</body>')
	rtn.append('</html>')

	return '\n'.join(rtn)
