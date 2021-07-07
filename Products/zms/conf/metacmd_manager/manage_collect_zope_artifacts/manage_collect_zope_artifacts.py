from Products.zms import standard
from Products.zms import zopeutil
from App.Management import Navigation

def manage_collect_zope_artifacts(self, request=None):
	rtn = []
	request = self.REQUEST
	RESPONSE =  request.RESPONSE
	btn = request.form.get('btn')
	came_from = request.get('came_from',request['HTTP_REFERER'])
	if came_from.find('?') > 0:
		came_from = came_from[:came_from.find('?')]


	zope_objects = self.metaobj_manager.valid_zopetypes
	include_paths = []
	exclude_paths = []
	for metaobjId in self.getMetaobjIds():
		for metaobjAttrId in self.getMetaobjAttrIds(metaobjId,types=zope_objects):
			exclude_paths.append(metaobjAttrId)

	def traverse(node,execute):
		rtn = []
		meta_type = node.meta_type
		if node.meta_type in ['Folder']:
			for childNode in node.objectValues():
				rtn.extend(traverse(childNode,execute))
		elif meta_type in zope_objects:
			path = '/'.join(node.getPhysicalPath())[len('/'.join(self.getHome().getPhysicalPath()))+1:]
			if path not in exclude_paths:
				i = {}
				i['path'] = path
				i['node'] = node
				i['status'] = []
				if execute and path in request.get('ids',[]):
					id = request['meta_id']
					oldId = None
					newId = path
					newName = path
					newType = node.meta_type
					newCustom = zopeutil.readData(node)
					if type(newCustom) is not str:
						newCustom = str(newCustom)
					self.metaobj_manager.setMetaobjAttr(id=id, oldId=oldId, newId=newId, newName=newName, newType=newType, newCustom=newCustom)
					i['status'].append(newId)
				rtn.append(i)
		return rtn

	execute = request.get('btn')=='Collect'
	t = traverse(self.getHome(),execute)

	rtn.append('<!DOCTYPE html>')
	rtn.append('<html>')
	rtn.append(self.zmi_html_head(self,request))
	rtn.append('<body class="%s">'%(' '.join(['zmi',request['lang'],self.meta_id])))
	rtn.append(self.zmi_body_header(self,request,options=[{'action':'#','label':'Collect Artifacts'}]))
	rtn.append('<div id="zmi-tab">')
	rtn.append(self.zmi_breadcrumbs(self,request))
	rtn.append('<form class="form-horizontal pt-3" method="post" enctype="multipart/form-data">')
	rtn.append('<input type="hidden" name="lang" value="%s"/>'%request['lang'])
	rtn.append('<input type="hidden" name="came_from" value="%s"/>'%came_from)
	rtn.append('<p class="zmi_help alert alert-info"><b>Transfer Zope Artifacts to a ZMS Content-Object Library:</b> Please make sure, that the ZMS Content-Object Library you want to place the Zope objects is existing in the select list. If not, please change to the <a target="_blank" href="../content/metaobj_manager/manage_main">ZMS Content Object Menu</a> first, add a new one and refresh this page. After selecting the ZMS Lib as a target then select one more items from the Zope artifact list below. To start the transfer, please click the button <i>Collect</i>.</p>')

	# --- Cancel.
	# ---------------------------------
	if btn==self.getZMILangStr('BTN_CANCEL'):
		request.response.redirect(self.url_append_params(came_from,{'lang':request['lang']}))

	# --- Form.
	# ---------------------------------
	rtn.append('<div class="form-group py-3" id="meta_id">')
	rtn.append('<div class="col-12">')
	rtn.append('<select class="form-control" name="meta_id">')
	rtn.append('<option value="">--- Content-Object Library... ---</option>')
	for metaobjId in standard.sort_list(self.getMetaobjIds()):
		metaobj = self.getMetaobj(metaobjId)
		if metaobj['type'] in ['ZMSLibrary']:
			rtn.append('<option value="%s"%s>%s</option>'%(metaobjId,['',' selected="selected"'][request.get('meta_id')==metaobjId],metaobjId))
	rtn.append('</select>')
	rtn.append('</div>')
	rtn.append('</div><!-- .form-group -->')

	rtn.append('<div class="form-group">')
	rtn.append('<div class="col-12 save">')
	rtn.append('<button type="submit" name="btn" class="btn btn-primary" value="Collect">%s</button>'%('Collect'))
	rtn.append('<button type="submit" name="btn" class="btn btn-default" value="BTN_REFRESH">%s</button>'%(self.getZMILangStr('BTN_REFRESH')))
	rtn.append('<button type="submit" name="btn" class="btn btn-default" value="BTN_CANCEL">%s</button>'%(self.getZMILangStr('BTN_CANCEL')))
	rtn.append('</div><!-- .col-12 -->')
	rtn.append('</div><!-- .form-group -->')

	rtn.append('<table class="table table-bordered table-striped">')
	rtn.append('<thead>')
	rtn.append('<tr>')
	rtn.append('''<th class="text-center">
					<span class="btn btn-default" title="%s/%s" onclick="zmiToggleSelectionButtonClick(this)"><i class="icon-check fas fa-check"></i></span>
				</th>'''%(self.getZMILangStr('BTN_SLCTALL'),self.getZMILangStr('BTN_SLCTNONE')))
	rtn.append('<th class="w-100">Objekt</th>')
	rtn.append('<th>Status</th>')
	rtn.append('</tr>')
	rtn.append('</thead>')
	rtn.append('<tbody>')
	rtn.append('\n'.join(['<tr><td class="text-center"><input type="checkbox" name="ids:list" value="%s" checked="checked"/></td><td><a href="%s/manage_main" target="_blank"><span title="%s"><i class="%s"></i></span> %s</a></td><td>%s</td></tr>'%(
			x['path'],
			x['path'],
			x['node'].meta_type,
			x['node'].zmi_icon,
			x['path'],
			'<br>'.join(x['status']),
			) for x in t]))
	rtn.append('</tbody>')
	rtn.append('</table><!-- .table -->')

	# ---------------------------------

	rtn.append('</form><!-- .form-horizontal -->')
	rtn.append('</div><!-- #zmi-tab -->')
	try:
		rtn.append(self.zmi_body_footer(self,request))
	except:
		rtn.append('<pre>ERROR:zmi_body_footer</pre>')
	rtn.append("""<script>$(function() {
	$(".table tr").each(function() {
			var $tr = $(this);
			if ($(".state.bg-success,.arrow-left",$tr).length > 0) {
				$("input:checkbox",$tr).remove();
				$tr.addClass("bg-danger");
			}
		});
	var can_commit = $(".table tr input:checkbox:visible").length > 0;
	if (!can_commit) {
		$("#Commit-message,#toggle-checkboxes,button[value='Commit']").hide();
	}
});</script>""")
	try:
		rtn.append(Navigation.manage_page_footer(self,request))
	except:
		rtn.append('<pre>ERROR:manage_page_footer</pre>')
	rtn.append('</body>')
	rtn.append('</html>')

	return '\n'.join(rtn)